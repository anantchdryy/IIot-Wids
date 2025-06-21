import React, { useState, useEffect } from 'react'
import './analytics.css'

export default function AnalyticsPage() {
  const [anomalies, setAnomalies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [isExpandedCSS, setIsExpandedCSS] = useState(false)
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('http://localhost:5000/api/anomalies')
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setAnomalies(data)
      } catch (e) {
        console.error('Fetch anomalies error:', e)
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  function handleToggle() {
    if (!isExpandedCSS) {
      setShowAll(true)
      requestAnimationFrame(() => setIsExpandedCSS(true))
    } else {
      setIsExpandedCSS(false)
      setTimeout(() => setShowAll(false), 500)
    }
  }

  const shown = showAll ? anomalies : anomalies.slice(0, 1)

  if (loading) return <p>Loading anomalies…</p>
  if (error)   return <p className="error">Error: {error}</p>

  return (
    <div className="analytics-page">
      <h1 className="analytics-title">Anomaly Counter</h1>
      <h2 className="analytics-subtitle">Past anomalies</h2>

      <div className={`anomaly-list ${isExpandedCSS ? 'expanded' : ''}`}>
        {shown.map((a, i) => (
          <div className="anomaly-card" key={i}>
            <div className="card-left">
              <p><strong>Timestamp :</strong> {a.timestamp}</p>
              <p><strong>Label :</strong> {a.label}</p>
              <p>
                <strong>Probability :</strong>{' '}
                {(a.probability * 100).toFixed(1)}%
              </p>
              <p>
                <strong>Packet Size :</strong>{' '}
                {a.features['Packet Size']} B
              </p>
              <p>
                <strong>Packet Length :</strong>{' '}
                {a.features['Packet Length']} B
              </p>
              <p>
                <strong>Inter-Arrival Time :</strong>{' '}
                {a.features['Inter-Arrival Time']} s
              </p>
              <p>
                <strong>Flow Duration :</strong>{' '}
                {a.features['Flow Duration']} s
              </p>
              <p>
                <strong>Total Packets :</strong>{' '}
                {a.features['Total Packets']}
              </p>
              <p>
                <strong>Average Packet Size :</strong>{' '}
                {a.features['Average Packet Size']} B
              </p>
              <p>
                <strong>Packet Arrival Rate :</strong>{' '}
                {a.features['Packet Arrival Rate']} pps
              </p>
            </div>
            <div className="card-right">
              <p>
                <strong>Payload Entropy :</strong>{' '}
                {a.features['Payload Entropy']}
              </p>
              <p>
                <strong>Flow Entropy :</strong>{' '}
                {a.features['Flow Entropy']}
              </p>
              <p>
                <strong>Baseline Deviation :</strong>{' '}
                {a.features['Baseline Deviation']}
              </p>
              <p>
                <strong>Packet Size Variance :</strong>{' '}
                {a.features['Packet Size Variance']}
              </p>
              <p>
                <strong>Known IoC :</strong>{' '}
                {a.features['Known IoC'] ? 'True' : 'False'}
              </p>
              <p>
                <strong>C&C Communication :</strong>{' '}
                {a.features['C&C Communication'] ? 'True' : 'False'}
              </p>
              <p>
                <strong>Data Exfiltration :</strong>{' '}
                {a.features['Data Exfiltration'] ? 'True' : 'False'}
              </p>
              <p>
                <strong>Protocol Type (one-hot):</strong>{' '}
                {JSON.stringify(a.features['Protocol Type (one-hot)'])}
              </p>
              <p>
                <strong>Flags (one-hot):</strong>{' '}
                {JSON.stringify(a.features['Flags (one-hot)'])}
              </p>
            </div>
          </div>
        ))}
      </div>

      {anomalies.length > 1 && (
        <button
          className={`toggle-icon-button ${
            isExpandedCSS ? 'expanded' : ''
          }`}
          onClick={handleToggle}
          aria-label={
            isExpandedCSS
              ? 'Collapse anomalies'
              : 'Expand anomalies'
          }
        >
          <svg width="48" height="48" viewBox="0 0 48 48">
            <circle
              cx="24"
              cy="24"
              r="22"
              className="toggle-icon-circle"
            />
            <polyline
              points="16,20 24,28 32,20"
              className="toggle-icon-chevron"
            />
          </svg>
        </button>
      )}
    </div>
  )
}
