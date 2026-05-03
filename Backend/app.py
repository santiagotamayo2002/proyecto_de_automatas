"""
=============================================================================
app.py — Punto de entrada de la aplicación Flask (servidor backend)
=============================================================================

Propósito:
    Inicializa y configura la aplicación Flask que expone la API REST del
    Simulador AFND. Este archivo es el que se ejecuta directamente para
    levantar el servidor en desarrollo:

        cd Backend
        python app.py

Configuración:
    - Puerto por defecto: 5000  (http://localhost:5000)
    - CORS habilitado para todas las rutas /api/* y todos los orígenes (*),
      lo que permite que el frontend de Vite (localhost:5173) haga peticiones
      al backend sin problemas de política de mismo origen (SOP).
    - Las rutas de la API están definidas en routes/api_routes.py y se
      montan como un Blueprint con prefijo /api.

Endpoint raíz:
    GET /  → Retorna un JSON de comprobación de salud:
             { "status": "ok", "message": "AFND Simulator API v1.0" }
=============================================================================
"""

from flask import Flask
from flask_cors import CORS
from routes.api_routes import api_bp


def create_app():
    """
    Factory function que construye y configura la aplicación Flask.

    Usar una factory en lugar de un módulo global permite crear múltiples
    instancias de la app (útil en tests) sin efectos secundarios.

    Returns:
        app: Instancia configurada de Flask.
    """
    app = Flask(__name__)

    # Habilitar CORS solo en las rutas de la API para permitir peticiones
    # cross-origin desde el frontend (Vite corre en puerto 5173 por defecto)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar el Blueprint con todas las rutas de la API REST
    app.register_blueprint(api_bp)

    @app.route("/")
    def health():
        """Endpoint de comprobación de salud del servidor."""
        return {"status": "ok", "message": "AFND Simulator API v1.0"}

    return app


if __name__ == "__main__":
    # Modo desarrollo: debug=True activa el reloader automático y el debugger
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
