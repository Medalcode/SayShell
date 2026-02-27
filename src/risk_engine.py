"""
SayShell — Risk Engine
Scores PowerShell commands on a 0–100 risk scale and classifies them.
"""

import re
from dataclasses import dataclass, field


@dataclass
class RiskResult:
    level: str        # SAFE | CAUTION | DANGEROUS | BLOCKED
    score: int        # 0–100+
    reasons: list[str] = field(default_factory=list)
    blocked: bool = False


# ─── Pattern tables ────────────────────────────────────────────────────────────

# ⛔ Instant BLOCK — always dangerous, no exceptions
BLOCKED_PATTERNS: list[tuple[str, str]] = [
    (r"format-volume|format-disk|clear-disk",      "Formatea o borra discos completos"),
    (r"invoke-expression|iex\b",                   "Ejecuta código arbitrario (iex / Invoke-Expression)"),
    (r"[A-Za-z0-9+/]{20,}==?\s*\|\s*iex",         "Detectado patrón de ejecución de base64 ofuscado"),
    (r"new-object.*webclient.*download",           "Descarga y ejecución remota detectada"),
    (r"start-process.*-verb.*runas",               "Intento de escalación de privilegios"),
]

# 🔴 DANGEROUS (+60 pts each)
HIGH_RISK_PATTERNS: list[tuple[str, str]] = [
    (r"remove-item\b",        "remove-item puede borrar archivos o carpetas"),
    (r"\brm\b",               "rm puede borrar archivos"),
    (r"shutdown\b",           "Apaga el sistema"),
    (r"restart-computer\b",   "Reinicia el sistema"),
    (r"stop-computer\b",      "Apaga el sistema"),
    (r"disable-netadapter\b", "Desactiva la conexión de red"),
]

# 🟡 CAUTION (+25 pts each)
MEDIUM_RISK_PATTERNS: list[tuple[str, str]] = [
    (r"stop-process\b",          "Detiene un proceso en ejecución"),
    (r"kill\b",                  "Termina un proceso forzosamente"),
    (r"set-executionpolicy\b",   "Cambia la política de ejecución de scripts"),
    (r"set-service\b",           "Modifica un servicio del sistema"),
    (r"net\s+user\b",            "Modifica cuentas de usuario"),
    (r"reg\s+(add|delete)\b",    "Modifica el registro de Windows"),
    (r"schtasks\b",              "Programa tareas del sistema"),
]

# 🔺 Flag/path penalties
FLAG_PENALTIES: list[tuple[str, int, str]] = [
    (r"-force\b",       20, "Flag -Force fuerza la operación sin confirmación"),
    (r"-recurse\b",     20, "Flag -Recurse actúa sobre subdirectorios recursivamente"),
    (r"-confirm:?\$?false", 15, "Suprime confirmaciones del sistema"),
]

SENSITIVE_PATH_PATTERNS: list[tuple[str, int, str]] = [
    (r"c:\\windows\\system32", 30, "Afecta System32 — directorio crítico del sistema"),
    (r"c:\\windows",           20, "Afecta el directorio de Windows"),
    (r"c:\\",                  15, "Afecta la raíz del disco C:"),
    (r"hklm:|hkcu:",           15, "Modifica el registro de Windows"),
]


def _match(pattern: str, cmd: str) -> bool:
    return bool(re.search(pattern, cmd, re.IGNORECASE))


def analyze_risk(command: str) -> RiskResult:
    """Analyze a PowerShell command and return a RiskResult."""
    cmd = command.strip()
    score = 0
    reasons: list[str] = []

    # ── Instant block check ──────────────────────────────────────────────────
    for pattern, reason in BLOCKED_PATTERNS:
        if _match(pattern, cmd):
            return RiskResult(level="BLOCKED", score=100, reasons=[reason], blocked=True)

    # ── High risk ────────────────────────────────────────────────────────────
    for pattern, reason in HIGH_RISK_PATTERNS:
        if _match(pattern, cmd):
            score += 60
            reasons.append(reason)

    # ── Medium risk ──────────────────────────────────────────────────────────
    for pattern, reason in MEDIUM_RISK_PATTERNS:
        if _match(pattern, cmd):
            score += 25
            reasons.append(reason)

    # ── Flag penalties ───────────────────────────────────────────────────────
    for pattern, pts, reason in FLAG_PENALTIES:
        if _match(pattern, cmd):
            score += pts
            reasons.append(reason)

    # ── Sensitive path penalties ─────────────────────────────────────────────
    for pattern, pts, reason in SENSITIVE_PATH_PATTERNS:
        if _match(pattern, cmd):
            score += pts
            reasons.append(reason)

    # ── Classify ─────────────────────────────────────────────────────────────
    score = min(score, 100)
    blocked = score >= 90

    if blocked:
        level = "BLOCKED"
    elif score >= 60:
        level = "DANGEROUS"
    elif score >= 25:
        level = "CAUTION"
    else:
        level = "SAFE"

    return RiskResult(level=level, score=score, reasons=reasons, blocked=blocked)
