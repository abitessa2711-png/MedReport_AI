import { Route, Routes, Link } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import AuthModal from './components/AuthModal'
import HomePage from './pages/HomePage'
import UploadPage from './pages/UploadPage'
import HistoryPage from './pages/HistoryPage'
import AboutPage from './pages/AboutPage'
import ReportDetailPage from './pages/ReportDetailPage'

export default function App() {
  return (
    <AuthProvider>
      <div className="app-layout">
        <Navbar />
        <AuthModal />

        <main className="app-main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analysis" element={<UploadPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/reports/:id" element={<ReportDetailPage />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <div className="footer-container">
            <div className="footer-brand">
              <span className="brand-name">MedReport <span className="brand-accent">AI</span></span>
              <p>Bilingual Medical Report Explanation &amp; Educational Intelligence</p>
            </div>
            <div className="footer-links">
              <Link to="/">Home</Link>
              <Link to="/analysis">New Analysis</Link>
              <Link to="/history">History</Link>
              <Link to="/about">About</Link>
            </div>
            <div className="footer-disclaimer">
              <p>Educational tool only. Does not diagnose disease or prescribe medications.</p>
            </div>
          </div>
        </footer>
      </div>
    </AuthProvider>
  )
}

