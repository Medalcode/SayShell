"""
SayShell — Prompt Builder
Constructs a structured, context-aware prompt sent to the LLM.
"""

import os
import platform


def build_prompt(user_intent: str, lang: str = "es") -> str:
    """
    Build the user message sent to the model.
    Includes OS context and current directory for accurate command generation.
    """
    cwd = os.getcwd()
    win_version = platform.version()

    if lang == "es":
        context = (
            f"Directorio actual: {cwd}\n"
            f"Sistema operativo: Windows {win_version}\n"
            f"Solicitud del usuario: {user_intent}"
        )
    else:
        context = (
            f"Current directory: {cwd}\n"
            f"Operating system: Windows {win_version}\n"
            f"User request: {user_intent}"
        )

    return context


def build_system_prompt(lang: str = "es") -> str:
    """
    Build the system prompt that instructs the model on output format.
    """
    if lang == "es":
        return (
            "Eres SayShell, un asistente experto en PowerShell para Windows.\n\n"
            "REGLAS ESTRICTAS:\n"
            "1. Responde SIEMPRE en formato JSON con exactamente estas dos claves:\n"
            '   {"command": "<comando powershell>", "explanation": "<explicación en español>"}\n'
            "2. El campo 'command' debe contener SOLO el comando PowerShell listo para ejecutar. "
            "Sin explicaciones, sin comentarios, sin markdown.\n"
            "3. El campo 'explanation' debe explicar en español simple (máximo 2 oraciones) "
            "qué hace el comando y qué efecto tendrá.\n"
            "4. Si la solicitud es ambigua o peligrosa, devuelve: "
            '{"command": "#UNSAFE", "explanation": "<razón por qué no puedes cumplir la solicitud>"}\n'
            "5. Usa cmdlets de PowerShell modernos cuando sea posible (Get-ChildItem, New-Item, etc.).\n"
            "6. No incluyas texto fuera del JSON."
        )
    else:
        return (
            "You are SayShell, a PowerShell expert assistant for Windows.\n\n"
            "STRICT RULES:\n"
            "1. Always respond in JSON with exactly these two keys:\n"
            '   {"command": "<powershell command>", "explanation": "<brief explanation>"}\n'
            "2. The 'command' field must contain ONLY the raw PowerShell command. No markdown, no comments.\n"
            "3. The 'explanation' field must explain in plain language (max 2 sentences) what the command does.\n"
            "4. If the request is ambiguous or dangerous, return: "
            '{"command": "#UNSAFE", "explanation": "<reason>"}\n'
            "5. Prefer modern PowerShell cmdlets.\n"
            "6. No text outside the JSON."
        )
