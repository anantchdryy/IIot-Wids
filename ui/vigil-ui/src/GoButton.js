import React from 'react'
import './home.css'

export default function GoButton({ isRunning, text, onClick }) {
  return (
    <button
      className={`go-button ${isRunning ? 'running' : ''}`}
      onClick={onClick}
    >
      <svg width="266" height="266" viewBox="0 0 266 266">
        {/* Base border */}
        <circle
          cx="133"
          cy="133"
          r="130"
          className="go-circle-base"
        />
        {/* Animated dash */}
        <circle
          cx="133"
          cy="133"
          r="130"
          className="go-circle-dash"
        />
      </svg>
      <span className="go-text">{text}</span>
    </button>
  )
}