#!/usr/bin/env python3
"""
影子管理器 (mindreader-skill)

负责影子文件的创建、更新、列表、删除操作。

用法：
    python shadow_manager.py --action create --slug xiaomei --name 小美 --base-dir ./shadows
    python shadow_manager.py --action update --slug xiaomei --message-count 100 --base-dir ./shadows
    python shadow_manager.py --action list --base-dir ./shadows
    python shadow_manager.py --action delete --slug xiaomei --base-dir ./shadows
    python shadow_manager.py --action get --slug xiaomei --base-dir ./shadows
"""

from __future__ import annotations

import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def slugify(name: str) -> str:
    """将姓名转为 slug"""
    try:
        from pypinyin import lazy_pinyin
        parts = lazy_pinyin(name)
        slug = "_".join(parts)
    except ImportError:
        import unicodedata
        result = []
        for char in name.lower():
            if char.isascii() and (char.isalnum() or char in ("-", "_")):
                result.append(char)
            elif char == " ":
                result.append("_")
        slug = "".join(result)

    import re
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug if slug else "shadow"


def build_identity_string(meta: dict) -> str:
    """从 meta 构建关系描述字符串"""
    profile = meta.get("profile", {})
    parts = []

    gender = profile.get("gender", "")
    age_range = profile.get("age_range", "")
    rel_stage = profile.get("rel_stage", "")
    duration = profile.get("duration", "")
    zodiac = profile.get("zodiac", "")
    mbti = profile.get("mbti", "")

    if gender:
        parts.append(gender)
    if age_range:
        parts.append(age_range)
    if rel_stage and duration:
        parts.append(f"{duration} {rel_stage}")
    elif rel_stage:
        parts.append(rel_stage)
    elif duration:
        parts.append(f"在一起 {duration}")
    if zodiac:
        parts.append(zodiac)
    if mbti:
        parts.append(f"MBTI {mbti}")

    return "，".join(parts) if parts else "关系"


def create_shadow(
    base_dir: Path,
    slug: str,
    meta: dict,
    shadow_content: str,
) -> Path:
    """创建新的影子目录结构"""

    shadow_dir = base_dir / slug
    shadow_dir.mkdir(parents=True, exist_ok=True)

    # 创建子目录
    (shadow_dir / "versions").mkdir(exist_ok=True)
    (shadow_dir / "knowledge" / "chats").mkdir(parents=True, exist_ok=True)

    # 写入 shadow.md
    (shadow_dir / "shadow.md").write_text(shadow_content, encoding="utf-8")

    # 写入 meta.json
    now = datetime.now(timezone.utc).isoformat()
    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)
    meta.setdefault("message_count", 0)

    (shadow_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return shadow_dir


def update_shadow(
    shadow_dir: Path,
    shadow_patch: Optional[str] = None,
    correction: Optional[dict] = None,
    new_message_count: int = 0,
) -> str:
    """更新现有影子，先存档当前版本，再写入更新"""

    meta_path = shadow_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    current_version = meta.get("version", "v1")
    try:
        version_num = int(current_version.lstrip("v").split("_")[0]) + 1
    except ValueError:
        version_num = 2
    new_version = f"v{version_num}"

    # 存档当前版本
    version_dir = shadow_dir / "versions" / current_version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("shadow.md",):
        src = shadow_dir / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    # 应用 shadow patch 或 correction
    if shadow_patch or correction:
        current_shadow = (shadow_dir / "shadow.md").read_text(encoding="utf-8")

        if correction:
            correction_line = (
                f"\n- [{correction.get('scene', '通用')}] "
                f"错误：{correction['wrong']}；"
                f"正确：{correction['correct']}\n"
                f"  来源：用户纠正，{datetime.now().strftime('%Y-%m-%d')}"
            )
            target = "## Correction 记录"
            if target in current_shadow:
                insert_pos = current_shadow.index(target) + len(target)
                rest = current_shadow[insert_pos:]
                skip = "\n\n（暂无记录）"
                if rest.startswith(skip):
                    rest = rest[len(skip):]
                new_shadow = current_shadow[:insert_pos] + correction_line + rest
            else:
                new_shadow = (
                    current_shadow
                    + f"\n\n## Correction 记录\n{correction_line}\n"
                )
            meta["corrections_count"] = meta.get("corrections_count", 0) + 1
        else:
            new_shadow = current_shadow + "\n\n" + shadow_patch

        (shadow_dir / "shadow.md").write_text(new_shadow, encoding="utf-8")

    # 更新消息数量
    if new_message_count:
        meta["message_count"] = meta.get("message_count", 0) + new_message_count

    # 更新 meta
    meta["version"] = new_version
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return new_version


def list_shadows(base_dir: Path) -> list:
    """列出所有已创建的影子"""
    shadows = []

    if not base_dir.exists():
        return shadows

    for shadow_dir in sorted(base_dir.iterdir()):
        if not shadow_dir.is_dir():
            continue
        meta_path = shadow_dir / "meta.json"
        if not meta_path.exists():
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        shadows.append({
            "slug": meta.get("slug", shadow_dir.name),
            "name": meta.get("name", shadow_dir.name),
            "identity": build_identity_string(meta),
            "version": meta.get("version", "v1"),
            "updated_at": meta.get("updated_at", ""),
            "corrections_count": meta.get("corrections_count", 0),
            "message_count": meta.get("message_count", 0),
        })

    return shadows


def delete_shadow(base_dir: Path, slug: str) -> bool:
    """删除影子目录"""
    shadow_dir = base_dir / slug
    if not shadow_dir.exists():
        print(f"错误：找不到影子目录 {shadow_dir}", file=sys.stderr)
        return False

    shutil.rmtree(shadow_dir)
    print(f"[OK] Deleted shadow: {slug}")
    return True


def get_shadow(base_dir: Path, slug: str) -> Optional[dict]:
    """获取影子内容"""
    shadow_dir = base_dir / slug
    if not shadow_dir.exists():
        return None

    shadow_path = shadow_dir / "shadow.md"
    meta_path = shadow_dir / "meta.json"

    if not shadow_path.exists():
        return None

    result = {
        "slug": slug,
        "shadow_content": shadow_path.read_text(encoding="utf-8"),
        "meta": {},
    }

    if meta_path.exists():
        result["meta"] = json.loads(meta_path.read_text(encoding="utf-8"))

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="mindreader 影子管理器")
    parser.add_argument("--action", required=True, choices=["create", "update", "list", "delete", "get"])
    parser.add_argument("--slug", help="影子 slug（用于目录名）")
    parser.add_argument("--name", help="影子称呼")
    parser.add_argument("--meta", help="meta.json 文件路径")
    parser.add_argument("--shadow", help="shadow.md 内容文件路径")
    parser.add_argument("--shadow-patch", help="shadow.md 增量更新内容文件路径")
    parser.add_argument("--message-count", type=int, default=0, help="新增消息数量")
    parser.add_argument("--base-dir", default="./shadows", help="影子根目录（默认：./shadows）")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        shadows = list_shadows(base_dir)
        if not shadows:
            print("暂无已创建的影子")
        else:
            print(f"已创建 {len(shadows)} 个影子：\n")
            for s in shadows:
                updated = s["updated_at"][:10] if s["updated_at"] else "未知"
                print(f"  [{s['slug']}]  {s['name']} — {s['identity']}")
                print(f"    版本: {s['version']}  消息数: {s['message_count']}  纠正次数: {s['corrections_count']}  更新: {updated}")
                print()

    elif args.action == "create":
        if not args.slug and not args.name:
            print("错误：create 操作需要 --slug 或 --name", file=sys.stderr)
            sys.exit(1)

        meta: dict = {}
        if args.meta:
            meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
        if args.name:
            meta["name"] = args.name

        slug = args.slug or slugify(meta.get("name", "shadow"))

        shadow_content = ""
        if args.shadow:
            shadow_content = Path(args.shadow).read_text(encoding="utf-8")

        shadow_dir = create_shadow(base_dir, slug, meta, shadow_content)
        print(f"[OK] Shadow created: {shadow_dir}")

    elif args.action == "update":
        if not args.slug:
            print("错误：update 操作需要 --slug", file=sys.stderr)
            sys.exit(1)

        shadow_dir = base_dir / args.slug
        if not shadow_dir.exists():
            print(f"错误：找不到影子目录 {shadow_dir}", file=sys.stderr)
            sys.exit(1)

        shadow_patch = Path(args.shadow_patch).read_text(encoding="utf-8") if args.shadow_patch else None
        new_version = update_shadow(shadow_dir, shadow_patch, None, args.message_count)
        print(f"[OK] Shadow updated to {new_version}")

    elif args.action == "delete":
        if not args.slug:
            print("错误：delete 操作需要 --slug", file=sys.stderr)
            sys.exit(1)

        delete_shadow(base_dir, args.slug)

    elif args.action == "get":
        if not args.slug:
            print("错误：get 操作需要 --slug", file=sys.stderr)
            sys.exit(1)

        result = get_shadow(base_dir, args.slug)
        if not result:
            print(f"错误：找不到影子 {args.slug}", file=sys.stderr)
            sys.exit(1)

        print(f"=== {result['meta'].get('name', result['slug'])} (v{result['meta'].get('version', '?')}) ===")
        print(result["shadow_content"])


if __name__ == "__main__":
    main()
