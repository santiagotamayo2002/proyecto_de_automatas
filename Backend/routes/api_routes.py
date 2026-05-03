"""
=============================================================================
api_routes.py — Definición de todos los endpoints REST del simulador AFND
=============================================================================

Propósito:
    Este módulo declara el Blueprint `api_bp` que agrupa los tres endpoints
    de la API. Flask lo monta con el prefijo /api desde app.py.

Endpoints disponibles:
    GET  /api/automatas
        → Lista todos los autómatas registrados junto con su definición
          formal (estados, alfabeto, transiciones, ejemplos, etc.).
        → Usado por el frontend al cargar la página para construir las pestañas.

    GET  /api/automatas/<automata_key>
        → Retorna la definición formal de un autómata específico.
        → Útil para inspeccionar un autómata en particular sin cargar todos.

    POST /api/simulate/<automata_key>
        → Simula el autómata indicado con la cadena de tokens del cuerpo JSON.
        → Cuerpo esperado: { "tokens": ["TOKEN1", "TOKEN2", ...] }
        → Retorna: { accepted, trace, final_states, result_message }
        → Validaciones: tokens no vacío, máximo 100 tokens, tokens en lista,
          normalización automática a mayúsculas.

Códigos de error:
    400 Bad Request  → Cuerpo mal formado o tokens inválidos.
    404 Not Found    → Clave de autómata no registrada en AUTOMATA_REGISTRY.
=============================================================================
"""

from flask import Blueprint, request, jsonify
from automatas import get_automata, list_automata, AUTOMATA_REGISTRY

# Blueprint que agrupa todos los endpoints bajo el prefijo /api
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/automatas", methods=["GET"])
def get_all_automata():
    """
    GET /api/automatas

    Retorna la lista completa de autómatas disponibles con sus definiciones
    formales. El frontend usa esta respuesta para renderizar las pestañas y
    los formularios de entrada de tokens.

    Response 200:
        {
            "success": true,
            "automatas": {
                "<key>": { states, alphabet, transitions, initial_state, accept_states,
                           name, description, language, examples, state_labels }
            }
        }
    """
    return jsonify({
        "success": True,
        "automatas": list_automata()
    })


@api_bp.route("/automatas/<string:automata_key>", methods=["GET"])
def get_automata_definition(automata_key: str):
    """
    GET /api/automatas/<automata_key>

    Retorna la definición formal de un único autómata identificado por su clave.

    Args (URL):
        automata_key: Clave del autómata (ej: "ip", "mac", "iot", "genetica").

    Response 200:
        { "success": true, "automata": { ... definición completa ... } }

    Response 404:
        { "success": false, "error": "Autómata '<key>' no encontrado. ..." }
    """
    automata = get_automata(automata_key)
    if not automata:
        return jsonify({
            "success": False,
            "error": f"Autómata '{automata_key}' no encontrado. Disponibles: {list(AUTOMATA_REGISTRY.keys())}"
        }), 404

    return jsonify({
        "success": True,
        "automata": automata.get_definition()
    })


@api_bp.route("/simulate/<string:automata_key>", methods=["POST"])
def simulate(automata_key: str):
    """
    POST /api/simulate/<automata_key>

    Ejecuta la simulación del AFND indicado sobre la cadena de tokens
    proporcionada en el cuerpo de la petición.

    Args (URL):
        automata_key: Clave del autómata (ej: "ip", "mac", "iot").

    Body JSON:
        { "tokens": ["T1", "T2", ...] }

        Los tokens se normalizan automáticamente a mayúsculas antes de
        pasarse al motor de simulación.

    Response 200:
        {
            "success": true,
            "accepted": bool,
            "trace": [
                {
                    "step": int,
                    "token": str | null,
                    "states_before": [str],
                    "states_after":  [str],
                    "description":   str
                },
                ...
            ],
            "final_states":    [str],
            "result_message":  str
        }

    Response 400:
        { "success": false, "error": "..." }  → Cuerpo inválido o tokens vacíos/excesivos.

    Response 404:
        { "success": false, "error": "..." }  → Autómata no encontrado.
    """
    # Verificar que el autómata existe
    automata = get_automata(automata_key)
    if not automata:
        return jsonify({
            "success": False,
            "error": f"Autómata '{automata_key}' no encontrado."
        }), 404

    # Parsear y validar el cuerpo JSON
    data = request.get_json()
    if not data or "tokens" not in data:
        return jsonify({
            "success": False,
            "error": "El cuerpo debe contener el campo 'tokens' (lista de strings)."
        }), 400

    tokens = data["tokens"]
    if not isinstance(tokens, list):
        return jsonify({
            "success": False,
            "error": "'tokens' debe ser una lista."
        }), 400

    if len(tokens) == 0:
        return jsonify({
            "success": False,
            "error": "La cadena de entrada no puede estar vacía."
        }), 400

    # Límite de seguridad para evitar procesamiento excesivo
    if len(tokens) > 100:
        return jsonify({
            "success": False,
            "error": "La cadena no puede tener más de 100 tokens."
        }), 400

    # Normalizar todos los tokens a mayúsculas (ej: "a" → "A", "f" → "F")
    tokens = [str(t).strip().upper() for t in tokens]

    # Ejecutar la simulación y retornar el resultado completo
    result = automata.simulate(tokens)
    return jsonify({
        "success": True,
        **result
    })
