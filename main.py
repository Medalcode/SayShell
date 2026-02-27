"""
SayShell — AI-Powered PowerShell Terminal
Entry point for the interactive CLI session.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.rule import Rule
from rich import print as rprint

from src.config import get_config
from src.ai_engine import generate_command
from src.risk_engine import analyze_risk, RiskResult
from src.executor import run_powershell

console = Console()

BANNER = """
███████╗ █████╗ ██╗   ██╗███████╗██╗  ██╗███████╗██╗     ██╗
██╔════╝██╔══██╗╚██╗ ██╔╝██╔════╝██║  ██║██╔════╝██║     ██║
███████╗███████║ ╚████╔╝ ███████╗███████║█████╗  ██║     ██║
╚════██║██╔══██║  ╚██╔╝  ╚════██║██╔══██║██╔══╝  ██║     ██║
███████║██║  ██║   ██║   ███████║██║  ██║███████╗███████╗███████╗
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
"""

RISK_STYLES: dict[str, tuple[str, str]] = {
    "SAFE":      ("green",  "🟢 SEGURO"),
    "CAUTION":   ("yellow", "🟡 PRECAUCIÓN"),
    "DANGEROUS": ("red",    "🔴 PELIGROSO"),
    "BLOCKED":   ("bold red on white", "⛔ BLOQUEADO"),
}


def render_risk_badge(risk: RiskResult) -> None:
    color, label = RISK_STYLES.get(risk.level, ("white", risk.level))
    score_bar = "█" * (risk.score // 10) + "░" * (10 - risk.score // 10)

    console.print(f"\n  [{color}]{label}[/]  Score: [{color}]{risk.score}/100[/]  [{color}]{score_bar}[/]")

    if risk.reasons:
        console.print("  [dim]Motivos:[/]")
        for reason in risk.reasons:
            console.print(f"    [dim]• {reason}[/]")


def confirm_execution(risk: RiskResult) -> bool:
    """Ask the user to confirm, with stricter wording for higher risk levels."""
    if risk.level == "BLOCKED":
        return False

    if risk.level == "DANGEROUS":
        console.print(
            "\n  [bold red]⚠️  Este comando es potencialmente peligroso.[/]\n"
            "  [red]Escribe exactamente 'EJECUTAR' (en mayúsculas) para confirmar:[/]"
        )
        answer = Prompt.ask("  Confirmación", default="no")
        return answer.strip() == "EJECUTAR"

    answer = Prompt.ask("\n  ¿Ejecutar? [bold][y/n][/]", default="n")
    return answer.strip().lower() in ("y", "s", "si", "sí")


def run_session(config: dict) -> None:
    """Main interactive REPL loop."""
    console.print(f"[bold cyan]{BANNER}[/]", highlight=False)
    console.print(
        Panel(
            Text.from_markup(
                f"  Conectado a [bold green]Groq[/] · Modelo: [cyan]{config['model']}[/]\n"
                "  Escribe tu solicitud en español o inglés.\n"
                "  Escribe [bold]salir[/] o [bold]exit[/] para terminar."
            ),
            title="[bold]SayShell[/] — Terminal Inteligente",
            border_style="cyan",
            padding=(0, 2),
        )
    )

    history: list[dict] = []

    while True:
        console.print()
        console.print(Rule(style="dim"))

        try:
            user_input = Prompt.ask("\n[bold cyan]  ¿Qué quieres hacer?[/]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[dim]  Sesión terminada.[/]\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("salir", "exit", "quit"):
            console.print("\n[dim]  Hasta luego. 👋[/]\n")
            break

        # ── History command ──────────────────────────────────────────────
        if user_input.lower() in ("historial", "history"):
            if not history:
                console.print("  [dim]Sin historial todavía.[/]")
            else:
                for i, entry in enumerate(history, 1):
                    lvl_color = RISK_STYLES.get(entry["risk"], ("white", entry["risk"]))[0]
                    console.print(
                        f"  [dim]{i:>2}.[/] [{lvl_color}]{entry['risk']:10}[/] [cyan]{entry['command']}[/]"
                    )
            continue

        # ── Generate command via AI ──────────────────────────────────────
        console.print()
        with console.status("[bold cyan]  Pensando...[/]", spinner="dots"):
            try:
                command, explanation = generate_command(
                    user_intent=user_input,
                    api_key=config["api_key"],
                    model=config["model"],
                    lang=config["lang"],
                )
            except ValueError as err:
                console.print(f"\n  [bold red]⚠️  Error de IA:[/] {err}")
                continue

        # Handle AI refusing unsafe requests
        if command.startswith("#UNSAFE"):
            console.print(
                Panel(
                    f"[red]{explanation}[/]",
                    title="[bold red]Solicitud rechazada por la IA[/]",
                    border_style="red",
                    padding=(0, 2),
                )
            )
            continue

        # ── Render command + explanation ─────────────────────────────────
        console.print(
            Panel(
                Text.from_markup(
                    f"  [bold white]{command}[/]\n\n"
                    f"  [dim]{explanation}[/]"
                ),
                title="[bold]💡 Comando sugerido[/]",
                border_style="blue",
                padding=(0, 2),
            )
        )

        # ── Risk analysis ─────────────────────────────────────────────────
        risk = analyze_risk(command)
        render_risk_badge(risk)

        # Record in history
        history.append({"command": command, "risk": risk.level, "explanation": explanation})

        # ── Blocked → no execution ────────────────────────────────────────
        if risk.blocked:
            console.print(
                "\n  [bold red]⛔ Comando bloqueado automáticamente.[/] "
                "No se puede ejecutar por razones de seguridad."
            )
            continue

        # ── Confirm + execute ─────────────────────────────────────────────
        if not confirm_execution(risk):
            console.print("  [dim]Cancelado.[/]")
            continue

        console.print("\n  [dim]Ejecutando...[/]")
        stdout, stderr, returncode = run_powershell(command)

        if stdout:
            console.print(
                Panel(stdout, title="[bold green]📤 Resultado[/]", border_style="green", padding=(0, 2))
            )

        if stderr:
            console.print(
                Panel(stderr, title="[bold red]❌ Error[/]", border_style="red", padding=(0, 2))
            )

        if not stdout and not stderr:
            status = "✅ Completado sin salida." if returncode == 0 else f"⚠️ Código de salida: {returncode}"
            console.print(f"\n  [dim]{status}[/]")


def main() -> None:
    config = get_config()
    run_session(config)


if __name__ == "__main__":
    main()
