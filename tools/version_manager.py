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

import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

MAX_VERSIONS = 10


def list_versions(shadow_dir: Path) -> list:
    versions_dir = shadow_dir / "versions"
    if not versions_dir.exists():
        return []

    versions = []
    for v_dir in sorted(versions_dir.iterdir()):
        if not v_dir.is_dir():
            continue
        mtime = v_dir.stat().st_mtime
        archived_at = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
        files = [f.name for f in v_dir.iterdir() if f.is_file()]
        versions.append({
            "version": v_dir.name,
            "archived_at": archived_at,
            "files": files,
        })

    return versions


def rollback(shadow_dir: Path, target_version: str) -> bool:
    version_dir = shadow_dir / "versions" / target_version
    if not version_dir.exists():
        print(f"错误：版本 {target_version} 不存在", file=sys.stderr)
        return False

    meta_path = shadow_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        current_version = meta.get("version", "v?")
        backup_dir = shadow_dir / "versions" / f"{current_version}_before_rollback"
        backup_dir.mkdir(parents=True, exist_ok=True)
        for fname in ("shadow.md",):
            src = shadow_dir / fname
            if src.exists():
                shutil.copy2(src, backup_dir / fname)

    restored_files = []
    for fname in ("shadow.md",):
        src = version_dir / fname
        if src.exists():
            shutil.copy2(src, shadow_dir / fname)
            restored_files.append(fname)

    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["version"] = target_version + "_restored"
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        meta["rollback_from"] = current_version
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已回滚到 {target_version}，恢复文件：{', '.join(restored_files)}")
    return True


def cleanup_old_versions(shadow_dir: Path, max_versions: int = MAX_VERSIONS):
    versions_dir = shadow_dir / "versions"
    if not versions_dir.exists():
        return

    version_dirs = sorted(
        [d for d in versions_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
    )
    to_delete = version_dirs[:-max_versions] if len(version_dirs) > max_versions else []
    for old_dir in to_delete:
        shutil.rmtree(old_dir)
        print(f"已清理旧版本：{old_dir.name}")


def main():
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
            for v in versions:
                print(f"  {v['version']}  存档时间: {v['archived_at']}  文件: {', '.join(v['files'])}")

    elif args.action == "rollback":
        if not args.version:
            print("错误：rollback 操作需要 --version", file=sys.stderr)
            sys.exit(1)
        rollback(shadow_dir, args.version)

    elif args.action == "cleanup":
        cleanup_old_versions(shadow_dir)
        print("清理完成")


if __name__ == "__main__":
    main()
