import { createContext, useContext, useState, useEffect } from 'react'
import { registerUser, loginUser, claimReport } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('medreport_user')
      if (!saved || saved === 'undefined' || saved === 'null') return null
      const parsed = JSON.parse(saved)
      return (parsed && typeof parsed === 'object' && (parsed.email || parsed.id)) ? parsed : null
    } catch {
      return null
    }
  })

  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [authModalTab, setAuthModalTab] = useState('signin')

  useEffect(() => {
    try {
      if (user) {
        localStorage.setItem('medreport_user', JSON.stringify(user))
      } else {
        localStorage.removeItem('medreport_user')
      }
    } catch (e) {
      console.warn("localStorage sync warning:", e)
    }
  }, [user])

  const login = async (email, password) => {
    const userData = await loginUser(email, password)
    setUser(userData)
    setIsAuthModalOpen(false)
    return userData
  }

  const register = async (email, password, fullName) => {
    const userData = await registerUser(email, password, fullName)
    setUser(userData)
    setIsAuthModalOpen(false)
    return userData
  }

  const logout = () => {
    setUser(null)
  }

  const openAuthModal = (tab = 'signin') => {
    setAuthModalTab(tab)
    setIsAuthModalOpen(true)
  }

  const closeAuthModal = () => {
    setIsAuthModalOpen(false)
  }

  const claimCurrentReportToUser = async (reportId) => {
    if (!user || !user.email || !reportId) return null
    return await claimReport(reportId, user.email)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoggedIn: !!user,
        isAuthModalOpen,
        authModalTab,
        setAuthModalTab,
        openAuthModal,
        closeAuthModal,
        login,
        register,
        logout,
        claimCurrentReportToUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
