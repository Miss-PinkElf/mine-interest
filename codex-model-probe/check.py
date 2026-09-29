#!/usr/bin/env python3
"""
Codex 降级 / 额度告警 —— 由 Codex hooks 调用。

设计原则：只对「可信信号」发通知，避免误报淹没你。
  - 可信：额度百分比、safety-buffering 模型变化、HTTP 错误码
  - 存疑：response.created.model 与请求模型不一致 —— 只记录，默认不通知
             （无法区分「服务端如实报告降级」和「body 回显请求值」，
               直到有一次真实降级样本才能校准；见 --strict 可强制通知）

用法：
    Codex 会自动以 hook 方式调用（stdin 传 JSON）。
    手动查看最近状态：  python3 ~/.codex-probe/check.py --report
"""
import argparse
import json
import os
import subprocess
import sys
import time

TURNS = os.path.expanduser("~/.codex-probe/turns.jsonl")
STATE = os.path.expanduser("~/.codex-probe/state.json")

# 额度告警阈值（5 小时窗口）
PRIMARY_WARN = 85
PRIMARY_CRIT = 95

# 等待代理写入记录的宽限（秒），用于吸收 hook 与代理的写入竞态
GRACE_SECONDS = 2.0


def notify(title, message):
    """macOS 桌面通知。失败静默——通知不该影响 Codex 运行。"""
    try:
        script = (
            'display notification {} with title {} sound name "Funk"'
        ).format(json.dumps(message), json.dumps(title))
        subprocess.run(["osascript", "-e", script],
                       timeout=5, capture_output=True)
    except Exception:
        pass


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(s):
    try:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def read_turns():
    out = []
    try:
        with open(TURNS, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return out


def latest_turn(turns, since_ts=None):
    """最近一条 /responses 记录。"""
    cands = [t for t in turns if t.get("path", "").endswith("/responses")]
    if not cands:
        return None
    cands.sort(key=lambda t: t.get("ts", 0))
    for t in reversed(cands):
        if since_ts is None or t.get("ts", 0) >= since_ts:
            return t
    return cands[-1]


def judge(turn, state, strict=False):
    """返回 (level, title, message) 列表，level ∈ {'alert','info'}"""
    findings = []
    if not turn:
        return findings

    signals = turn.get("signals") or {}
    req_model = turn.get("req_model")

    # --- 1. HTTP 错误 ---
    status = turn.get("status")
    if status and status != 200:
        findings.append(("alert", "Codex 请求异常",
                         "上轮返回 HTTP {}，可能被限流或模型不可用".format(status)))

    # --- 2. 额度（事前预警，最有价值）---
    pct_raw = signals.get("x-codex-primary-used-percent")
    try:
        pct = int(pct_raw)
    except (TypeError, ValueError):
        pct = None
    if pct is not None:
        prev = state.get("primary_used_percent")
        if pct >= PRIMARY_CRIT:
            findings.append(("alert", "Codex 额度告急",
                             "5 小时窗口已用 {}%，降级风险高".format(pct)))
        elif pct >= PRIMARY_WARN and (prev is None or prev < PRIMARY_WARN):
            findings.append(("info", "Codex 额度提示",
                             "5 小时窗口已用 {}%，接近阈值".format(pct)))
        state["primary_used_percent"] = pct

    # --- 3. safety-buffering 模型变化 ---
    sb_model = signals.get("x-codex-safety-buffering-faster-model")
    sb_prev = state.get("safety_buffering_model")
    if sb_model and sb_prev and sb_model != sb_prev:
        findings.append(("info", "Codex 缓冲模型变化",
                         "safety buffering 模型 {} → {}".format(sb_prev, sb_model)))
    if sb_model:
        state["safety_buffering_model"] = sb_model

    # --- 4. 模型不一致（存疑，默认只记录）---
    created = (turn.get("response.created") or {}).get("model")
    if req_model and created and created != req_model:
        entry = {"ts": turn.get("ts"), "requested": req_model, "served": created}
        state.setdefault("model_mismatches", []).append(entry)
        state["model_mismatches"] = state["model_mismatches"][-20:]
        if strict:
            findings.append(("alert", "Codex 模型不一致",
                             "请求 {}，服务端标注 {}".format(req_model, created)))

    # --- 5. 记录档位 ---
    plan = signals.get("x-codex-plan-type")
    if plan:
        state["plan_type"] = plan

    return findings


def server_model(turn):
    """服务端在 SSE 里标注的模型。没有则返回 None。"""
    if not turn:
        return None
    for key in ("response.completed", "response.created"):
        model = (turn.get(key) or {}).get("model")
        if model:
            return model
    return None


def actual_model_line(turn):
    """底部状态栏风格的一行：实际 model:xxxx。"""
    if not turn:
        return "实际 model: 未采集到"
    served = server_model(turn)
    requested = turn.get("req_model")
    if served and requested and served != requested:
        return "实际 model: {} · 请求 {}".format(served, requested)
    if served:
        return "实际 model: {}".format(served)
    if requested:
        return "实际 model: {} · 仅请求侧".format(requested)
    return "实际 model: 未采集到"


def actual_model_message(turn, findings):
    parts = [actual_model_line(turn)]
    parts.extend(message for _, _, message in findings)
    return " · ".join(parts)


def do_report():
    turns = read_turns()
    turn = latest_turn(turns)
    state = load_state()
    if not turn:
        print("暂无记录。确认探测代理已启动，并已按文档配置 config.toml。")
        return 0
    signals = turn.get("signals") or {}
    print("=" * 58)
    print("最近一轮 Codex 请求")
    print("=" * 58)
    print("  时间          :", time.strftime("%Y-%m-%d %H:%M:%S",
                                            time.localtime(turn.get("ts", 0))))
    print("  HTTP 状态     :", turn.get("status"))
    print("  请求模型      :", turn.get("req_model"))
    print("  服务端标注模型:", server_model(turn))
    print(" ", actual_model_line(turn))
    print("  首字节/总时长 : {} ms / {} ms".format(
        turn.get("first_chunk_ms"), turn.get("total_stream_ms")))
    print("  --- 服务端信号 ---")
    for k in sorted(signals):
        print("    {}: {}".format(k, signals[k]))
    print("  --- 累计状态 ---")
    print("  计划类型      :", state.get("plan_type"))
    print("  5h 窗口用量   :", state.get("primary_used_percent"), "%")
    print("  缓冲模型      :", state.get("safety_buffering_model"))
    mm = state.get("model_mismatches") or []
    print("  模型不一致次数:", len(mm))
    for e in mm[-5:]:
        print("     {} → {}".format(e.get("requested"), e.get("served")))
    print()
    print("注意：『服务端标注模型』跟随请求值，无法区分如实报告与回显，")
    print("      在拿到真实降级样本前不要据此下结论。")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="打印最近状态")
    ap.add_argument("--strict", action="store_true",
                    help="模型不一致时也发通知（未校准，谨慎）")
    args = ap.parse_args()

    if args.report:
        return do_report()

    # hook 模式：stdin 有 JSON
    started = time.time()
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        hook_input = {}

    # 等代理把本轮记录落盘，吸收写入竞态
    turns = read_turns()
    turn = latest_turn(turns)
    deadline = started + GRACE_SECONDS
    while time.time() < deadline:
        if turn and turn.get("ts", 0) >= int(started) - 1:
            break
        time.sleep(0.2)
        turns = read_turns()
        turn = latest_turn(turns)

    state = load_state()
    findings = judge(turn, state, strict=args.strict)
    save_state(state)

    for level, title, message in findings:
        if level == "alert":
            notify(title, message)
        elif level == "info":
            notify(title, message)
        print("[{}] {}: {}".format(level, title, message), file=sys.stderr)

    # Stop 的 stdout 必须是 JSON。systemMessage 会显示在 TUI 里。
    # 0.157 的 status_line 只有内置项，不能把这行插进底部状态栏。
    print(json.dumps({"systemMessage": actual_model_message(turn, findings)},
                     ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
