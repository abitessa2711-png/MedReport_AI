import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, isLoggedIn, logout, openAuthModal } = useAuth()
  const navigate = useNavigate()

  return (
    <header className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-brand">
          <div className="brand-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              <path d="M12 9v6" />
              <path d="M9 12h6" />
            </svg>
          </div>
          <div className="brand-text">
            <span className="brand-name">MedReport <span className="brand-accent">AI</span></span>
            <span className="brand-tag">Bilingual Health Explainer</span>
          </div>
        </NavLink>

        <nav className="navbar-links">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
            Home
          </NavLink>
          <NavLink to="/analysis" className={({ isActive }) => (isActive ? 'active' : '')}>
            New Analysis
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => (isActive ? 'active' : '')}>
            History
          </NavLink>
          <NavLink to="/about" className={({ isActive }) => (isActive ? 'active' : '')}>
            About
          </NavLink>
        </nav>

        <div className="navbar-actions">
          {isLoggedIn && user ? (
            <div className="user-profile-menu">
              <div className="user-chip">
                <span className="user-avatar">
                  {user.full_name && user.full_name.length > 0
                    ? user.full_name[0].toUpperCase()
                    : user.email && user.email.length > 0
                    ? user.email[0].toUpperCase()
                    : 'U'}
                </span>
                <span className="user-email">{user.full_name || user.email || 'User'}</span>
              </div>
              <button className="btn btn-outline-sm" onClick={logout}>
                Sign Out
              </button>
            </div>
          ) : (
            <div className="guest-actions">
              <button className="btn btn-ghost" onClick={() => openAuthModal('signin')}>
                Sign In
              </button>
              <button className="btn btn-primary-sm" onClick={() => navigate('/analysis')}>
                Quick Analysis
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
