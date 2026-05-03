"""
=============================================================================
base.py — Clase base abstracta para todos los autómatas finitos no deterministas
=============================================================================

Propósito:
    Define el contrato común que debe cumplir cualquier autómata implementado
    en este proyecto. Toda clase concreta (ValidadorIpAFND, ValidadorMacAFND, etc.)
    hereda de AFNDSimulator e implementa únicamente
    el método `_setup()` para configurar sus estados, alfabeto y transiciones.

Arquitectura:
    - Se usa el patrón Template Method: __init__ llama a _setup() de la subclase,
      asegurando que el autómata esté listo antes de cualquier uso.
    - La simulación implementa la definición formal de un AFND:
        δ: Q × Σ → P(Q)  (la función de transición devuelve un CONJUNTO de estados)
    - Al procesar cada token, se expanden todos los estados activos en paralelo
      (superposición de estados, característica fundamental del no-determinismo).

Métodos públicos:
    simulate(tokens)     → Ejecuta la simulación y devuelve traza + resultado.
    get_definition()     → Retorna la estructura del autómata serializable a JSON.
    get_next_states(...) → Retorna el conjunto de estados alcanzados desde un estado
                           al consumir un token.

Para añadir un nuevo autómata al sistema:
    1. Crear un nuevo archivo .py en esta misma carpeta (ej: mi_automata.py).
    2. Definir una clase que herede de AFNDSimulator.
    3. Implementar _setup() asignando self.states, self.alphabet,
       self.initial_state, self.accept_states y self.transitions.
    4. (Opcional) Sobreescribir get_definition() para añadir metadatos
       adicionales (name, description, examples, state_labels).
    5. Registrar la clase en automatas/__init__.py.
=============================================================================
"""

from abc import ABC, abstractmethod
from typing import Set, List, Dict, Any


class AFNDSimulator(ABC):
    """
    Clase base abstracta para Autómatas Finitos No Deterministas (AFND).

    Un AFND se define formalmente como la 5-tupla M = (Q, Σ, δ, q0, F) donde:
        Q   → Conjunto finito de estados         (self.states)
        Σ   → Alfabeto de entrada                (self.alphabet)
        δ   → Función de transición Q × Σ → P(Q) (self.transitions)
        q0  → Estado inicial                      (self.initial_state)
        F   → Conjunto de estados de aceptación   (self.accept_states)

    Las subclases deben implementar _setup() para inicializar estos atributos.
    """

    def __init__(self):
        # Atributos de la 5-tupla; _setup() los rellena en la subclase.
        self.states: Set[str] = set()
        self.alphabet: List[str] = []
        self.transitions: Dict[str, Dict[str, Set[str]]] = {}
        self.initial_state: str = ""
        self.accept_states: Set[str] = set()
        # Invoca la configuración de la subclase concreta (Template Method)
        self._setup()

    @abstractmethod
    def _setup(self):
        """
        Configura los atributos del autómata. Debe ser implementado por
        cada clase concreta (IoTProtocolAFND, ValidadorIpAFND, etc.).
        """
        pass

    def get_next_states(self, current_state: str, token: str) -> Set[str]:
        """
        Aplica la función de transición δ para un estado y un token.

        Args:
            current_state: Estado actual del autómata.
            token:         Símbolo a consumir del alfabeto Σ.

        Returns:
            Conjunto (posiblemente vacío) de estados alcanzados.
        """
        return self.transitions.get(current_state, {}).get(token, set())

    def simulate(self, input_tokens: List[str]) -> Dict[str, Any]:
        """
        Simula el AFND procesando la secuencia de tokens de entrada.

        El algoritmo mantiene un CONJUNTO de estados activos simultáneamente
        (subset construction en tiempo de ejecución), lo que modela el
        no-determinismo: ante cada token, todos los estados activos avanzan
        en paralelo y sus resultados se unen.

        Args:
            input_tokens: Lista de strings. Cada elemento debe pertenecer a self.alphabet.

        Returns:
            Diccionario con los campos:
                accepted      (bool)   → True si la cadena es aceptada.
                trace         (list)   → Lista de pasos con estados antes/después.
                final_states  (list)   → Estados activos al finalizar la simulación.
                result_message (str)   → Mensaje legible con el veredicto.
                error         (str)    → Solo presente si hay un token inválido.
        """
        # El autómata comienza en el estado inicial (conjunto unitario)
        current_states: Set[str] = {self.initial_state}
        trace = []

        # Paso 0: estado inicial antes de consumir cualquier token
        trace.append({
            "step": 0,
            "token": None,
            "states_before": list(current_states),
            "states_after": list(current_states),
            "description": f"Estado inicial: {{{', '.join(sorted(current_states))}}}"
        })

        for idx, token in enumerate(input_tokens):
            # Rechazar inmediatamente si el token no pertenece al alfabeto
            if token not in self.alphabet:
                return {
                    "accepted": False,
                    "trace": trace,
                    "final_states": [],
                    "error": f"Token '{token}' no pertenece al alfabeto {self.alphabet}"
                }

            states_before = set(current_states)
            next_states: Set[str] = set()

            # Expansión no-determinista: unión de todos los δ(q, token) para q ∈ current_states
            for state in current_states:
                next_states |= self.get_next_states(state, token)

            # Registrar este paso en la traza
            trace.append({
                "step": idx + 1,
                "token": token,
                "states_before": sorted(list(states_before)),
                "states_after": sorted(list(next_states)),
                "description": (
                    f"δ({{{', '.join(sorted(states_before))}}}, {token}) = "
                    f"{{{', '.join(sorted(next_states)) if next_states else '∅'}}}"
                )
            })

            current_states = next_states

            # Si el conjunto de estados activos queda vacío, la cadena es rechazada
            if not current_states:
                return {
                    "accepted": False,
                    "trace": trace,
                    "final_states": [],
                    "result_message": "Cadena RECHAZADA: no hay estados activos."
                }

        # La cadena es aceptada si algún estado activo final pertenece a F
        accepted = bool(current_states & self.accept_states)
        return {
            "accepted": accepted,
            "trace": trace,
            "final_states": sorted(list(current_states)),
            "result_message": (
                "Cadena ACEPTADA ✓" if accepted
                else "Cadena RECHAZADA: estados finales no son de aceptación."
            )
        }

    def get_definition(self) -> Dict[str, Any]:
        """
        Serializa la definición formal del autómata a un diccionario JSON-friendly.

        Convierte los sets internos (no serializables) a listas ordenadas.
        Las subclases pueden llamar a super().get_definition() y agregar campos
        adicionales como 'name', 'description', 'examples' o 'state_labels'.

        Returns:
            Diccionario con states, alphabet, transitions, initial_state, accept_states.
        """
        # Convertir sets de destinos en listas ordenadas (JSON no soporta sets)
        serializable_transitions = {}
        for state, trans in self.transitions.items():
            serializable_transitions[state] = {
                token: sorted(list(targets))
                for token, targets in trans.items()
            }
        return {
            "states": sorted(list(self.states)),
            "alphabet": self.alphabet,
            "transitions": serializable_transitions,
            "initial_state": self.initial_state,
            "accept_states": sorted(list(self.accept_states)),
        }
