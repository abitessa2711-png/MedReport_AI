import { useNavigate } from 'react-router-dom'

export default function PurpleBanner() {
  const navigate = useNavigate()

  return (
    <section className="purple-banner-section">
      <div className="banner-container">
        <div className="banner-content">
          <span className="banner-eyebrow">Instant & Private</span>
          <h2>Ready to Understand Your Lab Report?</h2>
          <p>
            No waiting time, no mandatory sign-up required. Upload your report sheet and get a complete bilingual summary in seconds.
          </p>
          <div className="banner-actions">
            <button className="btn btn-white" onClick={() => navigate('/analysis')}>
              Start Quick Analysis
            </button>
          </div>
        </div>

        <div className="banner-graphic">
          <div className="banner-illustration-box">
            <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.9)" strokeWidth="1.5">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
              <polyline points="14 2 14 8 20 8" />
              <path d="M12 18v-6" />
              <path d="M9 15h6" />
            </svg>
          </div>
        </div>
      </div>
    </section>
  )
}
