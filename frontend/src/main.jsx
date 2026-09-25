import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './styles/index.css'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error("React ErrorBoundary caught error:", error, errorInfo)
    this.setState({ errorInfo })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', maxWidth: '640px', margin: '60px auto', fontFamily: 'system-ui, sans-serif', background: '#ffffff', border: '1px solid #fee2e2', borderRadius: '16px', boxShadow: '0 20px 40px rgba(0,0,0,0.08)' }}>
          <h2 style={{ color: '#dc2626', marginTop: 0, fontSize: '22px' }}>Application Notice</h2>
          <p style={{ color: '#475569', fontSize: '15px', lineHeight: '1.5' }}>
            A client-side initialization issue occurred. Click the button below to clear cached session data and reload cleanly.
          </p>
          <pre style={{ background: '#f8fafc', padding: '14px', borderRadius: '8px', color: '#991b1b', overflowX: 'auto', fontSize: '12.5px', border: '1px solid #e2e8f0', margin: '16px 0' }}>
            {this.state.error && this.state.error.toString()}
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
          <button
            onClick={() => {
              try { localStorage.clear(); sessionStorage.clear(); } catch(e) {}
              window.location.href = '/';
            }}
            style={{ background: '#7c3aed', color: '#ffffff', border: 'none', padding: '12px 24px', borderRadius: '9999px', cursor: 'pointer', fontWeight: '700', fontSize: '14px' }}
          >
            Clear Cache &amp; Reload Application
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>,
)
