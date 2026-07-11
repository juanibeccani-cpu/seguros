"""
app.py
------
Punto de entrada de la aplicación web. Acá definimos las RUTAS (URLs)
y conectamos el formulario HTML con la lógica de calculadora.py.

Para correrlo:
    pip install flask
    python app.py

Después abrí en el navegador: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request
from calculadora import (
    cotizar_todas_las_ramas,
    calcular_caucion,
    ZONAS,
    USOS,
    FRANQUICIAS,
    RAMAS,
    TIPOS_CAUCION,
)
from calculadora_incendio import calcular_incendio, TIPOS_RIESGO, ADICIONALES
from calculadora_naval import (
    calcular_buque, COBERTURAS_BUQUE,
    calcular_embarcacion_placer, COBERTURAS_PLACER, ADICIONALES_PLACER,
    calcular_aeronave, COBERTURAS_AERONAVE,
)
from calculadora_rc import calcular_rc, COBERTURAS_RC
from calculadora_robo import (
    calcular_actividades_comerciales,
    calcular_vivienda,
    calcular_valores_caja,
    calcular_valores_transito,
    calcular_alhajas, COBERTURAS_ALHAJAS,
    calcular_infidelidad_empleados, CATEGORIAS_INFIDELIDAD,
)

app = Flask(__name__)


@app.errorhandler(ValueError)
def manejar_error_validacion(error):
    """
    Cuando alguna calculadora rechaza los datos (ej: casco muy viejo,
    valores negativos), mostramos un mensaje claro en vez del error 500
    genérico de Flask.
    """
    volver_url = request.referrer or "/"
    return render_template("error.html", mensaje=str(error), volver_url=volver_url), 400


@app.route("/", methods=["GET"])
def index():
    """Muestra el formulario de cotización vacío."""
    return render_template("index.html", zonas=ZONAS, usos=USOS, franquicias=FRANQUICIAS)


@app.route("/cotizar", methods=["POST"])
def cotizar():
    """
    Recibe los datos del formulario (POST), calcula la cotización
    de las 3 ramas y muestra el resultado.
    """
    # request.form nos da acceso a los datos que mandó el <form>
    valor_vehiculo = float(request.form["valor_vehiculo"])
    anio_vehiculo = int(request.form["anio_vehiculo"])
    zona_id = request.form["zona"]
    uso_id = request.form["uso"]
    franquicia_id = request.form.get("franquicia", "sin_franquicia")

    resultados = cotizar_todas_las_ramas(
        valor_vehiculo=valor_vehiculo,
        anio_vehiculo=anio_vehiculo,
        zona_id=zona_id,
        uso_id=uso_id,
        franquicia_id=franquicia_id,
    )

    datos_vehiculo = {
        "valor": valor_vehiculo,
        "anio": anio_vehiculo,
        "zona": ZONAS[zona_id]["nombre"],
        "uso": USOS[uso_id]["nombre"],
    }

    return render_template("resultado.html", resultados=resultados, datos=datos_vehiculo)


@app.route("/caucion", methods=["GET"])
def caucion_form():
    """Muestra el formulario de cotización de Cauciones Comercio."""
    return render_template("caucion.html", tipos=TIPOS_CAUCION)


@app.route("/cotizar-caucion", methods=["POST"])
def cotizar_caucion():
    """Calcula y muestra la cotización de una caución comercial."""
    tipo_id = request.form["tipo_caucion"]
    monto = float(request.form["monto_garantizado"])
    plazo = int(request.form["plazo_meses"])

    resultado = calcular_caucion(tipo_id, monto, plazo)
    return render_template("resultado_caucion.html", r=resultado)


@app.route("/incendio", methods=["GET"])
def incendio_form():
    """Muestra el formulario de cotización de Incendio."""
    return render_template("incendio.html", tipos_riesgo=TIPOS_RIESGO, adicionales=ADICIONALES)


@app.route("/cotizar-incendio", methods=["POST"])
def cotizar_incendio():
    """Calcula y muestra la cotización de Incendio."""
    valor_edificio = float(request.form.get("valor_edificio") or 0)
    valor_contenido = float(request.form.get("valor_contenido") or 0)
    tipo_riesgo = request.form["tipo_riesgo"]
    adicionales_ids = request.form.getlist("adicionales")

    resultado = calcular_incendio(valor_edificio, valor_contenido, tipo_riesgo, adicionales_ids)
    return render_template("resultado_incendio.html", r=resultado)


@app.route("/naval", methods=["GET"])
def naval_form():
    """Muestra el formulario de cotización de Casco / Embarcaciones / Aeronavegación."""
    return render_template(
        "naval.html",
        coberturas_buque=COBERTURAS_BUQUE,
        coberturas_placer=COBERTURAS_PLACER,
        adicionales_placer=ADICIONALES_PLACER,
        coberturas_aeronave=COBERTURAS_AERONAVE,
    )


@app.route("/cotizar-naval", methods=["POST"])
def cotizar_naval():
    """Calcula y muestra la cotización de la categoría náutica/aérea elegida."""
    categoria = request.form["categoria"]

    if categoria == "buque":
        resultado = calcular_buque(
            request.form["cobertura_buque"],
            float(request.form["valor_buque"]),
            incluir_adicional_colision=("adicional_colision" in request.form),
        )
        return render_template("resultado_naval.html", categoria="Casco de Buque", r=resultado, tipo="buque")

    elif categoria == "placer":
        resultado = calcular_embarcacion_placer(
            request.form["cobertura_placer"],
            float(request.form["valor_placer"]),
            int(request.form["anio_placer"]),
            adicionales_ids=request.form.getlist("adicionales_placer"),
        )
        return render_template("resultado_naval.html", categoria="Embarcación de Placer", r=resultado, tipo="placer")

    elif categoria == "aeronave":
        resultado = calcular_aeronave(
            request.form["cobertura_aeronave"],
            float(request.form["valor_aeronave"]),
            float(request.form["peso_aeronave"]),
            incluir_rc=("incluir_rc" in request.form),
        )
        return render_template("resultado_naval.html", categoria="Aeronave", r=resultado, tipo="aeronave")

    else:
        raise ValueError(f"Categoría desconocida: {categoria}")


@app.route("/rc", methods=["GET"])
def rc_form():
    """Muestra el formulario de cotización de Responsabilidad Civil."""
    coberturas_lista = [{"id": id_, **datos} for id_, datos in COBERTURAS_RC.items()]
    return render_template("rc.html", coberturas=COBERTURAS_RC, coberturas_lista=coberturas_lista)


@app.route("/cotizar-rc", methods=["POST"])
def cotizar_rc():
    """Calcula y muestra la cotización de Responsabilidad Civil."""
    cobertura_id = request.form["cobertura_rc"]
    suma_asegurada = float(request.form["suma_asegurada"])
    incluir_costas = "incluir_costas" in request.form

    resultado = calcular_rc(cobertura_id, suma_asegurada, incluir_costas)
    return render_template("resultado_rc.html", r=resultado)


@app.route("/robo", methods=["GET"])
def robo_form():
    """Muestra el formulario de cotización de Robo y Riesgos similares."""
    return render_template(
        "robo.html",
        coberturas_alhajas=COBERTURAS_ALHAJAS,
        categorias_infidelidad=CATEGORIAS_INFIDELIDAD,
    )


@app.route("/cotizar-robo", methods=["POST"])
def cotizar_robo():
    """Calcula y muestra la cotización de la categoría de Robo elegida."""
    categoria = request.form["categoria"]

    if categoria == "actividades":
        resultado = calcular_actividades_comerciales(
            float(request.form["contenido_actividades"]),
        )
        return render_template("resultado_robo.html", categoria="Actividades comerciales, industriales y civiles", r=resultado, tipo="actividades")

    elif categoria == "vivienda":
        resultado = calcular_vivienda(
            float(request.form["contenido_vivienda"]),
            cubre_huespedes=("cubre_huespedes" in request.form),
        )
        return render_template("resultado_robo.html", categoria="Vivienda particular", r=resultado, tipo="vivienda")

    elif categoria == "valores_caja":
        resultado = calcular_valores_caja(
            float(request.form["valor_caja"]),
            en_caja_fuerte=("en_caja_fuerte" in request.form),
        )
        return render_template("resultado_robo.html", categoria="Valores en caja fuerte y en locales", r=resultado, tipo="valores_caja")

    elif categoria == "valores_transito":
        resultado = calcular_valores_transito(
            float(request.form["valor_transito"]),
            recorrido_km=float(request.form.get("recorrido_km") or 0),
        )
        return render_template("resultado_robo.html", categoria="Valores en tránsito", r=resultado, tipo="valores_transito")

    elif categoria == "alhajas":
        resultado = calcular_alhajas(
            request.form["cobertura_alhajas"],
            float(request.form["valor_alhajas"]),
        )
        return render_template("resultado_robo.html", categoria="Joyas, alhajas, pieles y objetos diversos", r=resultado, tipo="alhajas")

    elif categoria == "infidelidad":
        resultado = calcular_infidelidad_empleados(
            request.form["categoria_infidelidad"],
            float(request.form["suma_por_empleado"]),
            int(request.form["cantidad_empleados"]),
        )
        return render_template("resultado_robo.html", categoria="Infidelidad de empleados", r=resultado, tipo="infidelidad")

    else:
        raise ValueError(f"Categoría de robo desconocida: {categoria}")


if __name__ == "__main__":
    # debug=True reinicia el server solito cada vez que guardás un cambio
    app.run(debug=True)
