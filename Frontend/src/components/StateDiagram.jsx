/**
 * =============================================================================
 * StateDiagram.jsx — Diagrama visual de estados del autómata
 * =============================================================================
 *
 * Propósito:
 *   Renderiza un diagrama SVG interactivo del autómata seleccionado.
 *   Los estados activos se resaltan con brillo (glow) en tiempo real según
 *   avanza la simulación o el usuario navega por la traza de pasos.
 *
 * Modos de renderizado:
 *   1. Renderer genérico (para iot, genetica, ecommerce, pagos, pedidos, cerradura):
 *      Usa posiciones predefinidas en el objeto LAYOUTS para dibujar los estados
 *      como círculos SVG y las transiciones como arcos curvos con flechas.
 *
 *   2. IpStatePath (para 'ip' y 'mac'):
 *      Renderer especializado para autómatas con muchos estados.
 *      En lugar de mostrar todos los nodos a la vez (lo que causaría
 *      superposición), muestra SOLO los últimos 5 estados del historial
 *      de la simulación en un carril horizontal limpio con flechas entre ellos.
 *      Los estados más antiguos aparecen más transparentes.
 *      El estado de aceptación activo muestra un badge "✓ ACEPTA".
 *
 * Props:
 *   definition    {Object}   - Definición formal del autómata (de la API).
 *   activeStates  {string[]} - Estados activos en el paso actual de la simulación.
 *   stateHistory  {string[]} - Historial ordenado de estados visitados (para ip/mac).
 *   automataKey   {string}   - Clave del autómata activo (ej: "ip", "iot", "mac").
 *
 * Elementos visuales:
 *   → Flecha entrante al estado inicial.
 *   ○○ Doble círculo para estados de aceptación (F).
 *   ✦ Efecto glow en estados activos.
 *   ··· Indicador de que hay estados anteriores fuera de la ventana de 5 (ip/mac).
 * =============================================================================
 */
import React, { useMemo } from 'react'

// Layout positions for each automaton's states (not used for 'ip')
const LAYOUTS = {
  iot: {
    q0: { x: 80, y: 150 }, q1: { x: 240, y: 150 }, q2: { x: 400, y: 150 }, q3: { x: 560, y: 150 },
  },
  genetica: {
    q0: { x: 70, y: 150 }, q1: { x: 200, y: 150 }, q2: { x: 330, y: 150 },
    q3: { x: 460, y: 220 }, q4: { x: 560, y: 150 },
  },
  ecommerce: {
    q0: { x: 80, y: 150 }, q1: { x: 240, y: 150 }, q2: { x: 400, y: 150 }, q3: { x: 560, y: 150 },
  },
  pagos: {
    inicial: { x: 80, y: 150 }, autorizado: { x: 210, y: 150 }, capturado: { x: 340, y: 150 },
    completado: { x: 470, y: 150 }, cancelado: { x: 210, y: 240 }, error: { x: 470, y: 240 },
  },
  pedidos: {
    q_init: { x: 50, y: 150 }, q_cre: { x: 150, y: 150 }, q_emp: { x: 250, y: 150 },
    q_env: { x: 350, y: 150 }, q_ent: { x: 450, y: 150 }, q_dev: { x: 550, y: 150 },
    q_can: { x: 200, y: 250 },
  },
  cerradura: {
    q0: { x: 80, y: 100 }, q1: { x: 220, y: 100 }, q2: { x: 360, y: 100 },
    q3: { x: 500, y: 100 }, q4: { x: 290, y: 220 }, block: { x: 620, y: 100 },
  },
}

const R = 36

function arc(x1, y1, x2, y2) {
  const dx = x2 - x1, dy = y2 - y1
  const dist = Math.sqrt(dx * dx + dy * dy)
  const ux = dx / dist, uy = dy / dist
  const nx = -uy
  const cx = (x1 + x2) / 2 + nx * 40
  const cy = (y1 + y2) / 2 + (ux) * 40
  return `M ${x1 + ux * R} ${y1 + uy * R} Q ${cx} ${cy} ${x2 - ux * R} ${y2 - uy * R}`
}

function selfLoop(x, y) {
  return `M ${x - 10} ${y - R} C ${x - 50} ${y - 90} ${x + 50} ${y - 90} ${x + 10} ${y - R}`
}

// ─── Componente especial para el autómata IP ──────────────────────────────────
// Muestra en un carril horizontal los últimos 5 estados por donde ha pasado el
// autómata, con flechas entre ellos. Limpio, legible y sin superposición.
function IpStatePath({ activeStates, stateHistory, accept_states, state_labels, placeholder }) {
  const MAX = 5
  const last5 = stateHistory.slice(-MAX)
  const ph = placeholder || { emoji: '🌐', text: 'Ingresa una cadena para ver los estados' }

  if (last5.length === 0) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: 180, color: 'var(--text-muted)', fontSize: 13,
        fontFamily: 'var(--font-mono)', flexDirection: 'column', gap: 8,
      }}>
        <span style={{ fontSize: 28 }}>{ph.emoji}</span>
        <span>{ph.text}</span>
      </div>
    )
  }

  const NODE_R = 38
  const SPACING = 118
  const SVG_H = 200
  const total = last5.length
  const SVG_W = Math.max(380, total * SPACING + 60)
  const CY = SVG_H / 2

  // Posición X del i-ésimo nodo, centrado en el SVG
  const nodeX = (i) => {
    const totalWidth = (total - 1) * SPACING
    const startX = (SVG_W - totalWidth) / 2
    return startX + i * SPACING
  }

  return (
    <div style={{
      background: 'var(--bg-deep)', border: '1px solid var(--border)',
      borderRadius: 'var(--radius)', padding: '8px', overflow: 'auto',
    }}>
      <svg viewBox={`0 0 ${SVG_W} ${SVG_H}`} width="100%" style={{ minWidth: 320 }}>
        <defs>
          <marker id="ip-arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#2a4070" />
          </marker>
          <marker id="ip-arrow-active" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#00d4ff" />
          </marker>
          <marker id="ip-arrow-accept" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#00ff88" />
          </marker>
          <filter id="ip-glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Indicador "···" si hay estados anteriores fuera de la ventana */}
        {stateHistory.length > MAX && (
          <text x="8" y={CY} fill="#3d5470" fontSize="22"
            fontFamily="JetBrains Mono" dominantBaseline="middle">···</text>
        )}

        {/* Flechas entre nodos consecutivos */}
        {last5.map((s, i) => {
          if (i === 0) return null
          const x1 = nodeX(i - 1)
          const x2 = nodeX(i)
          const isAcc = accept_states.includes(s)
          const isAct = activeStates.includes(s)
          const arrowColor = isAcc ? '#00ff88' : (isAct ? '#00d4ff' : '#2a4070')
          const markerId = isAcc ? 'ip-arrow-accept' : (isAct ? 'ip-arrow-active' : 'ip-arrow')
          return (
            <line key={`e-${i}`}
              x1={x1 + NODE_R} y1={CY} x2={x2 - NODE_R - 2} y2={CY}
              stroke={arrowColor} strokeWidth={isAct ? 2 : 1.5}
              markerEnd={`url(#${markerId})`}
              filter={isAct ? 'url(#ip-glow)' : undefined}
              style={{ transition: 'stroke 0.3s' }}
            />
          )
        })}

        {/* Nodos de estado */}
        {last5.map((s, i) => {
          const cx = nodeX(i)
          const isAct = activeStates.includes(s)
          const isAcc = accept_states.includes(s)
          const fillColor = isAct ? (isAcc ? '#00ff88' : '#00d4ff') : (isAcc ? '#00ff8844' : 'transparent')
          const strokeColor = isAct ? (isAcc ? '#00ff88' : '#00d4ff') : '#2a4070'
          const textColor = isAct ? (isAcc ? '#00ff88' : '#00d4ff') : '#7a9cc0'
          const label = state_labels[s] || ''
          // Los estados más antiguos aparecen más transparentes
          const opacity = 0.35 + 0.65 * (i / Math.max(1, last5.length - 1))

          return (
            <g key={s} transform={`translate(${cx}, ${CY})`}
              style={{ opacity, transition: 'opacity 0.4s' }}>
              {/* Doble círculo para estado de aceptación */}
              {isAcc && (
                <circle r={NODE_R + 6} fill="none"
                  stroke={isAct ? '#00ff88' : '#1e3a2a'} strokeWidth={1.5}
                  style={{ transition: 'stroke 0.3s' }}
                />
              )}
              {/* Círculo principal */}
              <circle r={NODE_R}
                fill={fillColor} fillOpacity={isAct ? 0.18 : 0.06}
                stroke={strokeColor} strokeWidth={isAct ? 2.5 : 1.5}
                filter={isAct ? 'url(#ip-glow)' : undefined}
                style={{ transition: 'all 0.3s' }}
              />
              {/* Nombre del estado */}
              <text textAnchor="middle" dominantBaseline="middle" y={label ? -8 : 0}
                fill={textColor} fontSize="13" fontWeight="700"
                fontFamily="JetBrains Mono" style={{ transition: 'fill 0.3s' }}>
                {s}
              </text>
              {/* Etiqueta descriptiva */}
              {label && (
                <text textAnchor="middle" dominantBaseline="middle" y={8}
                  fill={isAct ? '#ffffff88' : '#3d5470'}
                  fontSize="7" fontFamily="Syne" style={{ transition: 'fill 0.3s' }}>
                  {label}
                </text>
              )}
              {/* Badge "✓ ACEPTA" bajo el estado de aceptación activo */}
              {isAcc && isAct && (
                <text textAnchor="middle" y={NODE_R + 18}
                  fill="#00ff88" fontSize="9" fontWeight="700" fontFamily="JetBrains Mono">
                  ✓ ACEPTA
                </text>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}
// ─────────────────────────────────────────────────────────────────────────────

export default function StateDiagram({ definition, activeStates = [], stateHistory = [], automataKey }) {
  const layout = LAYOUTS[automataKey] || {}
  const { states = [], transitions = {}, initial_state, accept_states = [], state_labels = {} } = definition

  // Para los autómatas IP y MAC usamos el renderer especializado de camino lineal
  if (automataKey === 'ip' || automataKey === 'mac') {
    // Personaliza el mensaje de placeholder según el autómata
    const placeholder = automataKey === 'mac'
      ? { emoji: '🔌', text: 'Ingresa una dirección MAC para ver los estados' }
      : { emoji: '🌐', text: 'Ingresa una dirección IP para ver los estados' }
    return (
      <IpStatePath
        activeStates={activeStates}
        stateHistory={stateHistory}
        accept_states={accept_states}
        state_labels={state_labels}
        placeholder={placeholder}
      />
    )
  }

  // ── Renderer genérico para los demás autómatas ──
  const edges = []
  const edgeMap = {}
  for (const [from, trans] of Object.entries(transitions)) {
    for (const [token, targets] of Object.entries(trans)) {
      for (const to of targets) {
        const key = `${from}→${to}`
        if (!edgeMap[key]) edgeMap[key] = { from, to, tokens: [] }
        edgeMap[key].tokens.push(token)
      }
    }
  }
  for (const edge of Object.values(edgeMap)) edges.push(edge)

  const isActive = (s) => activeStates.includes(s)
  const isAccept = (s) => accept_states.includes(s)

  return (
    <div style={{ background: 'var(--bg-deep)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '8px', overflow: 'auto' }}>
      <svg viewBox="0 0 650 300" width="100%" style={{ minWidth: 500 }}>
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#2a4070" />
          </marker>
          <marker id="arrow-active" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#00d4ff" />
          </marker>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {edges.map(({ from, to, tokens }) => {
          const p1 = layout[from], p2 = layout[to]
          if (!p1 || !p2) return null
          const isSelf = from === to
          const active = isActive(from) && isActive(to)
          const color = active ? '#00d4ff' : '#2a4070'
          const label = tokens.join(', ')
          const d = isSelf ? selfLoop(p1.x, p1.y) : arc(p1.x, p1.y, p2.x, p2.y)
          const lx = (p1.x + p2.x) / 2
          const ly = isSelf ? p1.y - 72 : (p1.y + p2.y) / 2 - 28
          return (
            <g key={`${from}-${to}`}>
              <path d={d} fill="none" stroke={color}
                strokeWidth={active ? 2 : 1.5}
                markerEnd={`url(#${active ? 'arrow-active' : 'arrow'})`}
                filter={active ? 'url(#glow)' : undefined}
                style={{ transition: 'stroke 0.3s, stroke-width 0.3s' }}
              />
              <text x={lx} y={ly} textAnchor="middle"
                fill={active ? '#00d4ff' : '#7a9cc0'}
                fontSize="10" fontFamily="JetBrains Mono"
                style={{ transition: 'fill 0.3s' }}>
                {label}
              </text>
            </g>
          )
        })}

        {states.map((s) => {
          const pos = layout[s]
          if (!pos) return null
          const active = isActive(s)
          const accept = isAccept(s)
          const isInit = s === initial_state
          const color = active ? (accept ? '#00ff88' : '#00d4ff') : (accept ? '#00ff8844' : 'transparent')
          const stroke = active ? (accept ? '#00ff88' : '#00d4ff') : '#2a4070'
          return (
            <g key={s} transform={`translate(${pos.x}, ${pos.y})`}>
              {isInit && (
                <line x1={-R - 28} y1={0} x2={-R - 4} y2={0}
                  stroke="#2a4070" strokeWidth={1.5} markerEnd="url(#arrow)" />
              )}
              {accept && (
                <circle r={R + 6} fill="none"
                  stroke={active ? '#00ff88' : '#1e3a2a'} strokeWidth={1.5}
                  style={{ transition: 'stroke 0.3s' }}
                />
              )}
              <circle r={R} fill={color} fillOpacity={active ? 0.15 : 0.05}
                stroke={stroke} strokeWidth={active ? 2 : 1.5}
                filter={active ? 'url(#glow)' : undefined}
                style={{ transition: 'all 0.3s' }}
              />
              <text textAnchor="middle" dominantBaseline="middle" y={-6}
                fill={active ? (accept ? '#00ff88' : '#00d4ff') : '#7a9cc0'}
                fontSize="13" fontWeight="600" fontFamily="JetBrains Mono"
                style={{ transition: 'fill 0.3s' }}>
                {s}
              </text>
              <text textAnchor="middle" dominantBaseline="middle" y={9}
                fill={active ? '#ffffff88' : '#3d5470'} fontSize="8" fontFamily="Syne"
                style={{ transition: 'fill 0.3s' }}>
                {state_labels[s] || ''}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
