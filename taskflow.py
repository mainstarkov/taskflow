#!/usr/bin/env python3
"""TaskFlow — terminal task manager with priorities and categories."""

import argparse
import json
import os
import sys
from datetime import datetime

class C:
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    STRIKE  = "\033[9m"
    RESET   = "\033[0m"


BANNER = f"""
{C.CYAN}{C.BOLD}  ████████╗ █████╗ ███████╗██╗  ██╗███████╗██╗      ██████╗ ██╗    ██╗
  ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██║     ██╔═══██╗██║    ██║
     ██║   ███████║███████╗█████╔╝ █████╗  ██║     ██║   ██║██║ █╗ ██║
     ██║   ██╔══██║╚════██║██╔═██╗ ██╔══╝  ██║     ██║   ██║██║███╗██║
     ██║   ██║  ██║███████║██║  ██╗██║     ███████╗╚██████╔╝╚███╔███╔╝
     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝{C.RESET}
{C.GRAY}  ────────────────────────────────────────────────────────────────{C.RESET}
{C.DIM}  Terminal Task Manager v1.0                      {C.GRAY}by mainstarkov{C.RESET}
{C.GRAY}  ────────────────────────────────────────────────────────────────{C.RESET}
"""

PRIORITY_COLORS = {"high": C.RED, "medium": C.YELLOW, "low": C.GREEN}
PRIORITY_ICONS = {"high": "🔴", "medium": "🟡", "low": "🟢"}
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

def load_tasks() -> list[dict]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks: list[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def next_id(tasks: list[dict]) -> int:
    return max((t["id"] for t in tasks), default=0) + 1

def cmd_add(args):
    tasks = load_tasks()
    task = {
        "id": next_id(tasks),
        "title": " ".join(args.title),
        "priority": args.priority,
        "category": args.category or "general",
        "done": False,
        "created": datetime.now().isoformat(),
        "completed": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    pc = PRIORITY_COLORS[task["priority"]]
    pi = PRIORITY_ICONS[task["priority"]]
    print(f"\n  {C.GREEN}✓{C.RESET} Task #{task['id']} added: {C.BOLD}{task['title']}{C.RESET}")
    print(f"    {pi} {pc}{task['priority']}{C.RESET}  📂 {task['category']}\n")


def cmd_done(args):
    tasks = load_tasks()
    found = [t for t in tasks if t["id"] == args.id]
    if not found:
        print(f"\n  {C.RED}✗ Task #{args.id} not found{C.RESET}\n")
        return
    found[0]["done"] = True
    found[0]["completed"] = datetime.now().isoformat()
    save_tasks(tasks)
    print(f"\n  {C.GREEN}✓{C.RESET} Task #{args.id} completed: {C.STRIKE}{found[0]['title']}{C.RESET}\n")


def cmd_remove(args):
    tasks = load_tasks()
    before = len(tasks)
    tasks = [t for t in tasks if t["id"] != args.id]
    if len(tasks) == before:
        print(f"\n  {C.RED}✗ Task #{args.id} not found{C.RESET}\n")
        return
    save_tasks(tasks)
    print(f"\n  {C.GREEN}✓{C.RESET} Task #{args.id} removed\n")


def cmd_list(args):
    tasks = load_tasks()

    if args.category:
        tasks = [t for t in tasks if t.get("category") == args.category]
    if args.priority:
        tasks = [t for t in tasks if t.get("priority") == args.priority]
    if not args.all:
        tasks = [t for t in tasks if not t["done"]]

    if not tasks:
        print(f"\n  {C.GRAY}No tasks found.{C.RESET}\n")
        return

    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks.sort(key=lambda t: (t["done"], priority_order.get(t.get("priority", "low"), 9)))

    categories = sorted(set(t.get("category", "general") for t in tasks))

    w = 64
    print(f"\n{C.CYAN}  ╔{'═' * w}╗{C.RESET}")
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    header = f"Tasks: {total} total, {done} done, {total - done} pending"
    pad = max(0, w - 2 - len(header))
    print(f"{C.CYAN}  ║ {C.BOLD}{header}{C.RESET}{' ' * pad}{C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}  ╠{'═' * w}╣{C.RESET}")

    for cat in categories:
        cat_tasks = [t for t in tasks if t.get("category", "general") == cat]
        print(f"{C.CYAN}  ║{C.RESET}  {C.MAGENTA}📂 {cat.upper()}{C.RESET}{' ' * max(0, w - 5 - len(cat))}{C.CYAN}║{C.RESET}")
        print(f"{C.CYAN}  ╟{'─' * w}╢{C.RESET}")

        for t in cat_tasks:
            tid = t["id"]
            title = t["title"]
            pri = t.get("priority", "low")
            pi = PRIORITY_ICONS.get(pri, "⚪")
            pc = PRIORITY_COLORS.get(pri, C.WHITE)

            if t["done"]:
                check = f"{C.GREEN}✔{C.RESET}"
                title_fmt = f"{C.GRAY}{C.STRIKE}{title}{C.RESET}"
            else:
                check = f"{C.GRAY}○{C.RESET}"
                title_fmt = f"{C.WHITE}{title}{C.RESET}"

            line = f"  {check}  {C.GRAY}#{tid:<4}{C.RESET} {pi} {title_fmt}"
            visible = 6 + len(str(tid)) + 3 + len(title) + 2
            pad = max(0, w - visible)
            pri_tag = f"{pc}{pri}{C.RESET}"
            print(f"{C.CYAN}  ║{C.RESET}{line}{' ' * pad}  {pri_tag}  {C.CYAN}║{C.RESET}")

        print(f"{C.CYAN}  ╟{'─' * w}╢{C.RESET}")

    # Progress bar
    if total > 0:
        pct = done / total
        bar_w = 30
        filled = int(pct * bar_w)
        bar = f"{C.GREEN}{'█' * filled}{C.GRAY}{'░' * (bar_w - filled)}{C.RESET}"
        pct_str = f"{pct * 100:.0f}%"
        pad = max(0, w - 2 - bar_w - 2 - len(pct_str) - 12)
        print(f"{C.CYAN}  ║{C.RESET}  Progress: {bar}  {C.BOLD}{pct_str}{C.RESET}{' ' * pad}{C.CYAN}║{C.RESET}")

    print(f"{C.CYAN}  ╚{'═' * w}╝{C.RESET}\n")


def cmd_clear(args):
    tasks = load_tasks()
    remaining = [t for t in tasks if not t["done"]]
    removed = len(tasks) - len(remaining)
    save_tasks(remaining)
    print(f"\n  {C.GREEN}✓{C.RESET} Cleared {removed} completed tasks\n")

def main():
    parser = argparse.ArgumentParser(prog="taskflow", description="Terminal task manager")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="add a new task")
    p_add.add_argument("title", nargs="+", help="task title")
    p_add.add_argument("-p", "--priority", choices=["high", "medium", "low"], default="medium")
    p_add.add_argument("-c", "--category", help="task category (default: general)")

    p_done = sub.add_parser("done", help="mark task as completed")
    p_done.add_argument("id", type=int, help="task ID")

    p_rm.add_argument("id", type=int, help="task ID")

    p_list = sub.add_parser("list", help="show tasks")
    p_list.add_argument("-c", "--category", help="filter by category")
    p_list.add_argument("-p", "--priority", choices=["high", "medium", "low"])
    p_list.add_argument("-a", "--all", action="store_true", help="include completed tasks")

    sub.add_parser("clear", help="remove all completed tasks")

    args = parser.parse_args()
    print(BANNER)

    commands = {
        "add": cmd_add,
        "done": cmd_done,
        "remove": cmd_remove,
        "list": cmd_list,
        "clear": cmd_clear,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
