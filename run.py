#!/usr/bin/env python3

import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

load_dotenv()  # Load environment variables

from cli import app  # Import the Typer app with all commands

console = Console()

def print_help():
    console.print(Panel("[bold magenta]ShellMate CLI[/bold magenta]\n"
                        "Gemini-powered smart terminal assistant\n\n"
                        "[bold cyan]Commands:[/bold cyan]\n"
                        "  gen       Convert natural language instructions into shell commands\n"
                        "  explain   Explain a shell command in plain English\n\n"
                        "[bold cyan]Options:[/bold cyan]\n"
                        "  --help    Show this message and exit\n\n"
                        "[bold cyan]Examples:[/bold cyan]\n"
                        "  ./run.py gen \"move all .txt files\" --dry\n"
                        "  ./run.py explain \"chmod +x run.py\"\n"))

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
    else:
        app()