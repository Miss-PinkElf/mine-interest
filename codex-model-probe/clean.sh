#!/usr/bin/env bash
#
# 卸掉 Codex 模型探测：
#   1. 停止本机 probe_proxy.py
#   2. 从 ~/.codex/config.toml 删除 probe 路由，以及这份钩子的信任记录
#   3. 删除项目级 .codex/hooks.json，以及全局 ~/.codex/hooks.json
#      config.toml 里写死的全局钩子命令一并删除
#
# 不删除 ~/.codex/.env，不删除 ~/.codex-probe 里的记录，不删除仓库里的脚本。
#
#     ./clean.sh
#
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SRC/.." && pwd)"
CONFIG="${CODEX_CONFIG:-$HOME/.codex/config.toml}"
PROJECT_HOOKS="${PROJECT_HOOKS:-$ROOT/.codex/hooks.json}"
USER_HOOKS="${USER_HOOKS:-$HOME/.codex/hooks.json}"

say() { printf '%s\n' "$*"; }

stop_rc=0
if [ "${CLEAN_SKIP_STOP:-0}" != "1" ]; then
  "$SRC/stop.sh" || stop_rc=$?
else
  say "已跳过停止代理。"
fi

set +e
python3 - "$CONFIG" "$PROJECT_HOOKS" "$USER_HOOKS" <<'PY'
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

config_path, project_hooks, user_hooks = sys.argv[1:4]
PROBE_COMMAND_MARKERS = (
    "codex-model-probe/check.py",
    ".codex-probe/check.py",
)
PROVIDER_RE = re.compile(r"""^model_provider\s*=\s*(['"])probe\1\s*$""")


def say(text):
    print(text)


def is_table_header(text):
    return text.startswith("[") and text.endswith("]")


def remove_matching_tables(text, predicate):
    lines = text.splitlines(keepends=True)
    out = []
    removed = 0
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if is_table_header(stripped) and predicate(stripped[1:-1]):
            removed += 1
            index += 1
            while index < len(lines) and not is_table_header(lines[index].strip()):
                index += 1
            continue
        out.append(lines[index])
        index += 1
    return "".join(out), removed


def remove_empty_table(text, name):
    lines = text.splitlines(keepends=True)
    out = []
    removed = 0
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if is_table_header(stripped) and stripped[1:-1] == name:
            cursor = index + 1
            body_blank = True
            while cursor < len(lines) and not is_table_header(lines[cursor].strip()):
                if lines[cursor].strip():
                    body_blank = False
                    break
                cursor += 1
            if body_blank:
                removed += 1
                index = cursor
                continue
        out.append(lines[index])
        index += 1
    return "".join(out), removed


def strip_probe_provider(text):
    lines = text.splitlines(keepends=True)
    out = []
    removed_key = False
    other_provider = None
    for line in lines:
        stripped = line.strip()
        if PROVIDER_RE.match(stripped):
            removed_key = True
            continue
        match = re.match(r"""^model_provider\s*=\s*(['"])(.+)\1\s*$""", stripped)
        if match and match.group(2) != "probe":
            other_provider = match.group(2)
        out.append(line)
    body = "".join(out)
    body, removed_tables = remove_matching_tables(
        body,
        lambda header: header == "model_providers.probe" or header.startswith("model_providers.probe."),
    )
    return body, removed_key, removed_tables, other_provider


def validate_toml(path):
    candidates = [
        "/opt/homebrew/bin/python3.11",
        "/opt/homebrew/bin/python3.12",
        "/opt/homebrew/bin/python3.13",
        "python3.11",
        "python3.12",
        "python3.13",
    ]
    code = "import tomllib,sys; tomllib.load(open(sys.argv[1],'rb'))"
    for exe in candidates:
        try:
            result = subprocess.run([exe, "-c", code, path], capture_output=True, text=True)
        except OSError:
            continue
        if result.returncode == 0:
            return True, ""
        if "No module named 'tomllib'" in (result.stderr or ""):
            continue
        return False, result.stderr.strip() or "TOML 解析失败"
    return True, ""


def table_name(stripped):
    name = stripped.strip()
    while name.startswith("[") and name.endswith("]"):
        name = name[1:-1].strip()
    return name


def remove_inline_probe_hooks(text):
    """删除 config.toml 里命令指向探测脚本的全局钩子表。"""
    lines = text.splitlines(keepends=True)
    out = []
    removed = 0
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if is_table_header(stripped):
            header = table_name(stripped)
            body = []
            cursor = index + 1
            while cursor < len(lines) and not is_table_header(lines[cursor].strip()):
                body.append(lines[cursor])
                cursor += 1
            body_text = "".join(body)
            if header.startswith("hooks.") and not header.startswith("hooks.state") and command_is_probe(body_text):
                removed += 1
                index = cursor
                continue
        out.append(lines[index])
        index += 1
    updated = "".join(out)
    # 探测命令删掉后，空的 [[hooks.Stop]] 之类分组也去掉。hooks.state 不动。
    lines = updated.splitlines(keepends=True)
    names = [table_name(line.strip()) for line in lines if is_table_header(line.strip())]
    out = []
    removed_empty = 0
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if is_table_header(stripped):
            header = table_name(stripped)
            cursor = index + 1
            body_blank = True
            while cursor < len(lines) and not is_table_header(lines[cursor].strip()):
                if lines[cursor].strip():
                    body_blank = False
                    break
                cursor += 1
            has_child = any(name.startswith(header + ".") for name in names if name != header)
            if body_blank and header.startswith("hooks.") and not header.startswith("hooks.state") and not has_child:
                removed_empty += 1
                index = cursor
                continue
        out.append(lines[index])
        index += 1
    return "".join(out), removed + removed_empty


def clean_config(path):
    if not os.path.isfile(path):
        say("未找到 {}，跳过配置清理。".format(path))
        return 0
    with open(path, encoding="utf-8") as handle:
        original = handle.read()
    updated, removed_key, removed_tables, other_provider = strip_probe_provider(original)
    updated, removed_inline = remove_inline_probe_hooks(updated)
    hooks_paths = [project_hooks, user_hooks]
    removed_state = 0
    for hooks_path in hooks_paths:
        updated, count = remove_matching_tables(
            updated,
            lambda header, target=hooks_path: header.startswith("hooks.state.") and target in header,
        )
        removed_state += count
    has_state_child = any(line.strip().startswith("[hooks.state.") for line in updated.splitlines())
    removed_parent = 0
    if not has_state_child:
        updated, removed_parent = remove_empty_table(updated, "hooks.state")
    if updated == original:
        if other_provider:
            say("config.toml 的 model_provider 是 {}，不是 probe，未改路由。".format(other_provider))
        else:
            say("config.toml 里没有 probe 路由或探测钩子信任记录。")
        return 0
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    backup = path + ".bak-" + stamp
    shutil.copy2(path, backup)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(updated)
    ok, error = validate_toml(path)
    if not ok:
        shutil.copy2(backup, path)
        say("config.toml 改完无法解析，已恢复备份：{}".format(error))
        return 1
    say("已清理 config.toml（备份 {}）。".format(backup))
    if removed_key:
        say("  已删除 model_provider = \"probe\"。")
    elif other_provider:
        say("  model_provider 仍是 {}，未改这个根键。".format(other_provider))
    if removed_tables:
        say("  已删除 [model_providers.probe]。")
    if removed_inline:
        say("  已删除 config.toml 里的全局探测钩子。")
    if removed_state:
        say("  已删除项目级和全局钩子的 hooks.state 信任记录。")
    elif removed_parent:
        say("  已删除空的 [hooks.state]。")
    say("请重启 Codex，正在运行的会话还记着旧路由。")
    return 0


def command_is_probe(command):
    return any(marker in (command or "") for marker in PROBE_COMMAND_MARKERS)


def clean_hooks_file(path, label):
    if not os.path.isfile(path):
        say("{} 不存在，跳过。".format(label))
        return 0
    with open(path, encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            say("{} 不是合法 JSON，未修改：{}".format(label, exc))
            return 1
    if not isinstance(data, dict):
        say("{} 的内容不是对象，未修改。".format(label))
        return 1
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        say("{} 里没有 hooks 对象，未修改。".format(label))
        return 0
    changed = False
    for event in list(hooks.keys()):
        groups = hooks.get(event)
        if not isinstance(groups, list):
            continue
        kept_groups = []
        for group in groups:
            if not isinstance(group, dict):
                kept_groups.append(group)
                continue
            handlers = group.get("hooks")
            if not isinstance(handlers, list):
                kept_groups.append(group)
                continue
            kept = []
            for handler in handlers:
                command = handler.get("command") if isinstance(handler, dict) else ""
                if command_is_probe(command):
                    changed = True
                    continue
                kept.append(handler)
            if kept:
                group = dict(group)
                group["hooks"] = kept
                kept_groups.append(group)
            elif handlers:
                changed = True
        if kept_groups:
            hooks[event] = kept_groups
        else:
            if event in hooks and groups:
                changed = True
            hooks.pop(event, None)
    if not changed:
        say("{} 里没有探测钩子。".format(label))
        return 0
    if hooks:
        data["hooks"] = hooks
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        say("已从 {} 删除探测钩子。".format(label))
        return 0
    os.remove(path)
    say("已删除 {}，里面只剩探测钩子。".format(label))
    return 0


rc = 0
rc = clean_config(config_path) or rc
rc = clean_hooks_file(project_hooks, "项目级钩子 " + project_hooks) or rc
rc = clean_hooks_file(user_hooks, "全局钩子 " + user_hooks) or rc
sys.exit(rc)
PY
file_rc=$?
set -e

if [ "$stop_rc" != "0" ]; then
  say "停止代理未完成，退出码 ${stop_rc}。配置和钩子的清理结果见上方。"
  exit "$stop_rc"
fi
exit "$file_rc"
