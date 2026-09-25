import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { extractErrorMessage } from '../api/client'

export default function AuthModal() {
  const { isAuthModalOpen, authModalTab, setAuthModalTab, closeAuthModal, login, register } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [infoMsg, setInfoMsg] = useState(null)

  if (!isAuthModalOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setInfoMsg(null)
    setBusy(true)

    try {
      if (authModalTab === 'signin') {
        await login(email, password)
        setEmail('')
        setPassword('')
      } else if (authModalTab === 'register') {
        await register(email, password, fullName)
        setEmail('')
        setPassword('')
        setFullName('')
      } else if (authModalTab === 'forgot') {
        if (!email) {
          setError('Please enter your email address.')
          setBusy(false)
          return
        }
        setInfoMsg(`Password reset instructions have been sent to ${email}.`)
      }
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={closeAuthModal}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={closeAuthModal}>&times;</button>
        
        <div className="modal-tabs">
          <button
            className={`tab-btn ${authModalTab === 'signin' ? 'active' : ''}`}
            onClick={() => { setAuthModalTab('signin'); setError(null); setInfoMsg(null); }}
          >
            Sign In
          </button>
          <button
            className={`tab-btn ${authModalTab === 'register' ? 'active' : ''}`}
            onClick={() => { setAuthModalTab('register'); setError(null); setInfoMsg(null); }}
          >
            Create Account
          </button>
        </div>

        <div className="modal-header">
          <h3>
            {authModalTab === 'signin' && 'Welcome Back'}
            {authModalTab === 'register' && 'Create Your Account'}
            {authModalTab === 'forgot' && 'Reset Password'}
          </h3>
          <p>
            {authModalTab === 'signin' && 'Sign in to access your saved lab reports & history.'}
            {authModalTab === 'register' && 'Save reports permanently and access history anytime.'}
            {authModalTab === 'forgot' && 'Enter your email to receive a password reset link.'}
          </p>
        </div>

        {error && <div className="error-banner">{error}</div>}
        {infoMsg && <div className="info-banner">{infoMsg}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          {authModalTab === 'register' && (
            <div className="field">
              <label>Full Name (Optional)</label>
              <input
                type="text"
                placeholder="Dr. John Doe / Sarah"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          )}

          <div className="field">
            <label>Email Address</label>
            <input
              type="email"
              required
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {authModalTab !== 'forgot' && (
            <div className="field">
              <label>Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          )}

          {authModalTab === 'signin' && (
            <div className="form-link-row">
              <button
                type="button"
                className="link-btn"
                onClick={() => { setAuthModalTab('forgot'); setError(null); }}
              >
                Forgot Password?
              </button>
            </div>
          )}

          <button type="submit" className="btn btn-primary btn-block" disabled={busy}>
            {busy ? 'Processing...' : (
              authModalTab === 'signin' ? 'Sign In' :
              authModalTab === 'register' ? 'Create Account' : 'Send Reset Link'
            )}
          </button>
        </form>

        <div className="modal-footer-guest">
          <p>Or want to test without an account?</p>
          <button className="btn btn-ghost-sm" onClick={() => { closeAuthModal(); }}>
            Continue as Guest
          </button>
        </div>
      </div>
    </div>
  )
}
