"""
=============================================================================
__init__.py — Registro central de autómatas del sistema
=============================================================================

Propósito:
    Actúa como el punto de entrada del paquete `automatas`. Importa todas las
    clases de autómatas disponibles y las registra en el diccionario
    AUTOMATA_REGISTRY, que es la única fuente de verdad que usa la API REST
    para descubrir, instanciar y simular autómatas.

Cómo añadir un nuevo autómata al sistema:
    1. Crear el archivo con la clase en esta misma carpeta
       (ej: mi_automata.py con clase MiAFND(AFNDSimulator)).
    2. Importar la clase aquí abajo.
    3. Agregar una entrada al diccionario AUTOMATA_REGISTRY con la clave
       que usará la URL de la API (ej: "mi_automata": MiAFND).
    4. El frontend la detectará automáticamente en el próximo GET /api/automatas.

Autómatas registrados:
    iot       → Protocolo de Telemetría IoT    (iot_protocol.py)
    genetica  → Secuencias Genéticas           (genetic_sequence.py)
    ecommerce → Comportamiento E-commerce      (ecommerce.py)
    ip        → Validador de Dirección IPv4    (validador_ip.py)
    mac       → Validador de Dirección MAC     (validador_mac.py)
=============================================================================
"""


from .validador_ip import ValidadorIpAFND
from .validador_mac import ValidadorMacAFND

# Diccionario que mapea clave URL → clase del autómata.
# La API REST usa este registro en todos sus endpoints (/api/automatas, /api/simulate/<key>, etc.)
AUTOMATA_REGISTRY = {
    "ip": ValidadorIpAFND,
    "mac": ValidadorMacAFND,
}


def get_automata(key: str):
    """
    Retorna una instancia fresca del autómata identificado por `key`.

    Args:
        key: Clave del autómata (debe coincidir con una entrada en AUTOMATA_REGISTRY).

    Returns:
        Instancia de la clase correspondiente, o None si la clave no existe.
    """
    cls = AUTOMATA_REGISTRY.get(key)
    if not cls:
        return None
    return cls()


def list_automata():
    """
    Lista todos los autómatas disponibles junto con su definición formal.

    Se invoca desde el endpoint GET /api/automatas para que el frontend
    pueda construir dinámicamente las pestañas y los formularios de simulación.

    Returns:
        Diccionario { clave → definición } para todos los autómatas registrados.
    """
    result = {}
    for key, cls in AUTOMATA_REGISTRY.items():
        instance = cls()
        result[key] = instance.get_definition()
    return result
