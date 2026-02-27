# SayShell — Skills

> **Principio rector:** Antes de crear una skill nueva, verifica si una existente
> puede recibir un **parámetro extra** para hacer lo mismo.
> Preferimos skills paramétricas a archivos proliferados.

---

## Skill 1: `generate_command`

**Archivo:** [`src/ai_engine.py`](src/ai_engine.py) · **Función:** `generate_command()` · **Líneas:** 15–74

**Input:** `user_intent: str, api_key: str, model: str, lang: str`
**Output:** `(command: str, explanation: str)`

**Qué hace:**
- Construye mensajes system + user vía `build_prompt` / `build_system_prompt`
- Llama a Groq API (`client.chat.completions.create`)
- Limpia markdown fences del response (`re.sub`)
- Parsea JSON `{"command": ..., "explanation": ...}`
- Maneja errores de API con mensajes en español

**Punto de extensión (NO crear nueva skill):**
Para cambiar el proveedor de IA (OpenAI, Mistral, etc.), agrega parámetro
`base_url: str = None` a `generate_command()` y pásalo al constructor de `Groq`.
No se necesita una skill separada por proveedor.

```
# Insertar en línea 26 de src/ai_engine.py:
client = Groq(api_key=api_key, base_url=base_url) if base_url else Groq(api_key=api_key)
```

---

## Skill 2: `analyze_risk`

**Archivo:** [`src/risk_engine.py`](src/risk_engine.py) · **Función:** `analyze_risk()` · **Líneas:** 69–117

**Input:** `command: str`
**Output:** `RiskResult(level, score, reasons, blocked)`

**Qué hace:**
- Compara contra `BLOCKED_PATTERNS` (bloqueo instantáneo)
- Acumula score: `HIGH_RISK_PATTERNS` (+60), `MEDIUM_RISK_PATTERNS` (+25)
- Aplica penalizaciones: `FLAG_PENALTIES` (-Force, -Recurse) y `SENSITIVE_PATH_PATTERNS`
- Clasifica en SAFE / CAUTION / DANGEROUS / BLOCKED

**Punto de extensión (NO crear nueva skill):**
Para añadir nuevos patrones de riesgo, edita las tablas en `src/risk_engine.py`:

- Nuevo bloqueo total → añadir a `BLOCKED_PATTERNS` (línea 21)
- Nuevo cmdlet peligroso → añadir a `HIGH_RISK_PATTERNS` (línea 30)
- Nuevo cmdlet sensible → añadir a `MEDIUM_RISK_PATTERNS` (línea 40)
- Nuevo flag peligroso → añadir a `FLAG_PENALTIES` (línea 51)
- Nueva ruta sensible → añadir a `SENSITIVE_PATH_PATTERNS` (línea 57)

**NO crear** `analyze_risk_strict()` o `analyze_risk_lite()` — usa el parámetro
`strict: bool = False` si necesitas modo más agresivo:

```
# Insertar en línea 105 de src/risk_engine.py (antes del min()):
if strict:
    score += 20  # Penalización extra en modo estricto
```

---

## Skill 3: `run_powershell`

**Archivo:** [`src/executor.py`](src/executor.py) · **Función:** `run_powershell()` · **Líneas:** 10–37

**Input:** `command: str, timeout: int = 30`
**Output:** `(stdout: str, stderr: str, returncode: int)`

**Qué hace:**
- Lanza `powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command <cmd>`
- Captura stdout/stderr por separado
- Maneja timeout, PowerShell no encontrado, y errores inesperados

**Punto de extensión (NO crear nueva skill):**
Para modo `dry_run` (simular sin ejecutar), agrega parámetro `dry_run: bool = False`:

```
# Insertar en línea 10 de src/executor.py (nueva firma):
def run_powershell(command: str, timeout: int = 30, dry_run: bool = False) -> Tuple[str, str, int]:

# Insertar en línea 15 (antes del try):
    if dry_run:
        return f"[DRY-RUN] Se ejecutaría: {command}", "", 0
```

---

## Skill 4: `build_prompt` + `build_system_prompt`

**Archivo:** [`src/prompt_builder.py`](src/prompt_builder.py) · **Líneas:** 10–65

**Input:** `user_intent: str, lang: str = "es"`
**Output:** `str` (mensaje para el LLM)

**Qué hace:**
- `build_prompt`: inyecta CWD y versión de Windows como contexto en el mensaje usuario
- `build_system_prompt`: define identidad, formato JSON obligatorio y reglas del modelo

**Punto de extensión (NO crear nueva skill):**
Para añadir más contexto al prompt (usuario de Windows, historial reciente),
extiende `build_prompt()` con parámetros opcionales en lugar de crear `build_prompt_v2`:

```
# Modificar firma en línea 10 de src/prompt_builder.py:
def build_prompt(user_intent: str, lang: str = "es", recent_history: list[str] | None = None) -> str:

# Insertar después de línea 29 (antes del return):
    if recent_history:
        history_block = "\n".join(f"- {h}" for h in recent_history[-3:])
        label = "Comandos recientes de esta sesión" if lang == "es" else "Recent session commands"
        context += f"\n{label}:\n{history_block}"
```

---

## Skill 5: `load_config`

**Archivo:** [`src/config.py`](src/config.py) · **Función:** `get_config()` · **Líneas:** 14–27

**Input:** ninguno (lee `.env`)
**Output:** `dict {api_key, model, lang}`

**Qué hace:**
- Llama a `load_dotenv()`
- Lee `GROQ_API_KEY`, `GROQ_MODEL`, `SAYSHELL_LANG`
- Valida que API key exista y no sea placeholder
- Imprime error descriptivo y hace `SystemExit(1)` si falta

**No requiere extensión actualmente.** Si en el futuro se soportan perfiles
múltiples, agregar parámetro `profile: str = "default"` aquí.

---

## Mapa de dependencias

```
ShellAgent (main.py)
    ├── load_config          → src/config.py
    ├── generate_command     → src/ai_engine.py
    │       └── build_prompt / build_system_prompt  → src/prompt_builder.py
    ├── analyze_risk         → src/risk_engine.py
    └── run_powershell       → src/executor.py
```

---

## Archivos huérfanos tras esta arquitectura

| Archivo | Estado | Razón |
|---------|--------|-------|
| `test_risk.py` | ✅ Activo | Script de smoke test, mantener |
| `src/__init__.py` | ✅ Activo | Necesario para imports del paquete |
| Ningún archivo huérfano | — | El proyecto nació limpio, sin duplicados |

---

## Regla de reutilización (resumen)

| Antes de... | Verifica primero... |
|-------------|---------------------|
| Crear `analyze_risk_strict` | Agregar `strict: bool` a `analyze_risk()` |
| Crear `generate_command_openai` | Agregar `base_url: str` a `generate_command()` |
| Crear `run_powershell_dry` | Agregar `dry_run: bool` a `run_powershell()` |
| Crear `build_prompt_with_history` | Agregar `recent_history: list` a `build_prompt()` |
| Crear nuevo agente | ¿Tiene estado propio + decisiones autónomas? Si no → skill |
