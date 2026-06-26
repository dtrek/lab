# Setup de la ZBook — instalar Claude Code y Databrain (Fase 0)

Guía paso a paso pensada para alguien que **nunca usó la terminal**. Seguila en
orden. Cada bloque gris es un comando: lo copiás, lo pegás en la terminal y
apretás **Enter**.

> **Plataforma:** HP ZBook con Windows 10, con permisos de administrador.

---

## Conceptos en 1 minuto (para no perderte)

- **Terminal / PowerShell:** una ventana negra (o azul) donde escribís
  comandos en vez de hacer clics. Para abrirla: botón de inicio → escribí
  `PowerShell` → clic en **Windows PowerShell**.
- **Comando:** una línea de texto que le da una orden a la compu. Escribís y
  apretás Enter. Si no devuelve un error en rojo, salió bien.
- **No te asustes con el texto que aparece:** la terminal "habla mucho". Lo
  importante es que **no diga `error` en rojo** al final.

---

## Lo que vamos a instalar (en este orden)

| # | Programa | Para qué |
|---|----------|----------|
| 1 | Python **3.10** | Correr Databrain (el Tobii exige 3.10, NO el 3.12+) |
| 2 | Node.js LTS | Claude Code corre sobre Node |
| 3 | Git para Windows | Bajar el repo del proyecto |
| 4 | Claude Code | Que Claude te asista en la terminal |

---

## Paso 1 — Python 3.10

1. Entrá a: <https://www.python.org/downloads/release/python-31011/>
2. Bajá hasta "Files" y descargá **"Windows installer (64-bit)"**.
3. Abrí el instalador. **MUY IMPORTANTE:** antes de tocar nada, tildá abajo de
   todo la casilla **"Add python.exe to PATH"**. Si no la marcás, después la
   terminal "no encuentra" Python.
4. Clic en **"Install Now"** y esperá a que termine.

**Verificar que quedó bien** — abrí PowerShell (inicio → escribí `PowerShell` →
Enter) y pegá:

```powershell
python --version
```

Tiene que responder algo como `Python 3.10.11`. Si dice eso, perfecto.

> Si dice `Python 3.12` o más alto, tenés otra versión vieja instalada. Avisame
> y lo resolvemos (no es grave).

---

## Paso 2 — Node.js (para Claude Code)

1. Entrá a: <https://nodejs.org>
2. Descargá el botón grande que dice **"LTS"** (es la versión estable).
3. Instalá: siguiente → siguiente → instalar. No hace falta cambiar nada.

**Verificar** — en PowerShell:

```powershell
node --version
```

Tiene que responder algo como `v20.x.x` o `v22.x.x`.

---

## Paso 3 — Git (para bajar el repo)

1. Entrá a: <https://git-scm.com/download/win>
2. Se baja solo el instalador ("64-bit Git for Windows Setup").
3. Instalá: siguiente → siguiente → instalar (todas las opciones por defecto
   están bien).

**Verificar:**

```powershell
git --version
```

Tiene que responder algo como `git version 2.xx`.

> Después de instalar Git, **cerrá y volvé a abrir PowerShell** para que tome el
> cambio.

---

## Paso 4 — Claude Code

En PowerShell, pegá:

```powershell
npm install -g @anthropic-ai/claude-code
```

Va a tardar un minuto y mostrar varias líneas. Cuando vuelve a aparecer el
cursor para escribir, terminó.

**Verificar:**

```powershell
claude --version
```

---

## Paso 5 — Bajar el proyecto Databrain

Vamos a guardarlo en tu carpeta de usuario. Pegá estos comandos **uno por uno**:

```powershell
cd $HOME
git clone https://github.com/dtrek/lab.git databrain-proyecto
cd databrain-proyecto
git checkout claude/databrain-architecture-plan-tmijjd
```

Qué hace cada uno:
- `cd $HOME` → te para en tu carpeta personal.
- `git clone ...` → descarga el repo en una carpeta llamada `databrain-proyecto`.
- `cd databrain-proyecto` → entrás a esa carpeta.
- `git checkout ...` → te pasás a la rama donde está el trabajo.

---

## Paso 6 — Crear el entorno de Python e instalar dependencias

Esto crea un "Python aislado" para el proyecto (no ensucia el resto del sistema).
Pegá uno por uno:

```powershell
python -m venv databrain-env
databrain-env\Scripts\activate
python -m pip install -U pip setuptools
pip install -r databrain\requirements.txt
```

- Después del segundo comando vas a ver que al principio de la línea aparece
  `(databrain-env)`. Eso significa que el entorno está **activado**. Bien.
- El último comando instala todo (LSL, MNE, el Tobii, etc.). Tarda varios
  minutos. Es normal.

> **Si el `pip install` se corta por culpa del Tobii**, hacé esto en su lugar:
> ```powershell
> pip install pylsl mne neurokit2 transformers torch pillow opencv-python pandas numpy matplotlib
> pip install tobii-research==1.11.0
> ```

---

## Paso 7 — Arrancar Claude Code en el proyecto

Asegurate de estar dentro de la carpeta del proyecto (debería decir
`databrain-proyecto` en la ruta) y pegá:

```powershell
claude
```

La primera vez te va a pedir **iniciar sesión** con tu cuenta de Anthropic (la
misma que usás acá). Se abre el navegador, confirmás, y volvés a la terminal.

A partir de ahí, **escribime directamente en esa ventana** y te asisto con los
sensores ya enchufados. Por ejemplo, podés pedirme:

> "corré el test de detección del Tobii y ayudame a interpretar el resultado"

---

## Resumen de verificación rápida

Cuando termines, estos 4 comandos tienen que responder sin error:

```powershell
python --version    # Python 3.10.x
node --version      # v20+ o v22+
git --version       # git version 2.xx
claude --version    # version de Claude Code
```

Si alguno falla, copiame el texto del error y lo resolvemos.

---

## Glosario de problemas comunes

- **"python no se reconoce como comando":** no marcaste "Add to PATH" al instalar
  Python. Reinstalalo marcando esa casilla.
- **Algo "no se reconoce" justo después de instalarlo:** cerrá y reabrí
  PowerShell. Windows necesita reabrir la terminal para ver los programas nuevos.
- **El Tobii no se detecta:** revisá que `pip show tobii-research` diga `1.11.0`
  (no 2.x) y que el tracker esté enchufado por USB. Ver `databrain/README.md`.
