/**
 * =============================================================================
 * TransitionTable.jsx — Tabla de transiciones δ: Q × Σ → P(Q)
 * =============================================================================
 *
 * Propósito:
 *   Renderiza la función de transición de un autómata como una tabla HTML
 *   clásica, donde las filas son los estados Q y las columnas son los
 *   símbolos del alfabeto Σ. Cada celda muestra el conjunto de estados
 *   alcanzables (notación de conjuntos: {q1, q2} o ∅ si no hay transición).
 *
 * Props:
 *   definition    {Object} - Definición formal del autómata (de la API).
 *                            Contiene: states, alphabet, transitions,
 *                            accept_states, initial_state.
 *   activeStates  {string[]} - Lista de estados actualmente activos en la
 *                              simulación. Se resaltan en la tabla.
 *
 * Comportamiento visual:
 *   - Las filas de estados activos se resaltan en azul cyan.
 *   - Los estados de aceptación (F) se marcan con un asterisco (*).
 *   - El estado inicial (q0) se marca con una flecha (→).
 *   - Las celdas sin transición muestran ∅ (conjunto vacío).
 *
 * Nota:
 *   Este componente NO se renderiza para los autómatas 'ip' y 'mac' porque
 *   tienen demasiados estados (48 y 36 respectivamente). El filtrado se
 *   controla en App.jsx mediante la condición `selected !== 'ip'`.
 * =============================================================================
 */
import React from 'react'

const S = {
  wrap: { overflowX: 'auto' },
  table: {
    width: '100%', borderCollapse: 'collapse',
    fontFamily: 'var(--font-mono)', fontSize: 13,
  },
  th: {
    padding: '8px 16px', textAlign: 'center',
    background: 'var(--bg-deep)', color: 'var(--accent-cyan)',
    borderBottom: '1px solid var(--border-bright)',
    fontSize: 11, letterSpacing: 2, textTransform: 'uppercase',
  },
  thState: {
    padding: '8px 16px', textAlign: 'left',
    background: 'var(--bg-deep)', color: 'var(--text-secondary)',
    borderBottom: '1px solid var(--border-bright)',
    fontSize: 11, letterSpacing: 2, textTransform: 'uppercase',
  },
  td: (active) => ({
    padding: '10px 16px', textAlign: 'center',
    borderBottom: '1px solid var(--border)',
    color: active ? 'var(--accent-green)' : 'var(--text-secondary)',
    fontWeight: active ? 700 : 400,
    transition: 'all 0.3s',
    background: active ? 'rgba(0,255,136,0.04)' : 'transparent',
  }),
  tdState: (active, isAccept) => ({
    padding: '10px 16px', textAlign: 'left',
    borderBottom: '1px solid var(--border)',
    color: active ? 'var(--accent-cyan)' : isAccept ? 'var(--accent-green)' : 'var(--text-primary)',
    fontWeight: active ? 700 : 600,
    background: active ? 'rgba(0,212,255,0.06)' : 'transparent',
    transition: 'all 0.3s',
  }),
}

/**
 * Tabla de transiciones para visualizar la función δ de un AFND.
 *
 * @param {Object}   props
 * @param {Object}   props.definition    - Definición del autómata (states, alphabet, etc.).
 * @param {string[]} props.activeStates  - Estados actualmente activos (resaltados).
 */
export default function TransitionTable({ definition, activeStates = [] }) {
  const { states = [], alphabet = [], transitions = {}, accept_states = [], initial_state } = definition

  const getCell = (state, token) => {
    const targets = transitions[state]?.[token]
    if (!targets || targets.length === 0) return '∅'
    return `{${targets.join(', ')}}`
  }

  return (
    <div style={S.wrap}>
      <table style={S.table}>
        <thead>
          <tr>
            <th style={S.thState}>Estado</th>
            {alphabet.map(t => <th key={t} style={S.th}>{t}</th>)}
          </tr>
        </thead>
        <tbody>
          {states.map(s => {
            const active = activeStates.includes(s)
            const isAccept = accept_states.includes(s)
            const isInit = s === initial_state
            return (
              <tr key={s}>
                <td style={S.tdState(active, isAccept)}>
                  {isInit ? '→ ' : '   '}
                  {isAccept ? '* ' : '  '}
                  {s}
                </td>
                {alphabet.map(t => (
                  <td key={t} style={S.td(active)}>
                    {getCell(s, t)}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
