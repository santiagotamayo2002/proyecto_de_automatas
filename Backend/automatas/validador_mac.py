"""
=============================================================================
validador_mac.py — Autómata Finito No Determinista para validación de MAC
=============================================================================

Propósito:
    Implementa la clase ValidadorMacAFND que valida si una cadena de tokens
    representa una dirección MAC válida en el formato XX-XX-XX-XX-XX-XX,
    donde cada XX es un par de dígitos hexadecimales (00–FF).

Origen del autómata:
    Los estados, transiciones y estados de aceptación fueron extraídos del
    archivo 'MAC_verificacion_no_determinista - copia.xml' (formato JFLAP),
    ubicado en la raíz del proyecto. Las transiciones épsilon (ε) presentes
    en el XML fueron expandidas manualmente para compatibilidad con el
    simulador base (que no soporta ε-transiciones directamente).

Formato aceptado:
    Una dirección MAC está compuesta por 6 pares hexadecimales separados
    por guiones. Cada par puede contener dígitos 0-9 y letras A-F.
    Ejemplo válido:  00-1A-2B-3C-4D-5E
    → tokens: ['0','0','-','1','A','-','2','B','-','3','C','-','4','D','-','5','E']
    Ejemplo inválido: GG-1A-2B-3C-4D-5E  (G no es hexadecimal)

Estructura del autómata (36 estados):
    Cada octeto hexadecimal (XX) se procesa con dos nibbles (half-bytes):
      - 1er nibble: puede ser 0-9 → ruta numérica, o A-F → ruta literal
      - 2do nibble: similar al primero
    El autómata replica esta lógica para los 6 octetos con 5 guiones separadores:

      q0 → [1er octeto: nibble 1] → q1/q19 → [nibble 2] → q2/q20 → q5 (guion 1)
      q5 → [2do octeto] → q6/q33 → q7 (guion 2)
      q4 → [3er octeto] → q8/q10 → q18 (guion 3)
      q18 → [4to octeto] → q13/q16 → q15 (guion 4)
      q15 → [5to octeto] → q37/q38 → q43 (guion 5)
      q43 → [6to octeto] → q42/q44 → q46/q47 (ACEPTACIÓN)

Estados de aceptación: q46, q47
    q46 → 6to octeto completado con 2do nibble numérico (0-9)
    q47 → 6to octeto completado con 2do nibble literal (A-F)

Alfabeto (tokens que el usuario ingresa uno por uno):
    '0'-'9', 'A'-'F', '-'

Integración con el frontend:
    - Clave de registro: "mac"
    - No muestra tabla de transiciones (demasiados estados).
    - El diagrama usa el modo IpStatePath: muestra los últimos 5 estados
      visitados en un carril horizontal limpio (igual que el validador IP).
=============================================================================
"""

from .base import AFNDSimulator


class ValidadorMacAFND(AFNDSimulator):
    """
    AFND para validar direcciones MAC en formato XX-XX-XX-XX-XX-XX.

    Cada 'XX' representa un byte hexadecimal (00–FF). El autómata procesa
    la dirección token a token (un carácter o guion por vez) usando
    no-determinismo para cubrir simultáneamente las rutas numéricas (0-9)
    y literales (A-F) en cada nibble.

    Estados de aceptación:
        q46  → 6to octeto con 2do nibble numérico (0-9)
        q47  → 6to octeto con 2do nibble literal (A-F)
    """

    def _setup(self):
        """
        Configura el autómata con los 36 estados y las transiciones del XML.

        Organización de los grupos de estados por sección de la MAC:
          1er octeto: q0 → q1/q19 → q2/q20 → guion (q5)
          2do octeto: q5 → q6/q33 → q7 → guion (q4)
          3er octeto: q4 → q8/q10 → q9/q12 → guion (q18)
          4to octeto: q18 → q13/q16 → q14/q17 → guion (q15)
          5to octeto: q15 → q37/q38 → q40/q41 → guion (q43)
          6to octeto: q43 → q42/q44 → q46/q47 (★ ACEPTACIÓN)

        Nota: las transiciones ε del XML original se expandieron directamente
        en los conjuntos de destino para evitar necesitar un motor ε-NFA.
        """
        # Conjunto de todos los estados del autómata
        self.states = {
            'q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9',
            'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q16', 'q17', 'q18', 'q19',
            'q20', 'q33', 'q34', 'q35', 'q36', 'q37', 'q38', 'q39',
            'q40', 'q41', 'q42', 'q43', 'q44', 'q45', 'q46', 'q47'
        }

        # Alfabeto: dígitos hexadecimales (0-9, A-F) más el separador guion
        # Nota: el AFND original usa épsilon ('') internamente, pero la simulación
        # trabaja solo con los símbolos que el usuario ingresa como tokens.
        self.alphabet = [
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'A', 'B', 'C', 'D', 'E', 'F', '-'
        ]

        # Estado inicial del autómata
        self.initial_state = 'q0'

        # Estados de aceptación (dirección MAC válida)
        self.accept_states = {'q46', 'q47'}

        # Función de transición δ: estado × símbolo → conjunto de estados
        # Las transiciones con '' (épsilon) se han expandido manualmente para
        # mantener la compatibilidad con el simulador base que no soporta ε-transiciones.
        self.transitions = {
            # Estado inicial: acepta 0-9 (→ q1 y q19) y A-F (→ q3→ε→q1,q19)
            'q0': {
                '0': {'q1', 'q19'}, '1': {'q1', 'q19'}, '2': {'q1', 'q19'},
                '3': {'q1', 'q19'}, '4': {'q1', 'q19'}, '5': {'q1', 'q19'},
                '6': {'q1', 'q19'}, '7': {'q1', 'q19'}, '8': {'q1', 'q19'},
                '9': {'q1', 'q19'},
                # A-F van a q3, que tiene ε hacia q1 y q19 → expandimos directamente
                'A': {'q1', 'q19'}, 'B': {'q1', 'q19'}, 'C': {'q1', 'q19'},
                'D': {'q1', 'q19'}, 'E': {'q1', 'q19'}, 'F': {'q1', 'q19'},
            },
            # Primer nibble (0-9) del primer octeto → segundo nibble
            'q1': {
                '0': {'q2'}, '1': {'q2'}, '2': {'q2'}, '3': {'q2'},
                '4': {'q2'}, '5': {'q2'}, '6': {'q2'}, '7': {'q2'},
                '8': {'q2'}, '9': {'q2'},
                'A': {'q2'}, 'B': {'q2'}, 'C': {'q2'},
                'D': {'q2'}, 'E': {'q2'}, 'F': {'q2'},
            },
            # Segundo nibble completo → separador '-'
            'q2': {'-': {'q5'}},
            # Primer nibble (A-F) del primer octeto → ε-cierre: igual que q1
            # q3 expandido (ε→q1, ε→q19)
            'q19': {
                '0': {'q20'}, '1': {'q20'}, '2': {'q20'}, '3': {'q20'},
                '4': {'q20'}, '5': {'q20'}, '6': {'q20'}, '7': {'q20'},
                '8': {'q20'}, '9': {'q20'},
                'A': {'q20'}, 'B': {'q20'}, 'C': {'q20'},
                'D': {'q20'}, 'E': {'q20'}, 'F': {'q20'},
            },
            'q20': {'-': {'q5'}},
            # Primer nibble del 2do octeto (después de 1er guion)
            'q5': {
                '0': {'q6', 'q33'}, '1': {'q6', 'q33'}, '2': {'q6', 'q33'},
                '3': {'q6', 'q33'}, '4': {'q6', 'q33'}, '5': {'q6', 'q33'},
                '6': {'q6', 'q33'}, '7': {'q6', 'q33'}, '8': {'q6', 'q33'},
                '9': {'q6', 'q33'},
                # A-F: q35 → ε → q33, q6
                'A': {'q6', 'q33'}, 'B': {'q6', 'q33'}, 'C': {'q6', 'q33'},
                'D': {'q6', 'q33'}, 'E': {'q6', 'q33'}, 'F': {'q6', 'q33'},
            },
            # 2do nibble del 2do octeto (rama 0-9)
            'q6': {
                '0': {'q7'}, '1': {'q7'}, '2': {'q7'}, '3': {'q7'},
                '4': {'q7'}, '5': {'q7'}, '6': {'q7'}, '7': {'q7'},
                '8': {'q7'}, '9': {'q7'},
                'A': {'q7'}, 'B': {'q7'}, 'C': {'q7'},
                'D': {'q7'}, 'E': {'q7'}, 'F': {'q7'},
            },
            'q7': {'-': {'q4'}},
            # 1er nibble del 2do octeto (rama A-F: q33 → A-F → q34)
            'q33': {
                'A': {'q34'}, 'B': {'q34'}, 'C': {'q34'},
                'D': {'q34'}, 'E': {'q34'}, 'F': {'q34'},
                '0': {'q7'}, '1': {'q7'}, '2': {'q7'}, '3': {'q7'},
                '4': {'q7'}, '5': {'q7'}, '6': {'q7'}, '7': {'q7'},
                '8': {'q7'}, '9': {'q7'},
            },
            'q34': {'-': {'q4'}},
            # 1er nibble del 3er octeto (después de 2do guion)
            'q4': {
                '0': {'q8', 'q10'}, '1': {'q8', 'q10'}, '2': {'q8', 'q10'},
                '3': {'q8', 'q10'}, '4': {'q8', 'q10'}, '5': {'q8', 'q10'},
                '6': {'q8', 'q10'}, '7': {'q8', 'q10'}, '8': {'q8', 'q10'},
                '9': {'q8', 'q10'},
                # A-F: q11 → ε → q10, q8
                'A': {'q8', 'q10'}, 'B': {'q8', 'q10'}, 'C': {'q8', 'q10'},
                'D': {'q8', 'q10'}, 'E': {'q8', 'q10'}, 'F': {'q8', 'q10'},
            },
            # 2do nibble del 3er octeto (rama 0-9)
            'q8': {
                '0': {'q9'}, '1': {'q9'}, '2': {'q9'}, '3': {'q9'},
                '4': {'q9'}, '5': {'q9'}, '6': {'q9'}, '7': {'q9'},
                '8': {'q9'}, '9': {'q9'},
                'A': {'q9'}, 'B': {'q9'}, 'C': {'q9'},
                'D': {'q9'}, 'E': {'q9'}, 'F': {'q9'},
            },
            'q9': {'-': {'q18'}},
            # 2do nibble del 3er octeto (rama A-F)
            'q10': {
                'A': {'q12'}, 'B': {'q12'}, 'C': {'q12'},
                'D': {'q12'}, 'E': {'q12'}, 'F': {'q12'},
                '0': {'q9'}, '1': {'q9'}, '2': {'q9'}, '3': {'q9'},
                '4': {'q9'}, '5': {'q9'}, '6': {'q9'}, '7': {'q9'},
                '8': {'q9'}, '9': {'q9'},
            },
            'q12': {'-': {'q18'}},
            # 1er nibble del 4to octeto (después de 3er guion)
            'q18': {
                '0': {'q13', 'q16'}, '1': {'q13', 'q16'}, '2': {'q13', 'q16'},
                '3': {'q13', 'q16'}, '4': {'q13', 'q16'}, '5': {'q13', 'q16'},
                '6': {'q13', 'q16'}, '7': {'q13', 'q16'}, '8': {'q13', 'q16'},
                '9': {'q13', 'q16'},
                # A-F: q36 → ε → q13, q16
                'A': {'q13', 'q16'}, 'B': {'q13', 'q16'}, 'C': {'q13', 'q16'},
                'D': {'q13', 'q16'}, 'E': {'q13', 'q16'}, 'F': {'q13', 'q16'},
            },
            # 2do nibble del 4to octeto (rama 0-9)
            'q13': {
                '0': {'q14'}, '1': {'q14'}, '2': {'q14'}, '3': {'q14'},
                '4': {'q14'}, '5': {'q14'}, '6': {'q14'}, '7': {'q14'},
                '8': {'q14'}, '9': {'q14'},
                'A': {'q14'}, 'B': {'q14'}, 'C': {'q14'},
                'D': {'q14'}, 'E': {'q14'}, 'F': {'q14'},
            },
            'q14': {'-': {'q15'}},
            # 2do nibble del 4to octeto (rama A-F)
            'q16': {
                'A': {'q17'}, 'B': {'q17'}, 'C': {'q17'},
                'D': {'q17'}, 'E': {'q17'}, 'F': {'q17'},
                '0': {'q14'}, '1': {'q14'}, '2': {'q14'}, '3': {'q14'},
                '4': {'q14'}, '5': {'q14'}, '6': {'q14'}, '7': {'q14'},
                '8': {'q14'}, '9': {'q14'},
            },
            'q17': {'-': {'q15'}},
            # 1er nibble del 5to octeto (después de 4to guion)
            'q15': {
                '0': {'q37', 'q38'}, '1': {'q37', 'q38'}, '2': {'q37', 'q38'},
                '3': {'q37', 'q38'}, '4': {'q37', 'q38'}, '5': {'q37', 'q38'},
                '6': {'q37', 'q38'}, '7': {'q37', 'q38'}, '8': {'q37', 'q38'},
                '9': {'q37', 'q38'},
                # A-F: q39 → ε → q37, q38
                'A': {'q37', 'q38'}, 'B': {'q37', 'q38'}, 'C': {'q37', 'q38'},
                'D': {'q37', 'q38'}, 'E': {'q37', 'q38'}, 'F': {'q37', 'q38'},
            },
            # 2do nibble del 5to octeto (rama 0-9)
            'q37': {
                '0': {'q40'}, '1': {'q40'}, '2': {'q40'}, '3': {'q40'},
                '4': {'q40'}, '5': {'q40'}, '6': {'q40'}, '7': {'q40'},
                '8': {'q40'}, '9': {'q40'},
                'A': {'q40'}, 'B': {'q40'}, 'C': {'q40'},
                'D': {'q40'}, 'E': {'q40'}, 'F': {'q40'},
            },
            'q40': {'-': {'q43'}},
            # 2do nibble del 5to octeto (rama A-F)
            'q38': {
                'A': {'q41'}, 'B': {'q41'}, 'C': {'q41'},
                'D': {'q41'}, 'E': {'q41'}, 'F': {'q41'},
                '0': {'q40'}, '1': {'q40'}, '2': {'q40'}, '3': {'q40'},
                '4': {'q40'}, '5': {'q40'}, '6': {'q40'}, '7': {'q40'},
                '8': {'q40'}, '9': {'q40'},
            },
            'q41': {'-': {'q43'}},
            # 1er nibble del 6to (último) octeto (después de 5to guion)
            'q43': {
                '0': {'q42', 'q44'}, '1': {'q42', 'q44'}, '2': {'q42', 'q44'},
                '3': {'q42', 'q44'}, '4': {'q42', 'q44'}, '5': {'q42', 'q44'},
                '6': {'q42', 'q44'}, '7': {'q42', 'q44'}, '8': {'q42', 'q44'},
                '9': {'q42', 'q44'},
                # A-F: q45 → ε → q42, q44
                'A': {'q42', 'q44'}, 'B': {'q42', 'q44'}, 'C': {'q42', 'q44'},
                'D': {'q42', 'q44'}, 'E': {'q42', 'q44'}, 'F': {'q42', 'q44'},
            },
            # 2do nibble del 6to octeto (rama 0-9) → ACEPTACIÓN
            'q42': {
                '0': {'q46'}, '1': {'q46'}, '2': {'q46'}, '3': {'q46'},
                '4': {'q46'}, '5': {'q46'}, '6': {'q46'}, '7': {'q46'},
                '8': {'q46'}, '9': {'q46'},
                'A': {'q46'}, 'B': {'q46'}, 'C': {'q46'},
                'D': {'q46'}, 'E': {'q46'}, 'F': {'q46'},
            },
            # 2do nibble del 6to octeto (rama A-F) → ACEPTACIÓN
            'q44': {
                'A': {'q47'}, 'B': {'q47'}, 'C': {'q47'},
                'D': {'q47'}, 'E': {'q47'}, 'F': {'q47'},
                '0': {'q46'}, '1': {'q46'}, '2': {'q46'}, '3': {'q46'},
                '4': {'q46'}, '5': {'q46'}, '6': {'q46'}, '7': {'q46'},
                '8': {'q46'}, '9': {'q46'},
            },
            # Estados de aceptación (sin transiciones salientes)
            'q46': {},
            'q47': {},
        }

    def get_definition(self):
        """Retorna la definición formal del autómata para el frontend."""
        base = super().get_definition()
        base.update({
            "name": "Validador de Dirección MAC",
            "description": "Valida direcciones MAC en formato XX-XX-XX-XX-XX-XX, donde X es un dígito hexadecimal (0-9, A-F).",
            "language": "L = { w | w es una dirección MAC válida de 6 octetos hexadecimales separados por guiones }",
            "state_labels": {
                'q0': 'Inicio',
                'q5': '1er guión',
                'q7': '2do guión (00-FF)',
                'q4': '2do guión',
                'q18': '3er guión',
                'q15': '4to guión',
                'q43': '5to guión',
                'q46': 'MAC válida ✓',
                'q47': 'MAC válida ✓',
            },
            "examples": {
                "valid": [
                    ["0", "0", "-", "1", "A", "-", "2", "B", "-", "3", "C", "-", "4", "D", "-", "5", "E"],
                    ["F", "F", "-", "F", "F", "-", "F", "F", "-", "F", "F", "-", "F", "F", "-", "F", "F"],
                    ["0", "0", "-", "0", "0", "-", "0", "0", "-", "0", "0", "-", "0", "0", "-", "0", "0"],
                    ["A", "B", "-", "C", "D", "-", "E", "F", "-", "1", "2", "-", "3", "4", "-", "5", "6"],
                ],
                "invalid": [
                    ["0", "0", "-", "1", "A", "-", "2", "B", "-", "3", "C", "-", "4", "D"],
                    ["G", "G", "-", "1", "A", "-", "2", "B", "-", "3", "C", "-", "4", "D", "-", "5", "E"],
                    ["0", "0", "1", "A", "2", "B", "3", "C", "4", "D", "5", "E"],
                    ["0", "0", "-", "1", "A", "-", "2", "B", "-", "3", "C", "-", "4", "D", "-"],
                ]
            }
        })
        return base
