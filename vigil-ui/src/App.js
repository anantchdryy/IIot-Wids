import React from 'react';
import { Routes, Route, Navigate, NavLink } from 'react-router-dom';
import Navbar from './navbar';
import GoButton from './GoButton';
import AnalyticsPage from './AnalyticsPage';
import AboutPage from './AboutPage';
import HomePage from './HomePage';

function NotFoundPage() {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>404 – Page not found</h1>
      <p>
        Oops! That URL doesn’t exist.{' '}
        <NavLink to="/analytics">Go back to Analytics</NavLink>.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <div className="App">
      <Navbar />

      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/analytics" replace />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/about"     element={<AboutPage />} />
          <Route path="/home"      element={<HomePage />} />
          <Route path="*"          element={<NotFoundPage />} />
        </Routes>
      </main>
    </div>
  );
}