"""
api/index.py
------------
Vercel corre Python como "funciones serverless". Este archivo es el punto
de entrada que Vercel ejecuta: importa la app de Flask real (definida en
app.py, en la raíz del proyecto) y la expone para que Vercel la use.

No hace falta tocar nada acá ni entender el detalle: es solo un "puente".
"""
import sys
import os

# Agrega la carpeta raíz del proyecto (un nivel arriba de /api) al path,
# para poder importar app.py desde acá.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402  (la app de Flask ya armada)

# Vercel busca una variable llamada "app" (o "handler") en este archivo.
