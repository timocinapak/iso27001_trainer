import click


@click.group()
def cli() -> None:
    """Compliance AI Factory — Enterprise Dataset Engineering Platform."""


@cli.group()
def knowledge() -> None:
    """Manage Knowledge Packs."""


@knowledge.command()
@click.argument("path")
def build(path: str) -> None:
    """Build a Knowledge Pack from source documents."""
    click.echo(f"Building Knowledge Pack from {path}...")


@knowledge.command()
def list() -> None:
    """List available Knowledge Packs."""
    click.echo("Available Knowledge Packs:")


@cli.group()
def generate() -> None:
    """Generate datasets."""


@generate.command()
@click.option("--scenario", help="Scenario ID to reuse")
@click.option("--standard", default="iso27001", help="Compliance standard")
@click.option("--count", default=10, help="Number of samples to generate")
@click.option("--output", default="output", help="Output directory")
def dataset(scenario: str | None, standard: str, count: int, output: str) -> None:
    """Generate a dataset."""
    click.echo(f"Generating {count} {standard} samples...")


@cli.group()
def validate() -> None:
    """Validate generated datasets."""


@validate.command()
@click.argument("path")
def dataset(path: str) -> None:
    """Validate a dataset file."""
    click.echo(f"Validating dataset at {path}...")


@cli.group()
def export() -> None:
    """Export datasets."""


@export.command()
@click.argument("path")
@click.option("--format", "-f", default="jsonl", help="Export format")
def dataset(path: str, format: str) -> None:
    """Export a dataset."""
    click.echo(f"Exporting dataset at {path} to {format}...")


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
