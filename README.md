# GH-BOT-REPOS — Windows Edition

<p align="center">
  <img src="assets/icon.png" width="128" height="128" alt="GH-BOT-REPOS Logo">
</p>

<p align="center">
  <b>Sistema autónomo de supervisión, control de versiones y sincronización continua en segundo plano para repositorios Git en Windows.</b><br>
  Diseñado para entornos de desarrollo en Windows 10 y Windows 11 con interfaz Glassmorphism y persistencia en el sistema.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Plataforma-Windows%2010%20%7C%2011%20(x64)-0078D6?style=flat-square&logo=windows" alt="Windows Platform">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python" alt="Python Version">
  <img src="https://img.shields.io/badge/Tests-27%2F27%20Aprobados-10B981?style=flat-square" alt="Tests Status">
  <img src="https://img.shields.io/badge/Licencia-MIT-informational?style=flat-square" alt="License">
</p>

---

## 📋 Índice

- [Visión General](#-visión-general)
- [Arquitectura del Ciclo de Sincronización](#-arquitectura-del-ciclo-de-sincronización)
- [Características Principales](#-características-principales)
- [Seguridad y Protección de Datos](#-seguridad-y-protección-de-datos)
- [Interfaz de Usuario (Glassmorphism)](#-interfaz-de-usuario-glassmorphism)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Compilación del Ejecutable Nativo (.exe)](#-compilación-del-ejecutable-nativo-exe)
- [Suite de Pruebas Unitarias](#-suite-de-pruebas-unitarias)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Licencia](#-licencia)

---

## 🔭 Visión General

**GH-BOT-REPOS** es una solución de ingeniería de software diseñada para desarrolladores que trabajan en múltiples proyectos locales y requieren que sus repositorios Git permanezcan sincronizados con GitHub de manera desatendida y confiable.

A diferencia de scripts básicos o tareas programadas fijas, **GH-BOT-REPOS** implementa observadores del sistema de archivos con **debounce reactivo**, detectando cuándo el desarrollador deja de editar antes de consolidar los cambios. Esto garantiza que cada confirmación contenga unidades lógicas de trabajo completas, previniendo micro-commits redundantes y preservando la integridad del historial de Git.

---

## 🔄 Arquitectura del Ciclo de Sincronización

```
[ EVENTO DEL SISTEMA DE ARCHIVOS ]
                │
                ▼
       [ FILTRO DE RUTAS ]
  (Ignora .git, node_modules,
   .venv, binarios temporales)
                │
                ▼
       [ DEBOUNCE REACTIVO ]
  (Reinicia conteo ante nuevas
   escrituras; espera periodo de calma)
                │
                ▼
       [ BARRERA DE SEGURIDAD ]
  (Escaneo preventivo de secretos .env,
   claves privadas y límites de volumen)
                │
                ▼
         [ git add / commit ]
  (Genera mensaje semántico con
   estadísticas de archivos y timestamp)
                │
                ▼
         [ git push seguro ]
  (Envío con credenciales del sistema;
   reintentos automáticos si no hay red)
```

---

## ✨ Características Principales

### 1. Supervisión Multicarpeta Aislada
Permite monitorizar de forma simultánea múltiples directorios independientes. Cada proyecto opera con su propio hilo de ejecución, debounce configurable y estado de vigilancia.

### 2. Modos de Operación por Proyecto
- **`AUTO`:** Detección automática de cambios, periodo de espera (debounce), creación de commit y push automático al repositorio remoto en GitHub.
- **`COMMIT_ONLY`:** Realiza el ciclo completo hasta la confirmación local (`git commit`), omitiendo el push al remoto para entornos de trabajo desconectados o ramas privadas.
- **`PAUSED`:** Suspende la vigilancia del proyecto sin alterar los archivos ni el repositorio Git.

### 3. Sincronización Inmediata (`Subir Ahora`)
Botón de acción inmediata que ejecuta el ciclo de sincronización sin esperar a que expire el temporizador de debounce. Si no se detectan diferencias reales mediante `git status`, la aplicación previene la creación de commits vacíos.

### 4. Soporte para Cualquier Directorio Local
Permite añadir cualquier carpeta en el disco. Si el directorio seleccionado aún no es un repositorio Git, la interfaz ofrece inicializarlo (`git init`) con un solo clic.

### 5. Resiliencia ante Fallos de Red (Retry Queue)
Si la red se interrumpe durante el envío (`git push`), el commit local queda consolidado y la tarea de sincronización remota entra en una cola de reintentos con algoritmo de retroceso exponencial (*exponential backoff*). Al restaurarse la conectividad, las tareas pendientes se procesan ordenadamente.

### 6. Ejecución en Segundo Plano e Integración con Windows
- **Minimización a la Bandeja del Sistema (System Tray):** Cerrar la ventana principal mantiene la aplicación activa en la bandeja de notificación.
- **Menú Contextual:** Acceso directo para pausar, reanudar o forzar la subida de todos los proyectos desde el icono de la barra de tareas.
- **Inicio Automático:** Opción de inicio conjunto con Windows configurada directamente en el Registro del Usuario (`HKCU`), sin requerir privilegios de administrador.
- **Persistencia Robusta:** Los proyectos y ajustes se almacenan en `%APPDATA%\GH-BOT-REPOS\projects.json`, garantizando persistencia entre reinicios y respaldos espejo en el workspace.

---

## 🔒 Seguridad y Protección de Datos

La aplicación sigue principios estrictos de seguridad orientados a prevenir fugas de información sensible y operaciones destructivas en Git:

1. **Almacenamiento de Credenciales con Windows DPAPI:**
   - Los Personal Access Tokens (PAT) de GitHub no se guardan en archivos JSON ni en texto plano. Se almacenan cifrados a nivel de sistema operativo utilizando **Windows Credential Manager** (`keyring` / DPAPI).
2. **Safety Guard (Anti-Fuga de Secretos):**
   - Análisis heurístico de extensiones y nombres de archivo críticos (`.env`, `.pem`, `.key`, `id_rsa`, `id_ed25519`, `credentials.json`).
   - Si se detecta un archivo de riesgo no protegido por `.gitignore`, el commit se detiene y se notifica al usuario.
3. **Umbrales contra Eliminación Accidental:**
   - Protección configurable que alerta y detiene la confirmación si un cambio supera umbrales masivos de borrado de líneas o archivos.
4. **Enmascaramiento de Logs (Log Sanitization):**
   - Cualquier token accidentalmente presente en salidas de error o URLs remotas es sustituido por `[REDACTED_SECRET]` antes de registrarse en disco.
5. **Políticas de Git Seguro:**
   - **GH-BOT-REPOS** tiene prohibido a nivel arquitectónico invocar comandos destructivos como `git push --force` o `git reset --hard`.

---

## 🎨 Interfaz de Usuario (Glassmorphism)

La interfaz gráfica de usuario está construida sobre **CustomTkinter** y optimizada para pantallas de alta densidad (DPI scaling) en Windows 11/10:

- **Estilo Glassmorphism:** Fondo en negro obsidiana profundo (`#02040A` / `#030712`), tarjetas en azul medianoche translúcido (`#0B1528`) y bordes refractarios de vidrio de 1 píxel (`#1E3A8A`).
- **Acentos Funcionales:** Azul eléctrico vibrante (`#0066FF`) para llamadas a la acción primarias y verde esmeralda (`#10B981`) para confirmaciones de estado.
- **Cero Artefactos de Renderizado:** Renderizado nítido en esquinas redondeadas mediante alineación precisa de `bg_color` sobre el lienzo vectorial de Tkinter.

---

## 💻 Requisitos del Sistema

- **Sistema Operativo:** Windows 10 (versión 1809 o superior) o Windows 11 (64-bit).
- **Git para Windows:** Versión 2.30 o superior, accesible en el `PATH` del sistema.
- **Python:** 3.10 o superior (necesario únicamente si se ejecuta desde el código fuente; no requerido para el ejecutable independiente).

---

## 🚀 Instalación y Configuración

### Opción 1: Ejecutar desde Código Fuente

1. **Clonar el repositorio:**
   ```powershell
   git clone https://github.com/MateoHdzC/GH-BOT-REPOS.git
   cd GH-BOT-REPOS
   ```

2. **Crear y activar un entorno virtual:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Instalar dependencias:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Iniciar la aplicación:**
   ```powershell
   python main.py
   ```

   Para iniciar directamente minimizado en la bandeja del sistema:
   ```powershell
   python main.py --tray
   ```

---

## 🔨 Compilación del Ejecutable Nativo (.exe)

El proyecto incluye un script de automatización con `PyInstaller` para generar un ejecutable autónomo para Windows:

```powershell
python scripts/build_app.py
```

El binario listo para distribución se genera en:
```
dist\GH-BOT-REPOS\GH-BOT-REPOS.exe
```

---

## 🧪 Suite de Pruebas Unitarias

El sistema cuenta con una cobertura integral de pruebas automatizadas sobre configuración, motor de debounce, filtros de seguridad, integración con Git y colas de reintento:

```powershell
python scripts/run_tests.py
```

También es posible invocar directamente el ejecutor de pruebas:
```powershell
pytest tests/ -v
```

---

## 📂 Estructura del Proyecto

```
GH-BOT-REPOS/
├── assets/
│   ├── icon.ico                     # Icono nativo para ejecutables de Windows
│   └── icon.png                     # Icono en alta resolución para la interfaz
├── config/
│   └── projects.json                # Respaldo local de configuración de proyectos
├── docs/
│   ├── ARCHITECTURE.md              # Especificación técnica detallada de componentes
│   └── USER_GUIDE.md                # Manual operativo paso a paso
├── logs/
│   └── app.log                      # Registro operativo en rotación con ofuscación
├── scripts/
│   ├── build_app.py                 # Pipeline de compilación con PyInstaller
│   └── run_tests.py                 # Verificador automatizado de la suite de pruebas
├── src/
│   ├── config/
│   │   ├── manager.py               # Gestor de persistencia en AppData y migraciones
│   │   └── models.py                # Modelos y esquemas de datos del sistema
│   ├── core/
│   │   ├── engine.py                # Orquestador del ciclo de vida y despacho de eventos
│   │   ├── project_manager.py       # Máquina de estados y sincronización por proyecto
│   │   ├── retry_queue.py           # Encolador de reintentos con retroceso exponencial
│   │   ├── safety_guard.py          # Barrera de inspección heurística de archivos y secretos
│   │   └── startup.py               # Integración con el registro de arranque de Windows
│   ├── git/
│   │   ├── credentials.py           # Puente con Windows Credential Manager (DPAPI)
│   │   └── manager.py               # Wrapper seguro de comandos del binario Git
│   ├── ui/
│   │   ├── app.py                   # Ventana principal y controlador de vistas
│   │   ├── theme.py                 # Definición de tokens de diseño y paleta Glassmorphism
│   │   ├── tray.py                  # Integración con la bandeja del sistema (System Tray)
│   │   └── components/
│   │       ├── dashboard_view.py    # Métricas y estadísticas en tiempo real
│   │       ├── logs_view.py         # Visualizador en vivo de registros con filtros
│   │       ├── modal_add_project.py # Asistente de alta y validación de repositorios
│   │       ├── modal_history.py     # Historial cronológico de sincronizaciones
│   │       ├── project_card.py      # Tarjeta interactiva por proyecto supervisado
│   │       ├── settings_view.py     # Gestión de credenciales GitHub y arranque
│   │       └── sidebar.py           # Barra de navegación lateral
│   └── watcher/
│       ├── debounce.py              # Temporizador de quietud reactivo multihilo
│       ├── filter.py                # Reglas de exclusión de rutas y artefactos
│       └── service.py               # Conexión con el servicio nativo watchdog
├── tests/                           # Suite de pruebas con pytest (27 tests)
├── main.py                          # Punto de entrada de la aplicación
├── requirements.txt                 # Dependencias del proyecto
├── README.md                        # Documentación principal del repositorio
└── LICENSE                          # Licencia de código abierto (MIT)
```

---

## 📄 Licencia

Este software se encuentra bajo los términos de la licencia [MIT](LICENSE). Consulte el archivo de licencia para obtener más detalles.
