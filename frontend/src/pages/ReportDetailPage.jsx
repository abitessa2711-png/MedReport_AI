import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getReport, extractErrorMessage } from '../api/client'
import ReportDashboard from '../components/ReportDashboard'
import Disclaimer from '../components/Disclaimer'

export default function ReportDetailPage() {
  const { id } = useParams()
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setReport(null)
    setError(null)
    getReport(id)
      .then(setReport)
      .catch((err) => setError(extractErrorMessage(err)))
  }, [id])

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow"><Link to="/history">&larr; Back to history</Link></div>
        <h1>{report ? report.original_filename : 'Report'}</h1>
        {report && (
          <p className="sub">
            Uploaded {new Date(report.created_at).toLocaleString()}
            {report.report_date ? ` · Report date: ${report.report_date}` : ''}
          </p>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}
      {!report && !error && <p className="empty-state">Loading…</p>}

      {report && report.status === 'failed' && (
        <div className="error-banner">
          {report.error_message || 'This report could not be processed.'}
        </div>
      )}

      {report && report.status === 'analyzed' && (
        <>
          <Disclaimer />
          <ReportDashboard report={report} />
        </>
      )}
    </div>
  )
}
