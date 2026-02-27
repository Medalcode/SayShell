"""
SayShell — PowerShell Executor
Runs a command via PowerShell subprocess with timeout protection.
"""

import subprocess
from typing import Tuple


def run_powershell(command: str, timeout: int = 30) -> Tuple[str, str, int]:
    """
    Execute a PowerShell command.
    Returns (stdout, stderr, returncode).
    """
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", command,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    except subprocess.TimeoutExpired:
        return "", f"⏱️ El comando excedió el límite de {timeout} segundos y fue cancelado.", 1

    except FileNotFoundError:
        return "", "❌ PowerShell no fue encontrado. Verifica que esté instalado y en el PATH.", 1

    except Exception as e:  # noqa: BLE001
        return "", f"Error inesperado: {e}", 1
