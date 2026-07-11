"""
calculadora_rc.py
------------------
Lógica de cotización para la rama RESPONSABILIDAD CIVIL, basada en el
Manual de Responsabilidad Civil (Centro Federal de Capacitación) y en los
artículos 109 a 120 de la Ley de Seguros N° 17.418.

Ideas clave tomadas del manual:
- El asegurador se obliga a mantener indemne al asegurado por lo que deba
  a un tercero por su responsabilidad civil (Art. 109), incluyendo costas
  judiciales y extrajudiciales (Art. 110).
- No hay cobertura si el asegurado provoca el hecho con dolo o culpa grave
  (Art. 114).
- El asegurado participa en cada siniestro con un 10% de la indemnización
  (mínimo 1% - máximo 5% de la suma asegurada), según "Suma Asegurada
  Deducible" del manual.
- Se dividen las coberturas en tres grandes grupos: RC Extracontractual,
  RC Contractual y RC Profesional, cada una con sus propias variantes.

Las tasas usadas son valores de referencia con fines educativos, ya que el
manual no fija un tarifario público: en la práctica cada aseguradora tiene
su propia tarifa técnica aprobada por la Superintendencia de Seguros.
"""

# ---------------------------------------------------------------------------
# 1) COBERTURAS DE RESPONSABILIDAD CIVIL
#    (unificamos Extracontractual, Contractual y Profesional en un solo
#    diccionario, agrupado por "grupo" para mostrarlo ordenado en el form)
# ---------------------------------------------------------------------------

COBERTURAS_RC = {
    # --- Extracontractual ---
    "comprensiva": {
        "nombre": "RC Comprensiva (local/predio/actividad)",
        "grupo": "Extracontractual",
        "tasa_anual": 0.010,
        "nota": "Ampara hechos o circunstancias del ejercicio de la actividad en el local declarado.",
    },
    "hechos_privados": {
        "nombre": "RC Hechos Privados (familia, vivienda)",
        "grupo": "Extracontractual",
        "tasa_anual": 0.006,
        "nota": "Ampara al asegurado, cónyuge conviviente y personas por quienes responde legalmente.",
    },
    "ascensores": {
        "nombre": "RC Ascensores y Montacargas",
        "grupo": "Extracontractual",
        "tasa_anual": 0.008,
        "nota": "Daños a terceros por el uso de ascensores y/o montacargas.",
    },
    "carteles": {
        "nombre": "RC Carteles y letreros",
        "grupo": "Extracontractual",
        "tasa_anual": 0.005,
        "nota": "Instalación, uso, mantenimiento, reparación y desmantelamiento de carteles.",
    },
    "demoliciones": {
        "nombre": "RC Demoliciones",
        "grupo": "Extracontractual",
        "tasa_anual": 0.014,
        "nota": "Consecuencia directa de los trabajos de demolición declarados.",
    },
    "construcciones": {
        "nombre": "RC Construcciones, refacciones y pintura",
        "grupo": "Extracontractual",
        "tasa_anual": 0.012,
        "nota": "Derrumbe, caída de objetos, incendio/explosión, cables, cargas y zanjas.",
    },
    "operativa": {
        "nombre": "RC Operativa (empresas)",
        "grupo": "Extracontractual",
        "tasa_anual": 0.011,
        "nota": "Resguarda el patrimonio de la empresa por el impacto de su actividad en terceros.",
    },
    # --- Contractual ---
    "garajes": {
        "nombre": "RC Garajes y locales similares",
        "grupo": "Contractual",
        "tasa_anual": 0.009,
        "nota": "Incendio/explosión básico + robo/hurto, caídas y lesiones a terceros (opcional).",
    },
    "brokers": {
        "nombre": "RC Brókers, Productores y Asesores de Seguros",
        "grupo": "Contractual",
        "tasa_anual": 0.007,
        "nota": "Indemnizaciones a clientes por negligencia, imprudencia o impericia profesional.",
    },
    "espectadores": {
        "nombre": "RC Espectadores (Ley 19.628)",
        "grupo": "Contractual",
        "tasa_anual": 0.010,
        "nota": "Daños físicos a espectadores en espectáculos deportivos con control de ingreso.",
    },
    "tintorerias": {
        "nombre": "RC Tintorerías y similares",
        "grupo": "Contractual",
        "tasa_anual": 0.004,
        "nota": "Pérdida o daño de bienes de terceros bajo guarda a título oneroso.",
    },
    "productos": {
        "nombre": "RC Productos",
        "grupo": "Contractual",
        "tasa_anual": 0.013,
        "nota": "Uso/consumo de productos inherentes a la actividad, desde su entrega.",
    },
    "clinicas": {
        "nombre": "RC Clínicas y Establecimientos de Salud",
        "grupo": "Contractual",
        "tasa_anual": 0.018,
        "nota": "Lesiones o muerte de pacientes/acompañantes, con derecho de repetición contra el médico.",
    },
    # --- Profesional ---
    "medica": {
        "nombre": "RC Profesional Médica",
        "grupo": "Profesional",
        "tasa_anual": 0.020,
        "nota": "Actos, hechos u omisiones negligentes o culposos en el ejercicio liberal de la medicina.",
    },
    "no_medica": {
        "nombre": "RC Profesional No Médica (abogados, arquitectos, contadores, escribanos)",
        "grupo": "Profesional",
        "tasa_anual": 0.012,
        "nota": "Culpa o negligencia en el ejercicio liberal de la profesión.",
    },
    "errores_omisiones": {
        "nombre": "RC Errores y Omisiones (E&O)",
        "grupo": "Profesional",
        "tasa_anual": 0.015,
        "nota": "Indemniza a terceros por errores u omisiones en el desempeño profesional.",
    },
    "directores": {
        "nombre": "RC Directores y Gerentes (D&O)",
        "grupo": "Profesional",
        "tasa_anual": 0.016,
        "nota": "Ley 19.550 Art. 59: responsabilidad ilimitada y solidaria por daños de administradores.",
    },
}

# ---------------------------------------------------------------------------
# 2) FRANQUICIA / PARTICIPACIÓN DEL ASEGURADO (Riesgos No Asegurados, "Suma
#    Asegurada Deducible" del manual): 10% del siniestro, mín 1% - máx 5%
#    de la suma asegurada.
# ---------------------------------------------------------------------------

PORC_PARTICIPACION_SINIESTRO = 0.10
PARTICIPACION_MINIMA = 0.01   # 1% de la suma asegurada
PARTICIPACION_MAXIMA = 0.05   # 5% de la suma asegurada


def calcular_rc(cobertura_id, suma_asegurada, incluir_costas=True):
    """
    Calcula la prima de una cobertura de Responsabilidad Civil y estima
    la participación (franquicia) del asegurado por siniestro, según el
    esquema del manual (Art. 110 costas + regla del 10%/1%/5%).
    """
    if cobertura_id not in COBERTURAS_RC:
        raise ValueError(f"Cobertura de RC desconocida: {cobertura_id}")
    if suma_asegurada <= 0:
        raise ValueError("La suma asegurada debe ser mayor a 0")

    cobertura = COBERTURAS_RC[cobertura_id]
    prima_base = suma_asegurada * cobertura["tasa_anual"]

    # El pago de costas judiciales/extrajudiciales (Art. 110) agrega un 15%
    # sobre la prima base cuando el asegurado quiere incluir esa cobertura.
    prima_costas = prima_base * 0.15 if incluir_costas else 0.0

    prima_anual = round(prima_base + prima_costas, 2)

    # Participación del asegurado por siniestro (a modo informativo, no se
    # cobra como prima: es lo que el asegurado pone de su bolsillo).
    participacion_minima = round(suma_asegurada * PARTICIPACION_MINIMA, 2)
    participacion_maxima = round(suma_asegurada * PARTICIPACION_MAXIMA, 2)

    return {
        "cobertura": cobertura["nombre"],
        "grupo": cobertura["grupo"],
        "nota": cobertura["nota"],
        "suma_asegurada": suma_asegurada,
        "prima_base": round(prima_base, 2),
        "incluye_costas": incluir_costas,
        "prima_costas": round(prima_costas, 2),
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
        "participacion_pct": PORC_PARTICIPACION_SINIESTRO,
        "participacion_minima": participacion_minima,
        "participacion_maxima": participacion_maxima,
    }
