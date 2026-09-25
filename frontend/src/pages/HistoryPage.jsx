import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { listReports, extractErrorMessage } from '../api/client'

const STATUS_LABEL = {
  uploaded: 'Uploaded',
  extracted: 'Extracted',
  analyzed: 'Analyzed',
  failed: 'Failed',
}

const STATUS_CLASS = {
  uploaded: 'badge badge-unknown',
  extracted: 'badge badge-low',
  analyzed: 'badge badge-normal',
  failed: 'badge badge-high',
}

export default function HistoryPage() {
  const { user, isLoggedIn, openAuthModal } = useAuth()
  const [reports, setReports] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isLoggedIn && user?.email) {
      listReports(user.email)
        .then(setReports)
        .catch((err) => setError(extractErrorMessage(err)))
    } else {
      setReports([])
    }
  }, [isLoggedIn, user])

  return (
    <div className="history-page-container">
      <div className="page-header">
        <div className="eyebrow">Personal Dashboard</div>
        <h1>Report History</h1>
        <p className="sub">Access your saved medical report sheet analyses and bilingual summaries anytime.</p>
      </div>

      {!isLoggedIn && (
        <div className="card guest-history-card">
          <div className="guest-history-content">
            <div className="history-icon-box">📁</div>
            <h2>You are in Quick Analysis / Guest Mode</h2>
            <p>
              Reports processed as a guest are not stored in permanent account history to protect your privacy.
              Sign in or create a free account to automatically save your reports.
            </p>
            <div className="guest-history-actions">
              <button className="btn btn-primary" onClick={() => openAuthModal('signin')}>
                Sign In to Enable History
              </button>
              <button className="btn btn-secondary" onClick={() => openAuthModal('register')}>
                Create Free Account
              </button>
            </div>
          </div>
        </div>
      )}

      {isLoggedIn && (
        <div className="card history-list-card">
          <div className="history-card-header flex-between">
            <h2>Saved Lab Reports ({reports ? reports.length : 0})</h2>
            <span className="user-email-tag">{user?.email}</span>
          </div>

          {error && <div className="error-banner">{error}</div>}

          {reports === null && !error && <p className="empty-state">Loading your reports...</p>}
          
          {reports && reports.length === 0 && (
            <div className="empty-history-box">
              <p>No saved reports found for your account.</p>
              <Link to="/analysis" className="btn btn-primary-sm">
                Analyze a Report Now
              </Link>
            </div>
          )}

          {reports && reports.map((r) => (
            <Link key={r.id} to={`/reports/${r.id}`} className="history-row-modern">
              <div className="row-left">
                <div className="doc-icon">📄</div>
                <div>
                  <div className="fname">{r.original_filename}</div>
                  <div className="fmeta">
                    Analyzed on {new Date(r.created_at).toLocaleDateString()} at {new Date(r.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    {r.report_date ? ` • Report Date: ${r.report_date}` : ''}
                  </div>
                  {r.overall_summary_en && (
                    <div className="summary-snippet">
                      {r.overall_summary_en.slice(0, 110)}...
                    </div>
                  )}
                </div>
              </div>
              <div className="row-right">
                <span className={STATUS_CLASS[r.status] || 'badge badge-unknown'}>
                  {STATUS_LABEL[r.status] || r.status}
                </span>
                <span className="chevron-icon">→</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
