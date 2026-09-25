export default function TeamAbout() {
  return (
    <section className="team-about-section">
      <div className="section-container">
        <div className="section-header">
          <span className="section-eyebrow">Medical Review Guidelines</span>
          <h2 className="section-title">Designed for Patient Empowerment</h2>
          <p className="section-subtitle">
            MedReport AI simplifies complex medical terminology so you can have more informed conversations with your physician.
          </p>
        </div>

        <div className="team-grid">
          <div className="team-card">
            <div className="team-avatar-box avatar-purple-1">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="1.8">
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <div className="team-role">General Health & Diagnostics</div>
            <h3>Patient Communication</h3>
            <p>
              Helps patients translate complex lab parameters into plain everyday words in both English and Tamil.
            </p>
          </div>

          <div className="team-card">
            <div className="team-avatar-box avatar-purple-2">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="1.8">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
              </svg>
            </div>
            <div className="team-role">Clinical Reference Accuracy</div>
            <h3>Strict Range Validation</h3>
            <p>
              Values are strictly validated against your report's printed reference range — never guessing or inventing numbers.
            </p>
          </div>

          <div className="team-card">
            <div className="team-avatar-box avatar-purple-3">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" strokeWidth="1.8">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <div className="team-role">Privacy & Compliance</div>
            <h3>Educational Disclaimer</h3>
            <p>
              Does not diagnose diseases or prescribe medications. Encourages consultation with certified healthcare professionals.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
