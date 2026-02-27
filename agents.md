# SayShell — Agents

> **Principio rector:** Un agente por responsabilidad conceptual, no por tarea.
> SayShell tiene un pipeline lineal: Entrada → IA → Riesgo → Ejecución → Salida.
> No necesita múltiples agentes — necesita **un agente orquestador** y **capas funcionales** bien definidas.

---

## Agente Único: `ShellAgent`

**Archivo:** `main.py` → función `run_session()`

**Rol:** Orquestador generalista del ciclo completo de la sesión.

**Responsabilidades:**
1. Recibir el prompt del usuario (lenguaje natural)
2. Delegar generación de comando → `skill: generate_command`
3. Delegar análisis de riesgo → `skill: analyze_risk`
4. Presentar resultado con contexto visual (badge, explicación, score)
5. Gestionar flujo de confirmación según nivel de riesgo
6. Delegar ejecución → `skill: run_powershell`
7. Mostrar output o error
8. Mantener historial de sesión en memoria

**Estado interno (en memoria, no persistido):**
```python
history: list[dict]  # {command, risk, explanation}
config: dict         # {api_key, model, lang}
```

**Por qué NO se divide en agentes separados:**
- No hay concurrencia. El pipeline es secuencial.
- Un "RiskAgent" o "ExecutorAgent" separado añadiría capas de indirección
  sin beneficio real — sus responsabilidades son skills, no agentes.
- Regla: si no tiene estado propio ni toma decisiones autónomas → es una skill.

---

## Regla de Densidad

> Antes de crear un nuevo agente, pregunta:
> ¿Tiene **estado persistente propio**? ¿Toma **decisiones autónomas**?
> Si la respuesta a ambas es NO → es una **skill**, no un agente.

### Decisiones ya tomadas por esta regla:

| Candidato descartado | Razón | Dónde vive |
|---------------------|-------|------------|
| `RiskAgent` | Sin estado, sin decisión autónoma | `skill: analyze_risk` |
| `ExecutorAgent` | Wrapper de subprocess | `skill: run_powershell` |
| `PromptAgent` | Builder puro, sin lógica propia | `skill: build_prompt` |
| `ConfigAgent` | Lee .env una vez al arrancar | `skill: load_config` |

---

## Extensión futura (cuando SÍ justificaría un segundo agente)

Crear un `HistoryAgent` **solo si**:
- El historial se persiste en disco/DB entre sesiones
- El agente puede buscar, filtrar y exportar historial de forma autónoma
- Tiene su propia capa de almacenamiento y acceso

Hasta entonces: `history` vive como lista en `ShellAgent`.
