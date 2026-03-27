import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import styles from '../App.module.css'

export default function Signup() {
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
    setError('')
    setIsLoading(true)

    // Debug logs
    console.log('=== SIGNUP DEBUG ===')
    console.log('Submission ID:', formData.submission_id)
    console.log('Email:', formData.email)
    console.log('Password:', formData.password)
    console.log('Remember Me:', formData.rememberMe)
    console.log('Full formData:', formData)
    console.log('==================')

    try {
      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          full_name: '',
          submission_id: formData.submission_id,
          remember_me: formData.rememberMe
        })
      })

      // Read response text ONCE
      const responseText = await response.text()
      console.log('Signup response status:', response.status)
      console.log('Signup response text:', responseText)

      if (response.ok) {
        const data = JSON.parse(responseText)
        console.log('Signup data:', data)
        
        // Use AuthContext login function to update state
        login({
          id: data.user_id,
          email: formData.email || formData.submission_id,
          role: data.role || 'user',
          submission_id: formData.submission_id
        }, data.access_token)
        
        console.log('Login function called, redirecting to home')
        // Redirect to home
        navigate('/')
      } else {
        console.log('Signup failed, response not ok')
        try {
          const errorData = JSON.parse(responseText)
          setError(errorData.detail || 'Signup failed. Please try again.')
        } catch (parseError) {
          setError('Signup failed. Please try again.')
        }
      }
    } catch (err) {
      console.log('Signup error:', err)
      navigate('/')
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
            <h1 className={styles.loginTitle}>Create Account</h1>
            <p className={styles.loginSubtitle}>Join EchoAI today</p>
          </div>

          <form className={styles.loginForm} onSubmit={handleSubmit}>
            {error && <div className={styles.errorMessage}>{error}</div>}
            
            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="submission_id">
                Submission ID *
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
                Email Address (Optional)
              </label>
              <input
                type="email"
                id="email"
                name="email"
                className={styles.formInput}
                placeholder="Enter your email (optional)"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="password">
                Password (Optional)
              </label>
              <input
                type="password"
                id="password"
                name="password"
                className={styles.formInput}
                placeholder="Create a password (optional)"
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
            </div>

            <button
              type="submit"
              className={`${styles.loginButton} ${styles.buttonPrimary}`}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className={styles.loading}></span>
                  Creating Account...
                </>
              ) : (
                'Sign Up'
              )}
            </button>
          </form>

          <div className={styles.loginFooter}>
            <p className={styles.signupPrompt}>
              Already have an account?{' '}
              <Link to="/login" className={styles.signupLink}>
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
