'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api, mediaUrl } from '../../lib/api.js'

function severity(study) {
  const posCount = Object.keys(study.positive_findings || {}).length
  if (posCount === 0) return { label: 'No findings', cls: 'normal' }
  if (study.overall_confidence >= 0.85) return { label: 'Flagged', cls: 'flagged' }
  return { label: 'Borderline', cls: 'borderline' }
}

export default function Worklist() {
  const [studies, setStudies] = useState(null)

  useEffect(() => {
    api.listStudies().then(setStudies).catch(() => setStudies([]))
  }, [])

  return (
    <div>
      <div className="eyebrow">Worklist</div>
      <h1 className="page-title">All studies</h1>
      <p className="page-sub">Every chest X-ray processed through the pipeline, ranked most recent first.</p>

      {studies === null && <div className="loading-panel"><span className="spinner" /></div>}

      {studies && studies.length === 0 && (
        <div className="panel empty-state">
          <div className="empty-state-title">No studies yet</div>
          <div style={{ fontSize: 14, marginBottom: 18 }}>Upload a chest X-ray to see it here.</div>
          <Link href="/" className="btn">Upload a study</Link>
        </div>
      )}

      {studies && studies.length > 0 && (
        <div className="panel">
          <div className="worklist-header">
            <span>Image</span>
            <span>Reference</span>
            <span>Top finding</span>
            <span>Confidence</span>
            <span>Status</span>
          </div>
          {studies.map((s) => {
            const sev = severity(s)
            const topFinding = Object.keys(s.positive_findings || {})[0]
            return (
              <Link key={s.id} href={`/study/${s.id}`} className="worklist-row">
                <img className="worklist-thumb" src={mediaUrl(s.display_path)} alt="" />
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{s.patient_ref || `Study #${s.id}`}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--muted)' }}>
                    {s.modality_note || '—'} · {s.created_at ? new Date(s.created_at).toLocaleDateString() : ''}
                  </div>
                </div>
                <div style={{ fontSize: 13, textTransform: 'capitalize' }}>{topFinding || 'None flagged'}</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 13 }}>{Math.round(s.overall_confidence * 100)}%</div>
                <span className={`severity-chip ${sev.cls}`}>{sev.label}</span>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
