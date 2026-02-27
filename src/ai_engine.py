"""
SayShell — AI Engine
Calls the Groq API (OpenAI-compatible) and parses the structured response.
"""

import json
import re
from typing import Tuple

from groq import Groq, APIConnectionError, AuthenticationError, RateLimitError

from src.prompt_builder import build_prompt, build_system_prompt


def generate_command(
    user_intent: str,
    api_key: str,
    model: str = "llama3-70b-8192",
    lang: str = "es",
) -> Tuple[str, str]:
    """
    Ask the LLM to generate a PowerShell command for the given intent.
    Returns (command, explanation).
    Raises ValueError on AI/API errors with a user-friendly message.
    """
    client = Groq(api_key=api_key)

    system_prompt = build_system_prompt(lang)
    user_message = build_prompt(user_intent, lang)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
            max_tokens=256,
        )
    except AuthenticationError:
        raise ValueError(
            "La API key de Groq es inválida. Verifica tu archivo .env."
        )
    except RateLimitError:
        raise ValueError(
            "Límite de solicitudes alcanzado en Groq. Espera unos segundos e intenta de nuevo."
        )
    except APIConnectionError:
        raise ValueError(
            "No se pudo conectar a la API de Groq. Verifica tu conexión a internet."
        )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if the model added them
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
        command = data.get("command", "").strip()
        explanation = data.get("explanation", "").strip()
    except json.JSONDecodeError:
        # Fallback: try to extract something useful from raw text
        raise ValueError(
            f"La IA devolvió una respuesta inesperada. Intenta reformular tu solicitud.\n"
            f"Respuesta raw: {raw[:200]}"
        )

    if not command:
        raise ValueError("La IA no pudo generar un comando para esa solicitud.")

    return command, explanation
