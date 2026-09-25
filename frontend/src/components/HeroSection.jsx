import { useNavigate } from 'react-router-dom'

export default function HeroSection() {
  const navigate = useNavigate()

  return (
    <section className="hero-section">
      <div className="hero-container">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="sparkle-dot"></span>
            <span>AI-Powered Medical Intelligence</span>
          </div>

          <h1 className="hero-title">
            Understand Your <span className="purple-gradient-text">Lab Report.</span> Simply.
          </h1>

          <p className="hero-subtitle">
            Instant OCR extraction, reference-range verification, and plain-language
            bilingual summaries in <strong>English</strong> and <strong>Tamil (தமிழ்)</strong>.
          </p>

          <div className="hero-actions">
            <button className="btn btn-primary-lg" onClick={() => navigate('/analysis')}>
              Analyze My Report
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </button>

            <button className="btn btn-secondary-lg" onClick={() => navigate('/analysis')}>
              Continue as Guest
            </button>
          </div>

          <div className="trust-note">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            <span>Educational tool • Not a medical diagnosis • Privacy First</span>
          </div>
        </div>

        <div className="hero-visual">
          <div className="lavender-backdrop-circle"></div>
          <div className="hero-card-stack">
            <div className="hero-card hero-card-main">
              <div className="card-pill-row">
                <span className="pill pill-lavender">Bilingual AI</span>
                <span className="pill pill-success">Real OCR</span>
              </div>
              <div className="card-mock-row">
                <div className="mock-icon">🩸</div>
                <div className="mock-info">
                  <h4>Hemoglobin (Hb)</h4>
                  <p>13.5 g/dL • Reference: 12.0 - 15.5</p>
                </div>
                <span className="mock-badge badge-normal">Normal</span>
              </div>
              <div className="card-mock-summary">
                <p className="en-preview">Your hemoglobin levels are well within the standard reference range.</p>
                <p className="ta-preview">உங்கள் ஹீமோகுளோபின் அளவு இயல்பு எல்லையில் உள்ளது.</p>
              </div>
            </div>

            <div className="hero-card hero-card-floating">
              <div className="floating-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              </div>
              <div>
                <strong>Instant Analysis</strong>
                <p>No waiting • Instant Tamil conversion</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
