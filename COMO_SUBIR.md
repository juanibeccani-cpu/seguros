# Cómo subir esta app a GitHub y Vercel (paso a paso, sin errores de carpetas)

## 0) Si ya tenías un repo con la estructura mal armada

En GitHub: entrá al repo → Settings (del repo, al final del todo) → Danger Zone →
"Delete this repository". Empezamos de cero para evitar arrastrar el problema.

En Vercel: entrá al proyecto → Settings → Advanced → "Delete Project".

## 1) Ubicar la carpeta en tu compu

Descomprimí este zip. Vas a tener una carpeta llamada `seguros_app`.
Anotá bien dónde quedó (ej: `Descargas/seguros_app` o `Escritorio/seguros_app`).

## 2) Abrir ESA carpeta en Cursor

File → Open Folder → elegí `seguros_app` (la carpeta que tiene `app.py` adentro,
NO su carpeta contenedora, NO una carpeta vacía).

## 3) Abrir la terminal integrada (Ctrl + `) y correr, EN ORDEN

```bash
# Confirmá dónde estás parado (tiene que terminar en /seguros_app)
pwd

# Tiene que listar: api  app.py  calculadora.py  ...  vercel.json
ls

# Recién ahora, git init
git init
git add .
git status
```

En `git status` tenés que ver una lista corta (unos 20-25 archivos).
**Si ves miles de archivos o carpetas raras (venv, node_modules, .cursor, etc.),
NO sigas — avisame y lo revisamos antes de continuar.**

## 4) Commit y conexión con GitHub

```bash
git commit -m "Primera version de la app"
git branch -M main
```

Creá el repo nuevo en github.com (botón verde "New", vacío, sin README).
Copiá la URL que te da (`https://github.com/tu-usuario/seguros-app.git`) y:

```bash
git remote add origin https://github.com/tu-usuario/seguros-app.git
git push -u origin main
```

## 5) Verificar en GitHub ANTES de ir a Vercel

Entrá a la página del repo en github.com. Tenés que ver, sueltos en la raíz
(sin tener que entrar a ninguna carpeta primero):

```
api/
static/
templates/
.gitignore
app.py
calculadora.py
calculadora_incendio.py
calculadora_naval.py
calculadora_rc.py
calculadora_robo.py
requirements.txt
vercel.json
```

Si en cambio ves una sola carpeta (ej. `seguros_app/`) y hay que entrar ahí
para ver `app.py`, algo se hizo mal en el paso 2 o 3 — no sigas a Vercel todavía.

## 6) Recién ahora, Vercel

vercel.com → Add New → Project → importá el repo → Deploy.
No toques "Root Directory" (dejalo vacío): con la estructura del paso 5,
Vercel encuentra todo solo en la raíz.
