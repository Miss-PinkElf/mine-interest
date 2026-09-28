"""B 站文档预演与迁移（Bilibili Rerender）：默认只读。"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.client import BilibiliClient, FetchError
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.store import Store, atomic_write, image_extension, required_media_urls, write_json
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.sourcehub.bili_ingest import record_to_fragment
from integrations.astrbot.astrbot_plugin_sourcehub_bilibili.sourcehub.vault import Vault

LINK_PATTERN = re.compile(r"\]\((\.\./[^)]+)\)")
BACKUP_FILE_NAMES = {"content.md", "envelope.json"}
CATALOG_FILE = "catalog.sqlite3"


def records(root: Path) -> list[tuple[Path, dict]]:
    result = []
    for path in root.glob("*/items/*/record.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if data.get("source_url"):
            result.append((path, data))
    return sorted(result, key=lambda pair: (str(pair[1].get("attempted_at") or ""), str(pair[0])))


def missing_media(path: Path, record: dict) -> list[str]:
    missing = [
        str(media.get("local_path") or "<无本地文件>")
        for media in record.get("media") or []
        if not media.get("source_url") or not media.get("local_path") or not (path.parent / str(media["local_path"])).is_file()
    ]
    available_urls = {
        str(media.get("source_url") or "")
        for media in record.get("media") or []
        if media.get("local_path") and (path.parent / str(media["local_path"])).is_file()
    }
    missing.extend("<源图片未列入媒体映射>" for _ in required_media_urls(record) - available_urls)
    return missing


def missing_links(vault: Path) -> list[str]:
    broken = []
    for path in (vault / "items" / "bilibili").rglob("content.md"):
        for href in LINK_PATTERN.findall(path.read_text(encoding="utf-8")):
            if not (path.parent / href).is_file():
                broken.append(f"{path.relative_to(vault)}: {href}")
    return broken


def _copy_backup_file(source: str, target: str) -> str:
    if Path(source).name in BACKUP_FILE_NAMES:
        return shutil.copy2(source, target)
    try:
        os.link(source, target)
        return target
    except OSError:
        return shutil.copy2(source, target)


def tree_state(root: Path) -> dict[str, list[int]]:
    return {
        str(path.relative_to(root)): [path.stat().st_size, path.stat().st_mtime_ns]
        for path in root.rglob("*") if path.is_file()
    } if root.exists() else {}


def record_state(root: Path) -> dict[str, list[int]]:
    return {
        str(path.relative_to(root)): [path.stat().st_size, path.stat().st_mtime_ns]
        for path in root.glob("*/items/*/record.json")
    }


def backup_documents(vault: Path, backup: Path, source_records: list[tuple[Path, dict]]) -> None:
    if backup.exists():
        raise FileExistsError("backup_exists")
    source_tree = vault / "items" / "bilibili"
    if source_tree.resolve() in backup.resolve().parents:
        raise ValueError("backup_inside_bilibili_tree")
    if any(path.is_symlink() for path in source_tree.rglob("*")):
        raise ValueError("bilibili_tree_contains_symlink")
    if source_tree.exists():
        shutil.copytree(source_tree, backup / "vault" / "items" / "bilibili", copy_function=_copy_backup_file)
    else:
        (backup / "vault" / "items" / "bilibili").mkdir(parents=True)
    catalog = vault / CATALOG_FILE
    if catalog.exists():
        target = backup / "vault" / catalog.name
        target.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(catalog) as source_db, sqlite3.connect(target) as target_db:
            source_db.backup(target_db)
    for path, _ in source_records:
        target = backup / "records" / path.relative_to(path.parents[3])
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    (backup / "manifest.json").write_text(json.dumps({
        "vault": str(vault.resolve()),
        "archive_root": str(source_records[0][0].parents[3].resolve()),
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def rollback(vault: Path, archive_root: Path, backup: Path) -> None:
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("vault") != str(vault.resolve()) or manifest.get("archive_root") != str(archive_root.resolve()):
        raise ValueError("backup_target_mismatch")
    backup_tree = backup / "vault" / "items" / "bilibili"
    current_tree = vault / "items" / "bilibili"
    applied_state = backup / "post_apply_state.json"
    expected_state = json.loads(applied_state.read_text(encoding="utf-8")) if applied_state.exists() else {}
    if tree_state(current_tree) != expected_state.get("tree") or record_state(archive_root) != expected_state.get("records"):
        raise ValueError("bilibili_tree_changed_after_migration")
    displaced = vault / "items" / ".bilibili-before-rollback"
    record_safety = vault / "spool" / ".bilibili-records-before-rollback"
    if displaced.exists():
        raise FileExistsError("rollback_displaced_tree_exists")
    if record_safety.exists():
        raise FileExistsError("rollback_record_safety_exists")
    for old_record in (backup / "records").rglob("record.json"):
        current_record = archive_root / old_record.relative_to(backup / "records")
        if current_record.exists():
            target = record_safety / old_record.relative_to(backup / "records")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(current_record, target)
    if current_tree.exists():
        current_tree.rename(displaced)
    try:
        shutil.copytree(backup_tree, current_tree)
        for old_record in (backup / "records").rglob("record.json"):
            target = archive_root / old_record.relative_to(backup / "records")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(old_record, target)
        backed_catalog = backup / "vault" / CATALOG_FILE
        if backed_catalog.exists():
            with sqlite3.connect(backed_catalog) as old_db, sqlite3.connect(vault / CATALOG_FILE) as current_db:
                rows = old_db.execute("SELECT item_id, platform, object_key, path, updated_at FROM items WHERE platform = 'bilibili'").fetchall()
                with current_db:
                    current_db.execute("DELETE FROM items WHERE platform = 'bilibili'")
                    current_db.executemany("INSERT INTO items(item_id, platform, object_key, path, updated_at) VALUES (?, ?, ?, ?, ?)", rows)
    except Exception:
        if current_tree.exists():
            shutil.rmtree(current_tree)
        if displaced.exists():
            displaced.rename(current_tree)
        for saved in record_safety.rglob("record.json") if record_safety.exists() else []:
            target = archive_root / saved.relative_to(record_safety)
            shutil.copy2(saved, target)
        raise
    if displaced.exists():
        shutil.rmtree(displaced)
    if record_safety.exists():
        shutil.rmtree(record_safety)


async def fetch_missing_media(source_records: list[tuple[Path, dict]], proxy_url: str = "") -> tuple[int, list[str]]:
    downloaded = 0
    gaps = []
    cache: dict[str, bytes] = {}
    client = BilibiliClient("", proxy_url=proxy_url)
    try:
        for path, record in source_records:
            objects = record.get("objects") or []
            first = objects[0] if objects and isinstance(objects[0], dict) else {}
            cover_url = str(first.get("pic") or "") if first.get("bvid") else ""
            media_items = record.setdefault("media", [])
            known_urls = {str(media.get("source_url") or "") for media in media_items}
            for url in sorted(required_media_urls(record) - known_urls):
                media_items.append({"source_url": url})
            changed = False
            for media in media_items:
                relative = media.get("local_path")
                if relative and (path.parent / relative).is_file():
                    continue
                url = str(media.get("source_url") or "")
                if not url:
                    gaps.append(f"{path.parent.name}: media_source_missing")
                    continue
                try:
                    data = cache.get(url)
                    if data is None:
                        data = await client.image(url)
                        cache[url] = data
                    name = hashlib.sha256(data).hexdigest() + image_extension(data)
                    relative = f"media/{name}"
                    atomic_write(path.parent / relative, data)
                    media["local_path"] = relative
                    media.pop("error", None)
                    if url == cover_url:
                        record["cover_url"] = cover_url
                    downloaded += 1
                    changed = True
                except FetchError as exc:
                    gaps.append(f"{path.parent.name}: media_{exc}")
            if changed:
                write_json(path, record)
    finally:
        await client.close()
    return downloaded, gaps


def main() -> int:
    parser = argparse.ArgumentParser(description="B 站资料排版预演；--apply 才更新真实 Vault")
    parser.add_argument("--archive-root", type=Path, required=True, help="B 站插件数据目录")
    parser.add_argument("--vault", type=Path, required=True, help="SourceHub 资料目录")
    parser.add_argument("--apply", action="store_true", help="先备份，再更新真实资料")
    parser.add_argument("--backup-dir", type=Path, help="备份目录；默认与 Vault 同级")
    parser.add_argument("--rollback", type=Path, help="从指定备份恢复 B 站条目树与索引")
    parser.add_argument("--proxy", default="", help="可选本机 HTTP 代理，仅用于补取媒体")
    args = parser.parse_args()
    if args.rollback:
        rollback(args.vault, args.archive_root, args.rollback)
        print("B 站条目树、索引与原始记录已从备份恢复。")
        return 0
    source_records = records(args.archive_root)
    if not source_records:
        print("没有找到可重渲染的 B 站记录。")
        return 1
    bad_media = [(path, missing_media(path, data)) for path, data in source_records]
    bad_media = [(path, gaps) for path, gaps in bad_media if gaps]
    works = {
        (fragment["kind"], fragment["object_id"])
        for _, data in source_records
        if (fragment := record_to_fragment(data))
    }
    covers = sum(bool((data.get("objects") or [{}])[0].get("pic")) and not any(
        media.get("source_url") == (data.get("objects") or [{}])[0].get("pic") and media.get("local_path")
        for media in data.get("media") or []
    ) for _, data in source_records if (data.get("objects") or [{}])[0].get("bvid"))
    current_broken = missing_links(args.vault)
    print(f"记录：{len(source_records)}；作品：{len(works)}；已有媒体缺口：{len(bad_media)}；待补视频封面：{covers}；现有本地断链：{len(current_broken)}")
    if not args.apply:
        print("预演结束；真实资料未修改。")
        return 0
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = args.backup_dir or args.vault.with_name(args.vault.name + f"-bilibili-backup-{stamp}")
    backup_documents(args.vault, backup, source_records)
    downloaded, media_gaps = asyncio.run(fetch_missing_media(source_records, args.proxy))
    blocked_works = set()
    for path, record in source_records:
        if missing_media(path, record):
            fragment = record_to_fragment(record)
            if fragment:
                blocked_works.add((fragment["kind"], fragment["object_id"]))
    print(f"备份：{backup}；已补媒体：{downloaded}；媒体缺口：{len(media_gaps)}；跳过作品：{len(blocked_works)}")
    vault = Vault(args.vault, git_enabled=False)
    count = 0
    try:
        for path, record in source_records:
            fragment = record_to_fragment(record)
            if not fragment or (fragment["kind"], fragment["object_id"]) in blocked_works:
                continue
            store = Store(path.parents[2], vault=vault)
            store._export_vault(record, path.parent)
            count += 1
    finally:
        (backup / "post_apply_state.json").write_text(
            json.dumps({
                "tree": tree_state(args.vault / "items" / "bilibili"),
                "records": record_state(args.archive_root),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    broken = missing_links(args.vault)
    print(f"已重渲染记录：{count}；断链：{len(broken)}")
    return 0 if not broken and not blocked_works else 1


if __name__ == "__main__":
    raise SystemExit(main())
