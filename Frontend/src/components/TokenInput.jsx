/**
 * =============================================================================
 * TokenInput.jsx — Panel de construcción de la cadena de entrada
 * =============================================================================
 *
 * Propósito:
 *   Permite al usuario construir la cadena de tokens que será simulada por
 *   el autómata. Muestra el alfabeto del autómata actual como botones clicables;
 *   cada clic agrega el token al final de la cadena en construcción.
 *
 * Props:
 *   alphabet    {string[]} - Lista de símbolos del alfabeto del autómata activo.
 *                            Proviene de `definition.alphabet` (retornado por la API).
 *   onSimulate  {Function} - Callback invocado al presionar "Simular". Recibe la
 *                            lista de tokens seleccionados como argumento.
 *   loading     {boolean}  - Si es true, deshabilita el botón de simular y
 *                            muestra "Simulando..." mientras espera la respuesta.
 *
 * Comportamiento:
 *   - Clic en un chip del alfabeto → agrega el token a la cadena.
 *   - Clic en × en un token → lo elimina de la cadena.
 *   - Botón "Limpiar" → resetea la cadena a vacío.
 *   - Botón "Simular" → valida que haya al menos un token y llama a onSimulate.
 * =============================================================================
 */
import React, { useState } from 'react'

const S = {
  wrap: { display: 'flex', flexDirection: 'column', gap: 12 },
  label: { fontSize: 11, letterSpacing: 2, color: 'var(--text-secondary)', textTransform: 'uppercase' },
  chips: { display: 'flex', flexWrap: 'wrap', gap: 8 },
  chip: (active) => ({
    padding: '6px 14px', border: `1px solid ${active ? 'var(--accent-cyan)' : 'var(--border)'}`,
    borderRadius: 4, cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: 12,
    color: active ? 'var(--accent-cyan)' : 'var(--text-secondary)',
    background: active ? 'rgba(0,212,255,0.1)' : 'var(--bg-deep)',
    transition: 'all 0.15s', userSelect: 'none',
  }),
  tokens: { display: 'flex', flexWrap: 'wrap', gap: 6, minHeight: 40, alignItems: 'center' },
  token: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '4px 10px', background: 'var(--bg-panel)',
    border: '1px solid var(--border-bright)', borderRadius: 4,
    fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--accent-amber)',
  },
  removeBtn: {
    background: 'none', border: 'none', cursor: 'pointer',
    color: 'var(--text-muted)', fontSize: 14, lineHeight: 1,
    padding: '0 2px', display: 'flex', alignItems: 'center',
  },
  row: { display: 'flex', gap: 8 },
  btn: (primary) => ({
    flex: primary ? 1 : 'none',
    padding: '10px 20px', border: 'none', borderRadius: 'var(--radius)',
    cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: 12,
    fontWeight: 600, letterSpacing: 1, textTransform: 'uppercase',
    background: primary ? 'var(--accent-cyan)' : 'var(--bg-panel)',
    color: primary ? '#050810' : 'var(--text-secondary)',
    transition: 'all 0.15s',
    border: primary ? 'none' : '1px solid var(--border)',
  }),
  error: { fontSize: 12, color: 'var(--accent-red)', padding: '8px 12px', background: 'rgba(255,59,92,0.08)', borderRadius: 4 }
}

export default function TokenInput({ alphabet, onSimulate, loading }) {
  const [selected, setSelected] = useState([])
  const [error, setError] = useState('')

  const add = (token) => {
    setSelected(prev => [...prev, token])
    setError('')
  }

  const remove = (i) => setSelected(prev => prev.filter((_, idx) => idx !== i))

  const clear = () => { setSelected([]); setError('') }

  const run = () => {
    if (selected.length === 0) { setError('Agrega al menos un token.'); return }
    onSimulate(selected)
  }

  return (
    <div style={S.wrap}>
      <div>
        <div style={S.label}>Alfabeto — haz clic para agregar tokens</div>
        <div style={{ height: 8 }} />
        <div style={S.chips}>
          {alphabet.map(t => (
            <div key={t} style={S.chip(false)} onClick={() => add(t)}>{t}</div>
          ))}
        </div>
      </div>

      <div>
        <div style={S.label}>Cadena de entrada</div>
        <div style={{ height: 8 }} />
        <div style={S.tokens}>
          {selected.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>Vacío — agrega tokens arriba</span>}
          {selected.map((t, i) => (
            <div key={i} style={S.token}>
              {t}
              <button style={S.removeBtn} onClick={() => remove(i)}>×</button>
            </div>
          ))}
        </div>
      </div>

      {error && <div style={S.error}>{error}</div>}

      <div style={S.row}>
        <button style={S.btn(true)} onClick={run} disabled={loading}>
          {loading ? 'Simulando...' : '▶ Simular'}
        </button>
        <button style={S.btn(false)} onClick={clear}>Limpiar</button>
      </div>
    </div>
  )
}
