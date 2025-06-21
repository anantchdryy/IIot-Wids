import React, { useState, useRef, useEffect } from 'react'
import GoButton from './GoButton'
import './home.css'

export default function HomePage() {
  const [isRunning, setIsRunning] = useState(false)
  const [result, setResult]       = useState({ label: '', probability: '' })
  const pollRef = useRef(null)

  
  async function fetchLatest() {
    try {
      const res = await fetch('http://localhost:5000/api/latest')
      if (!res.ok) throw new Error(`Status ${res.status}`)
      const data = await res.json()
      setResult({
        label: data.label,
        probability: (data.probability * 100).toFixed(1) + '%'
      })
    } catch (err) {
      console.error('Error polling /api/latest:', err)
    }
  }

  
  async function handleToggle() {
    if (!isRunning) {
      console.log('Starting predictor...')
      await fetch('http://localhost:5000/api/start', { method: 'POST' })
      setIsRunning(true)
      fetchLatest()
      pollRef.current = setInterval(fetchLatest, 1000)
    } else {
      console.log('Stopping predictor...')
      clearInterval(pollRef.current)
      await fetch('http://localhost:5000/api/stop', { method: 'POST' })
      setIsRunning(false)
    }
  }

  
  useEffect(() => {
    return () => clearInterval(pollRef.current)
  }, [])

  return (
    <div className="home-page">
      <div className={`go-container ${isRunning ? 'running' : ''}`}>
        <GoButton
          isRunning={isRunning}
          text={isRunning ? 'Running' : 'GO'}
          onClick={handleToggle}
        />
      </div>

      
      <p className={`current-status ${isRunning || result.label ? 'visible' : ''}`}>
        Current Status
      </p>

      
      <div className={`results ${result.label ? 'visible' : ''}`}>
        <div className="result-item anomaly">
          Anomaly&nbsp;: <strong>{result.label || '–––'}</strong>
        </div>
        <div className="result-item probability">
          Probability&nbsp;: <strong>{result.probability || '–––'}</strong>
        </div>
      </div>
    </div>
  )
}