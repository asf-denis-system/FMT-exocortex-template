#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


STATUS_ALIASES = {
    "done": "done",
    "completed": "done",
    "in_progress": "in_progress",
    "in progress": "in_progress",
    "partial": "in_progress",
    "pending": "pending",
    "not started": "pending",
    "paused": "paused",
    "archived": "archived",
    "merged": "merged",
}

STATUS_ORDER = {
    "in_progress": 0,
    "pending": 1,
    "paused": 2,
    "done": 3,
    "archived": 4,
    "merged": 5,
}

REGISTRY_ICONS = {
    "done": "✅",
    "in_progress": "🔄",
    "pending": "⏳",
    "paused": "⏸",
    "archived": "📦",
    "merged": "↗️",
}


@dataclass
class WeekPlanMeta:
    week: str
    status: str
    period: str
    date_start: str
    date_end: str
    path: Path


@dataclass
class WorkProductRow:
    wp_id: str
    name: str
    budget: str
    status: str
    deadline: str
    ordinal: int


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def normalize_status(value: str) -> str:
    key = re.sub(r"[_-]+", " ", value.strip().lower())
    return STATUS_ALIASES.get(key, value.strip())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def handle_remove_readonly(func, path, exc_info) -> None:
    del exc_info
    os.chmod(path, 0o700)
    func(path)


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return {}, text
    meta_block = parts[1]
    body = parts[2]
    meta: dict[str, str] = {}
    for raw_line in meta_block.splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body


def parse_period(meta: dict[str, str]) -> tuple[str, str]:
    period = meta.get("period", "")
    if ".." in period:
        start, end = period.split("..", 1)
        return start.strip(), end.strip()
    return meta.get("date_start", "").strip(), meta.get("date_end", "").strip()


def score_weekplan(meta: WeekPlanMeta, today: date) -> tuple[int, float]:
    contains_today = False
    if meta.date_start and meta.date_end:
        contains_today = meta.date_start <= today.isoformat() <= meta.date_end

    status = meta.status.lower()
    score = 0
    if contains_today and status not in {"archived", "done"}:
        score = 300
    elif status in {"active", "confirmed", "in_progress"}:
        score = 200
    elif status == "draft":
        score = 100
    return score, meta.path.stat().st_mtime


def select_weekplan(strategy_repo: Path, explicit: Path | None) -> WeekPlanMeta:
    if explicit is not None:
        meta_raw, _ = parse_frontmatter(explicit)
        date_start, date_end = parse_period(meta_raw)
        return WeekPlanMeta(
            week=meta_raw.get("week", ""),
            status=meta_raw.get("status", ""),
            period=meta_raw.get("period", ""),
            date_start=date_start,
            date_end=date_end,
            path=explicit,
        )

    weekplans = sorted((strategy_repo / "current").glob("WeekPlan W*.md"))
    if not weekplans:
        raise FileNotFoundError(f"No WeekPlan W*.md files found in {(strategy_repo / 'current')}")

    today = date.today()
    metas: list[WeekPlanMeta] = []
    for path in weekplans:
        meta_raw, _ = parse_frontmatter(path)
        date_start, date_end = parse_period(meta_raw)
        metas.append(
            WeekPlanMeta(
                week=meta_raw.get("week", ""),
                status=meta_raw.get("status", ""),
                period=meta_raw.get("period", ""),
                date_start=date_start,
                date_end=date_end,
                path=path,
            )
        )

    metas.sort(key=lambda item: score_weekplan(item, today), reverse=True)
    return metas[0]


def extract_work_products(weekplan_path: Path) -> tuple[WeekPlanMeta, list[WorkProductRow]]:
    meta_raw, body = parse_frontmatter(weekplan_path)
    date_start, date_end = parse_period(meta_raw)
    meta = WeekPlanMeta(
        week=meta_raw.get("week", ""),
        status=meta_raw.get("status", ""),
        period=meta_raw.get("period", ""),
        date_start=date_start,
        date_end=date_end,
        path=weekplan_path,
    )

    lines = body.splitlines()
    start_idx = None
    for idx, line in enumerate(lines):
        if line.startswith("## Рабочие продукты"):
            start_idx = idx
            break
    if start_idx is None:
        raise ValueError(f"Cannot find '## Рабочие продукты' section in {weekplan_path}")

    header_idx = None
    for idx in range(start_idx + 1, len(lines)):
        if lines[idx].strip().startswith("| # |"):
            header_idx = idx
            break
    if header_idx is None or header_idx + 2 >= len(lines):
        raise ValueError(f"Cannot find work-products table in {weekplan_path}")

    headers = split_markdown_row(lines[header_idx])
    header_map = {name: pos for pos, name in enumerate(headers)}
    required = {"#", "РП", "Бюджет", "Статус"}
    missing = required.difference(header_map)
    if missing:
        raise ValueError(f"Missing columns in work-products table: {sorted(missing)}")

    rows: list[WorkProductRow] = []
    ordinal = 0
    for line in lines[header_idx + 2 :]:
        if not line.strip().startswith("|"):
            break
        cells = split_markdown_row(line)
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        rows.append(
            WorkProductRow(
                wp_id=cells[header_map["#"]],
                name=cells[header_map["РП"]],
                budget=cells[header_map["Бюджет"]],
                status=normalize_status(cells[header_map["Статус"]]),
                deadline=cells[header_map["Дедлайн"]] if "Дедлайн" in header_map else "—",
                ordinal=ordinal,
            )
        )
        ordinal += 1

    if not rows:
        raise ValueError(f"No work-product rows parsed from {weekplan_path}")
    return meta, rows


def workspace_tail_slug(workspace_root: Path) -> str:
    parts = [part for part in workspace_root.parts if part not in (workspace_root.anchor, "")]
    if len(parts) >= 2:
        return f"{parts[-2]}-{parts[-1]}"
    return workspace_root.name or "workspace"


def fallback_claude_slug(workspace_root: Path) -> str:
    slug = workspace_root.as_posix().replace("/", "-").replace("\\", "-")
    return re.sub(r"[^A-Za-z0-9._-]", "-", slug)


def discover_memory_file(workspace_root: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit

    projects_dir = Path.home() / ".claude" / "projects"
    tail_slug = workspace_tail_slug(workspace_root).lower()
    candidates = sorted(projects_dir.glob("*/memory/MEMORY.md"))
    preferred = [path for path in candidates if tail_slug in str(path.parent.parent).lower()]
    if preferred:
        return preferred[0]
    if candidates:
        return candidates[0]
    return projects_dir / fallback_claude_slug(workspace_root) / "memory" / "MEMORY.md"


def build_memory_section(meta: WeekPlanMeta, rows: list[WorkProductRow]) -> str:
    week_label = meta.week or "W?"
    if meta.date_start and meta.date_end:
        heading = f"## РП текущей недели ({week_label}: {meta.date_start}..{meta.date_end})"
    elif meta.period:
        heading = f"## РП текущей недели ({week_label}: {meta.period})"
    else:
        heading = f"## РП текущей недели ({week_label})"

    sorted_rows = sorted(rows, key=lambda item: (STATUS_ORDER.get(item.status, 99), item.ordinal))

    lines = [
        heading,
        "",
        "> Порядок: in_progress → pending → paused → done.",
        "",
        "| # | РП | Бюджет | Статус | Дедлайн |",
        "|---|-----|--------|--------|---------|",
    ]
    for row in sorted_rows:
        deadline = row.deadline or "—"
        lines.append(f"| {row.wp_id} | {row.name} | {row.budget} | {row.status} | {deadline} |")
    lines.extend(["", ""])
    return "\n".join(lines)


def sync_memory(memory_file: Path, template_memory_file: Path, section_text: str, dry_run: bool) -> bool:
    if memory_file.exists():
        current = read_text(memory_file)
    else:
        current = read_text(template_memory_file)

    pattern = re.compile(r"(?ms)^## РП текущей недели.*?(?=^---\s*$)")
    if pattern.search(current):
        updated = pattern.sub(section_text, current, count=1)
    else:
        updated = current.rstrip() + "\n\n" + section_text + "---\n"

    changed = updated != current
    if changed and not dry_run:
        write_text(memory_file, updated)
    return changed


def sync_registry(registry_file: Path, rows: list[WorkProductRow], dry_run: bool) -> bool:
    if not registry_file.exists():
        return False

    current = read_text(registry_file)
    lines = current.splitlines()

    header_idx = None
    for idx, line in enumerate(lines):
        if line.strip() == "| # | Название | Статус |":
            header_idx = idx
            break
    if header_idx is None:
        raise ValueError(f"Cannot find registry table header in {registry_file}")

    table_start = header_idx + 2
    table_end = table_start
    while table_end < len(lines) and lines[table_end].strip().startswith("|"):
        table_end += 1

    existing_rows = []
    for line in lines[table_start:table_end]:
        cells = split_markdown_row(line)
        if len(cells) != 3:
            continue
        existing_rows.append({"id": cells[0], "name": cells[1], "status": cells[2]})

    current_map = {
        row.wp_id: {
            "id": row.wp_id,
            "name": row.name,
            "status": REGISTRY_ICONS.get(row.status, row.status),
        }
        for row in rows
    }

    seen_ids = set()
    merged_rows = []
    for item in existing_rows:
        if item["id"] in current_map:
            merged_rows.append(current_map[item["id"]])
            seen_ids.add(item["id"])
        else:
            merged_rows.append(item)

    missing = [current_map[row.wp_id] for row in reversed(rows) if row.wp_id not in seen_ids]
    if missing:
        merged_rows = missing + merged_rows

    new_table_lines = [f"| {row['id']} | {row['name']} | {row['status']} |" for row in merged_rows]
    updated_lines = lines[:table_start] + new_table_lines + lines[table_end:]
    updated = "\n".join(updated_lines) + "\n"
    changed = updated != current
    if changed and not dry_run:
        write_text(registry_file, updated)
    return changed


def refresh_exocortex_backup(
    workspace_root: Path,
    backup_root: Path,
    memory_dir: Path,
    root_claude: Path,
    dry_run: bool,
) -> Path:
    snapshot_name = f"{date.today().isoformat()}-{workspace_tail_slug(workspace_root)}"
    snapshot_dir = backup_root / snapshot_name

    if dry_run:
        return snapshot_dir

    if snapshot_dir.exists():
        shutil.rmtree(snapshot_dir, onerror=handle_remove_readonly)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    if root_claude.exists():
        shutil.copy2(root_claude, snapshot_dir / "CLAUDE.md")

    memory_snapshot_dir = snapshot_dir / "memory"
    shutil.copytree(memory_dir, memory_snapshot_dir)
    return snapshot_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministically sync MEMORY.md, WP-REGISTRY and exocortex backup.")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--strategy-repo", type=Path, default=None)
    parser.add_argument("--weekplan", type=Path, default=None)
    parser.add_argument("--memory-file", type=Path, default=None)
    parser.add_argument("--backup-memory-dir", type=Path, default=None)
    parser.add_argument("--backup-root", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    role_dir = script_dir.parent
    roles_dir = role_dir.parent
    template_dir = roles_dir.parent
    workspace_root = (args.workspace_root or template_dir.parent).resolve()
    strategy_repo = (args.strategy_repo or (workspace_root / "DS-strategy")).resolve()
    backup_root = (args.backup_root or (strategy_repo / "exocortex")).resolve()
    root_claude = workspace_root / "CLAUDE.md"
    template_memory_file = template_dir / "memory" / "MEMORY.md"

    selected_weekplan = select_weekplan(strategy_repo, args.weekplan.resolve() if args.weekplan else None)
    meta, rows = extract_work_products(selected_weekplan.path)

    live_memory_file = discover_memory_file(workspace_root, None)
    memory_file = discover_memory_file(workspace_root, args.memory_file.resolve() if args.memory_file else None)
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    if args.backup_memory_dir:
        backup_memory_dir = args.backup_memory_dir.resolve()
    elif memory_file.parent.name.lower() == "memory":
        backup_memory_dir = memory_file.parent
    else:
        backup_memory_dir = live_memory_file.parent
    backup_memory_dir.mkdir(parents=True, exist_ok=True)

    memory_section = build_memory_section(meta, rows)
    memory_changed = sync_memory(memory_file, template_memory_file, memory_section, dry_run=args.dry_run)
    registry_changed = sync_registry(strategy_repo / "docs" / "WP-REGISTRY.md", rows, dry_run=args.dry_run)
    snapshot_dir = refresh_exocortex_backup(
        workspace_root,
        backup_root,
        backup_memory_dir,
        root_claude,
        dry_run=args.dry_run,
    )

    print(f"WeekPlan: {selected_weekplan.path}")
    print(f"Rows synced: {len(rows)}")
    print(f"MEMORY: {memory_file} ({'updated' if memory_changed else 'no change'})")
    print(
        f"WP-REGISTRY: {strategy_repo / 'docs' / 'WP-REGISTRY.md'} "
        f"({'updated' if registry_changed else 'no change'})"
    )
    print(f"Backup snapshot: {snapshot_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
