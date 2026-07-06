import json
from pathlib import Path

import click

from compliance_ai_factory.common.models.base import DatasetSample
from compliance_ai_factory.dataset_exporter.export_manager import ExportManager
from compliance_ai_factory.dataset_generator.pipeline import ConcreteDatasetGeneratorPipeline
from compliance_ai_factory.dataset_validator.pipeline import ConcreteValidationPipeline
from compliance_ai_factory.dataset_validator.validators import (
    ConsistencyValidator,
    DuplicateDetector,
    GrammarValidator,
    HallucinationDetector,
    IsoValidator,
    KnowledgeValidator,
    MetadataValidator,
    ReasoningValidator,
)
from compliance_ai_factory.knowledge_pack.loader import KnowledgePackLoader
from compliance_ai_factory.scenario_generator.generator import ConcreteScenarioGenerator
from compliance_ai_factory.scenario_generator.repository import FileScenarioRepository

KNOWLEDGE_DIR = Path(__file__).parents[2] / "knowledge"
OUTPUT_DIR = Path(__file__).parents[2] / "output"


@click.group()
def cli() -> None:
    """Compliance AI Factory — Enterprise Dataset Engineering Platform."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@cli.group()
def knowledge() -> None:
    """Manage Knowledge Packs."""


@knowledge.command()
@click.argument("path")
def build(path: str) -> None:
    """Build a Knowledge Pack from source documents."""
    click.echo(f"Building Knowledge Pack from {path}...")
    click.echo("[yellow]Knowledge Builder not yet implemented — use the JSON-based pack system[/]")


@knowledge.command()
def list() -> None:
    """List available Knowledge Packs."""
    loader = KnowledgePackLoader(KNOWLEDGE_DIR)
    available = loader.list_available() if hasattr(loader, 'list_available') else []
    if not available:
        loader2 = KnowledgePackLoader(KNOWLEDGE_DIR / "iso27001")
        available = loader2.list_available()
    if available:
        click.echo("Available Knowledge Packs:")
        for pack in available:
            click.echo(f"  - {pack}")
    else:
        click.echo("No Knowledge Packs found.")


@cli.group()
def scenario() -> None:
    """Manage scenarios."""


@scenario.command()
@click.option("--seed", type=int, default=None, help="Random seed for reproducibility")
@click.option("--save", is_flag=True, default=True, help="Save scenario to disk")
def generate(seed: int | None, save: bool) -> None:
    """Generate a new scenario."""
    generator = ConcreteScenarioGenerator()
    scen = generator.generate(seed=seed)
    click.echo(f"Generated scenario: {scen.id}")
    click.echo(f"  Organization: {scen.organization.name}")
    click.echo(f"  Industry: {scen.organization.industry.value}")
    click.echo(f"  Size: {scen.organization.size.value}")
    click.echo(f"  Maturity: {scen.organization.maturity.value}")
    click.echo(f"  Departments: {', '.join(scen.organization.departments)}")
    click.echo(f"  Employees: {len(scen.organization.employees)}")
    if save:
        repo = FileScenarioRepository(OUTPUT_DIR / "scenarios")
        path = repo.save(scen)
        click.echo(f"Saved to: {path}")


@cli.group()
def generate_cmd() -> None:
    """Generate datasets."""


@generate_cmd.command()
@click.option("--scenario-id", help="Scenario ID to reuse (generates new if not provided)")
@click.option("--standard", default="iso27001", help="Compliance standard")
@click.option("--count", default=10, help="Number of samples to generate")
@click.option("--output", default=None, help="Output directory")
@click.option("--seed", type=int, default=None, help="Random seed")
def dataset(scenario_id: str | None, standard: str, count: int, output: str | None, seed: int | None) -> None:
    """Generate a dataset."""
    pack_path = KNOWLEDGE_DIR / standard
    if not pack_path.exists():
        click.echo(f"Error: Knowledge Pack '{standard}' not found at {pack_path}")
        return

    loader = KnowledgePackLoader(pack_path)
    pack = loader.load()

    generator = ConcreteScenarioGenerator()
    repo = FileScenarioRepository(OUTPUT_DIR / "scenarios")

    if scenario_id:
        try:
            scen = repo.load(scenario_id)
            click.echo(f"Using existing scenario: {scenario_id}")
        except Exception:
            click.echo(f"Scenario {scenario_id} not found, generating new one")
            scen = generator.generate(seed=seed)
    else:
        scen = generator.generate(seed=seed)
        repo.save(scen)
        click.echo(f"Generated new scenario: {scen.id} ({scen.organization.name})")

    pipeline = ConcreteDatasetGeneratorPipeline()
    all_samples: list[DatasetSample] = []

    for control in pack.controls:
        import copy
        limited_pack = copy.deepcopy(pack)
        limited_pack.controls = [control]
        gen_samples = pipeline.run(scen, limited_pack)
        all_samples.extend(gen_samples)

    output_dir = Path(output) if output else (OUTPUT_DIR / "datasets")
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = output_dir / f"dataset_{scen.id}.json"
    with open(dataset_path, "w") as f:
        json.dump(
            [s.model_dump(mode="json") for s in all_samples],
            f,
            indent=2,
        )

    click.echo(f"Generated {len(all_samples)} samples")
    click.echo(f"Saved to: {dataset_path}")


@cli.group()
def validate() -> None:
    """Validate generated datasets."""


@validate.command()
@click.argument("path")
@click.option("--standard", default="iso27001", help="Compliance standard")
def dataset(path: str, standard: str) -> None:
    """Validate a dataset file."""
    dataset_path = Path(path)
    if not dataset_path.exists():
        click.echo(f"Error: File not found: {path}")
        return

    with open(dataset_path) as f:
        data = json.load(f)

    if isinstance(data, dict) and "samples" in data:
        samples_data = data["samples"]
    else:
        samples_data = data if isinstance(data, list) else []

    samples = [DatasetSample(**s) for s in samples_data]
    click.echo(f"Loaded {len(samples)} samples for validation")

    pack_path = KNOWLEDGE_DIR / standard
    if not pack_path.exists():
        click.echo(f"Warning: Knowledge Pack '{standard}' not found — skipping knowledge-aware validators")
        pack = None
    else:
        loader = KnowledgePackLoader(pack_path)
        pack = loader.load()

    validators = [
        IsoValidator(pack),
        KnowledgeValidator(pack),
        ConsistencyValidator(pack),
        GrammarValidator(pack),
        HallucinationDetector(pack),
        MetadataValidator(pack),
        ReasoningValidator(pack),
    ]
    if pack:
        dup_detector = DuplicateDetector(pack)
        dup_detector.set_all_samples(samples)
        validators.append(dup_detector)

    pipeline = ConcreteValidationPipeline(validators=validators, knowledge_pack=pack)
    validated = pipeline.validate_all(samples)
    summary = pipeline.get_summary(validated)

    click.echo("\nValidation Summary:")
    click.echo(f"  Total: {summary['total_samples']}")
    click.echo(f"  Passed: {summary['passed']}")
    click.echo(f"  Failed: {summary['failed']}")
    click.echo(f"  Pass Rate: {summary['pass_rate']}%")
    click.echo(f"  Avg Quality Score: {summary['average_quality_score']}")

    validated_path = dataset_path.with_stem(f"{dataset_path.stem}_validated")
    with open(validated_path, "w") as f:
        json.dump(
            {"samples": [s.model_dump(mode="json") for s in validated], "summary": summary},
            f,
            indent=2,
        )
    click.echo(f"Results saved to: {validated_path}")


@cli.group()
def export() -> None:
    """Export datasets."""


@export.command()
@click.argument("path")
@click.option("--format", "-f", default="jsonl", help="Export format (jsonl, json, csv, markdown, parquet)")
@click.option("--output-dir", default=None, help="Output directory")
def dataset(path: str, format: str, output_dir: str | None) -> None:
    """Export a dataset."""
    dataset_path = Path(path)
    if not dataset_path.exists():
        click.echo(f"Error: File not found: {path}")
        return

    with open(dataset_path) as f:
        data = json.load(f)

    if isinstance(data, dict) and "samples" in data:
        samples_data = data["samples"]
    else:
        samples_data = data if isinstance(data, list) else []

    samples = [DatasetSample(**s) for s in samples_data]
    click.echo(f"Loaded {len(samples)} samples for export")

    exporter = ExportManager()
    out_dir = Path(output_dir) if output_dir else (OUTPUT_DIR / "exports")

    try:
        result = exporter.export(
            samples=samples,
            format_name=format,
            output_dir=out_dir,
            run_validation=False,
        )
        click.echo("Export complete:")
        click.echo(f"  ID: {result['export_id']}")
        click.echo(f"  Format: {result['format']}")
        click.echo(f"  Samples: {result['sample_count']}")
        click.echo(f"  Path: {result['path']}")
    except Exception as e:
        click.echo(f"Export failed: {e}", err=True)


@cli.command()
def tui() -> None:
    """Launch the Terminal User Interface."""
    from compliance_ai_factory.tui.app import main
    main()


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--ui", is_flag=True, help="Serve the web UI alongside the API")
def serve(host: str, port: int, ui: bool) -> None:
    """Start the API server."""
    from compliance_ai_factory.api.server import serve, serve_with_ui
    if ui:
        click.echo(f"Starting server with UI at http://{host}:{port}")
        serve_with_ui(host=host, port=port)
    else:
        click.echo(f"Starting API server at http://{host}:{port}")
        serve(host=host, port=port)


if __name__ == "__main__":
    cli()
