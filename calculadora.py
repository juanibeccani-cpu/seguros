"""
calculadora.py
----------------
Acá vive toda la LÓGICA DE NEGOCIO del cotizador: nada de HTML ni de Flask.
La idea es que esta lógica se pueda testear sola, sin depender de la web.

Esto es un ejemplo EDUCATIVO con tarifas simplificadas e inventadas para que
puedas ver cómo se arma un motor de cotización. Para producción real vas a
necesitar tablas de tarifas actuariales provistas por la aseguradora.
"""

# ---------------------------------------------------------------------------
# 1) DATOS DE REFERENCIA (constantes)
# ---------------------------------------------------------------------------

# Cada rama tiene una tasa base = % del valor del vehículo que se cobra por año.
# RC no depende del valor del auto (es una prima fija por franja), las otras sí.
RAMAS = {
    "rc": {
        "nombre": "Responsabilidad Civil",
        "tipo": "fija",
        "prima_base": 45000,       # prima fija anual base en pesos (ejemplo)
    },
    "terceros_completo": {
        "nombre": "Terceros Completo",
        "tipo": "porcentaje",
        "tasa_anual": 0.028,       # 2.8% del valor del vehículo por año
    },
    "robo_incendio": {
        "nombre": "Robo e Incendio",
        "tipo": "porcentaje",
        "tasa_anual": 0.018,       # 1.8% del valor del vehículo por año
    },
    "todo_riesgo": {
        "nombre": "Todo Riesgo",
        "tipo": "porcentaje",
        "tasa_anual": 0.065,       # 6.5% del valor del vehículo por año
    },
}

# Franquicias disponibles solo para Todo Riesgo: a mayor franquicia, menor prima
FRANQUICIAS = {
    "sin_franquicia": {"nombre": "Sin franquicia", "descuento": 0.0},
    "franquicia_baja": {"nombre": "Franquicia baja", "descuento": 0.10},
    "franquicia_media": {"nombre": "Franquicia media", "descuento": 0.18},
    "franquicia_alta": {"nombre": "Franquicia alta", "descuento": 0.28},
}

# Ajuste por zona (algunas zonas tienen más siniestralidad/robo)
ZONAS = {
    "caba_gba": {"nombre": "CABA / GBA", "factor": 1.25},
    "capitales_interior": {"nombre": "Capitales del interior", "factor": 1.05},
    "resto_pais": {"nombre": "Resto del país", "factor": 1.0},
}

# Ajuste por uso del vehículo
USOS = {
    "particular": {"nombre": "Particular", "factor": 1.0},
    "comercial": {"nombre": "Comercial / de reparto", "factor": 1.35},
    "aplicaciones": {"nombre": "Aplicaciones (remis/plataformas)", "factor": 1.6},
}


# ---------------------------------------------------------------------------
# 2) FUNCIONES DE CÁLCULO
# ---------------------------------------------------------------------------

def factor_antiguedad(anio_vehiculo, anio_actual=2026):
    """
    Los autos más viejos son más baratos de asegurar en valor absoluto
    (valen menos) pero relativamente más riesgosos mecánicamente.
    Devolvemos un factor multiplicador simple según antigüedad.
    """
    antiguedad = anio_actual - anio_vehiculo
    if antiguedad < 0:
        antiguedad = 0

    if antiguedad <= 2:
        return 1.10   # 0 km / muy nuevo: más caro de reponer, factor robo alto
    elif antiguedad <= 5:
        return 1.0
    elif antiguedad <= 10:
        return 0.95
    else:
        return 0.9


def rama_disponible(rama_id, anio_vehiculo, anio_actual=2026):
    """
    Regla de negocio real: muchas aseguradoras no ofrecen Todo Riesgo
    para autos con más de 15 años de antigüedad.
    """
    antiguedad = anio_actual - anio_vehiculo
    if rama_id == "todo_riesgo" and antiguedad > 15:
        return False
    return True


def calcular_prima(rama_id, valor_vehiculo, anio_vehiculo, zona_id, uso_id,
                    franquicia_id="sin_franquicia", anio_actual=2026):
    """
    Función principal: calcula la prima anual y mensual para una rama.
    Devuelve un diccionario con el detalle del cálculo (para poder
    mostrar el desglose al usuario, algo que en seguros SIEMPRE se espera).
    """
    if rama_id not in RAMAS:
        raise ValueError(f"Rama desconocida: {rama_id}")

    if not rama_disponible(rama_id, anio_vehiculo, anio_actual):
        raise ValueError(
            "Todo Riesgo no está disponible para vehículos de más de 15 años"
        )

    rama = RAMAS[rama_id]
    zona = ZONAS[zona_id]
    uso = USOS[uso_id]
    fact_antig = factor_antiguedad(anio_vehiculo, anio_actual)

    # --- Prima base según el tipo de rama ---
    if rama["tipo"] == "fija":
        prima_base = rama["prima_base"]
    else:
        prima_base = valor_vehiculo * rama["tasa_anual"]

    # --- Aplicamos los factores de ajuste ---
    prima_ajustada = prima_base * zona["factor"] * uso["factor"] * fact_antig

    # --- Franquicia (descuento), solo aplica a Todo Riesgo ---
    descuento_franquicia = 0.0
    if rama_id == "todo_riesgo":
        franquicia = FRANQUICIAS[franquicia_id]
        descuento_franquicia = prima_ajustada * franquicia["descuento"]
        prima_ajustada -= descuento_franquicia

    prima_anual = round(prima_ajustada, 2)
    prima_mensual = round(prima_anual / 12, 2)

    return {
        "rama": rama["nombre"],
        "prima_base": round(prima_base, 2),
        "factor_zona": zona["factor"],
        "factor_uso": uso["factor"],
        "factor_antiguedad": fact_antig,
        "descuento_franquicia": round(descuento_franquicia, 2),
        "prima_anual": prima_anual,
        "prima_mensual": prima_mensual,
    }


def cotizar_todas_las_ramas(valor_vehiculo, anio_vehiculo, zona_id, uso_id,
                             franquicia_id="sin_franquicia", anio_actual=2026):
    """
    Devuelve la cotización de las 3 ramas juntas (para comparar),
    salteando las que no estén disponibles para ese vehículo.
    """
    resultados = {}
    for rama_id in RAMAS:
        if rama_disponible(rama_id, anio_vehiculo, anio_actual):
            resultados[rama_id] = calcular_prima(
                rama_id, valor_vehiculo, anio_vehiculo, zona_id, uso_id,
                franquicia_id, anio_actual
            )
    return resultados


# ---------------------------------------------------------------------------
# 3) CAUCIONES COMERCIO
# ---------------------------------------------------------------------------
# Es otra "rama" del ramo Ramas Varias, pero no depende de un vehículo:
# garantiza el cumplimiento de una obligación comercial/judicial/aduanera.
# Se cotiza como % del monto garantizado, prorrateado por el plazo.

TIPOS_CAUCION = {
    "comercial": {
        "nombre": "Caución Comercial",
        "tasa_anual": 0.030,   # 3.0% anual del monto garantizado
    },
    "judicial": {
        "nombre": "Caución Judicial",
        "tasa_anual": 0.045,   # 4.5% anual (mayor riesgo, mayor tasa)
    },
    "aduanera": {
        "nombre": "Caución Aduanera",
        "tasa_anual": 0.050,   # 5.0% anual
    },
}


def calcular_caucion(tipo_caucion_id, monto_garantizado, plazo_meses):
    """
    Calcula la prima de una caución comercial.

    - tipo_caucion_id: "comercial" | "judicial" | "aduanera"
    - monto_garantizado: monto en pesos que se está garantizando
    - plazo_meses: duración de la garantía en meses
    """
    if tipo_caucion_id not in TIPOS_CAUCION:
        raise ValueError(f"Tipo de caución desconocido: {tipo_caucion_id}")
    if monto_garantizado <= 0:
        raise ValueError("El monto garantizado debe ser mayor a 0")
    if plazo_meses <= 0:
        raise ValueError("El plazo debe ser mayor a 0 meses")

    tipo = TIPOS_CAUCION[tipo_caucion_id]

    # Prima anual completa, luego prorrateada según el plazo real
    prima_anual_completa = monto_garantizado * tipo["tasa_anual"]
    prima_prorrateada = prima_anual_completa * (plazo_meses / 12)

    # Piso mínimo de prima (práctica habitual en el mercado)
    prima_minima = 25000
    prima_final = max(prima_prorrateada, prima_minima)

    return {
        "tipo": tipo["nombre"],
        "monto_garantizado": monto_garantizado,
        "plazo_meses": plazo_meses,
        "tasa_anual": tipo["tasa_anual"],
        "prima_prorrateada": round(prima_prorrateada, 2),
        "prima_minima_aplicada": prima_prorrateada < prima_minima,
        "prima_final": round(prima_final, 2),
    }
