# Simulador de Autómatas Finitos No Deterministas (AFND)

Proyecto académico desarrollado para la asignatura **Teoría de Autómatas** (Semestre 6) en la **Universidad Nacional de Loja — FEIRNNR, Carrera de Computación**.

El sistema permite **definir, visualizar y simular** autómatas finitos no deterministas (AFND) de forma interactiva. El usuario construye una cadena de tokens símbolo por símbolo y el simulador ejecuta el autómata, mostrando la traza completa de transiciones paso a paso junto con un diagrama visual de los estados activos.

---

## Estructura del proyecto

```
proyecto_de_automatas/
│
├── Backend/                          # Servidor API REST — Python + Flask
│   ├── app.py                        # Punto de entrada: configura Flask y registra las rutas
│   ├── automatas/                    # Paquete con todos los autómatas implementados
│   │   ├── __init__.py               # Registro central de autómatas (AUTOMATA_REGISTRY)
│   │   ├── base.py                   # Clase abstracta AFNDSimulator (motor de simulación)
│   │   ├── validador_ip.py           # Autómata: Validador de Dirección IPv4
│   │   └── validador_mac.py          # Autómata: Validador de Dirección MAC
│   └── routes/
│       └── api_routes.py             # Definición de los endpoints REST de la API
│
├── Frontend/                         # Interfaz de usuario — React + Vite
│   ├── index.html                    # HTML raíz de la SPA
│   ├── vite.config.js                # Config de Vite (proxy /api → puerto 5000)
│   └── src/
│       ├── main.jsx                  # Punto de montaje de React
│       ├── App.jsx                   # Componente raíz: orquesta pestañas, simulación y diagrama
│       ├── styles/
│       │   └── global.css            # Variables CSS, tipografía y estilos globales
│       ├── data/
│       │   └── api.js                # Cliente HTTP (axios) para el backend
│       └── components/
│           ├── StateDiagram.jsx      # Diagrama SVG interactivo de estados
│           ├── TokenInput.jsx        # Panel de construcción de cadena de tokens
│           ├── SimulationTrace.jsx   # Visualizador de la traza de ejecución paso a paso
│           └── TransitionTable.jsx   # Tabla δ: Q × Σ → P(Q)
│
├── IP_verificacion_no_determinista.xml        # Definición del autómata IP (formato JFLAP)
└── MAC_verificacion_no_determinista - copia.xml  # Definición del autómata MAC (formato JFLAP)
```

---

## Autómatas disponibles

| Clave | Ícono | Nombre                      | Descripción breve |
|-------|-------|-----------------------------|-------------------|
| `ip`  | 🌐    | Validador de Dirección IPv4 | Valida `X.X.X.X` con octetos de 0–255 |
| `mac` | 🔌    | Validador de Dirección MAC  | Valida `XX-XX-XX-XX-XX-XX` en hexadecimal |

---

## Requisitos previos

- **Python** ≥ 3.10
- **Node.js** ≥ 18 y npm

---

## Instalación y ejecución

### 1. Backend (Flask)

```bash
cd Backend

# Crear y activar el entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install flask flask-cors

# Iniciar el servidor
python app.py
# → disponible en http://localhost:5000
```

### 2. Frontend (React + Vite)

```bash
cd Frontend

# Instalar dependencias
npm install

# Iniciar el servidor de desarrollo
npm run dev
# → disponible en http://localhost:5173
```

> Ambos servicios deben estar corriendo simultáneamente. El proxy de Vite redirige `/api/*` al puerto 5000 automáticamente.

---

## Endpoints de la API REST

Todos los endpoints usan el prefijo `/api` y retornan JSON.

---

### `GET /api/automatas`

Retorna la definición formal de **todos** los autómatas registrados en `AUTOMATA_REGISTRY`. El frontend lo consume al cargar la página para construir las pestañas dinámicamente.

**Response 200:**
```json
{
  "success": true,
  "automatas": {
    "ip": {
      "name": "Validador de Dirección IP",
      "description": "Valida direcciones IPv4 en el formato X.X.X.X, donde X es de 0 a 255.",
      "language": "L = { w | w es una dirección IPv4 válida de 4 octetos separados por puntos }",
      "states": ["q0", "q1", "..."],
      "alphabet": [".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
      "initial_state": "q0",
      "accept_states": ["q31", "q35", "q37", "q39", "q47"],
      "transitions": { "q0": { "1": ["q1", "q2", "q4"] }, "..." : "..." },
      "state_labels": { "q7": "punto de octeto", "...": "..." },
      "examples": {
        "valid": [["1","9","2",".","1","6","8",".","0",".","1"]],
        "invalid": [["2","5","6",".","1",".","1",".","1"]]
      }
    },
    "mac": { "..." : "..." }
  }
}
```

---

### `GET /api/automatas/<key>`

Retorna la definición de **un único** autómata identificado por su clave.

**Parámetro URL:** `key` — clave del autómata (`ip` o `mac`).

**Response 200:**
```json
{ "success": true, "automata": { "...definición completa..." } }
```

**Response 404:**
```json
{
  "success": false,
  "error": "Autómata 'xxx' no encontrado. Disponibles: ['ip', 'mac']"
}
```

---

### `POST /api/simulate/<key>`

Ejecuta la simulación del autómata sobre la cadena de tokens enviada en el cuerpo.

**Parámetro URL:** `key` — clave del autómata a simular.

**Body JSON:**
```json
{
  "tokens": ["1", "9", "2", ".", "1", "6", "8", ".", "0", ".", "1"]
}
```

> Los tokens se normalizan automáticamente a mayúsculas. Límite: 1–100 tokens.

**Response 200:**
```json
{
  "success": true,
  "accepted": true,
  "result_message": "Cadena ACEPTADA ✓",
  "final_states": ["q31"],
  "trace": [
    {
      "step": 0,
      "token": null,
      "states_before": ["q0"],
      "states_after":  ["q0"],
      "description":   "Estado inicial: {q0}"
    },
    {
      "step": 1,
      "token": "1",
      "states_before": ["q0"],
      "states_after":  ["q1", "q2", "q4"],
      "description":   "δ({q0}, 1) = {q1, q2, q4}"
    }
  ]
}
```

**Response 400** — token fuera del alfabeto, lista vacía o mal formada:
```json
{ "success": false, "error": "Token 'Z' no pertenece al alfabeto ['.', '0', ...]" }
```

**Response 404** — clave de autómata no registrada:
```json
{ "success": false, "error": "Autómata 'xyz' no encontrado." }
```

---

## Añadir un nuevo autómata

1. **Crear** `Backend/automatas/mi_automata.py`:

```python
from .base import AFNDSimulator

class MiAFND(AFNDSimulator):
    def _setup(self):
        self.states = {"q0", "q1", "q2"}
        self.alphabet = ["A", "B"]
        self.initial_state = "q0"
        self.accept_states = {"q2"}
        self.transitions = {
            "q0": {"A": {"q1"}},
            "q1": {"B": {"q2"}},
        }

    def get_definition(self):
        base = super().get_definition()
        base.update({
            "name": "Mi Autómata",
            "language": "L = { AB }",
            "examples": {
                "valid": [["A", "B"]],
                "invalid": [["A"], ["B"]]
            }
        })
        return base
```

2. **Registrar** en `Backend/automatas/__init__.py`:

```python
from .mi_automata import MiAFND

AUTOMATA_REGISTRY = {
    "ip":  ValidadorIpAFND,
    "mac": ValidadorMacAFND,
    "mi_automata": MiAFND,   # ← nueva línea
}
```

3. **Añadir metadatos visuales** en `Frontend/src/App.jsx`:

```js
const AUTOMATA_META = {
  ip:  { icon: '🌐', color: '#00d4ff' },
  mac: { icon: '🔌', color: '#a855f7' },
  mi_automata: { icon: '⚙', color: '#ffb300' },  // ← nueva línea
}
```

4. *(Opcional)* Si tiene muchos estados, añadir su clave a las condiciones que ocultan la tabla y activan el modo de carril `IpStatePath` en `App.jsx` y `StateDiagram.jsx`.

---

## Tecnologías utilizadas

| Capa     | Tecnología          |
|----------|---------------------|
| Backend  | Python 3.10+ / Flask |
| Backend  | flask-cors          |
| Frontend | React 18 + Vite 6   |
| Frontend | Axios               |

---

## Autores

Proyecto académico — Universidad Nacional de Loja · FEIRNNR · Computación  
Semestre 6 · Teoría de Autómatas · 2026
