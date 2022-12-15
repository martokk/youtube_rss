import typer
from loguru import logger
from rich.console import Console

from youtube_rss import version
from youtube_rss.example import ExampleClass

# Configure Loguru Logger
logger.add("log.log", level="TRACE", rotation="50 MB")

# Configure Rich Console
console = Console()

# Configure Typer
app = typer.Typer(
    name="youtube_rss",
    help="A python project created by Martokk.",
    add_completion=False,
)


# Print Current Version
def version_callback(print_version: bool) -> None:
    """Print the version of the package."""
    if print_version:
        console.print(f"[yellow]youtube_rss[/] version: [bold blue]{version}[/]")
        raise typer.Exit()


# Typer Commands
@app.command()
def main(
    profile: str = typer.Option(..., help="Profile to load."),
    print_version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Prints the version of the youtube_rss package.",
    ),
) -> None:

    # Example Entry Point
    console.print(ExampleClass().print_name(name="Ron Paul"))
    logger.info(f"Example Entry Point! {profile=}")

    # Example #DIV/0 Logging Error (caught by @logger.catch decorator)
    ExampleClass().example_divide_by_zero()


if __name__ == "__main__":
    app()
