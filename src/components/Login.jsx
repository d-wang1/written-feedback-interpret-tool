import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import styles from '../App.module.css'

export default function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    submission_id: '',
    rememberMe: false
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { login } = useAuth()

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
          submission_id: formData.submission_id,
          remember_me: formData.rememberMe
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        // Use AuthContext login function to update state
        login({
          id: data.user_id,
          email: formData.email || formData.submission_id,
          role: data.role || 'user',
          submission_id: formData.submission_id
        }, data.access_token)
        
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
      {/* EchoAI Logo that redirects home */}
      <div className={styles.loginLogoContainer}>
        <Link to="/" className={styles.loginLogoLink}>
          <div className={styles.loginLogo}>
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <circle cx="16" cy="16" r="14" stroke="#4F46E5" strokeWidth="2"/>
              <path d="M12 12L20 20M20 12L12 20" stroke="#4F46E5" strokeWidth="2"/>
              <circle cx="16" cy="16" r="3" fill="#4F46E5"/>
            </svg>
            <div className={styles.loginLogoText}>
              <span className={styles.echo}>Echo</span>
              <span className={styles.ai}>AI</span>
            </div>
          </div>
        </Link>
      </div>

      <div className={styles.loginContainer}>
        <div className={styles.loginCard}>
          <div className={styles.loginHeader}>
            <h1 className={styles.loginTitle}>Welcome Back</h1>
            <p className={styles.loginSubtitle}>Sign in to your EchoAI account</p>
          </div>

          <form className={styles.loginForm} onSubmit={handleSubmit}>
            {error && <div className={styles.errorMessage}>{error}</div>}
            
            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="submission_id">
                Submission ID
              </label>
              <input
                type="text"
                id="submission_id"
                name="submission_id"
                className={styles.formInput}
                placeholder="Enter your submission ID"
                value={formData.submission_id}
                onChange={handleChange}
                required
              />
            </div>

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
      </div>
    </div>
  )
}