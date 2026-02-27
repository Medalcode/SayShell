"""
SayShell — Config loader
Reads .env and validates required fields at startup.
"""

import os
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


def get_config() -> dict:
    api_key = os.getenv("GROQ_API_KEY", "")
    model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    lang = os.getenv("SAYSHELL_LANG", "es")

    if not api_key or api_key.startswith("gsk_xxx"):
        console.print(
            "\n[bold red]⛔ Error:[/] No se encontró una API key válida de Groq.\n"
            "   Copia [bold].env.example[/] a [bold].env[/] y agrega tu key.\n"
            "   Obtén tu key gratuita en: [link=https://console.groq.com]https://console.groq.com[/link]\n"
        )
        raise SystemExit(1)

    return {
        "api_key": api_key,
        "model": model,
        "lang": lang,
    }
