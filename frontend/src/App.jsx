import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Upload, FileText, Sparkles, Loader2,
  RotateCcw, CheckCircle2, AlertCircle,
  Lightbulb, Briefcase, ChevronRight
} from 'lucide-react'

/* ─────────────────────────────────────────────────────────────────────────────
   LOADING TICKER
   Cycles through status messages with animated colour transitions
───────────────────────────────────────────────────────────────────────────── */
const TICKER_STEPS = [
  { text: 'Reading your resume…',           color: '#a78bfa' },
  { text: 'Parsing document structure…',    color: '#60a5fa' },
  { text: 'Running compatibility tests…',   color: '#34d399' },
  { text: 'Mapping skills to JD…',          color: '#f59e0b' },
  { text: 'Scoring keyword matches…',       color: '#f472b6' },
  { text: 'Analysing experience gaps…',     color: '#38bdf8' },
  { text: 'Almost done…',                   color: '#a3e635' },
  { text: 'Generating feedback…',           color: '#fb923c' },
  { text: 'Hold on, still working…',        color: '#c084fc' },
  { text: 'Finalising recommendations…',    color: '#2dd4bf' },
]

function LoadingTicker() {
  const [idx, setIdx] = useState(0)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const cycle = () => {
      setVisible(false)
      setTimeout(() => {
        setIdx(i => (i + 1) % TICKER_STEPS.length)
        setVisible(true)
      }, 350)
    }
    const t = setInterval(cycle, 2200)
    return () => clearInterval(t)
  }, [])

  const step = TICKER_STEPS[idx]

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: '52px 20px', gap: 24
    }}>
      {/* Spinner ring */}
      <div style={{ position: 'relative', width: 56, height: 56 }}>
        <svg width="56" height="56" viewBox="0 0 56 56" style={{ position: 'absolute', top: 0, left: 0 }}>
          <circle cx="28" cy="28" r="22" fill="none" stroke="var(--border)" strokeWidth="3" />
        </svg>
        <motion.svg
          width="56" height="56" viewBox="0 0 56 56"
          style={{ position: 'absolute', top: 0, left: 0 }}
          animate={{ rotate: 360 }}
          transition={{ duration: 1.1, repeat: Infinity, ease: 'linear' }}
        >
          <circle
            cx="28" cy="28" r="22" fill="none"
            stroke={step.color} strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="138.2"
            strokeDashoffset="104"
            style={{ transition: 'stroke 0.4s ease' }}
          />
        </motion.svg>
        {/* centre dot */}
        <motion.div
          style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%,-50%)',
            width: 8, height: 8, borderRadius: '50%',
            background: step.color, transition: 'background 0.4s ease'
          }}
          animate={{ scale: [1, 1.4, 1] }}
          transition={{ duration: 1.1, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      {/* Status text */}
      <div style={{ height: 22, overflow: 'hidden', position: 'relative', minWidth: 260, textAlign: 'center' }}>
        <AnimatePresence mode="wait">
          <motion.p
            key={idx}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: visible ? 1 : 0, y: visible ? 0 : -8 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
            style={{
              fontSize: 13, fontWeight: 500,
              color: step.color,
              letterSpacing: '0.01em',
              transition: 'color 0.4s ease',
              whiteSpace: 'nowrap'
            }}
          >
            {step.text}
          </motion.p>
        </AnimatePresence>
      </div>

      {/* Progress dots */}
      <div style={{ display: 'flex', gap: 5 }}>
        {TICKER_STEPS.map((s, i) => (
          <motion.div
            key={i}
            style={{
              width: i === idx ? 16 : 4,
              height: 4, borderRadius: 2,
              background: i === idx ? step.color : 'var(--border-2)',
              transition: 'all 0.35s ease'
            }}
          />
        ))}
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   TEXT PARSER + RENDERER
   Strips ** markdown, renders numbered lists and bullet points properly
───────────────────────────────────────────────────────────────────────────── */
function parseText(raw = '') {
  // Strip bold markers
  const clean = raw.replace(/\*\*(.*?)\*\*/g, '$1').replace(/\*(.*?)\*/g, '$1').trim()

  // Split into lines, collapse blanks
  const lines = clean.split('\n').map(l => l.trim()).filter(Boolean)

  const blocks = []
  for (const line of lines) {
    const numbered = line.match(/^(\d+)[.)]\s+(.+)/)
    const bulleted = line.match(/^[-•*]\s+(.+)/)
    if (numbered) {
      blocks.push({ type: 'numbered', n: numbered[1], text: numbered[2] })
    } else if (bulleted) {
      blocks.push({ type: 'bullet', text: bulleted[1] })
    } else {
      blocks.push({ type: 'para', text: line })
    }
  }
  return blocks
}

/* ─────────────────────────────────────────────────────────────────────────────
   TYPEWRITER — operates on the raw string, renders structured blocks
   progressively as chars are revealed
───────────────────────────────────────────────────────────────────────────── */
function useTypewriter(text, { speed = 12, startDelay = 0, enabled = false } = {}) {
  const [displayed, setDisplayed] = useState('')
  const [done, setDone] = useState(false)
  const rafRef = useRef(null)
  const indexRef = useRef(0)

  useEffect(() => {
    if (!enabled || !text) return
    setDisplayed(''); setDone(false); indexRef.current = 0
    const timer = setTimeout(() => {
      let last = null
      const tick = (ts) => {
        if (!last) last = ts
        const chars = Math.floor((ts - last) / speed)
        if (chars > 0) {
          indexRef.current = Math.min(indexRef.current + chars, text.length)
          setDisplayed(text.slice(0, indexRef.current))
          last = ts
          if (indexRef.current >= text.length) { setDone(true); return }
        }
        rafRef.current = requestAnimationFrame(tick)
      }
      rafRef.current = requestAnimationFrame(tick)
    }, startDelay)
    return () => { clearTimeout(timer); if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [text, speed, startDelay, enabled])

  return { displayed, done }
}

function StructuredText({ text, speed = 12, startDelay = 0, enabled }) {
  const { displayed, done } = useTypewriter(text, { speed, startDelay, enabled })
  const blocks = parseText(displayed)
  const isTyping = enabled && !done

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {blocks.map((b, i) => {
        const isLast = i === blocks.length - 1
        const cursor = isLast && isTyping ? (
          <span style={{
            display: 'inline-block', width: 1.5, height: 12,
            background: 'var(--text-3)', marginLeft: 2,
            verticalAlign: 'middle', animation: 'blink 0.85s step-end infinite'
          }} />
        ) : null

        if (b.type === 'numbered') {
          return (
            <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
              <span style={{
                flexShrink: 0, width: 20, height: 20,
                borderRadius: 5, background: 'var(--surface-2)',
                border: '1px solid var(--border-2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 10, fontWeight: 600, color: 'var(--text-3)',
                marginTop: 2
              }}>{b.n}</span>
              <p style={{ fontSize: 13, lineHeight: 1.75, color: 'var(--text-2)', flex: 1 }}>
                {b.text}{cursor}
              </p>
            </div>
          )
        }

        if (b.type === 'bullet') {
          return (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <span style={{
                flexShrink: 0, width: 5, height: 5,
                borderRadius: '50%', background: 'var(--border-2)',
                marginTop: 8
              }} />
              <p style={{ fontSize: 13, lineHeight: 1.75, color: 'var(--text-2)', flex: 1 }}>
                {b.text}{cursor}
              </p>
            </div>
          )
        }

        return (
          <p key={i} style={{ fontSize: 13, lineHeight: 1.75, color: 'var(--text-2)' }}>
            {b.text}{cursor}
          </p>
        )
      })}

      {/* Show empty cursor while first chars haven't appeared yet */}
      {blocks.length === 0 && isTyping && (
        <span style={{
          display: 'inline-block', width: 1.5, height: 12,
          background: 'var(--text-3)',
          verticalAlign: 'middle', animation: 'blink 0.85s step-end infinite'
        }} />
      )}
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   SCORE RING
───────────────────────────────────────────────────────────────────────────── */
function ScoreRing({ score }) {
  const r = 54
  const circ = 2 * Math.PI * r
  const color = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444'
  const label = score >= 80 ? 'Excellent match' : score >= 60 ? 'Good match' : score >= 40 ? 'Fair match' : 'Needs work'

  return (
    <div style={{ position: 'relative', flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={r} fill="none" stroke="var(--border)" strokeWidth="5" />
        <motion.circle
          cx="70" cy="70" r={r} fill="none"
          stroke={color} strokeWidth="5" strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - (score / 100) * circ }}
          transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
          style={{ transform: 'rotate(-90deg)', transformOrigin: '70px 70px' }}
        />
      </svg>
      <div style={{
        position: 'absolute', top: '50%', left: '50%',
        transform: 'translate(-50%, -58%)',
        display: 'flex', alignItems: 'baseline', gap: 2, lineHeight: 1
      }}>
        <motion.span
          style={{ fontSize: 30, fontWeight: 600, letterSpacing: -1, color, fontVariantNumeric: 'tabular-nums' }}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >{score}</motion.span>
        <span style={{ fontSize: 12, color: 'var(--text-3)' }}>/100</span>
      </div>
      <motion.p
        style={{ fontSize: 11, fontWeight: 500, color, letterSpacing: '0.03em', marginTop: -2 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.85 }}
      >{label}</motion.p>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   RESULT SECTION CARD
───────────────────────────────────────────────────────────────────────────── */
function ResultSection({ icon: Icon, title, accentColor, text, speed, startDelay, enabled, delay }) {
  return (
    <motion.div
      style={{
        background: 'var(--surface)', border: '1px solid var(--border)',
        borderLeft: `2px solid ${accentColor}`,
        borderRadius: 10, overflow: 'hidden'
      }}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    >
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        padding: '12px 16px', borderBottom: '1px solid var(--border)'
      }}>
        <span style={{
          width: 22, height: 22, borderRadius: 5,
          background: 'var(--surface-2)', border: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--text-3)', flexShrink: 0
        }}><Icon size={12} /></span>
        <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--text-3)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
          {title}
        </span>
      </div>
      <div style={{ padding: '16px 16px' }}>
        <StructuredText text={text} speed={speed} startDelay={startDelay} enabled={enabled} />
      </div>
    </motion.div>
  )
}

/* ─────────────────────────────────────────────────────────────────────────────
   MAIN APP
───────────────────────────────────────────────────────────────────────────── */
export default function App() {
  const [file, setFile] = useState(null)
  const [jd, setJd] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [animateText, setAnimateText] = useState(false)

  const handleDrag = (e) => {
    e.preventDefault(); e.stopPropagation()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }
  const handleDrop = (e) => {
    e.preventDefault(); e.stopPropagation()
    setDragActive(false)
    const f = e.dataTransfer.files[0]
    if (f?.name.match(/\.(pdf|docx|txt)$/i)) setFile(f)
  }
  const handleSubmit = async () => {
    if (!file || !jd) return
    setLoading(true); setAnimateText(false)
    const form = new FormData()
    form.append('file', file); form.append('jd_text', jd)
    try {
      const res = await fetch('http://localhost:8000/analyze', { method: 'POST', body: form })
      const data = await res.json()
      setResult(data)
      setTimeout(() => setAnimateText(true), 500)
    } catch (err) { console.error(err) }
    setLoading(false)
  }
  const clearAll = () => { setFile(null); setJd(''); setResult(null); setAnimateText(false) }

  const score = parseInt(result?.match_percentage) || 0
  const SPEED = 10
  const sLen = result?.strengths?.length || 0
  const wLen = result?.weaknesses?.length || 0
  const wDelay  = sLen * SPEED + 400
  const sugDelay = (sLen + wLen) * SPEED + 800

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        :root {
          --bg:        #09090b;
          --surface:   #111113;
          --surface-2: #18181b;
          --border:    #27272a;
          --border-2:  #3f3f46;
          --text-1:    #fafafa;
          --text-2:    #a1a1aa;
          --text-3:    #71717a;
          --font: 'Geist', system-ui, sans-serif;
        }
        body { background: var(--bg); font-family: var(--font); color: var(--text-1); -webkit-font-smoothing: antialiased; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        @keyframes spin   { to { transform: rotate(360deg); } }
        .spin { animation: spin 0.75s linear infinite; }
        textarea:focus { outline: none; border-color: var(--border-2) !important; }
        textarea { transition: border-color 0.15s; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 3px; }
      `}</style>

      <div style={{
        minHeight: '100vh', padding: '52px 20px 80px',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        fontFamily: 'var(--font)'
      }}>

        {/* ── Wordmark ── */}
        <motion.div
          style={{ textAlign: 'center', marginBottom: 36 }}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 9, marginBottom: 8 }}>
            <div style={{
              width: 30, height: 30, borderRadius: 7,
              background: 'var(--surface-2)', border: '1px solid var(--border-2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--text-2)'
            }}><Sparkles size={13} /></div>
            <span style={{ fontSize: 16, fontWeight: 500, letterSpacing: '-0.3px' }}>ResumeAI</span>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-3)' }}>
            Match your resume to any job description
          </p>
        </motion.div>

        <AnimatePresence mode="wait">

          {/* ── Loading overlay ── */}
          {loading && (
            <motion.div
              key="loading"
              style={{ width: '100%', maxWidth: 580 }}
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.97 }}
              transition={{ duration: 0.25 }}
            >
              <div style={{
                background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: 12, overflow: 'hidden'
              }}>
                <LoadingTicker />
              </div>
            </motion.div>
          )}

          {/* ── Input form ── */}
          {!result && !loading && (
            <motion.div
              key="input"
              style={{ width: '100%', maxWidth: 580 }}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.28 }}
            >
              <div style={{
                background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: 12, overflow: 'hidden'
              }}>
                {/* Resume upload */}
                <div style={{ padding: 20, borderBottom: '1px solid var(--border)' }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    fontSize: 11, fontWeight: 500, letterSpacing: '0.07em',
                    textTransform: 'uppercase', color: 'var(--text-3)', marginBottom: 12
                  }}>
                    <FileText size={11} /> Resume
                  </div>
                  <div
                    onDragEnter={handleDrag} onDragLeave={handleDrag}
                    onDragOver={handleDrag} onDrop={handleDrop}
                    style={{
                      position: 'relative',
                      border: `1px ${file ? 'solid' : 'dashed'} ${file ? '#10b98140' : dragActive ? 'var(--border-2)' : 'var(--border)'}`,
                      background: file ? '#10b9810a' : dragActive ? 'var(--surface-2)' : 'transparent',
                      borderRadius: 8, padding: '22px 20px',
                      textAlign: 'center', cursor: 'pointer', transition: 'all 0.15s'
                    }}
                  >
                    <input
                      type="file" accept=".pdf,.docx,.txt"
                      onChange={(e) => setFile(e.target.files[0])}
                      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer', zIndex: 2 }}
                    />
                    <div style={{
                      width: 34, height: 34, borderRadius: 7, margin: '0 auto 10px',
                      background: file ? '#10b9810f' : 'var(--surface-2)',
                      border: `1px solid ${file ? '#10b98130' : 'var(--border)'}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: file ? '#10b981' : 'var(--text-3)'
                    }}>
                      {file ? <FileText size={15} /> : <Upload size={15} />}
                    </div>
                    <p style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-1)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 300, margin: '0 auto 3px' }}>
                      {file ? file.name : 'Drop file or click to browse'}
                    </p>
                    <p style={{ fontSize: 12, color: 'var(--text-3)' }}>
                      {file ? 'Click to replace' : 'PDF, DOCX or TXT'}
                    </p>
                  </div>
                </div>

                {/* JD */}
                <div style={{ padding: 20, borderBottom: '1px solid var(--border)' }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    fontSize: 11, fontWeight: 500, letterSpacing: '0.07em',
                    textTransform: 'uppercase', color: 'var(--text-3)', marginBottom: 12
                  }}>
                    <Briefcase size={11} /> Job description
                  </div>
                  <textarea
                    value={jd}
                    onChange={(e) => setJd(e.target.value)}
                    placeholder="Paste the job description…"
                    style={{
                      width: '100%', minHeight: 130,
                      background: 'var(--surface-2)', border: '1px solid var(--border)',
                      borderRadius: 7, color: 'var(--text-1)',
                      fontFamily: 'var(--font)', fontSize: 13,
                      lineHeight: 1.7, padding: '10px 12px',
                      resize: 'vertical', caretColor: 'var(--text-1)'
                    }}
                  />
                  <p style={{ fontSize: 11, color: 'var(--text-3)', textAlign: 'right', marginTop: 5, fontVariantNumeric: 'tabular-nums' }}>
                    {jd.length} chars
                  </p>
                </div>

                {/* Submit */}
                <div style={{ padding: '14px 20px' }}>
                  <button
                    onClick={handleSubmit}
                    disabled={!file || !jd || loading}
                    style={{
                      width: '100%', height: 38,
                      background: (!file || !jd || loading) ? 'var(--surface-2)' : 'var(--text-1)',
                      color: (!file || !jd || loading) ? 'var(--text-3)' : 'var(--bg)',
                      border: (!file || !jd || loading) ? '1px solid var(--border)' : 'none',
                      borderRadius: 7, fontFamily: 'var(--font)',
                      fontSize: 13, fontWeight: 500,
                      cursor: (!file || !jd || loading) ? 'not-allowed' : 'pointer',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6,
                      transition: 'all 0.15s', letterSpacing: '-0.1px'
                    }}
                  >
                    <Sparkles size={13} /> Analyze resume <ChevronRight size={12} />
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* ── Results ── */}
          {result && !loading && (
            <motion.div
              key="results"
              style={{ width: '100%', maxWidth: 580, display: 'flex', flexDirection: 'column', gap: 10 }}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
            >
              {/* Score card */}
              <div style={{
                background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: 12, padding: '24px 24px 20px',
                display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap'
              }}>
                <ScoreRing score={score} />
                <div style={{ flex: 1, minWidth: 180 }}>
                  <div style={{
                    display: 'inline-flex', alignItems: 'center', gap: 5,
                    fontSize: 11, fontWeight: 500, color: 'var(--text-3)',
                    background: 'var(--surface-2)', border: '1px solid var(--border)',
                    borderRadius: 4, padding: '3px 8px',
                    letterSpacing: '0.04em', textTransform: 'uppercase', marginBottom: 10
                  }}>
                    <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#10b981' }} />
                    Analysis complete
                  </div>
                  <h2 style={{ fontSize: 18, fontWeight: 600, letterSpacing: '-0.4px', marginBottom: 6 }}>
                    Resume reviewed
                  </h2>
                  <p style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.6 }}>
                    Compared against the job description. See the breakdown below.
                  </p>
                </div>
              </div>

              <ResultSection
                icon={CheckCircle2} title="Key strengths" accentColor="#10b981"
                text={result.strengths} speed={SPEED} startDelay={0}
                enabled={animateText} delay={0.08}
              />
              <ResultSection
                icon={AlertCircle} title="Areas to improve" accentColor="#f59e0b"
                text={result.weaknesses} speed={SPEED} startDelay={wDelay}
                enabled={animateText} delay={0.14}
              />
              <ResultSection
                icon={Lightbulb} title="Recommendations" accentColor="#3b82f6"
                text={result.suggestions} speed={SPEED} startDelay={sugDelay}
                enabled={animateText} delay={0.2}
              />

              <motion.button
                onClick={clearAll}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.35 }}
                whileHover={{ borderColor: 'var(--border-2)', color: 'var(--text-2)' }}
                style={{
                  width: '100%', height: 36,
                  background: 'transparent', color: 'var(--text-3)',
                  border: '1px solid var(--border)', borderRadius: 7,
                  fontFamily: 'var(--font)', fontSize: 12, fontWeight: 500,
                  cursor: 'pointer', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', gap: 6,
                  transition: 'all 0.15s'
                }}
              >
                <RotateCcw size={11} /> Analyze another resume
              </motion.button>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </>
  )
}
