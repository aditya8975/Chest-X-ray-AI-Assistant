'use client'

import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line,
} from 'recharts'
import { api } from '../../lib/api.js'

function toChartData(obj) {
  return Object.entries(obj || {}).map(([name, value]) => ({ name, value }))
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.dashboardStats().then(setStats).catch(() => setStats(null))
  }, [])

  if (!stats) return <div className="loading-panel"><span className="spinner" /></div>

  const pathologyData = toChartData(stats.pathology_frequency)
  const byDay = Object.entries(stats.studies_by_day || {}).map(([date, count]) => ({ date, count }))

  return (
    <div>
      <div className="eyebrow">Analytics</div>
      <h1 className="page-title">Cohort dashboard</h1>
      <p className="page-sub">A rollup across every study the pipeline has processed.</p>

      <div className="grid-4" style={{ marginBottom: 28 }}>
        <div className="panel stat-card">
          <div className="stat-value">{stats.total_studies}</div>
          <div className="stat-label">Total studies</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value" style={{ color: 'var(--teal)' }}>{stats.avg_positive_findings}</div>
          <div className="stat-label">Avg. findings / study</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value">{Math.round(stats.avg_confidence * 100)}%</div>
          <div className="stat-label">Avg. confidence</div>
        </div>
        <div className="panel stat-card">
          <div className="stat-value" style={{ color: stats.studies_flagged_high_risk > 0 ? 'var(--red)' : undefined }}>{stats.studies_flagged_high_risk}</div>
          <div className="stat-label">High-confidence flags</div>
        </div>
      </div>

      {stats.total_studies === 0 ? (
        <div className="panel empty-state">
          <div className="empty-state-title">No data yet</div>
          <div style={{ fontSize: 14 }}>Upload some studies to populate the dashboard.</div>
        </div>
      ) : (
        <div className="grid-2">
          <div className="panel" style={{ padding: 20 }}>
            <div className="section-title">Studies over time</div>
            <ResponsiveContainer width="100%" height={230}>
              <LineChart data={byDay}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262F3B" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#8C96A6' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#8C96A6' }} />
                <Tooltip contentStyle={{ background: '#151C25', border: '1px solid #262F3B' }} />
                <Line type="monotone" dataKey="count" stroke="#2DD4C8" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="panel" style={{ padding: 20 }}>
            <div className="section-title">Pathology frequency (positive findings)</div>
            <ResponsiveContainer width="100%" height={Math.max(230, pathologyData.length * 30)}>
              <BarChart data={pathologyData} layout="vertical" margin={{ left: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262F3B" />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fill: '#8C96A6' }} />
                <YAxis type="category" dataKey="name" width={130} tick={{ fontSize: 11.5, fill: '#E7EBF0' }} />
                <Tooltip contentStyle={{ background: '#151C25', border: '1px solid #262F3B' }} />
                <Bar dataKey="value" fill="#E5484D" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
