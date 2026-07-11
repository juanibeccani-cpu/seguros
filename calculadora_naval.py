"""
calculadora_naval.py
----------------------
Lógica de cotización para las ramas CASCO (buques), EMBARCACIONES DE PLACER
y AERONAVEGACIÓN, basada en el Manual de Casco. Embarcaciones de Placer.
Aeronavegación (Centro Federal de Capacitación).

Ideas clave tomadas del manual:
- Casco de buques: se cotiza con "fórmulas" que van de la cobertura más
  amplia a la más restringida: A-1 Todo Riesgo, A-2 Riesgos Enumerados,
  A-3 Libre de Avería Particular, A-4 Libre de Avería Particular
  Absolutamente y A-5 Pérdida Total Solamente. A mayor cobertura, mayor tasa.
- Embarcaciones de placer: fórmulas A1 (Básica Amplia) a A5/A7 (más
  restringidas). Un dato clave del manual: "Casco de más de 15 años de
  antigüedad" está EXCLUIDO (no se puede asegurar), salvo pacto en
  contrario según cada aseguradora.
- Aeronavegación: la cobertura de daños a la aeronave puede ser "Todo
  Riesgo" o "Pérdida total solamente". Además existe una Responsabilidad
  Civil obligatoria frente a terceros no transportados, cuyo límite legal
  el Código Aeronáutico lo fija en "Argentinos Oro" según el peso máximo
  de despegue — una unidad histórica que ya no se usa comercialmente, así
  que aquí se ofrece solo como una prima de referencia por franja de peso.

Las tasas son valores de referencia con fines educativos: cada aseguradora
tiene su propio tarifario técnico aprobado por la Superintendencia de
Seguros de la Nación.
"""

# ---------------------------------------------------------------------------
# 1) CASCO DE BUQUES (explotación comercial: cargueros, pesqueros, etc.)
# ---------------------------------------------------------------------------

COBERTURAS_BUQUE = {
    "a1_todo_riesgo": {
        "nombre": "A-1 Todo Riesgo",
        "tasa_anual": 0.035,
        "descripcion": "Cubre cualquier pérdida o avería del buque. La cobertura más amplia.",
    },
    "a2_riesgos_enumerados": {
        "nombre": "A-2 Riesgos Enumerados",
        "tasa_anual": 0.028,
        "descripcion": "El asegurado debe acreditar que el siniestro fue por un riesgo listado en la póliza.",
    },
    "a3_libre_averia_particular": {
        "nombre": "A-3 Libre de Avería Particular",
        "tasa_anual": 0.020,
        "descripcion": "Pérdida total o avería particular por choque, incendio, rayo, explosión, naufragio, etc.",
    },
    "a4_libre_averia_absolutamente": {
        "nombre": "A-4 Libre de Avería Particular Absolutamente",
        "tasa_anual": 0.014,
        "descripcion": "Solo pérdida total (real, presumida o virtual); excluye toda avería particular.",
    },
    "a5_perdida_total": {
        "nombre": "A-5 Pérdida Total Solamente",
        "tasa_anual": 0.009,
        "descripcion": "Ampara únicamente la pérdida total del buque.",
    },
}

ADICIONAL_RC_COLISION = {
    "nombre": "Responsabilidad emergente de colisión (ampliación al 1/4 remanente)",
    "tasa_anual": 0.003,
    "descripcion": "La cobertura básica de colisión cubre 3/4 partes; este adicional cubre el 1/4 restante.",
}


def calcular_buque(cobertura_id, valor_buque, incluir_adicional_colision=False):
    if cobertura_id not in COBERTURAS_BUQUE:
        raise ValueError(f"Cobertura de buque desconocida: {cobertura_id}")
    if valor_buque <= 0:
        raise ValueError("El valor del buque debe ser mayor a 0")

    cobertura = COBERTURAS_BUQUE[cobertura_id]
    prima_base = valor_buque * cobertura["tasa_anual"]

    prima_adicional = 0.0
    if incluir_adicional_colision:
        prima_adicional = valor_buque * ADICIONAL_RC_COLISION["tasa_anual"]

    prima_anual = round(prima_base + prima_adicional, 2)

    return {
        "cobertura": cobertura["nombre"],
        "descripcion": cobertura["descripcion"],
        "valor_buque": valor_buque,
        "prima_base": round(prima_base, 2),
        "adicional_colision": round(prima_adicional, 2) if incluir_adicional_colision else None,
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }


# ---------------------------------------------------------------------------
# 2) EMBARCACIONES DE PLACER
# ---------------------------------------------------------------------------

COBERTURAS_PLACER = {
    "a1_basica_amplia": {
        "nombre": "A1 Básica Amplia",
        "tasa_anual": 0.028,
        "descripcion": "Naufragio, tempestad, abordaje, varamiento, incendio/explosión, choque, RC a terceros.",
    },
    "a2_restringida": {
        "nombre": "A2 (Pérdida Total, Salvamento, Incendio, RC a cosas de terceros)",
        "tasa_anual": 0.020,
        "descripcion": "Cobertura intermedia sin la amplitud de la A1.",
    },
    "a3_restringida": {
        "nombre": "A3 (Pérdida Total, Salvamento, Incendio y RC a cosas de terceros)",
        "tasa_anual": 0.015,
        "descripcion": "Más acotada que la A2.",
    },
    "a4_incendio_rc": {
        "nombre": "A4 (Incendio + RC a cosas de terceros)",
        "tasa_anual": 0.009,
        "descripcion": "Solo incendio (parcial o total) y responsabilidad civil a terceros.",
    },
    "a5_solo_incendio": {
        "nombre": "A5 (Solo Incendio)",
        "tasa_anual": 0.005,
        "descripcion": "La cobertura más acotada: solo incendio parcial o total.",
    },
}

ADICIONALES_PLACER = {
    "robo_motor": {"nombre": "Robo de motor (fuera de borda)", "tasa_anual": 0.004},
    "rotura_palo": {"nombre": "Rotura de palo (veleros)", "tasa_anual": 0.002},
    "temporal": {"nombre": "Riesgo de temporal", "tasa_anual": 0.003},
    "transporte_trailer": {"nombre": "Transporte en tráiler", "tasa_anual": 0.002},
    "rc_transportados": {"nombre": "RC a personas transportadas", "tasa_anual": 0.003},
}

ANTIGUEDAD_MAXIMA_PLACER = 15  # años - excluido según el manual (Exclusión "j")


def calcular_embarcacion_placer(cobertura_id, valor_embarcacion, anio_embarcacion,
                                 adicionales_ids=None, anio_actual=2026):
    if cobertura_id not in COBERTURAS_PLACER:
        raise ValueError(f"Cobertura desconocida: {cobertura_id}")
    if valor_embarcacion <= 0:
        raise ValueError("El valor de la embarcación debe ser mayor a 0")

    antiguedad = anio_actual - anio_embarcacion
    if antiguedad > ANTIGUEDAD_MAXIMA_PLACER:
        raise ValueError(
            f"El casco tiene {antiguedad} años: el manual excluye embarcaciones "
            f"de placer con más de {ANTIGUEDAD_MAXIMA_PLACER} años de antigüedad."
        )

    adicionales_ids = adicionales_ids or []
    cobertura = COBERTURAS_PLACER[cobertura_id]
    prima_base = valor_embarcacion * cobertura["tasa_anual"]

    detalle_adicionales = []
    prima_adicionales = 0.0
    for adic_id in adicionales_ids:
        if adic_id not in ADICIONALES_PLACER:
            continue
        adic = ADICIONALES_PLACER[adic_id]
        prima_adic = valor_embarcacion * adic["tasa_anual"]
        prima_adicionales += prima_adic
        detalle_adicionales.append({"nombre": adic["nombre"], "prima": round(prima_adic, 2)})

    prima_anual = round(prima_base + prima_adicionales, 2)

    return {
        "cobertura": cobertura["nombre"],
        "descripcion": cobertura["descripcion"],
        "valor_embarcacion": valor_embarcacion,
        "antiguedad": antiguedad,
        "prima_base": round(prima_base, 2),
        "adicionales": detalle_adicionales,
        "prima_adicionales": round(prima_adicionales, 2),
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }


# ---------------------------------------------------------------------------
# 3) AERONAVEGACIÓN
# ---------------------------------------------------------------------------

COBERTURAS_AERONAVE = {
    "todo_riesgo": {
        "nombre": "Todo Riesgo (en tierra, agua, carreteo y/o vuelo)",
        "tasa_anual": 0.045,
    },
    "perdida_total": {
        "nombre": "Pérdida Total Solamente",
        "tasa_anual": 0.020,
    },
}

# Prima de referencia de RC obligatoria a terceros no transportados, por
# franja de peso máximo de despegue (simplificación de la escala en
# Argentinos Oro del Art. 160 del Código Aeronáutico).
RC_AERONAVE_POR_PESO = [
    {"hasta_kg": 1000, "nombre": "Hasta 1.000 kg", "prima_anual": 180000},
    {"hasta_kg": 6000, "nombre": "1.001 a 6.000 kg", "prima_anual": 420000},
    {"hasta_kg": 20000, "nombre": "6.001 a 20.000 kg", "prima_anual": 950000},
    {"hasta_kg": float("inf"), "nombre": "Más de 20.000 kg", "prima_anual": 1800000},
]


def _franja_rc_aeronave(peso_kg):
    for franja in RC_AERONAVE_POR_PESO:
        if peso_kg <= franja["hasta_kg"]:
            return franja
    return RC_AERONAVE_POR_PESO[-1]


def calcular_aeronave(cobertura_id, valor_aeronave, peso_kg, incluir_rc=True):
    if cobertura_id not in COBERTURAS_AERONAVE:
        raise ValueError(f"Cobertura de aeronave desconocida: {cobertura_id}")
    if valor_aeronave <= 0:
        raise ValueError("El valor de la aeronave debe ser mayor a 0")
    if peso_kg <= 0:
        raise ValueError("El peso máximo de despegue debe ser mayor a 0")

    cobertura = COBERTURAS_AERONAVE[cobertura_id]
    prima_danos = valor_aeronave * cobertura["tasa_anual"]

    prima_rc = 0.0
    franja_rc = None
    if incluir_rc:
        franja_rc = _franja_rc_aeronave(peso_kg)
        prima_rc = franja_rc["prima_anual"]

    prima_anual = round(prima_danos + prima_rc, 2)

    return {
        "cobertura": cobertura["nombre"],
        "valor_aeronave": valor_aeronave,
        "peso_kg": peso_kg,
        "prima_danos": round(prima_danos, 2),
        "incluye_rc": incluir_rc,
        "franja_rc": franja_rc["nombre"] if franja_rc else None,
        "prima_rc": round(prima_rc, 2),
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }
