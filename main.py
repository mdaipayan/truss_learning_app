"""Truss Learning App — interactive tutorial and quiz."""

import sys
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich import box

from questions import TUTORIALS, QUESTIONS

console = Console()


def clear():
    console.clear()


def press_enter(msg="Press [bold]Enter[/bold] to continue..."):
    console.print(f"\n[dim]{msg}[/dim]")
    input()


# ── Tutorial ────────────────────────────────────────────────────────────────

def run_tutorial():
    clear()
    console.print(Panel("[bold cyan]TRUSS LEARNING — TUTORIALS[/bold cyan]",
                        subtitle="Learn at your own pace", border_style="cyan"))

    for i, t in enumerate(TUTORIALS, 1):
        console.print(f"  [bold]{i}.[/bold] {t['title']}")

    console.print("  [bold]0.[/bold] Back to main menu\n")

    while True:
        choice = Prompt.ask("[cyan]Select a topic[/cyan]",
                            choices=[str(i) for i in range(len(TUTORIALS) + 1)],
                            show_choices=False)
        if choice == "0":
            return
        idx = int(choice) - 1
        show_tutorial(idx)


def show_tutorial(idx: int):
    t = TUTORIALS[idx]
    clear()
    console.print(Panel(
        f"[bold white]{t['title']}[/bold white]",
        border_style="cyan",
        subtitle=f"Topic {idx + 1} of {len(TUTORIALS)}",
    ))
    console.print()
    console.print(t["content"])

    nav = []
    if idx > 0:
        nav.append("[bold]P[/bold]revious")
    if idx < len(TUTORIALS) - 1:
        nav.append("[bold]N[/bold]ext")
    nav.append("[bold]M[/bold]enu")
    console.print(f"\n[dim]{'  |  '.join(nav)}[/dim]")

    while True:
        key = Prompt.ask("", default="n" if idx < len(TUTORIALS) - 1 else "m",
                         show_default=False).strip().lower()
        if key in ("n", "") and idx < len(TUTORIALS) - 1:
            show_tutorial(idx + 1)
            return
        elif key == "p" and idx > 0:
            show_tutorial(idx - 1)
            return
        elif key == "m":
            return


# ── Quiz ─────────────────────────────────────────────────────────────────────

def run_quiz():
    clear()
    console.print(Panel("[bold yellow]TRUSS QUIZ[/bold yellow]",
                        subtitle="Test your knowledge", border_style="yellow"))

    topics = sorted({q["topic"] for q in QUESTIONS})
    console.print("\n[bold]Choose a quiz mode:[/bold]")
    console.print("  [bold]1.[/bold] Full quiz (all topics)")
    for i, t in enumerate(topics, 2):
        console.print(f"  [bold]{i}.[/bold] {t} only")
    console.print("  [bold]0.[/bold] Back\n")

    choices = [str(i) for i in range(len(topics) + 2)]
    choice = Prompt.ask("[yellow]Select[/yellow]", choices=choices, show_choices=False)
    if choice == "0":
        return

    if choice == "1":
        pool = QUESTIONS[:]
    else:
        topic = topics[int(choice) - 2]
        pool = [q for q in QUESTIONS if q["topic"] == topic]

    random.shuffle(pool)
    administer_quiz(pool)


def administer_quiz(pool: list):
    score = 0
    wrong = []

    for num, q in enumerate(pool, 1):
        clear()
        console.print(Panel(
            f"[bold]Question {num} of {len(pool)}[/bold]  —  Topic: [cyan]{q['topic']}[/cyan]",
            border_style="yellow",
        ))
        console.print(f"\n[bold white]{q['question']}[/bold white]\n")

        for i, opt in enumerate(q["options"], 1):
            console.print(f"  [bold]{i}.[/bold] {opt}")

        console.print()
        valid = [str(i) for i in range(1, len(q["options"]) + 1)]
        choice = Prompt.ask("[yellow]Your answer[/yellow]", choices=valid, show_choices=False)
        selected = int(choice) - 1

        if selected == q["answer"]:
            score += 1
            console.print("\n[bold green]✓ Correct![/bold green]")
        else:
            correct_text = q["options"][q["answer"]]
            console.print(f"\n[bold red]✗ Incorrect.[/bold red]  "
                          f"The correct answer was: [green]{correct_text}[/green]")
            wrong.append(q)

        console.print(f"\n[dim italic]{q['explanation']}[/dim italic]")
        press_enter()

    show_results(score, len(pool), wrong)


def show_results(score: int, total: int, wrong: list):
    clear()
    pct = score / total * 100
    color = "green" if pct >= 75 else "yellow" if pct >= 50 else "red"

    console.print(Panel(
        f"[bold {color}]{score} / {total}  ({pct:.0f}%)[/bold {color}]",
        title="[bold]Quiz Complete[/bold]",
        border_style=color,
    ))

    if pct == 100:
        console.print("\n[bold green]Perfect score! Outstanding work.[/bold green]")
    elif pct >= 75:
        console.print("\n[bold green]Great job! Keep reviewing the topics you missed.[/bold green]")
    elif pct >= 50:
        console.print("\n[bold yellow]Good effort. Review the tutorials on the topics below.[/bold yellow]")
    else:
        console.print("\n[bold red]More study needed. Work through the tutorials and try again.[/bold red]")

    if wrong:
        console.print("\n[bold]Topics to review:[/bold]")
        reviewed = set()
        for q in wrong:
            if q["topic"] not in reviewed:
                console.print(f"  • [cyan]{q['topic']}[/cyan]")
                reviewed.add(q["topic"])

    press_enter("Press Enter to return to the main menu...")


# ── Reference Card ───────────────────────────────────────────────────────────

def show_reference():
    clear()
    table = Table(title="Quick Reference — Truss Analysis", box=box.ROUNDED,
                  border_style="blue", header_style="bold cyan")
    table.add_column("Formula / Rule", style="bold white")
    table.add_column("Meaning", style="white")

    rows = [
        ("m + r = 2j", "Statically determinate planar truss"),
        ("m + r < 2j", "Unstable (mechanism)"),
        ("m + r > 2j", "Statically indeterminate"),
        ("ΣFx = 0, ΣFy = 0", "Equilibrium at each joint (Method of Joints)"),
        ("ΣFx=0, ΣFy=0, ΣM=0", "Equilibrium of cut section (Method of Sections)"),
        ("Cut ≤ 3 unknowns", "Limit for Method of Sections"),
        ("Negative force value", "Member is in compression (when tension assumed)"),
        ("2-member joint, no load", "Both members are zero-force"),
        ("3-member joint, 2 collinear,\nno external load", "Third member is zero-force"),
    ]
    for r, m in rows:
        table.add_row(r, m)

    console.print(table)
    press_enter()


# ── Main Menu ─────────────────────────────────────────────────────────────────

def main_menu():
    while True:
        clear()
        console.print(Panel(
            "[bold cyan]TRUSS LEARNING APP[/bold cyan]\n"
            "[dim]Structural analysis fundamentals[/dim]",
            border_style="cyan",
            padding=(1, 4),
        ))
        console.print("  [bold]1.[/bold] Tutorials")
        console.print("  [bold]2.[/bold] Quiz")
        console.print("  [bold]3.[/bold] Quick Reference Card")
        console.print("  [bold]0.[/bold] Exit\n")

        choice = Prompt.ask("[cyan]Select[/cyan]",
                            choices=["0", "1", "2", "3"],
                            show_choices=False)
        if choice == "1":
            run_tutorial()
        elif choice == "2":
            run_quiz()
        elif choice == "3":
            show_reference()
        elif choice == "0":
            clear()
            console.print("[bold cyan]Goodbye! Keep learning.[/bold cyan]\n")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main_menu()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Exited.[/dim]")
        sys.exit(0)
