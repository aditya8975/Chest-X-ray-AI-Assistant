'use client'

import { useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '../lib/api.js'

const STEPS = [
  'Normalizing image (DICOM / PNG / JPEG)',
  'Running pathology classifier (18 findings)',
  'Computing Grad-CAM heatmaps',
  'Drafting structured report',
]

export default function UploadPage() {
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [stepIdx, setStepIdx] = useState(0)
  const [error, setError] = useState(null)
  const [patientRef, setPatientRef] = useState('')
  const [modalityNote, setModalityNote] = useState('PA')
  const router = useRouter()

  const handleFile = useCallback(async (file) => {
    if (!file) return
    setError(null)
    setUploading(true)
    setStepIdx(0)
    const interval = setInterval(() => {
      setStepIdx((i) => (i < STEPS.length - 1 ? i + 1 : i))
    }, 1100)
    try {
      const study = await api.uploadStudy(file, patientRef, modalityNote)
      clearInterval(interval)
      router.push(`/study/${study.id}`)
    } catch (e) {
      clearInterval(interval)
      setError(e.message || 'Upload failed')
      setUploading(false)
    }
  }, [patientRef, modalityNote, router])

  const onDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  return (
    <div>
      <div className="eyebrow">Study intake</div>
      <h1 className="page-title">Upload a chest X-ray</h1>
      <p className="page-sub">
        Runs an 18-pathology classifier, generates Grad-CAM heatmaps for surfaced findings, and
        drafts a structured report. Every output is AI-generated and requires physician review —
        see the banner above.
      </p>

      {!uploading && (
        <>
          <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
            <div style={{ flex: 1 }}>
              <label className="stat-label" style={{ display: 'block', marginBottom: 6 }}>Study reference (optional)</label>
              <input
                value={patientRef}
                onChange={(e) => setPatientRef(e.target.value)}
                placeholder="e.g. Case 014"
                style={{ width: '100%', background: 'var(--panel)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 12px', color: 'var(--ink)', fontFamily: 'var(--font-mono)', fontSize: 13 }}
              />
            </div>
            <div style={{ width: 160 }}>
              <label className="stat-label" style={{ display: 'block', marginBottom: 6 }}>View</label>
              <select
                value={modalityNote}
                onChange={(e) => setModalityNote(e.target.value)}
                style={{ width: '100%', background: 'var(--panel)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 12px', color: 'var(--ink)', fontFamily: 'var(--font-mono)', fontSize: 13 }}
              >
                <option value="PA">PA</option>
                <option value="AP">AP</option>
                <option value="Lateral">Lateral</option>
              </select>
            </div>
          </div>

          <label
            className={`dropzone${dragActive ? ' active' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
          >
            <div className="dropzone-icon">↑</div>
            <div className="dropzone-title">Drag & drop, or click to browse</div>
            <div className="dropzone-sub">DICOM (.dcm) · JPEG · PNG</div>
            <input
              type="file"
              accept="image/jpeg,image/png,.dcm"
              style={{ display: 'none' }}
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
          </label>
        </>
      )}

      {uploading && (
        <div className="panel loading-panel">
          <span className="spinner" />
          <div className="loading-steps">{STEPS[stepIdx]}…</div>
        </div>
      )}

      {error && (
        <div className="panel" style={{ padding: 16, marginTop: 16, borderColor: 'var(--red)', background: 'var(--red-soft)', color: '#FF8388', fontSize: 14 }}>
          {error}
        </div>
      )}
    </div>
  )
}
