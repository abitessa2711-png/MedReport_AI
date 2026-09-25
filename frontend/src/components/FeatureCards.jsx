export default function FeatureCards() {
  return (
    <section className="features-section">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">How It Works</span>
          <h2 className="section-title">Three Steps to Health Clarity</h2>
          <p className="section-subtitle">
            No technical jargon. Everything is explained clearly using real data from your lab sheet.
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <h3>Upload & Read</h3>
            <p>
              Upload a clear photo or PDF of your blood test or lab report. Real Tesseract & PyMuPDF OCR extracts test parameters automatically.
            </p>
            <div className="card-footer-link">
              <span>Supports JPG, PNG & PDF</span>
            </div>
          </div>

          <div className="feature-card highlighted-feature-card">
            <div className="feature-icon-wrapper">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m22 2-7 20-4-9-9-4Z" />
                <path d="M22 2 11 13" />
              </svg>
            </div>
            <h3>Understand Results</h3>
            <p>
              Values are automatically verified against reference ranges, generating structured plain-language summaries in <strong>English</strong> and <strong>Tamil (தமிழ்)</strong>.
            </p>
            <div className="card-footer-link">
              <span>Bilingual AI Translation</span>
            </div>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2v20" />
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
              </svg>
            </div>
            <h3>Learn Healthy Habits</h3>
            <p>
              Receive personalized diet, food recommendations, lifestyle adjustments, and wellness questions to discuss during your doctor appointment.
            </p>
            <div className="card-footer-link">
              <span>Food & Lifestyle Tips</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
