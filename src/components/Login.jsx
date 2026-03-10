import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import styles from '../App.module.css'

export default function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          remember_me: formData.rememberMe
        })
      })

      if (response.ok) {
        const data = await response.json()
        // Store token in localStorage
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('user_id', data.user_id)
        localStorage.setItem('user_email', formData.email)
        
        // Redirect to dashboard or home
        navigate('/')
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Login failed. Please try again.')
      }
    } catch (err) {
      setError('Network error. Please check your connection.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={styles.loginPage}>
      <div className={styles.loginContainer}>
        <div className={styles.loginCard}>
          <div className={styles.loginHeader}>
            <div className={styles.loginLogo}>
              <svg width="48" height="48" viewBox="0 0 32 32" fill="none">
                <defs>
                  <linearGradient id="starGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#667eea"/>
                    <stop offset="100%" stopColor="#764ba2"/>
                  </linearGradient>
                </defs>
                <path 
                  d="M16 2L20 10L28 11L22 17L24 25L16 21L8 25L10 17L4 11Z" 
                  fill="url(#starGradient)"
                />
              </svg>
            </div>
            <h1 className={styles.loginTitle}>Welcome Back</h1>
            <p className={styles.loginSubtitle}>Sign in to your EchoAI account</p>
          </div>

          <form className={styles.loginForm} onSubmit={handleSubmit}>
            {error && <div className={styles.errorMessage}>{error}</div>}
            
            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="email">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                className={styles.formInput}
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="password">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                className={styles.formInput}
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className={styles.formOptions}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  name="rememberMe"
                  className={styles.checkbox}
                  checked={formData.rememberMe}
                  onChange={handleChange}
                />
                <span className={styles.checkboxText}>Remember me</span>
              </label>
              
              <Link to="/signup" className={styles.forgotLink}>
                Don't have an account? Sign up
              </Link>
            </div>

            <button
              type="submit"
              className={`${styles.loginButton} ${styles.buttonPrimary}`}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className={styles.loading}></span>
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className={styles.loginFooter}>
            <p className={styles.signupPrompt}>
              Forgot your password?{' '}
              <Link to="/forgot-password" className={styles.signupLink}>
                Reset it here
              </Link>
            </p>
          </div>
        </div>

        <div className={styles.loginInfo}>
          <h2 className={styles.infoTitle}>Transform Your Learning Experience</h2>
          <ul className={styles.infoList}>
            <li>🔄 Convert complex feedback into clear insights</li>
            <li>💬 Soften harsh tones for better understanding</li>
            <li>📚 Get case-based examples and support</li>
            <li>⚡ Save time with instant AI-powered analysis</li>
          </ul>
          <div className={styles.infoStats}>
            <div className={styles.stat}>
              <div className={styles.statNumber}>10K+</div>
              <div className={styles.statLabel}>Students Helped</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statNumber}>95%</div>
              <div className={styles.statLabel}>Success Rate</div>
            </div>
            <div className={styles.stat}>
              <div className={styles.statNumber}>24/7</div>
              <div className={styles.statLabel}>Available</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}