# SayShell 🐚

> **Terminal inteligente de PowerShell impulsado por IA.**
> Describe en español o inglés lo que quieres hacer. SayShell genera el comando, te explica qué hace, evalúa el riesgo y pide confirmación antes de ejecutar.

---

## ✨ Características

- 🧠 **IA con Groq** — generación rápida de comandos vía `llama3-70b` (API gratuita)
- 🛡️ **Motor de riesgo** — clasificación automática: SAFE / CAUTION / DANGEROUS / BLOCKED
- 📖 **Explicaciones en español** — sabes exactamente qué hará el comando antes de ejecutarlo
- ⛔ **Bloqueo automático** — comandos destructivos nunca llegan a ejecutarse
- 🔴 **Doble confirmación** — los comandos peligrosos requieren escribir `EJECUTAR`
- 📜 **Historial de sesión** — escribe `historial` para ver los comandos anteriores

---

## 🚀 Inicio rápido

### Requisitos
- Python 3.10+
- Windows con PowerShell

### 1. Clonar el repositorio
```bash
git clone https://github.com/Medalcode/SayShell.git
cd SayShell
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar API key de Groq (gratis)
1. Crea una cuenta en [https://console.groq.com](https://console.groq.com)
2. Ve a **API Keys** → **Create API Key**
3. Copia el archivo de configuración:
```bash
copy .env.example .env
```
4. Abre `.env` y pega tu key en `GROQ_API_KEY`

### 4. Ejecutar
```bash
python main.py
```

---

## 🖥️ Uso

```
███████╗ █████╗ ██╗   ██╗███████╗██╗  ██╗███████╗██╗     ██╗
...

  ¿Qué quieres hacer? > listar los archivos de esta carpeta

  💡 Comando sugerido
  Get-ChildItem

  Muestra el contenido del directorio actual, incluyendo archivos y carpetas.

  🟢 SEGURO  Score: 0/100  ██████████

  ¿Ejecutar? [y/n]: y

  📤 Resultado
  Directorio: D:\Github\SayShell
  ...
```

### Ejemplos de solicitudes

| Lo que escribes | Lo que genera |
|----------------|---------------|
| `listar archivos de esta carpeta` | `Get-ChildItem` |
| `crear una carpeta llamada proyectos` | `New-Item -ItemType Directory -Name "proyectos"` |
| `ver qué procesos están corriendo` | `Get-Process` |
| `mostrar la IP de esta computadora` | `Get-NetIPAddress` |
| `cuánta RAM libre tengo` | `Get-CimInstance Win32_OperatingSystem \| Select-Object FreePhysicalMemory` |
| `borrar archivos del sistema` | ⛔ BLOQUEADO |

### Comandos especiales de sesión

| Comando | Efecto |
|---------|--------|
| `historial` | Muestra los comandos de la sesión actual |
| `salir` / `exit` | Termina la sesión |

---

## 🛡️ Sistema de riesgo

| Nivel | Badge | Acción requerida |
|-------|-------|-----------------|
| SAFE | 🟢 verde | Confirmación simple `y/n` |
| CAUTION | 🟡 amarillo | Confirmación simple con advertencia |
| DANGEROUS | 🔴 rojo | Debes escribir `EJECUTAR` en mayúsculas |
| BLOCKED | ⛔ bloqueado | No se ejecuta bajo ninguna circunstancia |

**Siempre bloqueados:** `Remove-Item -Recurse -Force`, `Format-Volume`, `Invoke-Expression` / `iex`, payloads base64, escalación de privilegios, descarga y ejecución remota.

---

## 📁 Estructura del proyecto

```
SayShell/
├── main.py                  # REPL principal con TUI (rich)
├── requirements.txt
├── .env.example             # Plantilla de configuración
├── test_risk.py             # Tests del motor de riesgo
└── src/
    ├── config.py            # Carga y valida configuración
    ├── ai_engine.py         # Llama a Groq API y parsea respuesta JSON
    ├── prompt_builder.py    # Construye prompt con contexto (CWD, OS)
    ├── risk_engine.py       # Motor de riesgo: scoring 0–100
    └── executor.py          # Ejecutor de PowerShell con timeout
```

---

## ⚙️ Configuración (`.env`)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `GROQ_API_KEY` | requerida | Tu API key de [console.groq.com](https://console.groq.com) |
| `GROQ_MODEL` | `llama3-70b-8192` | Modelo a usar |
| `SAYSHELL_LANG` | `es` | Idioma de respuestas (`es` / `en`) |

---

## 🧪 Tests

Ejecuta los tests del motor de riesgo (sin API key necesaria):

```bash
python test_risk.py
```

Resultado esperado:
```
PASS ✅  [BLOCKED   ] score=100  cmd=Remove-Item -Recurse -Force C:\
PASS ✅  [SAFE      ] score=  0  cmd=Get-ChildItem
PASS ✅  [BLOCKED   ] score=100  cmd=iex (New-Object Net.WebClient)...
PASS ✅  [SAFE      ] score=  0  cmd=mkdir pruebas
PASS ✅  [CAUTION   ] score= 25  cmd=Stop-Process -Name chrome
=== TODOS LOS TESTS PASARON ===
```

---

## 📄 Licencia

MIT