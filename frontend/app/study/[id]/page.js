'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { api, mediaUrl } from '../../../lib/api.js'

function probColor(prob) {
  if (prob >= 0.7) return 'var(--red)'
  if (prob >= 0.5) return '#FF8388'
  return 'var(--amber)'
}

export default function StudyDetail() {
  const { id } = useParams()
  const router = useRouter()
  const [study, setStudy] = useState(null)
  const [error, setError] = useState(null)
  const [activePathology, setActivePathology] = useState(null)
  const [showOverlay, setShowOverlay] = useState(true)

  useEffect(() => {
    setStudy(null)
    api.getStudy(id)
      .then((s) => {
        setStudy(s)
        const heatmapKeys = Object.keys(s.heatmaps || {})
        setActivePathology(heatmapKeys[0] || null)
      })
      .catch((e) => setError(e.message))
  }, [id])

  if (error) return <div className="panel" style={{ padding: 24 }}>Couldn't load this study: {error}</div>
  if (!study) return <div className="loading-panel"><span className="spinner" /></div>

  const heatmapKeys = Object.keys(study.heatmaps || {})
  const allFindings = { ...study.positive_findings, ...study.borderline_findings }
  const sortedFindings = Object.entries(allFindings).sort((a, b) => b[1] - a[1])

  const currentImage = showOverlay && activePathology && study.heatmaps[activePathology]
    ? mediaUrl(study.heatmaps[activePathology])
    : mediaUrl(study.display_path)

  const handleDelete = async () => {
    if (!confirm('Delete this study? This cannot be undone.')) return
    await api.deleteStudy(id)
    router.push('/worklist')
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <Link href="/worklist" className="tag">← Back to worklist</Link>
        <button className="btn btn-ghost" onClick={handleDelete}>Delete study</button>
      </div>

      <div className="grid-2">
        {/* Viewer */}
        <div>
          <div className="viewer-frame">
            <img src={currentImage} alt="chest x-ray" />
          </div>

          <div className="viewer-controls">
            <button
              className={`pathology-chip${!showOverlay ? ' active' : ''}`}
              onClick={() => setShowOverlay(false)}
            >
              Original
            </button>
            {heatmapKeys.map((p) => (
              <button
                key={p}
                className={`pathology-chip${showOverlay && activePathology === p ? ' active' : ''}`}
                onClick={() => { setShowOverlay(true); setActivePathology(p) }}
              >
                {p} — Grad-CAM
              </button>
            ))}
          </div>
          {heatmapKeys.length === 0 && (
            <p style={{ color: 'var(--muted)', fontSize: 12.5, marginTop: 10, fontFamily: 'var(--font-mono)' }}>
              No findings cleared the heatmap threshold — nothing to visualize beyond the original image.
            </p>
          )}
        </div>

        {/* Findings + report */}
        <div>
          <div className="eyebrow">Explainability dashboard</div>
          <h1 className="page-title" style={{ fontSize: 24 }}>
            {study.patient_ref || `Study #${study.id}`}
          </h1>
          <p className="page-sub" style={{ marginBottom: 18 }}>
            {study.modality_note || 'View not specified'} · Model: {study.model_version} · Overall confidence {Math.round(study.overall_confidence * 100)}%
          </p>

          <div className="panel" style={{ padding: '6px 20px', marginBottom: 18 }}>
            <div className="section-title" style={{ fontSize: 14, marginTop: 14 }}>Findings ({sortedFindings.length})</div>
            {sortedFindings.length === 0 && (
              <div style={{ color: 'var(--muted)', fontSize: 13, paddingBottom: 16 }}>No findings above the borderline threshold.</div>
            )}
            {sortedFindings.map(([pathology, prob]) => {
              const positive = study.positive_findings[pathology] !== undefined
              return (
                <div className="finding-row" key={pathology}>
                  <span className={`finding-dot ${positive ? 'positive' : 'borderline'}`} />
                  <span className="finding-name">{pathology}</span>
                  <div className="finding-bar-track">
                    <div className="finding-bar-fill" style={{ width: `${prob * 100}%`, background: probColor(prob) }} />
                  </div>
                  <span className="finding-prob" style={{ color: probColor(prob) }}>{Math.round(prob * 100)}%</span>
                </div>
              )
            })}
          </div>

          <div className="section-title" style={{ fontSize: 14 }}>Draft report</div>
          <div className="report-block">{study.report_text}</div>
        </div>
      </div>
    </div>
  )
}
