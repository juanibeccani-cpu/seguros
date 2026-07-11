"""
calculadora_incendio.py
------------------------
Lógica de cotización para la rama INCENDIO, basada en el Manual de Incendio
(Centro Federal de Capacitación) y en los artículos 85 a 89 de la Ley 17.418.

Ideas clave tomadas del manual:
- La cobertura básica ampara daños directos e indirectos por fuego, rayo y
  explosión (Art. 85/86 Ley 17418), más 4 eventos que la amplían: tumulto
  popular/huelga, vandalismo/terrorismo, impacto de vehículos/aeronaves y humo.
- El bien asegurado se separa en EDIFICIO y CONTENIDO (mercaderías,
  maquinarias, mobiliario, etc.), cada uno con su propia suma asegurada.
- Existen "riesgos adicionales" que se cotizan con una extra-prima:
  remoción de escombros, huracán/ciclón/vendaval/tornado, incendio a
  consecuencia de terremoto, daños materiales por terremoto, granizo,
  responsabilidad civil por incendio/explosión a linderos, daños a
  mercadería por falta de frío, combustión espontánea, gastos
  extraordinarios y daños por agua.

Las tasas usadas son valores de referencia con fines educativos, ya que el
manual no fija un tarifario público: en la práctica cada aseguradora tiene
su propia tarifa técnica aprobada por la Superintendencia de Seguros.
"""

# ---------------------------------------------------------------------------
# 1) TASA BASE SEGÚN TIPO DE RIESGO (Ordinario vs Industrial)
# ---------------------------------------------------------------------------

TIPOS_RIESGO = {
    "ordinario": {
        "nombre": "Ordinario (oficina, vivienda, comercio, depósito no industrial)",
        "tasa_anual": 0.0015,   # 0.15% anual del valor asegurado
    },
    "industrial": {
        "nombre": "Industrial (elaboración, transformación, fraccionamiento)",
        "tasa_anual": 0.0035,   # 0.35% anual del valor asegurado
    },
}

# ---------------------------------------------------------------------------
# 2) RIESGOS ADICIONALES (extra-prima sobre la suma asegurada de edificio,
#    contenido, o ambos según corresponda)
# ---------------------------------------------------------------------------

ADICIONALES = {
    "remocion_escombros": {
        "nombre": "Remoción de escombros",
        "tasa_anual": 0.0002,
        "aplica_a": "ambos",
        "nota": "A primer riesgo absoluto, tope 5% de la suma asegurada.",
    },
    "huracan_ciclon": {
        "nombre": "Huracán, ciclón, vendaval y tornado",
        "tasa_anual": 0.0003,
        "aplica_a": "ambos",
        "nota": "No cubre vidrios/cristales ni grúas, chimeneas, antenas, silos abiertos.",
    },
    "incendio_terremoto": {
        "nombre": "Incendio a consecuencia de terremoto o temblor",
        "tasa_anual": 0.0005,
        "aplica_a": "ambos",
        "nota": "El asegurado debe probar que el daño fue causado únicamente por incendio.",
    },
    "danos_terremoto": {
        "nombre": "Daños materiales por terremoto o temblor",
        "tasa_anual": 0.0008,
        "aplica_a": "ambos",
        "nota": "Excluye sustracción/extravío durante o después del terremoto y lucro cesante.",
    },
    "granizo": {
        "nombre": "Granizo",
        "tasa_anual": 0.0002,
        "aplica_a": "ambos",
        "nota": "No incrementa la suma asegurada de la póliza.",
    },
    "rc_linderos": {
        "nombre": "Responsabilidad Civil por incendio/explosión (linderos)",
        "tasa_anual": 0.0002,
        "aplica_a": "ambos",
        "nota": "A primer riesgo absoluto. Franquicia 5% (mín 1% - máx 3%) de la suma asegurada.",
    },
    "falta_frio": {
        "nombre": "Daños a mercadería por falta de frío",
        "tasa_anual": 0.0003,
        "aplica_a": "contenido",
        "nota": "Solo si la falla dura más de 12h continuas o discontinuas en 24h.",
    },
    "combustion_espontanea": {
        "nombre": "Combustión espontánea (granos/silos)",
        "tasa_anual": 0.0002,
        "aplica_a": "contenido",
        "nota": "Requiere almacenamiento reglamentario y controles de humedad/temperatura.",
    },
    "gastos_extraordinarios": {
        "nombre": "Gastos extraordinarios (flete expreso, horas extra, alquiler temporal)",
        "tasa_anual": 0.0001,
        "aplica_a": "ambos",
        "nota": "Cubre sobrecostos razonables para reparar/reemplazar lo dañado.",
    },
    "danos_agua": {
        "nombre": "Daños por agua",
        "tasa_anual": 0.0003,
        "aplica_a": "ambos",
        "nota": "Por rotura, obstrucción o falla de instalaciones que contienen/distribuyen agua.",
    },
}


def calcular_incendio(valor_edificio, valor_contenido, tipo_riesgo_id, adicionales_ids=None):
    """
    Calcula la prima de la cobertura básica de incendio (edificio + contenido)
    más los riesgos adicionales seleccionados.
    """
    if tipo_riesgo_id not in TIPOS_RIESGO:
        raise ValueError(f"Tipo de riesgo desconocido: {tipo_riesgo_id}")
    if valor_edificio < 0 or valor_contenido < 0:
        raise ValueError("Los valores asegurados no pueden ser negativos")
    if valor_edificio == 0 and valor_contenido == 0:
        raise ValueError("Debe asegurar al menos edificio o contenido")

    adicionales_ids = adicionales_ids or []
    tipo_riesgo = TIPOS_RIESGO[tipo_riesgo_id]
    tasa_base = tipo_riesgo["tasa_anual"]

    prima_edificio_base = valor_edificio * tasa_base
    prima_contenido_base = valor_contenido * tasa_base
    prima_basica = prima_edificio_base + prima_contenido_base

    detalle_adicionales = []
    prima_adicionales = 0.0

    for adic_id in adicionales_ids:
        if adic_id not in ADICIONALES:
            continue
        adic = ADICIONALES[adic_id]
        if adic["aplica_a"] == "edificio":
            base = valor_edificio
        elif adic["aplica_a"] == "contenido":
            base = valor_contenido
        else:  # ambos
            base = valor_edificio + valor_contenido

        prima_adic = base * adic["tasa_anual"]
        prima_adicionales += prima_adic
        detalle_adicionales.append({
            "nombre": adic["nombre"],
            "nota": adic["nota"],
            "prima": round(prima_adic, 2),
        })

    prima_anual = round(prima_basica + prima_adicionales, 2)

    return {
        "tipo_riesgo": tipo_riesgo["nombre"],
        "valor_edificio": valor_edificio,
        "valor_contenido": valor_contenido,
        "prima_edificio_base": round(prima_edificio_base, 2),
        "prima_contenido_base": round(prima_contenido_base, 2),
        "prima_basica": round(prima_basica, 2),
        "adicionales": detalle_adicionales,
        "prima_adicionales": round(prima_adicionales, 2),
        "prima_anual": prima_anual,
        "prima_mensual": round(prima_anual / 12, 2),
    }
