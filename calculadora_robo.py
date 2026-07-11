"""
calculadora_robo.py
--------------------
Lógica de cotización para la rama ROBO Y RIESGOS SIMILARES, basada en el
Manual de Robo (Centro Federal de Capacitación).

Ideas clave tomadas del manual:
- ROBO: apoderamiento ilegítimo con fuerza en las cosas o violencia/intimidación
  en las personas. HURTO: apoderamiento ilegítimo SIN violencia ni fuerza.
- Cada cobertura tiene su propia "medida de la prestación" (Prorrata,
  Primer Riesgo Absoluto o Relativo) y sus propias exclusiones, según el
  "Ordenamiento contractual y tarifario" del manual (Capítulos I a VII).
- Los daños causados por los ladrones para cometer el delito (a la puerta,
  vidrieras, cerraduras, etc.) se cubren hasta un 15% de la suma asegurada
  en forma global, en Actividades Comerciales y en Vivienda.

Las tasas usadas son valores de referencia con fines educativos, ya que el
manual no fija un tarifario público: en la práctica cada aseguradora tiene
su propia tarifa técnica aprobada por la Superintendencia de Seguros.
"""

# ---------------------------------------------------------------------------
# 1) COBERTURAS DE ROBO (una por cada capítulo del manual)
# ---------------------------------------------------------------------------

# Capítulo II - Actividades comerciales, industriales y civiles
TASA_ACTIVIDADES = 0.012          # sobre el contenido general asegurado
TOPE_DANOS_LOCAL = 0.15           # 15% de la suma asegurada, daños para cometer el robo

# Capítulo III - Viviendas particulares
TASA_VIVIENDA = 0.008             # sobre el mobiliario / contenido general
TOPE_DANOS_VIVIENDA = 0.15        # 15% de la suma asegurada

# Capítulo IV - Robo de valores en caja fuerte y en locales
TASA_VALORES_CAJA = 0.020         # sobre el valor a proteger (dinero, cheques al portador, etc.)

# Capítulo V - Robo de valores en tránsito
TASA_VALORES_TRANSITO = 0.025     # sobre el valor transportado

# Capítulo VI - Joyas, alhajas, pieles y objetos diversos
COBERTURAS_ALHAJAS = {
    "todo_riesgo": {
        "nombre": "COB 1 - Todo Riesgo",
        "tasa_anual": 0.030,
        "nota": "Cualquier causa no exceptuada expresamente. Argentina y países limítrofes.",
    },
    "robo_hurto_incendio": {
        "nombre": "COB 2 - Robo/Hurto/Incendio",
        "tasa_anual": 0.020,
        "nota": "Robo o hurto y su tentativa, incendio, rayo o explosión (directa o indirecta).",
    },
    "robo_hurto": {
        "nombre": "COB 3 - Robo/Hurto",
        "tasa_anual": 0.015,
        "nota": "Solo robo o hurto y su tentativa, y daños resultantes de esos hechos.",
    },
}

# Capítulo VII - Infidelidad de empleados
CATEGORIAS_INFIDELIDAD = {
    "a": {
        "nombre": "Categoría A (alta responsabilidad y manejo de dinero)",
        "tasa_anual": 0.018,
    },
    "b": {
        "nombre": "Categoría B (responsabilidad media)",
        "tasa_anual": 0.010,
    },
    "c": {
        "nombre": "Categoría C (poca responsabilidad, sin manejo de dinero)",
        "tasa_anual": 0.005,
    },
}

MEDIDAS_PRESTACION = {
    "prorrata": "A prorrata",
    "primer_riesgo_absoluto": "A Primer Riesgo Absoluto",
    "primer_riesgo_relativo": "A Primer Riesgo Relativo",
}


def calcular_actividades_comerciales(contenido_asegurado, medida_prestacion="primer_riesgo_absoluto"):
    """Capítulo II: Robo en actividades comerciales, industriales y civiles."""
    if contenido_asegurado <= 0:
        raise ValueError("El valor del contenido asegurado debe ser mayor a 0")

    prima_base = contenido_asegurado * TASA_ACTIVIDADES
    tope_danos = contenido_asegurado * TOPE_DANOS_LOCAL
    prima_anual = round(prima_base, 2)

    return {
        "cobertura": "Robo - Actividades comerciales, industriales y civiles",
        "medida_prestacion": MEDIDAS_PRESTACION.get(medida_prestacion, medida_prestacion),
        "contenido_asegurado": contenido_asegurado,
        "prima_base": round(prima_base, 2),
        "tope_danos_al_local": round(tope_danos, 2),
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }


def calcular_vivienda(contenido_asegurado, cubre_huespedes=False, medida_prestacion="primer_riesgo_relativo"):
    """Capítulo III: Robo y Hurto en Viviendas particulares."""
    if contenido_asegurado <= 0:
        raise ValueError("El valor del contenido asegurado debe ser mayor a 0")

    prima_base = contenido_asegurado * TASA_VIVIENDA
    tope_danos = contenido_asegurado * TOPE_DANOS_VIVIENDA

    # Extensión a bienes de huéspedes: hasta 10% de la suma asegurada,
    # cotizada con una extra-prima chica sobre esa porción.
    prima_huespedes = (contenido_asegurado * 0.10 * 0.01) if cubre_huespedes else 0.0

    prima_anual = round(prima_base + prima_huespedes, 2)

    return {
        "cobertura": "Robo y Hurto - Viviendas particulares",
        "medida_prestacion": MEDIDAS_PRESTACION.get(medida_prestacion, medida_prestacion),
        "contenido_asegurado": contenido_asegurado,
        "prima_base": round(prima_base, 2),
        "tope_danos_a_la_vivienda": round(tope_danos, 2),
        "cubre_huespedes": cubre_huespedes,
        "prima_huespedes": round(prima_huespedes, 2),
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }


def calcular_valores_caja(valor_a_proteger, en_caja_fuerte=True):
    """Capítulo IV: Robo de valores en caja fuerte y en locales."""
    if valor_a_proteger <= 0:
        raise ValueError("El valor a proteger debe ser mayor a 0")

    # La cobertura fuera de horario habitual (caja fuerte) implica más
    # riesgo asumido por el asegurador, así que tiene una tasa mayor.
    tasa = TASA_VALORES_CAJA * (1.3 if en_caja_fuerte else 1.0)
    prima_anual = round(valor_a_proteger * tasa, 2)

    return {
        "cobertura": "Robo de valores en caja fuerte y en locales",
        "medida_prestacion": MEDIDAS_PRESTACION["primer_riesgo_absoluto"],
        "valor_a_proteger": valor_a_proteger,
        "en_caja_fuerte": en_caja_fuerte,
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }


def calcular_valores_transito(valor_transportado, recorrido_km=0):
    """Capítulo V: Robo de valores en tránsito."""
    if valor_transportado <= 0:
        raise ValueError("El valor transportado debe ser mayor a 0")
    if recorrido_km < 0:
        raise ValueError("El recorrido en km no puede ser negativo")

    prima_base = valor_transportado * TASA_VALORES_TRANSITO

    # El manual menciona que, cuando el recorrido excede los 100 km, se
    # permiten detenciones adicionales: modelamos eso como un pequeño
    # recargo por km extra (mayor exposición al riesgo en el trayecto).
    km_extra = max(0, recorrido_km - 100)
    recargo_km = valor_transportado * 0.00002 * km_extra

    prima_anual = round(prima_base + recargo_km, 2)

    return {
        "cobertura": "Robo de valores en tránsito",
        "medida_prestacion": MEDIDAS_PRESTACION["primer_riesgo_absoluto"],
        "valor_transportado": valor_transportado,
        "recorrido_km": recorrido_km,
        "prima_base": round(prima_base, 2),
        "recargo_km_extra": round(recargo_km, 2),
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }


def calcular_alhajas(cobertura_id, valor_bienes):
    """Capítulo VI: Joyas, alhajas, pieles y objetos diversos."""
    if cobertura_id not in COBERTURAS_ALHAJAS:
        raise ValueError(f"Cobertura de alhajas desconocida: {cobertura_id}")
    if valor_bienes <= 0:
        raise ValueError("El valor de los bienes debe ser mayor a 0")

    cobertura = COBERTURAS_ALHAJAS[cobertura_id]
    prima_anual = round(valor_bienes * cobertura["tasa_anual"], 2)

    return {
        "cobertura": cobertura["nombre"],
        "nota": cobertura["nota"],
        "medida_prestacion": MEDIDAS_PRESTACION["prorrata"],
        "valor_bienes": valor_bienes,
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }


def calcular_infidelidad_empleados(categoria_id, suma_asegurada, cantidad_empleados):
    """Capítulo VII: Infidelidad de empleados."""
    if categoria_id not in CATEGORIAS_INFIDELIDAD:
        raise ValueError(f"Categoría de infidelidad desconocida: {categoria_id}")
    if suma_asegurada <= 0:
        raise ValueError("La suma asegurada por empleado debe ser mayor a 0")
    if cantidad_empleados <= 0:
        raise ValueError("La cantidad de empleados debe ser mayor a 0")

    categoria = CATEGORIAS_INFIDELIDAD[categoria_id]

    # Si el personal excede las 25 personas, el manual permite la cobertura
    # "en forma innominada" (sin listar a cada uno): aplicamos un pequeño
    # descuento por volumen, ya que se simplifica la gestión del riesgo.
    innominado = cantidad_empleados > 25
    descuento = 0.90 if innominado else 1.0

    prima_por_empleado = suma_asegurada * categoria["tasa_anual"] * descuento
    prima_anual = round(prima_por_empleado * cantidad_empleados, 2)

    return {
        "cobertura": "Infidelidad de empleados",
        "categoria": categoria["nombre"],
        "medida_prestacion": MEDIDAS_PRESTACION["primer_riesgo_absoluto"],
        "suma_asegurada_por_empleado": suma_asegurada,
        "cantidad_empleados": cantidad_empleados,
        "modalidad": "Innominada (>25 empleados)" if innominado else "Nominada",
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }
