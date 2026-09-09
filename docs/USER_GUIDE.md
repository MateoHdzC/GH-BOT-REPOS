# GH-BOT-REPOS — Guía de Usuario (Windows)

Bienvenido a **GH-BOT-REPOS**, la solución de automatización y vigilancia continua de repositorios Git para Windows 10 y 11.

---

## 1. Inicio Rápido

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```
3. La interfaz se abrirá en modo oscuro con la paleta tecnológica moderna.

---

## 2. Añadir un Proyecto

1. Pulsa el botón **"+ Añadir Proyecto"** en la barra superior.
2. Pulsa **"Explorar..."** y selecciona cualquier carpeta de tu equipo (por ejemplo `C:\Users\TuUsuario\Proyectos\MiApp`).
3. Si la carpeta aún no es un repositorio Git, aparecerá un aviso amarillo con la opción **[Inicializar Git]**. Púlsala para ejecutar `git init` inmediatamente.
4. Completa o verifica:
   - **Nombre del proyecto**
   - **Repositorio remoto (GitHub URL)**
   - **Rama (Branch)**: por defecto `main`
   - **Modo**: `AUTO`, `COMMIT_ONLY` o `PAUSED`
   - **Debounce**: intervalo de espera tras cambios (1m, 4m, 5m, 10m, 30m, 1h, etc.)
   - **Safety Guard**: activa la protección contra secretos y eliminaciones masivas.
5. Pulsa **"Añadir Proyecto"**.

---

## 3. Modos de Sincronización

- **AUTO:** Detecta modificaciones -> espera debounce -> `git add -A` -> `git commit` -> `git push` a GitHub.
- **COMMIT_ONLY:** Detecta modificaciones -> espera debounce -> `git add -A` -> `git commit`. No realiza push remoto.
- **PAUSED:** Pausa temporalmente la vigilancia del proyecto sin alterar ni borrar nada de tu repositorio local.

---

## 4. ⚡ Subir Ahora (Manual)

Si estás trabajando y quieres sincronizar de inmediato sin esperar al temporizador:
- Pulsa el botón **"⚡ Subir ahora"** en la tarjeta del proyecto o en el menú del System Tray.
- Si no hay modificaciones en el directorio de trabajo, el bot mostrará en el log: `"No hay cambios para sincronizar"` y **no creará un commit vacío**.

---

## 5. Conexión Segura con GitHub

1. Navega a **Configuración** en la barra lateral.
2. Pega tu Personal Access Token (PAT) con permisos de `repo`.
3. Pulsa **"Conectar GitHub"**.
4. El token se valida directamente contra la API de GitHub y se guarda de forma encriptada en **Windows Credential Manager**. Nunca se guarda en archivos ni aparece en logs.

---

## 6. System Tray y Segundo Plano

- **Cerrar la ventana (X):** La aplicación no se detiene; se oculta a la bandeja del sistema (System Tray) y continúa vigilando tus proyectos.
- **Icono del Tray:**
  - Clic en **Abrir** para restaurar la ventana.
  - Submenú **Proyectos** para ver el estado de cada uno.
  - Opciones rápidas para pausar, reanudar o subir todos.
  - **Salir:** Finaliza de manera limpia todos los watchers, hilos y la aplicación.
