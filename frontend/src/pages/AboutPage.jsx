import Disclaimer from '../components/Disclaimer'

export default function AboutPage() {
  return (
    <div className="about-page-container">
      <div className="page-header text-center">
        <span className="eyebrow">About MedReport AI</span>
        <h1>Empowering Patients with Clear Health Intelligence</h1>
        <p className="sub">
          Bridging the gap between technical medical report sheets and everyday patient understanding in English and Tamil.
        </p>
      </div>

      <div className="about-grid">
        <div className="card about-card">
          <div className="card-badge-icon">🔬</div>
          <h2>Optical Character Recognition (OCR)</h2>
          <p>
            Lab reports come in various printed table layouts, scanned photos, and PDFs. MedReport AI uses real OCR engines (Tesseract & PyMuPDF) to extract test names, values, units, and reference ranges directly from your document.
          </p>
        </div>

        <div className="card about-card">
          <div className="card-badge-icon">🌐</div>
          <h2>Bilingual AI Explainer</h2>
          <p>
            Extracted test data is analyzed against reference ranges to determine status (Normal, Low, High). Large Language Models then generate clear, non-alarming summaries in natural English and conversational Tamil (தமிழ்).
          </p>
        </div>

        <div className="card about-card">
          <div className="card-badge-icon">🛡️</div>
          <h2>Guest Mode & Privacy</h2>
          <p>
            You are never forced to create an account to use the application. Guest mode allows instant analysis without storing personal history permanently, while registered users can save and revisit past reports.
          </p>
        </div>
      </div>

      <div className="about-disclaimer-wrapper">
        <Disclaimer />
      </div>
    </div>
  )
}
