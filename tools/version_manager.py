#!/usr/bin/env python3
"""
版本管理器 (mindreader-skill)

负责影子文件的版本存档和回滚。

用法：
    python version_manager.py --action list --slug xiaomei --base-dir ./shadows
    python version_manager.py --action rollback --slug xiaomei --version v2 --base-dir ./shadows
    python version_manager.py --action cleanup --slug xiaomei --base-dir ./shadows
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_VERSIONS = 10
VERSIONS_DIR_NAME = "versions"


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except ValueError:
                pass


def _copy_entry(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def _iter_state_entries(shadow_dir: Path) -> list[Path]:
    return [
        entry for entry in shadow_dir.iterdir()
        if entry.name != VERSIONS_DIR_NAME
    ]


def _read_meta(meta_path: Path) -> dict:
    if not meta_path.exists():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def snapshot_current_state(shadow_dir: Path, version_name: str, *, overwrite: bool = False) -> Path:
    versions_dir = shadow_dir / VERSIONS_DIR_NAME
    versions_dir.mkdir(parents=True, exist_ok=True)

    snapshot_dir = versions_dir / version_name
    if snapshot_dir.exists():
        if not overwrite:
            raise FileExistsError(f"版本快照已存在：{version_name}")
        shutil.rmtree(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    for entry in _iter_state_entries(shadow_dir):
        _copy_entry(entry, snapshot_dir / entry.name)

    return snapshot_dir


def list_versions(shadow_dir: Path) -> list[dict]:
    versions_dir = shadow_dir / VERSIONS_DIR_NAME
    if not versions_dir.exists():
        return []

    versions = []
    for version_dir in sorted(
        [entry for entry in versions_dir.iterdir() if entry.is_dir()],
        key=lambda entry: entry.stat().st_mtime,
        reverse=True,
    ):
        archived_at = datetime.fromtimestamp(
            version_dir.stat().st_mtime,
            tz=timezone.utc,
        ).strftime("%Y-%m-%d %H:%M")
        files = sorted(
            str(path.relative_to(version_dir))
            for path in version_dir.rglob("*")
            if path.is_file()
        )
        versions.append({
            "version": version_dir.name,
            "archived_at": archived_at,
            "files": files,
        })

    return versions


def rollback(shadow_dir: Path, target_version: str) -> bool:
    version_dir = shadow_dir / VERSIONS_DIR_NAME / target_version
    if not version_dir.exists():
        print(f"错误：版本 {target_version} 不存在", file=sys.stderr)
        return False

    meta_path = shadow_dir / "meta.json"
    current_meta = _read_meta(meta_path)
    current_version = current_meta.get("version", "v?")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_version = f"{current_version}_before_rollback_{timestamp}"
    snapshot_current_state(shadow_dir, backup_version)

    for entry in _iter_state_entries(shadow_dir):
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()

    restored_files = []
    for entry in version_dir.iterdir():
        destination = shadow_dir / entry.name
        _copy_entry(entry, destination)
        if entry.is_dir():
            restored_files.extend(
                sorted(str(path.relative_to(shadow_dir)) for path in destination.rglob("*") if path.is_file())
            )
        else:
            restored_files.append(entry.name)

    restored_meta = _read_meta(meta_path)
    restored_meta["version"] = f"{target_version}_restored"
    restored_meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    restored_meta["rollback_from"] = current_version
    meta_path.write_text(json.dumps(restored_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已回滚到 {target_version}，恢复文件：{', '.join(sorted(restored_files))}")
    return True


def cleanup_old_versions(shadow_dir: Path, max_versions: int = MAX_VERSIONS) -> None:
    versions_dir = shadow_dir / VERSIONS_DIR_NAME
    if not versions_dir.exists():
        return

    version_dirs = sorted(
        [entry for entry in versions_dir.iterdir() if entry.is_dir()],
        key=lambda entry: entry.stat().st_mtime,
    )
    to_delete = version_dirs[:-max_versions] if len(version_dirs) > max_versions else []
    for old_dir in to_delete:
        shutil.rmtree(old_dir)
        print(f"已清理旧版本：{old_dir.name}")


def main() -> None:
    configure_stdio()

    parser = argparse.ArgumentParser(description="mindreader 影子版本管理器")
    parser.add_argument("--action", required=True, choices=["list", "rollback", "cleanup"])
    parser.add_argument("--slug", required=True, help="影子 slug")
    parser.add_argument("--version", help="目标版本号（rollback 时使用）")
    parser.add_argument("--base-dir", default="./shadows", help="影子根目录")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()
    shadow_dir = base_dir / args.slug

    if not shadow_dir.exists():
        print(f"错误：找不到影子目录 {shadow_dir}", file=sys.stderr)
        sys.exit(1)

    if args.action == "list":
        versions = list_versions(shadow_dir)
        if not versions:
            print(f"{args.slug} 暂无历史版本")
        else:
            print(f"{args.slug} 的历史版本：\n")
            for version in versions:
                files = ", ".join(version["files"]) if version["files"] else "无文件"
                print(f"  {version['version']}  存档时间: {version['archived_at']}  文件: {files}")

    elif args.action == "rollback":
        if not args.version:
            print("错误：rollback 操作需要 --version", file=sys.stderr)
            sys.exit(1)
        if not rollback(shadow_dir, args.version):
            sys.exit(1)

    elif args.action == "cleanup":
        cleanup_old_versions(shadow_dir)
        print("清理完成")


if __name__ == "__main__":
    main()
