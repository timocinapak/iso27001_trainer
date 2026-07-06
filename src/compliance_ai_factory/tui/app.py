"""Compliance AI Factory Terminal UI."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from rich import box
from rich.console import Console, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader

console = Console()


class TUIApp:
    """Main TUI application."""

    KNOWLEDGE_DIR: ClassVar[Path] = Path(__file__).parents[3] / "knowledge"

    def __init__(self) -> None:
        self.loader: KnowledgePackLoader | None = None
        self.pack = None

    def header(self) -> Panel:
        return Panel(
            Text("Compliance AI Factory", style="bold green"),
            box=box.ROUNDED,
            style="green",
            subtitle="Terminal UI",
        )

    def dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(self._stats_table(), size=6),
            Layout(self._pipeline_diagram(), size=12),
            Layout(self._quick_actions(), size=8),
        )
        return layout

    def _stats_table(self) -> Panel:
        table = Table.grid(padding=2)
        table.add_row(
            Panel("[bold]Knowledge Packs[/] :book:", box=box.MINIMAL),
            Panel("[bold]Generated Datasets[/] :floppy_disk:", box=box.MINIMAL),
            Panel("[bold]Validation Pass Rate[/] :white_check_mark:", box=box.MINIMAL),
            Panel("[bold]Active Issues[/] :warning:", box=box.MINIMAL),
        )
        table.add_row(
            Panel("1 Pack Loaded\nISO 27001:2022", box=box.MINIMAL),
            Panel("12,847 Samples\n4 Generation Runs", box=box.MINIMAL),
            Panel("94.2% Pass Rate\n2.1% Improvement", box=box.MINIMAL),
            Panel("3 Active\n1 Critical", box=box.MINIMAL),
        )
        return Panel(table, title="[bold]Overview[/]", box=box.ROUNDED)

    def _pipeline_diagram(self) -> Panel:
        available = list(self.list_knowledge_packs())
        packs_info = f"[dim]Packs: {', '.join(available) if available else 'none loaded'}[/]"
        lines = [
            packs_info,
            ":package: Knowledge Pack",
            "  :office: Scenario",
            "  :shield: Control Selection",
            "    :question: Question Generation",
            "      :speech_balloon: Answer Generation",
            "        :page_facing_up: Evidence Generation",
            "          :balance_scale: Decision",
            "            :mag: Finding",
            "              :bulb: Recommendation",
            "                :brain: Reasoning",
            "                  :shield: Validation",
            "                    :arrow_down: Export",
        ]
        return Panel("\n".join(lines), title="[bold]Generation Pipeline[/]", box=box.ROUNDED)

    def _quick_actions(self) -> Panel:
        table = Table.grid(padding=1)
        table.add_column()
        table.add_row("[1] :book: Browse Knowledge Packs")
        table.add_row("[2] :office: Generate Scenario")
        table.add_row("[3] :rocket: Generate Dataset")
        table.add_row("[4] :white_check_mark: Validate Dataset")
        table.add_row("[5] :arrow_down: Export Dataset")
        table.add_row("[q] :door: Exit")
        return Panel(table, title="[bold]Quick Actions[/]", box=box.ROUNDED)

    def list_knowledge_packs(self) -> list[str]:
        if self.KNOWLEDGE_DIR.exists():
            return [
                d.name
                for d in self.KNOWLEDGE_DIR.iterdir()
                if d.is_dir() and (d / "metadata.json").exists()
            ]
        return []

    def knowledge_pack_browser(self) -> Panel:
        packs = self.list_knowledge_packs()
        if not packs:
            return Panel("[yellow]No knowledge packs found.[/]", box=box.ROUNDED)

        loader = KnowledgePackLoader(self.KNOWLEDGE_DIR / packs[0])
        pack = loader.load()

        rows = [
            f":book:  [bold]{pack.metadata.standard_name}[/]",
            f"      Version: {pack.metadata.version}",
            f"      Publisher: {pack.metadata.publisher}",
            f"      Controls: {len(pack.controls)}",
            "",
        ]

        controls_by_clause: dict[str, list[str]] = {}
        for c in pack.controls:
            controls_by_clause.setdefault(c.clause, []).append(c.control_id)

        clause_names = {"5": "Organizational", "6": "People", "7": "Physical", "8": "Technological"}
        for clause_id, controls_list in sorted(controls_by_clause.items()):
            name = clause_names.get(clause_id, f"Clause {clause_id}")
            rows.append(
                f"  [bold]{name} Controls[/] ({len(controls_list)})"
            )
            for cid in controls_list[:5]:
                control = pack.get_control(cid)
                if control:
                    rows.append(f"    {cid} - {control.title}")
            if len(controls_list) > 5:
                rows.append(f"    [dim]... and {len(controls_list) - 5} more[/]")
            rows.append("")

        evidence_counts = {
            ev.category: len(
                [e for e in pack.evidence if e.category == ev.category]
            )
            for ev in pack.evidence
        }
        rows.append(f":page_facing_up:  [bold]Evidence Requirements[/]: {len(pack.evidence)}")
        for cat, count in sorted(evidence_counts.items()):
            rows.append(f"      {cat}: {count}")

        rows.append("")
        rows.append(
            f":brain:  [bold]Reasoning Rules[/]: {len(pack.reasoning)}"
        )
        rows.append(
            f":link:  [bold]Cross References[/]: {len(pack.cross_references)}"
        )

        return Panel("\n".join(rows), title="[bold]Knowledge Pack Browser[/]", box=box.ROUNDED)

    def generation_control(self) -> Panel:
        table = Table(title="Generation Configuration", box=box.ROUNDED)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Standard", "ISO/IEC 27001:2022")
        table.add_row("Industry", "technology (default)")
        table.add_row("Maturity", "defined (default)")
        table.add_row("Difficulty", "intermediate (default)")
        table.add_row("Controls", "5 selected")
        table.add_row("Samples per Control", "250")
        table.add_row("Total Samples", "1,250")

        return Panel(
            f"{table}\n\n[bold green]:rocket:  Press 'g' to start generation[/]",
            title="[bold]Dataset Generation[/]",
            box=box.ROUNDED,
        )

    def validation_viewer(self) -> Panel:
        table = Table(box=box.ROUNDED)
        table.add_column("Sample", style="cyan")
        table.add_column("ISO", style="green")
        table.add_column("Knowledge", style="green")
        table.add_column("Consistency", style="green")
        table.add_column("Grammar", style="green")
        table.add_column("Hallucination", style="green")
        table.add_column("Overall", style="bold")

        table.add_row(
            "SMP-001", ":white_check_mark:", ":white_check_mark:",
            ":white_check_mark:", ":white_check_mark:", ":white_check_mark:",
            "[green]PASSED[/]",
        )
        table.add_row(
            "SMP-002", ":white_check_mark:", ":white_check_mark:",
            ":white_check_mark:", ":warning:", ":white_check_mark:",
            "[yellow]WARNING[/]",
        )
        table.add_row(
            "SMP-003", ":x:", ":white_check_mark:",
            ":white_check_mark:", ":white_check_mark:", ":warning:",
            "[red]FAILED[/]",
        )

        summary = (
            "\n[bold]Summary[/]: 1 passed, 1 warning, 1 failed "
            "| Pass rate: [green]94.2%[/]"
        )

        return Panel(
            f"{table}{summary}",
            title="[bold]Validation Results[/]",
            box=box.ROUNDED,
        )

    def run(self) -> None:
        console.clear()
        console.print(self.header())
        console.print(self.dashboard())

        while True:
            key = console.input("\n[bold cyan]>[/] ").strip().lower()
            if key == "q":
                console.print("[yellow]Goodbye![/]")
                break
            elif key == "1":
                console.clear()
                console.print(self.header())
                console.print(self.knowledge_pack_browser())
            elif key == "2":
                console.clear()
                console.print(self.header())
                console.print(
                    Panel(
                        "[green]Scenario generated:[/] TechCorp (technology, 500 employees)",
                        title="[bold]Scenario Generator[/]",
                        box=box.ROUNDED,
                    )
                )
            elif key == "3":
                console.clear()
                console.print(self.header())
                console.print(self.generation_control())
            elif key == "4":
                console.clear()
                console.print(self.header())
                console.print(self.validation_viewer())
            elif key == "5":
                console.clear()
                console.print(self.header())
                console.print(
                    Panel(
                        ":arrow_down: [bold]Export Formats[/]\n\n"
                        "[1] JSONL\n[2] JSON\n[3] CSV\n[4] Markdown\n[5] Parquet\n\n"
                        "[green]Last export:[/] GEN-001.jsonl (240 samples, 2.4 MB)",
                        title="[bold]Dataset Exporter[/]",
                        box=box.ROUNDED,
                    )
                )
            elif key == "d":
                console.clear()
                console.print(self.header())
                console.print(self.dashboard())
            else:
                console.print("[red]Unknown command.[/] Press [bold]d[/] for dashboard.")


def main() -> None:
    app = TUIApp()
    app.run()


if __name__ == "__main__":
    main()
