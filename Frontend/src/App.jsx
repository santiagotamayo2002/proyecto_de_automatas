import React, { useState, useEffect, useMemo } from 'react'
import { api } from './data/api'
import StateDiagram from './components/StateDiagram'
import TransitionTable from './components/TransitionTable'
import TokenInput from './components/TokenInput'
import SimulationTrace from './components/SimulationTrace'

const AUTOMATA_META = {
  iot: { icon: '📡', color: '#00d4ff' },
  genetica: { icon: '🧬', color: '#a855f7' },
  ecommerce: { icon: '🛒', color: '#00ff88' },
  pagos: { icon: '💳', color: '#ffb300' },
  pedidos: { icon: '📦', color: '#ff5e00' },
  cerradura: { icon: '🔒', color: '#ff0044' },
  ip: { icon: '🌐', color: '#00d4ff' },
  mac: { icon: '🔌', color: '#a855f7' },
}

const S = {
  app: { minHeight: '100vh', padding: '24px 20px', maxWidth: 1100, margin: '0 auto' },
  header: { marginBottom: 32, borderBottom: '1px solid var(--border)', paddingBottom: 20 },
  title: { fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 800, letterSpacing: -1, color: 'var(--text-primary)' },
  subtitle: { fontSize: 12, color: 'var(--text-secondary)', letterSpacing: 2, textTransform: 'uppercase', marginTop: 4 },
  tabs: { display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' },
  tab: (active, color) => ({
    padding: '10px 18px', border: `1px solid ${active ? color : 'var(--border)'}`,
    borderRadius: 'var(--radius)', cursor: 'pointer',
    background: active ? `${color}18` : 'var(--bg-deep)',
    color: active ? color : 'var(--text-secondary)',
    fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: active ? 700 : 400,
    transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: 8,
  }),
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 },
  gridFull: { display: 'grid', gridTemplateColumns: '1fr', gap: 16 },
  card: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: 20, display: 'flex', flexDirection: 'column', gap: 16 },
  cardTitle: { fontSize: 11, letterSpacing: 2, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: 2 },
  badge: (color) => ({ display: 'inline-block', padding: '3px 10px', borderRadius: 4, background: `${color}22`, border: `1px solid ${color}44`, color, fontSize: 11, fontFamily: 'var(--font-mono)', letterSpacing: 1 }),
  info: { display: 'flex', flexDirection: 'column', gap: 8 },
  infoRow: { display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'baseline' },
  infoLabel: { fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 2, minWidth: 70 },
  infoVal: { fontSize: 12, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' },
  loading: { display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 200, color: 'var(--text-muted)', fontSize: 14 },
  error: { color: 'var(--accent-red)', padding: 20, textAlign: 'center' },
  examples: { display: 'flex', flexWrap: 'wrap', gap: 6 },
  exChip: (valid) => ({
    padding: '3px 10px', borderRadius: 4, fontSize: 10,
    background: valid ? 'rgba(0,255,136,0.08)' : 'rgba(255,59,92,0.08)',
    border: `1px solid ${valid ? 'rgba(0,255,136,0.2)' : 'rgba(255,59,92,0.2)'}`,
    color: valid ? 'var(--accent-green)' : 'var(--accent-red)',
    cursor: 'default', fontFamily: 'var(--font-mono)',
  }),
}

export default function App() {
  const [automataList, setAutomataList] = useState(null)
  const [selected, setSelected] = useState('iot')
  const [simResult, setSimResult] = useState(null)
  const [simLoading, setSimLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [activeStates, setActiveStates] = useState([])

  useEffect(() => {
    api.getAutomata()
      .then(d => { setAutomataList(d.automatas); setLoading(false) })
      .catch(() => { setLoadError('No se pudo conectar al backend. Asegúrate de que Flask esté corriendo en el puerto 5000.'); setLoading(false) })
  }, [])

  useEffect(() => { setSimResult(null); setActiveStates([]) }, [selected])

  const definition = automataList?.[selected]

  // Historial ordenado de estados activos (uno por paso de la traza).
  // Para los autómatas IP y MAC se usan para mostrar el camino en el diagrama especializado.
  const stateHistory = useMemo(() => {
    const isLarge = selected === 'ip' || selected === 'mac'
    if (!isLarge || !definition) return []
    if (!simResult || !simResult.trace) return [definition.initial_state]
    // Por cada paso de la traza, tomamos el primer estado de states_after
    // (el más representativo) y lo añadimos si es distinto al anterior.
    const history = [definition.initial_state]
    simResult.trace.forEach(step => {
      if (step.states_after && step.states_after.length > 0) {
        step.states_after.forEach(s => {
          if (history[history.length - 1] !== s) history.push(s)
        })
      }
    })
    return history
  }, [simResult, definition, selected])
  const meta = AUTOMATA_META[selected] || { icon: '⚙', color: '#00d4ff' }

  const handleSimulate = async (tokens) => {
    setSimLoading(true)
    setSimResult(null)
    setActiveStates([])
    try {
      const res = await api.simulate(selected, tokens)
      setSimResult(res)
      // Show final states in diagram
      setActiveStates(res.final_states || [])
    } catch (e) {
      setSimResult({ error: 'Error al conectar con el servidor.', accepted: false, trace: [] })
    } finally {
      setSimLoading(false)
    }
  }

  // Animate through trace steps
  const handleStepView = (step) => {
    if (step?.states_after) setActiveStates(step.states_after)
  }

  if (loading) return <div style={S.loading}>Cargando autómatas...</div>
  if (loadError) return (
    <div style={{ ...S.error, padding: 40 }}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>⚠</div>
      <div>{loadError}</div>
    </div>
  )

  return (
    <div style={S.app}>
      {/* Header */}
      <div style={S.header}>
        <div style={S.title}>Simulador AFND</div>
        <div style={S.subtitle}>Autómatas Finitos No Deterministas — FEIRNNR Computación</div>
      </div>

      {/* Automata tabs */}
      <div style={S.tabs}>
        {Object.keys(automataList).map(key => {
          const m = AUTOMATA_META[key] || { icon: '⚙', color: '#00d4ff' }
          const def = automataList[key]
          return (
            <div key={key} style={S.tab(selected === key, m.color)} onClick={() => setSelected(key)}>
              <span>{m.icon}</span>
              <span>{def.name || key}</span>
            </div>
          )
        })}
      </div>

      {definition && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Info + Diagram */}
          <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 16 }}>
            {/* Definition card */}
            <div style={S.card}>
              <div>
                <div style={S.cardTitle}>Definición Formal</div>
                <div style={{ fontSize: 13, color: meta.color, fontWeight: 700, marginTop: 4 }}>
                  {definition.name}
                </div>
              </div>
              <div style={S.info}>
                <div style={S.infoRow}>
                  <span style={S.infoLabel}>Lenguaje</span>
                  <span style={{ ...S.infoVal, fontSize: 11, color: 'var(--text-secondary)' }}>{definition.language}</span>
                </div>
                <div style={S.infoRow}>
                  <span style={S.infoLabel}>Estados Q</span>
                  <span style={S.infoVal}>{definition.states?.join(', ')}</span>
                </div>
                <div style={S.infoRow}>
                  <span style={S.infoLabel}>Alfabeto Σ</span>
                  <span style={S.infoVal}>{definition.alphabet?.join(', ')}</span>
                </div>
                <div style={S.infoRow}>
                  <span style={S.infoLabel}>Inicial q₀</span>
                  <span style={S.infoVal}>{definition.initial_state}</span>
                </div>
                <div style={S.infoRow}>
                  <span style={S.infoLabel}>Aceptación F</span>
                  <span style={{ ...S.infoVal, color: 'var(--accent-green)' }}>{definition.accept_states?.join(', ')}</span>
                </div>
              </div>
              <div>
                <div style={{ ...S.cardTitle, marginBottom: 8 }}>Ejemplos válidos</div>
                <div style={S.examples}>
                  {definition.examples?.valid?.map((ex, i) => (
                    <span key={i} style={S.exChip(true)}>✓ {ex.join(' ')}</span>
                  ))}
                </div>
                <div style={{ height: 8 }} />
                <div style={{ ...S.cardTitle, marginBottom: 8 }}>Ejemplos inválidos</div>
                <div style={S.examples}>
                  {definition.examples?.invalid?.map((ex, i) => (
                    <span key={i} style={S.exChip(false)}>✗ {ex.join(' ')}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* Diagram */}
            <div style={S.card}>
              <div style={S.cardTitle}>Diagrama de Estados</div>
              <StateDiagram
                definition={definition}
                activeStates={activeStates}
                stateHistory={stateHistory}
                automataKey={selected}
              />
            </div>
          </div>

          {/* Transition Table: hidden for large automata like ip and mac */}
          {selected !== 'ip' && selected !== 'mac' && (
            <div style={S.card}>
              <div style={S.cardTitle}>Tabla de Transiciones δ: Q × Σ → P(Q)</div>
              <TransitionTable definition={definition} activeStates={activeStates} />
            </div>
          )}

          {/* Simulator */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={S.card}>
              <div style={S.cardTitle}>Entrada — Construir cadena</div>
              <TokenInput
                alphabet={definition.alphabet}
                onSimulate={handleSimulate}
                loading={simLoading}
              />
            </div>
            <div style={S.card}>
              <div style={S.cardTitle}>Resultado de la Simulación</div>
              {!simResult && !simLoading && (
                <div style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', padding: 40 }}>
                  Ingresa una cadena y haz clic en Simular
                </div>
              )}
              {simLoading && <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: 40, textAlign: 'center' }}>Procesando...</div>}
              {simResult && (
                <SimulationTrace
                  result={simResult}
                  definition={definition}
                  onStepChange={handleStepView}
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
