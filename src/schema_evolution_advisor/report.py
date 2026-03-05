import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .analyzer import Finding


RISK_COLORS = {
    "safe": "green",
    "cautious": "yellow",
    "dangerous": "red",
}


def render_table(findings: list[Finding], console: Console | None = None) -> None:
    if console is None:
        console = Console()

    table = Table(title="Schema Evolution Analysis", show_lines=True)
    table.add_column("File", style="cyan", max_width=40)
    table.add_column("Function", style="dim")
    table.add_column("Operation", style="bold")
    table.add_column("Target", style="magenta")
    table.add_column("Risk", justify="center")
    table.add_column("Rationale")
    table.add_column("Recommendation", style="dim")

    for f in findings:
        op = f.operation
        target = " ".join(op.args[:2]) if op.args else ""
        file_name = Path(op.source_file).name if op.source_file else ""
        risk_style = RISK_COLORS.get(f.risk_level, "white")

        table.add_row(
            file_name,
            op.function,
            op.op_type,
            target,
            f"[{risk_style}]{f.risk_level.upper()}[/{risk_style}]",
            f.rationale,
            f.recommendation,
        )

    console.print(table)

    # Summary
    counts = {"safe": 0, "cautious": 0, "dangerous": 0}
    for f in findings:
        counts[f.risk_level] = counts.get(f.risk_level, 0) + 1
    console.print(
        f"\n[green]{counts['safe']} safe[/green] | "
        f"[yellow]{counts['cautious']} cautious[/yellow] | "
        f"[red]{counts['dangerous']} dangerous[/red]"
    )


def render_json(findings: list[Finding]) -> str:
    data = []
    for f in findings:
        op = f.operation
        data.append({
            "file": Path(op.source_file).name if op.source_file else "",
            "function": op.function,
            "operation": op.op_type,
            "target": " ".join(op.args[:2]) if op.args else "",
            "risk_level": f.risk_level,
            "rationale": f.rationale,
            "recommendation": f.recommendation,
        })
    return json.dumps(data, indent=2)
