/**
 * Renders a summary section (overall / abnormal / normal / attention / lifestyle)
 * with English and Tamil text in clean side-by-side card styling.
 */
export default function SummaryCard({ title, icon = '📝', englishText, tamilText, highlight = false }) {
  return (
    <div className={`card summary-card-modern ${highlight ? 'card-highlighted' : ''}`}>
      <div className="summary-card-header">
        <span className="summary-card-icon">{icon}</span>
        <h3>{title}</h3>
      </div>
      <div className="summary-grid">
        <div className="lang-block lang-en">
          <div className="lang-label">English</div>
          <p>{englishText || '—'}</p>
        </div>
        <div className="lang-block lang-ta">
          <div className="lang-label">தமிழ் (Tamil)</div>
          <p>{tamilText || '—'}</p>
        </div>
      </div>
    </div>
  )
}
