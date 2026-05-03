/**
 * =============================================================================
 * api.js — Cliente HTTP del frontend para comunicarse con el backend Flask
 * =============================================================================
 *
 * Propósito:
 *   Centraliza todas las llamadas HTTP hacia la API REST del backend.
 *   Exporta un objeto `api` con métodos asíncronos que corresponden a
 *   cada endpoint disponible. Los componentes React importan este objeto
 *   en lugar de usar fetch/axios directamente.
 *
 * Rutas consumidas:
 *   GET  /api/automatas          → Lista todos los autómatas y sus definiciones.
 *   GET  /api/automatas/<key>    → Obtiene la definición de un autómata específico.
 *   POST /api/simulate/<key>     → Ejecuta la simulación con los tokens dados.
 *
 * La URL base "/api" se resuelve según la configuración del proxy de Vite
 * (vite.config.js), que redirige las peticiones al backend en localhost:5000.
 * =============================================================================
 */

import axios from 'axios'

/** Prefijo base de todos los endpoints de la API */
const BASE = '/api'

export const api = {
  /**
   * Obtiene la lista de todos los autómatas disponibles con sus definiciones.
   * Se llama una vez al montar el componente App para poblar las pestañas.
   *
   * @returns {Promise<{success: boolean, automatas: Object}>}
   */
  async getAutomata() {
    const { data } = await axios.get(`${BASE}/automatas`)
    return data
  },

  /**
   * Obtiene la definición formal de un autómata concreto por su clave.
   *
   * @param {string} key - Clave del autómata (ej: "ip", "mac", "iot").
   * @returns {Promise<{success: boolean, automata: Object}>}
   */
  async getDefinition(key) {
    const { data } = await axios.get(`${BASE}/automatas/${key}`)
    return data
  },

  /**
   * Envía los tokens al backend para simular el autómata indicado.
   * Los tokens se envían como lista de strings en el cuerpo JSON.
   *
   * @param {string} key      - Clave del autómata a simular.
   * @param {string[]} tokens - Lista de tokens del alfabeto.
   * @returns {Promise<{success, accepted, trace, final_states, result_message}>}
   */
  async simulate(key, tokens) {
    const { data } = await axios.post(`${BASE}/simulate/${key}`, { tokens })
    return data
  }
}
