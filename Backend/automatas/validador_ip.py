"""
=============================================================================
validador_ip.py — Autómata Finito No Determinista para validación de IPv4
=============================================================================

Propósito:
    Implementa la clase ValidadorIpAFND que valida si una cadena de tokens
    representa una dirección IPv4 válida en el rango 0.0.0.0 – 255.255.255.255.

Origen del autómata:
    Los estados, transiciones y estados de aceptación fueron extraídos
    directamente del archivo 'IP_verificacion_no_determinista.xml' (formato
    JFLAP 7.1), ubicado en la raíz del proyecto.

Formato aceptado:
    Una dirección IPv4 está compuesta por cuatro octetos decimales separados
    por puntos. Cada octeto debe estar en el rango 0–255.
    Ejemplo válido:  192.168.0.1  → tokens: ['1','9','2','.','1','6','8','.','0','.','1']
    Ejemplo inválido: 256.1.1.1   → rechazado porque 256 > 255

Estructura del autómata:
    - 48 estados en total (q0–q47), diseñados para cubrir los tres sub-rangos
      posibles de cada octeto:
        • 1 dígito   [0–9]     → p.ej. q1 (un dígito del 1er octeto)
        • 2 dígitos  [10–99]   → p.ej. q3 (dos dígitos del 1er octeto)
        • 3 dígitos  [100–199] → p.ej. q6 (tres dígitos del 1er octeto)
        • 3 dígitos  [200–249] → p.ej. q14→q15→q16 (rango 200-249)
        • 3 dígitos  [250–255] → p.ej. q17→q42→q43 (rango 250-255)
    - El autómata replica esta lógica para los cuatro octetos (con los puntos
      de separación en q7, q20 y q30).
    - Estados de aceptación: q31, q35, q37, q39, q47
      (cada uno corresponde a haber completado el último octeto en un
      rango válido diferente).

Alfabeto (tokens que el usuario ingresa uno por uno):
    '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'

Integración con el frontend:
    - Clave de registro: "ip"
    - No muestra tabla de transiciones (demasiados estados).
    - El diagrama de estados usa el modo IpStatePath: muestra solo los
      últimos 5 estados visitados en un carril horizontal limpio.
=============================================================================
"""

from .base import AFNDSimulator


class ValidadorIpAFND(AFNDSimulator):
    """
    AFND para validar direcciones IPv4 (0.0.0.0 – 255.255.255.255).

    El autómata procesa la dirección token a token (un carácter o punto
    por vez) y verifica simultáneamente todas las rutas posibles de
    interpretación de los octetos gracias al no-determinismo.

    Estados de aceptación: q31 (1 dígito), q35 (2 dígitos), q37 (100-199),
                           q39 (200-255), q47 (250-255).
    """

    def _setup(self):
        """
        Configura el autómata con los 48 estados y las transiciones del XML.

        Organización de los grupos de estados por octeto:
          Octeto 1 (q0 a q16/q42):
            q0        → estado inicial
            q1        → primer dígito [0-9] de 1 dígito
            q2→q3     → dos dígitos [10-99]
            q4→q5→q6  → tres dígitos [100-199]
            q14→q15→q16 → tres dígitos [200-249]
            q17→q42→q43 → tres dígitos [250-255]
            q40→q41   → rama del 5 en decenas (250-255)
          Punto 1 (q7): separador '.' entre octeto 1 y 2
          Octeto 2 (q7 a q19): misma lógica para el 2do octeto
          Punto 2 (q20): separador '.' entre octeto 2 y 3
          Octeto 3 (q20 a q29): misma lógica para el 3er octeto
          Punto 3 (q30): separador '.' entre octeto 3 y 4
          Octeto 4 (q30 a q47): misma lógica; estados q31/q35/q37/q39/q47 son de aceptación
        """

        # Conjunto completo de los 48 estados del autómata
        self.states = {
            'q0', 'q1', 'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19',
            'q2', 'q20', 'q21', 'q22', 'q23', 'q24', 'q25', 'q26', 'q27', 'q28', 'q29', 'q3',
            'q30', 'q31', 'q32', 'q33', 'q34', 'q35', 'q36', 'q37', 'q38', 'q39', 'q4', 'q40',
            'q41', 'q42', 'q43', 'q44', 'q45', 'q46', 'q47', 'q5', 'q6', 'q7', 'q8', 'q9'
        }

        # Símbolos del alfabeto: dígitos del 0 al 9 y el punto como separador de octetos
        self.alphabet = ['.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        # Estado de arranque del autómata
        self.initial_state = "q0"

        # Estados de aceptación: cada uno corresponde a haber completado
        # el 4to octeto en un rango válido distinto.
        self.accept_states = {"q31", "q35", "q37", "q39", "q47"}

        # ── Función de transición δ : Q × Σ → P(Q) ──────────────────────────
        # Cada entrada tiene la forma  'qN': { 'símbolo': {conjunto de destinos} }
        # Las transiciones de cada estado se describen con comentarios agrupados
        # por la sección lógica del autómata a la que pertenecen.
        self.transitions = {

            # ── OCTETO 1 ─────────────────────────────────────────────────────
            # q0: estado inicial; el 1er dígito del primer octeto ramifica
            #     en múltiples posibilidades (1 dígito, 2 dígitos, o inicio de 1xx/2xx)
            'q0': {'1': {'q2', 'q1', 'q4'}, '8': {'q2', 'q1'}, '9': {'q2', 'q1'},
                   '2': {'q2', 'q1', 'q14'}, '3': {'q2', 'q1'}, '6': {'q2', 'q1'},
                   '7': {'q2', 'q1'}, '4': {'q2', 'q1'}, '5': {'q2', 'q1'}, '0': {'q1'}},

            # q1: octeto de 1 dígito [0-9] → espera punto
            'q1': {'.': {'q7'}},

            # q2→q3: segundo dígito del octeto [10-99] → espera punto en q3
            'q2': {'1': {'q3'}, '0': {'q3'}, '3': {'q3'}, '2': {'q3'}, '5': {'q3'},
                   '4': {'q3'}, '7': {'q3'}, '6': {'q3'}, '9': {'q3'}, '8': {'q3'}},
            'q3': {'.': {'q7'}},

            # q4→q5→q6: octeto en rango [100-199]; 1xx con x,x ∈ [0-9]
            'q4': {'3': {'q5'}, '2': {'q5'}, '1': {'q5'}, '0': {'q5'}, '7': {'q5'},
                   '6': {'q5'}, '5': {'q5'}, '4': {'q5'}, '9': {'q5'}, '8': {'q5'}},
            'q5': {'8': {'q6'}, '9': {'q6'}, '6': {'q6'}, '7': {'q6'}, '4': {'q6'},
                   '5': {'q6'}, '2': {'q6'}, '3': {'q6'}, '0': {'q6'}, '1': {'q6'}},
            'q6': {'.': {'q7'}},

            # q14→q15→q16: octeto en rango [200-249]; 2[0-4]x
            'q14': {'4': {'q15'}, '0': {'q15'}, '1': {'q15'}, '2': {'q15'}, '3': {'q15'}, '5': {'q40'}},
            'q15': {'0': {'q16'}, '1': {'q16'}, '2': {'q16'}, '3': {'q16'}, '4': {'q16'},
                    '5': {'q16'}, '6': {'q16'}, '7': {'q16'}, '8': {'q16'}, '9': {'q16'}},
            'q16': {'.': {'q7'}},

            # q40→q41: rama del 25x (250-255) dentro del primer octeto
            'q40': {'1': {'q41'}, '0': {'q41'}, '3': {'q41'}, '2': {'q41'}, '5': {'q41'}, '4': {'q41'}},
            'q41': {'.': {'q7'}},

            # q17→q42→q43: octeto en rango [250-255]; 25[0-5]
            'q17': {'3': {'q18'}, '2': {'q18'}, '1': {'q18'}, '0': {'q18'}, '4': {'q18'}, '5': {'q42'}},
            'q42': {'2': {'q43'}, '3': {'q43'}, '0': {'q43'}, '1': {'q43'}, '4': {'q43'}, '5': {'q43'}},
            'q43': {'.': {'q20'}},
            'q18': {'9': {'q19'}, '8': {'q19'}, '1': {'q19'}, '0': {'q19'}, '3': {'q19'},
                    '2': {'q19'}, '5': {'q19'}, '4': {'q19'}, '7': {'q19'}, '6': {'q19'}},
            'q19': {'.': {'q20'}},

            # ── SEPARADOR PUNTO 1 → OCTETO 2 (q7) ───────────────────────────
            # q7: punto entre octeto 1 y 2; lanza la lógica del 2do octeto
            'q7': {'1': {'q8', 'q9', 'q10'}, '0': {'q8'}, '3': {'q8', 'q10'}, '2': {'q8', 'q10', 'q17'},
                   '5': {'q8', 'q10'}, '4': {'q8', 'q10'}, '7': {'q8', 'q10'}, '6': {'q8', 'q10'},
                   '9': {'q8', 'q10'}, '8': {'q8', 'q10'}},

            # q8: un dígito [0-9] del 2do octeto → espera punto en q20
            'q8': {'.': {'q20'}},
            # q9→q12→q13: 2do octeto en rango [100-199]
            'q9': {'6': {'q12'}, '7': {'q12'}, '4': {'q12'}, '5': {'q12'}, '2': {'q12'},
                   '3': {'q12'}, '0': {'q12'}, '1': {'q12'}, '8': {'q12'}, '9': {'q12'}},
            # q10→q11: dos dígitos [10-99] del 2do octeto
            'q10': {'3': {'q11'}, '2': {'q11'}, '1': {'q11'}, '0': {'q11'}, '7': {'q11'},
                    '6': {'q11'}, '5': {'q11'}, '4': {'q11'}, '9': {'q11'}, '8': {'q11'}},
            'q11': {'.': {'q20'}},
            'q12': {'1': {'q13'}, '0': {'q13'}, '3': {'q13'}, '2': {'q13'}, '5': {'q13'},
                    '4': {'q13'}, '7': {'q13'}, '6': {'q13'}, '9': {'q13'}, '8': {'q13'}},
            'q13': {'.': {'q20'}},

            # ── SEPARADOR PUNTO 2 → OCTETO 3 (q20) ──────────────────────────
            'q20': {'1': {'q21', 'q22', 'q23'}, '9': {'q21', 'q22'}, '8': {'q21', 'q22'},
                    '7': {'q21', 'q22'}, '6': {'q21', 'q22'}, '5': {'q21', 'q22'},
                    '4': {'q21', 'q22'}, '3': {'q21', 'q22'}, '2': {'q24', 'q21', 'q22'}, '0': {'q21'}},

            # q21: 1 dígito del 3er octeto → espera punto en q30
            'q21': {'.': {'q30'}},
            # q22→q25: dos dígitos [10-99] del 3er octeto
            'q22': {'9': {'q25'}, '8': {'q25'}, '3': {'q25'}, '2': {'q25'}, '1': {'q25'},
                    '0': {'q25'}, '7': {'q25'}, '6': {'q25'}, '5': {'q25'}, '4': {'q25'}},
            'q25': {'.': {'q30'}},
            # q23→q26→q27: 3er octeto en rango [100-199]
            'q23': {'0': {'q26'}, '1': {'q26'}, '2': {'q26'}, '3': {'q26'}, '4': {'q26'},
                    '5': {'q26'}, '6': {'q26'}, '7': {'q26'}, '8': {'q26'}, '9': {'q26'}},
            'q26': {'2': {'q27'}, '3': {'q27'}, '0': {'q27'}, '1': {'q27'}, '6': {'q27'},
                    '7': {'q27'}, '4': {'q27'}, '5': {'q27'}, '8': {'q27'}, '9': {'q27'}},
            'q27': {'.': {'q30'}},
            # q24→q28→q29: 3er octeto en rango [200-255]
            'q24': {'2': {'q28'}, '3': {'q28'}, '0': {'q28'}, '1': {'q28'}, '4': {'q28'}, '5': {'q44'}},
            'q28': {'9': {'q29'}, '8': {'q29'}, '1': {'q29'}, '0': {'q29'}, '3': {'q29'},
                    '2': {'q29'}, '5': {'q29'}, '4': {'q29'}, '7': {'q29'}, '6': {'q29'}},
            'q29': {'.': {'q30'}},
            # q44→q45: rama 25x del 3er octeto
            'q44': {'5': {'q45'}, '4': {'q45'}, '1': {'q45'}, '0': {'q45'}, '3': {'q45'}, '2': {'q45'}},
            'q45': {'.': {'q30'}},

            # ── SEPARADOR PUNTO 3 → OCTETO 4 (q30) — ESTADOS DE ACEPTACIÓN ──
            # q30: punto entre octeto 3 y 4; el 4to octeto lleva a estados finales
            'q30': {'1': {'q33', 'q31', 'q32'}, '2': {'q34', 'q31', 'q32'}, '6': {'q31', 'q32'},
                    '7': {'q31', 'q32'}, '4': {'q31', 'q32'}, '5': {'q31', 'q32'}, '3': {'q31', 'q32'},
                    '0': {'q31'}, '8': {'q31', 'q32'}, '9': {'q31', 'q32'}},

            # q31: ★ ACEPTACIÓN — octeto 4 de 1 dígito [0-9]
            'q31': {},

            # q32→q35: ★ ACEPTACIÓN — octeto 4 de 2 dígitos [10-99]
            'q32': {'0': {'q35'}, '1': {'q35'}, '2': {'q35'}, '3': {'q35'}, '4': {'q35'},
                    '5': {'q35'}, '6': {'q35'}, '7': {'q35'}, '8': {'q35'}, '9': {'q35'}},
            'q35': {},  # ★ ACEPTACIÓN

            # q33→q36→q37: ★ ACEPTACIÓN — octeto 4 en rango [100-199]
            'q33': {'4': {'q36'}, '5': {'q36'}, '6': {'q36'}, '7': {'q36'}, '0': {'q36'},
                    '1': {'q36'}, '2': {'q36'}, '3': {'q36'}, '8': {'q36'}, '9': {'q36'}},
            'q36': {'0': {'q37'}, '1': {'q37'}, '2': {'q37'}, '3': {'q37'}, '4': {'q37'},
                    '5': {'q37'}, '6': {'q37'}, '7': {'q37'}, '8': {'q37'}, '9': {'q37'}},
            'q37': {},  # ★ ACEPTACIÓN

            # q34→q38→q39: ★ ACEPTACIÓN — octeto 4 en rango [200-255]
            'q34': {'5': {'q46'}, '3': {'q38'}, '2': {'q38'}, '1': {'q38'}, '0': {'q38'}, '4': {'q38'}},
            'q38': {'9': {'q39'}, '8': {'q39'}, '7': {'q39'}, '6': {'q39'}, '5': {'q39'},
                    '4': {'q39'}, '3': {'q39'}, '2': {'q39'}, '1': {'q39'}, '0': {'q39'}},
            'q39': {},  # ★ ACEPTACIÓN

            # q46→q47: ★ ACEPTACIÓN — octeto 4 en rango [250-255]
            'q46': {'4': {'q47'}, '5': {'q47'}, '2': {'q47'}, '3': {'q47'}, '0': {'q47'}, '1': {'q47'}},
            'q47': {},  # ★ ACEPTACIÓN
        }

    def get_definition(self):
        """
        Retorna la definición completa del autómata en formato JSON-serializable.

        Extiende la definición base (estados, alfabeto, transiciones) con
        metadatos adicionales para el frontend: nombre, descripción, lenguaje
        formal, etiquetas legibles de los estados clave, y ejemplos de IPs
        válidas e inválidas para guiar al usuario.
        """
        base = super().get_definition()
        base.update({
            "name": "Validador de Dirección IP",
            "description": "Valida direcciones IPv4 en el formato X.X.X.X, donde X es de 0 a 255.",
            "language": "L = { w | w es una dirección IPv4 válida de 4 octetos separados por puntos }",
            # Etiquetas descriptivas para los estados más relevantes del diagrama
            "state_labels": {
                'q1': 'un dígito [0-9]',
                'q3': 'dos dígitos [10-99]',
                'q6': 'tres dígitos [100-199]',
                'q7': 'punto de octeto',
                'q8': 'un dígito [0-9]',
                'q11': 'dos dígitos [10-99]',
                'q13': 'tres dígitos [100-199]',
                'q16': 'tres dígitos [200-249]',
                'q19': 'tres dígitos [200-255]',
                'q20': 'punto de octeto',
                'q30': 'punto de octeto',
                'q31': 'un dígito [0-9]',
                'q35': 'dos dígitos [10-99]',
                'q37': 'tres dígitos [100-199]',
                'q39': 'tres dígitos [200-255]'
            },
            # Ejemplos que se muestran en la tarjeta de definición del frontend
            "examples": {
                "valid": [
                    ["1", "9", "2", ".", "1", "6", "8", ".", "0", ".", "1"],
                    ["1", "2", "7", ".", "0", ".", "0", ".", "1"],
                    ["2", "5", "5", ".", "2", "5", "5", ".", "2", "5", "5", ".", "2", "5", "5"],
                    ["0", ".", "0", ".", "0", ".", "0"]
                ],
                "invalid": [
                    ["2", "5", "6", ".", "1", ".", "1", ".", "1"],  # 256 > 255
                    ["1", ".", "2", ".", "3"],                       # solo 3 octetos
                    ["1", "0", ".", "0", ".", "0", ".", "0", "0"],   # octeto con 00 al final
                    ["1", "9", "2", ".", "1", "6", "8", ".", ".", "1"]  # dos puntos seguidos
                ]
            }
        })
        return base