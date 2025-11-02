import json
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from config import make_client
from context import get_local_context_snippet
from gemini_client import call_gemini_generate
from executor import safe_execute
from prompts import PROMPT_NL_TO_BASH, PROMPT_EXPLAIN
from logger import log_activity

console = Console()
app = typer.Typer(help="ShellMate — Gemini-powered smart terminal assistant")

def nl_to_bash(client, instruction: str, context: dict, model: str = "gemini-2.5-flash") -> tuple[str, dict]:
    prompt = PROMPT_NL_TO_BASH.format(context=json.dumps(context, indent=2), instruction=instruction)
    raw = call_gemini_generate(client, prompt, model=model)
    lines = [l for l in raw.splitlines() if l.strip()]
    cmd_line = lines[0] if lines else ""
    json_part = "\n".join(lines[1:]).strip()
    meta = {}
    if json_part:
        try:
            meta = json.loads(json_part)
        except Exception:
            meta = {"explanation": json_part, "risk_level": "unknown"}
    return cmd_line, meta

def explain_command(client, command: str, model: str = "gemini-2.5-flash") -> str:
    prompt = PROMPT_EXPLAIN.format(command=command)
    return call_gemini_generate(client, prompt, model=model)

def display_command_panel(instruction: str, ctx: dict, cmd_line: str, meta: dict):
    console.print("\n", Panel(f"\n[yellow]{instruction}[/yellow]", title="Instruction", style="green"))
    console.print(Panel(f"\n[bold magenta]{cmd_line}[/bold magenta]\n\n{meta.get('explanation','')}", title="Generated Command", style="bright_blue"))
    risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(meta.get("risk_level","unknown"), "white")
    console.print(Panel(Text(meta.get("risk_level","unknown").upper(), style=risk_color), title="Risk Level", style=risk_color))

@app.command()
def gen(
    instruction: str = typer.Argument(..., help="Natural language instruction"),
    dry: bool = typer.Option(True, "--dry/--no-dry", help="Dry run only?"),
    model: str = typer.Option("gemini-2.5-flash", help="Gemini model"),
):
    client = make_client()
    ctx = get_local_context_snippet(".")
    
    try:
        cmd_line, meta = nl_to_bash(client, instruction, ctx, model=model)
        display_command_panel(instruction, ctx, cmd_line, meta)
        log_activity({
            "type": "gen",
            "instruction": instruction,
            "generated_command": cmd_line,
            "meta": meta,
            "context": ctx,
        })
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    if dry:
        console.print("[cyan]Dry run: command not executed.[/cyan]")
        return

    if Confirm.ask("Execute this command now?", default=False):
        res = safe_execute(cmd_line, dry=False)
        if res.get("executed"):
            console.print(Panel(f"Return code: {res.get('returncode')}\n\nStdout:\n{res.get('stdout')}\n\nStderr:\n{res.get('stderr')}", title="Execution Result", style="bright_blue"))
            log_activity({
                "type": "execution_result",
                "command": cmd_line,
                "returncode": res.get("returncode"),
                "stdout": res.get("stdout"),
                "stderr": res.get("stderr"),
            })
        else:
            console.print("[red]Execution failed:[/red]", res)
    else:
        console.print("[yellow]Execution aborted by user.[/yellow]")

@app.command()
def explain(
    text: str = typer.Argument(..., help="Shell command to explain"),
    model: str = typer.Option("gemini-2.5-flash", help="Gemini model"),
):
    client = make_client()
    try:
        explanation = explain_command(client, text, model=model)
        console.print(Panel(explanation, title=f"Explanation of '{text}'", style="bright_green"))
        log_activity({
            "type": "explain",
            "command": text,
            "explanation": explanation,
        })
    except Exception as e:
        console.print(f"[red]Error explaining command:[/red] {e}")

@app.command()
def repl(model: str = typer.Option("gemini-2.5-flash", help="Gemini model")):
    client = make_client()
    console.print(Panel("[bold green]ShellMate REPL — type natural-language commands. Type 'exit' to quit.[/bold green]"))
    history = []
    
    while True:
        try:
            instruction = Prompt.ask("[bold cyan]shellmate>[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Exiting REPL. Goodbye![/bold red]")
            break
        if not instruction or instruction.strip().lower() in ("exit", "quit"):
            console.print("[bold yellow]Bye![/bold yellow]")
            break
        history.append(instruction)
        
        try:
            cmd_line, meta = nl_to_bash(client, instruction, model=model)
            log_activity({
                "type": "repl_gen",
                "instruction": instruction,
                "generated_command": cmd_line,
                "meta": meta
            })
            execute_now = Confirm.ask("Execute this command?", default=False)
            if execute_now:
                res = safe_execute(cmd_line, dry=False)
                if res.get("executed"):
                    console.print(Panel(res.get("stdout") or "(no stdout)", title="Stdout", style="bright_blue"))
                    if res.get("stderr"):
                        console.print(Panel(res.get("stderr"), title="Stderr", style="red"))
                    log_activity({
                        "type": "repl_execution_result",
                        "command": cmd_line,
                        "returncode": res.get("returncode"),
                        "stdout": res.get("stdout"),
                        "stderr": res.get("stderr"),
                    })
                else:
                    console.print("[red]Execution error:[/red]", res)
        except Exception as exc:
            console.print("[red]Error processing instruction:[/red]", exc)
