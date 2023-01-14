import typer
from rich.console import Console

from youtube_rss import settings, version
from youtube_rss.core.logger import logger
from youtube_rss.core.server import start_server

# Configure Rich Console
console = Console()

# Configure Typer
typer_app = typer.Typer(
    name=settings.project_name,
    help=settings.project_description,
    add_completion=False,
)


# Typer Command Callbacks
def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]{settings.project_name}[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


# Typer Commands
@typer_app.command()
def main(
    print_version: bool = typer.Option(  # pylint: disable=unused-argument
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the '{APP_NAME}' package.",
    ),
) -> None:
    """Main entrypoint into application"""

    # Start Uvicorn
    logger.debug("Starting Server...")
    start_server()
