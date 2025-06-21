import React from 'react'
import './about.css'

export default function AboutPage() {
  return (
    <div className="about-page">
      <h1 className="about-title">About the project</h1>
      <p className="about-intro">
        ViGiL is a fast, lightweight, real-time wireless network traffic monitoring and 
        classifying dashboard. Behind the scenes, it keeps taking short snippets of PCAP 
        into memory from your network interface, records a set of 15 flow-level features 
        (packet length, inter-arrival time, entropy metrics, etc.) and runs an ensemble 
        of tuned XGBoost classifiers to label each capture into one of a few threat classes 
        (Benign, Botnet, Ransomware, Spyware, Trojan, Worm). All forecasts and their 
        supporting probabilities stream directly into MongoDB and are driven to your 
        network’s security status.
      </p>

      <h2 className="features-heading">Key Features</h2>
      <ul className="features-list">
        <li>
          <strong>Live Capture & Analysis:</strong> Automatically captures traffic in 
          configurable windows, derives features using PyShark, and feeds them through 
          our pre-trained models without user intervention.
        </li>
        <li>
          <strong>Probability-Based Alerts:</strong> Each capture provides a probability 
          distribution over threat families; any malware probability above “Benign” is 
          marked and placed in a special anomalies collection for simple inspection.
        </li>
        <li>
          <strong>Interactive Dashboard:</strong> Based on Flask and Chart.js, ViGiL’s UI 
          graph risk probabilities over time, allows you to drill down into specific 
          prediction events, and can be further extended with MongoDB Charts or custom 
          Grafana panels.
        </li>
        <li>
          <strong>Modular & Customizable:</strong> Replace your own feature-extraction 
          logic, retrain the XGBoost models on fresh data, or containerize the whole stack 
          for production deployment—ViGiL’s modular architecture makes it easy.
        </li>
      </ul>
    </div>
  )
}