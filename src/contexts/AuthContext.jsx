import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)

  useEffect(() => {
    // Check for existing session on load
    const savedToken = localStorage.getItem('access_token')
    const savedUserId = localStorage.getItem('user_id')
    const savedEmail = localStorage.getItem('user_email')
    
    if (savedToken && savedUserId) {
      setToken(savedToken)
      setUser({
        id: savedUserId,
        email: savedEmail
      })
    }
  }, [])

  const login = (userData, authToken) => {
    setToken(authToken)
    setUser(userData)
    
    // Store in localStorage
    localStorage.setItem('access_token', authToken)
    localStorage.setItem('user_id', userData.id)
    localStorage.setItem('user_email', userData.email)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    
    // Clear localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_email')
  }

  const value = {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!user && !!token
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}