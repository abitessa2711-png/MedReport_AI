import { useState } from 'react'
import UploadArea from '../components/UploadArea'
import ResultsTable from '../components/ResultsTable'
import ReportDashboard from '../components/ReportDashboard'
import Disclaimer from '../components/Disclaimer'
import { useAuth } from '../context/AuthContext'
import {
  uploadReport, extractReport, analyzeReport, extractErrorMessage,
} from '../api/client'

const STEPS = ['Upload', 'Extract', 'Review', 'Analysis']

export default function UploadPage() {
  const { user, isLoggedIn, openAuthModal, claimCurrentReportToUser } = useAuth()

  const [file, setFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(null)
  const [reportId, setReportId] = useState(null)
  const [stepIndex, setStepIndex] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [claimedSuccess, setClaimedSuccess] = useState(false)

  const [rows, setRows] = useState([])
  const [reportDate, setReportDate] = useState(null)
  const [age, setAge] = useState('')
  const [gender, setGender] = useState('')
  const [symptoms, setSymptoms] = useState('')
  const [finalReport, setFinalReport] = useState(null)

  const [loaderStep, setLoaderStep] = useState(0)

  function resetAll() {
    setFile(null)
    setUploadProgress(null)
    setReportId(null)
    setStepIndex(0)
    setBusy(false)
    setError(null)
    setRows([])
    setReportDate(null)
    setFinalReport(null)
    setClaimedSuccess(false)
  }

  async function handleFileSelected(selected) {
    setFile(selected)
    setError(null)
    setBusy(true)
    setUploadProgress(0)
    try {
      const uploaded = await uploadReport(selected, age || null, gender || null, setUploadProgress)
      setReportId(uploaded.report_id)
      setStepIndex(1)
      await runExtraction(uploaded.report_id)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  async function runExtraction(id) {
    setBusy(true)
    setError(null)
    try {
      const result = await extractReport(id)
      setRows(result.extracted_results)
      setReportDate(result.report_date)
      setStepIndex(2)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  function updateRow(id, field, value) {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, [field]: value } : r)))
  }

  async function handleAnalyze() {
    setBusy(true)
    setError(null)
    setStepIndex(3)
    setLoaderStep(1)

    const timer1 = setTimeout(() => setLoaderStep(2), 800)
    const timer2 = setTimeout(() => setLoaderStep(3), 1600)

    try {
      const corrections = rows.map((r) => ({
        id: r.id,
        test_name: r.test_name,
        value: r.value,
        unit: r.unit,
        reference_range: r.reference_range,
      }))

      const result = await analyzeReport(reportId, {
        userEmail: user?.email || null,
        age: age ? Number(age) : null,
        gender: gender || null,
        symptoms: symptoms || null,
        corrections,
      })

      setFinalReport({
        extracted_results: result.extracted_results,
        analysis: result.analysis,
      })
    } catch (err) {
      setError(extractErrorMessage(err))
      setStepIndex(2)
    } finally {
      clearTimeout(timer1)
      clearTimeout(timer2)
      setBusy(false)
    }
  }

  async function handleClaimReport() {
    if (!isLoggedIn) {
      openAuthModal('signin')
      return
    }
    if (!reportId) return
    try {
      await claimCurrentReportToUser(reportId)
      setClaimedSuccess(true)
    } catch (err) {
      setError(extractErrorMessage(err))
    }
  }

  return (
    <div className="upload-page-container">
      <div className="page-header">
        <div className="eyebrow">Interactive AI Analysis</div>
        <h1>Upload Your Lab Report</h1>
        <p className="sub">
          Upload a clear image or PDF. OCR reads parameters directly from your document,
          cross-references normal ranges, and generates bilingual English &amp; Tamil explanations.
        </p>
      </div>

      <Disclaimer />

      <div className="step-track">
        {STEPS.map((label, i) => (
          <div
            key={label}
            className={`step ${i === stepIndex ? 'active' : i < stepIndex ? 'done' : ''}`}
          >
            <span className="step-num">{i + 1}</span> {label}
          </div>
        ))}
      </div>

      {error && <div className="error-banner">{error}</div>}

      {!finalReport && (
        <div className="card upload-main-card">
          <h2>Report File Upload</h2>
          <UploadArea
            file={file}
            uploadProgress={uploadProgress}
            onFileSelected={handleFileSelected}
            onRemove={resetAll}
          />

          <div className="optional-fields-header">
            <h3>Optional Clinical Context</h3>
            <p>Providing age, gender, or symptoms helps tailor explanations (All fields optional)</p>
          </div>

          <div className="field-row-3">
            <div className="field">
              <label>Age (Optional)</label>
              <input
                type="number"
                min="0"
                max="120"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="e.g. 34"
              />
            </div>

            <div className="field">
              <label>Gender (Optional)</label>
              <select value={gender} onChange={(e) => setGender(e.target.value)}>
                <option value="">Prefer not to say</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="field">
              <label>Symptoms (Optional)</label>
              <input
                type="text"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="e.g. fatigue, mild fever"
              />
            </div>
          </div>

          {busy && stepIndex === 1 && (
            <div className="loading-box">
              <div className="spinner-purple"></div>
              <p>Scanning document with OCR engine...</p>
            </div>
          )}
        </div>
      )}

      {stepIndex >= 2 && rows.length > 0 && !finalReport && (
        <div className="card review-card">
          <div className="review-header flex-between">
            <div>
              <h2>Review Extracted Test Parameters</h2>
              <p className="subtext-sm">
                {reportDate ? `Report Date Detected: ${reportDate}. ` : ''}
                Correct any OCR reading errors before generating your bilingual AI summary.
              </p>
            </div>
            <span className="badge-pill badge-lavender">{rows.length} Values Extracted</span>
          </div>

          <ResultsTable rows={rows} editable onChangeRow={updateRow} />

          {busy && stepIndex === 3 ? (
            <div className="ai-loader-card">
              <div className="spinner-purple-lg"></div>
              <h3>Generating Bilingual Intelligence...</h3>
              <div className="loader-steps">
                <div className={`loader-step-item ${loaderStep >= 1 ? 'active' : ''}`}>
                  ✓ Cross-checking values with printed reference ranges
                </div>
                <div className={`loader-step-item ${loaderStep >= 2 ? 'active' : ''}`}>
                  ✓ Translating parameters into simple Tamil (தமிழ்)
                </div>
                <div className={`loader-step-item ${loaderStep >= 3 ? 'active' : ''}`}>
                  ✓ Formulating food, lifestyle &amp; self-care tips
                </div>
              </div>
            </div>
          ) : (
            <div className="action-button-row">
              <button className="btn btn-primary-lg" disabled={busy} onClick={handleAnalyze}>
                Generate Bilingual Summary
              </button>
            </div>
          )}
        </div>
      )}

      {finalReport && (
        <div className="final-results-wrapper">
          {!isLoggedIn && (
            <div className="guest-save-banner">
              <div className="banner-left">
                <span className="banner-icon">🔒</span>
                <div>
                  <strong>Want to save your reports and access them later?</strong>
                  <p>Guest analyses are temporary. Sign in or create an account to save to history.</p>
                </div>
              </div>
              <button className="btn btn-purple-sm" onClick={handleClaimReport}>
                {claimedSuccess ? '✓ Saved to Account!' : 'Save to My Account'}
              </button>
            </div>
          )}

          {isLoggedIn && (
            <div className="saved-account-banner">
              <span>✓ Successfully saved to your permanent report history.</span>
            </div>
          )}

          <ReportDashboard report={finalReport} />

          <div className="new-analysis-bar">
            <button className="btn btn-primary" onClick={resetAll}>
              Analyze Another Lab Report
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
