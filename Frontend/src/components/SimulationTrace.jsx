/**
 * =============================================================================
 * SimulationTrace.jsx — Visualizador de la traza de ejecución del AFND
 * =============================================================================
 *
 * Propósito:
 *   Muestra el resultado de una simulación AFND de forma interactiva y
 *   paso a paso. Permite al usuario navegar por cada transición que ejecutó
 *   el autómata, ver qué estados estaban activos antes y después de consumir
 *   cada token, y conocer el veredicto final (ACEPTADA / RECHAZADA).
 *
 * Props:
 *   result       {Object}   - Respuesta del endpoint POST /api/simulate/<key>.
 *                             Contiene: accepted, trace[], final_states, result_message, error.
 *   definition   {Object}   - Definición del autómata actual (para conocer accept_states).
 *   onStepChange {Function} - Callback invocado cuando el usuario navega a un paso distinto.
 *                             Recibe el objeto del paso actual { step, token, states_after, ... }.
 *                             El componente padre (App.jsx) lo usa para actualizar el
 *                             diagrama de estados con los estados activos de ese paso.
 *
 * Comportamiento:
 *   1. Al recibir un nuevo `result`, reinicia el paso actual a 0 (useEffect).
 *   2. Cada cambio de paso notifica a App.jsx vía onStepChange (useEffect).
 *   3. Muestra un banner de resultado (verde=ACEPTADA, rojo=RECHAZADA).
 *   4. Permite navegar con botones ⏮ ◀ ▶ ⏭ entre todos los pasos de la traza.
 *   5. El paso actual se detalla con token consumido, estados antes/después y descripción.
 *   6. Todos los pasos están listados debajo y son clicables individualmente.
 * =============================================================================
 */
import React, { useState } from 'react'

const S = {
  wrap: { display: 'flex', flexDirection: 'column', gap: 12 },
  result: (accepted) => ({
    padding: '14px 20px',
    borderRadius: 'var(--radius)',
    border: `1px solid ${accepted ? 'var(--accent-green)' : 'var(--accent-red)'}`,
    background: accepted ? 'rgba(0,255,136,0.06)' : 'rgba(255,59,92,0.06)',
    color: accepted ? 'var(--accent-green)' : 'var(--accent-red)',
    fontFamily: 'var(--font-mono)', fontSize: 14, fontWeight: 700,
    letterSpacing: 1, display: 'flex', alignItems: 'center', gap: 12,
  }),
  icon: { fontSize: 22 },
  traceHeader: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    fontSize: 11, letterSpacing: 2, color: 'var(--text-secondary)',
    textTransform: 'uppercase', marginBottom: 4,
  },
  steps: { display: 'flex', flexDirection: 'column', gap: 4 },
  step: (isActive, isFirst) => ({
    padding: '10px 14px',
    borderRadius: 6,
    border: `1px solid ${isActive ? 'var(--border-bright)' : 'var(--border)'}`,
    background: isActive ? 'var(--bg-panel)' : 'var(--bg-deep)',
    cursor: 'pointer', transition: 'all 0.2s',
    animation: 'fadeSlideIn 0.25s ease forwards',
    animationDelay: isFirst ? '0ms' : '0ms',
  }),
  stepRow: { display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' },
  stepNum: { fontSize: 10, color: 'var(--text-muted)', minWidth: 24 },
  token: {
    padding: '2px 8px', borderRadius: 4,
    background: 'rgba(255,179,64,0.12)', border: '1px solid rgba(255,179,64,0.3)',
    color: 'var(--accent-amber)', fontSize: 11, fontWeight: 600,
  },
  states: { display: 'flex', gap: 4, flexWrap: 'wrap' },
  stateChip: (accept) => ({
    padding: '2px 8px', borderRadius: 4, fontSize: 11,
    background: accept ? 'rgba(0,255,136,0.12)' : 'rgba(0,212,255,0.1)',
    border: `1px solid ${accept ? 'rgba(0,255,136,0.3)' : 'rgba(0,212,255,0.3)'}`,
    color: accept ? 'var(--accent-green)' : 'var(--accent-cyan)',
    fontWeight: 600,
  }),
  desc: { fontSize: 11, color: 'var(--text-muted)', marginTop: 4, fontFamily: 'var(--font-mono)' },
  arrow: { color: 'var(--text-muted)', fontSize: 14 },
  emptyState: { color: 'var(--accent-red)', fontSize: 11, fontStyle: 'italic' },
  navRow: { display: 'flex', gap: 8, alignItems: 'center' },
  navBtn: (disabled) => ({
    padding: '4px 12px', border: '1px solid var(--border)', borderRadius: 4,
    background: 'var(--bg-deep)', color: disabled ? 'var(--text-muted)' : 'var(--text-secondary)',
    cursor: disabled ? 'not-allowed' : 'pointer', fontSize: 12, fontFamily: 'var(--font-mono)',
    opacity: disabled ? 0.4 : 1,
  }),
  progress: { fontSize: 11, color: 'var(--text-muted)' },
}

export default function SimulationTrace({ result, definition, onStepChange }) {
  const [currentStep, setCurrentStep] = useState(0)

  React.useEffect(() => {
    setCurrentStep(0)
  }, [result])

  React.useEffect(() => {
    if (result && result.trace && onStepChange) {
      onStepChange(result.trace[currentStep])
    }
  }, [currentStep, result, onStepChange])

  if (!result) return null

  const { trace = [], accepted, result_message, error } = result
  const { accept_states = [] } = definition

  if (error) return (
    <div style={{ padding: 16, color: 'var(--accent-red)', background: 'rgba(255,59,92,0.08)', borderRadius: 8, fontSize: 13 }}>
      ⚠ {error}
    </div>
  )

  const totalSteps = trace.length
  const step = trace[currentStep]

  return (
    <div style={S.wrap}>
      {/* Result banner */}
      <div style={S.result(accepted)}>
        <span style={S.icon}>{accepted ? '✓' : '✗'}</span>
        <span>{result_message}</span>
      </div>

      {/* Step navigator */}
      <div style={S.traceHeader}>
        <span>Traza de ejecución</span>
        <div style={S.navRow}>
          <button style={S.navBtn(currentStep === 0)} onClick={() => setCurrentStep(0)} disabled={currentStep === 0}>⏮</button>
          <button style={S.navBtn(currentStep === 0)} onClick={() => setCurrentStep(s => Math.max(0, s - 1))} disabled={currentStep === 0}>◀</button>
          <span style={S.progress}>{currentStep + 1} / {totalSteps}</span>
          <button style={S.navBtn(currentStep === totalSteps - 1)} onClick={() => setCurrentStep(s => Math.min(totalSteps - 1, s + 1))} disabled={currentStep === totalSteps - 1}>▶</button>
          <button style={S.navBtn(currentStep === totalSteps - 1)} onClick={() => setCurrentStep(totalSteps - 1)} disabled={currentStep === totalSteps - 1}>⏭</button>
        </div>
      </div>

      {/* Current step detail */}
      {step && (
        <div style={{ padding: '14px 16px', background: 'var(--bg-panel)', border: '1px solid var(--border-bright)', borderRadius: 8 }}>
          <div style={S.stepRow}>
            <span style={{ ...S.stepNum, color: 'var(--accent-purple)', fontSize: 13 }}>Paso {step.step}</span>
            {step.token && <><span style={S.token}>{step.token}</span><span style={S.arrow}>→</span></>}
            <div style={S.states}>
              {step.states_after.length === 0
                ? <span style={S.emptyState}>∅ (sin estados)</span>
                : step.states_after.map(s => (
                  <span key={s} style={S.stateChip(accept_states.includes(s))}>{s}</span>
                ))}
            </div>
          </div>
          <div style={S.desc}>{step.description}</div>
        </div>
      )}

      {/* Full trace */}
      <div style={S.traceHeader}><span>Todos los pasos</span></div>
      <div style={S.steps}>
        {trace.map((s, i) => (
          <div key={i} style={S.step(i === currentStep, i === 0)} onClick={() => setCurrentStep(i)}>
            <div style={S.stepRow}>
              <span style={S.stepNum}>{s.step}</span>
              {s.token
                ? <><span style={S.token}>{s.token}</span><span style={S.arrow}>→</span></>
                : <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>inicio</span>}
              <div style={S.states}>
                {s.states_after.length === 0
                  ? <span style={S.emptyState}>∅</span>
                  : s.states_after.map(st => (
                    <span key={st} style={S.stateChip(accept_states.includes(st))}>{st}</span>
                  ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
