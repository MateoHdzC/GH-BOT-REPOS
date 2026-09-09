# GH-BOT-REPOS (Windows)

<p align="center">
  <img src="assets/icon.png" width="128" height="128" alt="GH-BOT-REPOS Logo">
</p>

<p align="center">
  <b>Automatización y sincronización continua en segundo plano para repositorios Git en Windows.</b><br>
  Construido desde cero para Windows 10 y Windows 11.
</p>

---

## 🚀 ¿Qué es GH-BOT-REPOS?

**GH-BOT-REPOS** es una aplicación de escritorio nativa para Windows que supervisa activamente múltiples proyectos Git locales en segundo plano. Cuando detecta modificaciones en el sistema de archivos, gestiona un ciclo inteligente de **debounce reactivo**, comprueba la seguridad de los archivos (evitando la filtración de secretos o eliminaciones masivas accidentales), prepara los cambios (`git add`), crea el commit y realiza el `push` automático a GitHub.

---

## ✨ Características Principales

- **Vigilancia Multicarpeta Real:** Soporta múltiples proyectos Git simultáneos mediante `watchdog` con observadores aislados e independientes.
- **Debounce Inteligente por Proyecto:** Evita commits prematuros mientras estás escribiendo. Si guardas varias veces seguidas, el temporizador se reinicia hasta completar el periodo de calma (1m, 4m, 5m, 10m, 30m, 1h, 2h, 4h, 8h, 24h o personalizado).
- **Modos de Operación:**
  - `AUTO`: Detecta -> Debounce -> Commit -> Push a GitHub.
  - `COMMIT_ONLY`: Detecta -> Debounce -> Commit local únicamente.
  - `PAUSED`: Pausa la automatización sin tocar tus archivos ni tu Git local.
- **⚡ Subir Ahora:** Fuerza una sincronización inmediata ignorando el debounce. Si no hay cambios reales, **no crea commits vacíos**.
- **Cualquier Carpeta de Windows:** Permite vigilar cualquier directorio local. Si no es un repositorio Git, ofrece inicializarlo con `git init` en un solo clic.
- **Seguridad y Windows Credential Manager:**
  - Los Personal Access Tokens (PAT) de GitHub se almacenan cifrados mediante la API nativa de Windows (`keyring` / DPAPI).
  - **Nunca** se guardan tokens en archivos JSON ni se imprimen en logs.
  - El sistema enmascara automáticamente tokens detectados en cadenas de log (`[REDACTED_SECRET]`).
- **Safety Guard (Anti-Fugas y Anti-Destrucción):**
  - Bloquea commits automáticos si detecta archivos sospechosos (`.env`, `*.pem`, `*.key`, `id_rsa`, etc.).
  - Advierte y frena sincronizaciones si se supera el umbral de archivos modificados o líneas eliminadas.
- **Retry Queue:** Si un commit tiene éxito pero la conexión a internet falla durante el `push`, la operación se encola y se reintenta automáticamente con backoff exponencial cuando se restablece la red.
- **Modo DRY RUN:** Simula todo el proceso en los logs sin alterar el historial Git ni enviar datos a GitHub.
- **Segundo Plano y System Tray:**
  - Cerrar la ventana principal minimiza la aplicación a la bandeja del sistema (System Tray).
  - Menú contextual interactivo en la bandeja con acceso a proyectos, pausar todos, reanudar todos y subir todos.
- **Inicio con Windows:** Configura el arranque automático opcional mediante el Registro del Usuario (`HKCU`), sin requerir permisos de Administrador.
- **Interfaz Moderna Dark Mode:** Diseñada con CustomTkinter siguiendo la paleta tecnológica (`#141416`, `#1C1C1F`, `#232328`, `#0A84FF`, `#30D158`, `#FF9F0A`, `#FF453A`).

---

## 🛠 Requisitos del Sistema

- **Sistema Operativo:** Windows 10 o Windows 11 (64-bit).
- **Python:** 3.10 o superior (si se ejecuta desde código fuente).
- **Git para Windows:** Instalado y accesible en el `PATH` del sistema.

---

## 📦 Instalación y Puesta en Marcha

### 1. Clonar o descargar el repositorio
```powershell
git clone https://github.com/usuario/GH-BOT-REPOS.git
cd GH-BOT-REPOS
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Iniciar la aplicación
```powershell
python main.py
```

Para iniciar directamente en la bandeja del sistema:
```powershell
python main.py --tray
```

---

## 📐 Estructura de Arquitectura

```
GH-BOT-REPOS/
├── .github/
│   └── workflows/
│       └── ci.yml
├── assets/
│   ├── icon.ico
│   └── icon.png
├── config/
│   └── projects.json
├── docs/
│   ├── ARCHITECTURE.md
│   └── USER_GUIDE.md
├── logs/
│   ├── .gitkeep
│   └── app.log
├── scripts/
│   ├── build_app.py
│   └── run_tests.py
├── src/
│   ├── config/
│   │   ├── manager.py
│   │   └── models.py
│   ├── core/
│   │   ├── engine.py
│   │   ├── project_manager.py
│   │   ├── retry_queue.py
│   │   ├── safety_guard.py
│   │   └── startup.py
│   ├── git/
│   │   ├── credentials.py
│   │   └── manager.py
│   ├── ui/
│   │   ├── app.py
│   │   ├── theme.py
│   │   ├── tray.py
│   │   └── components/
│   │       ├── dashboard_view.py
│   │       ├── logs_view.py
│   │       ├── modal_add_project.py
│   │       ├── modal_history.py
│   │       ├── project_card.py
│   │       ├── settings_view.py
│   │       └── sidebar.py
│   ├── utils/
│   │   ├── logger.py
│   │   └── notifier.py
│   └── watcher/
│       ├── debounce.py
│       ├── filter.py
│       └── service.py
├── tests/
├── .gitignore
├── LICENSE
├── main.py
├── README.md
└── requirements.txt
```

---

## 🧪 Pruebas Automatizadas

El proyecto incluye una suite exhaustiva de tests unitarios y de integración con `pytest`:

```powershell
python scripts/run_tests.py
```

O directamente mediante `pytest`:
```powershell
python -m pytest tests/ -v
```

---

## 🔨 Generación del Ejecutable Windows (.exe)

Para compilar la aplicación en un paquete independiente listo para Windows sin depender de la consola de Python:

```powershell
python scripts/build_app.py
```

El ejecutable se generará en:
```
dist/GH-BOT-REPOS/GH-BOT-REPOS.exe
```

---

## 🔒 Principios de Seguridad

1. **Git Safe Mode:** `GH-BOT-REPOS` **nunca** ejecuta `git push --force` ni `git reset --hard`.
2. **Scrubbing de Logs:** Cualquier clave o token que aparezca en respuestas o URLs es ofuscado como `[REDACTED_SECRET]` antes de escribirse en `logs/app.log`.
3. **Persistencia No Sensible:** `config/projects.json` solo almacena nombres, rutas, debounce y modos de sincronización. Las credenciales de GitHub se delegan exclusivamente a las APIs nativas de Windows Credential Manager.

---

## 📄 Licencia

Este proyecto está distribuido bajo los términos de la licencia [MIT](LICENSE).
