import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import styles from '../App.module.css'

export default function Profile() {
  const [feedbacks, setFeedbacks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }
    fetchUserFeedbacks()
  }, [user, navigate])

  const fetchUserFeedbacks = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/feedback-records')
      if (response.ok) {
        const data = await response.json()
        // Filter feedbacks for current user
        const userFeedbacks = data.filter(feedback => 
          feedback.user_email === user.email
        )
        setFeedbacks(userFeedbacks)
      } else {
        setError('Failed to fetch feedback records')
      }
    } catch (err) {
      setError('Network error. Please check your connection.')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'America/New_York',
      timeZoneName: 'short'
    })
  }

  const formatOptions = (options) => {
    if (!options) return 'None'
    const selected = []
    if (options === "simplify") selected.push('Simplify')
    if (options === "soften") selected.push('Soften')
    if (options === "actionable") selected.push('Actionable')
    return selected.join(', ') || 'None'
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p>Loading your feedback history...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.errorContainer}>
          <p>{error}</p>
          <button onClick={fetchUserFeedbacks} className={styles.buttonPrimary}>
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.pageContent}>
        <div className={styles.profileHeader}>
          <h1 className={styles.pageTitle}>My Profile</h1>
          <div className={styles.profileInfo}>
            <h2 className={styles.profileEmail}>{user.email}</h2>
            <p className={styles.profileStats}>
              You have generated {feedbacks.length} feedback{feedbacks.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {feedbacks.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}></div>
            <h3>No Feedback History</h3>
            <p>You haven't generated any feedback yet. Start by submitting some feedback on the home page!</p>
            <button 
              className={styles.buttonPrimary}
              onClick={() => navigate('/')}
            >
              Generate Feedback
            </button>
          </div>
        ) : (
          <div className={styles.logsContainer}>
            <div className={styles.logsHeader}>
              <h2>Your Feedback History ({feedbacks.length})</h2>
              <button className={styles.refreshButton} onClick={fetchUserFeedbacks}>
                  Refresh
              </button>
            </div>
            
            <div className={styles.logsGrid}>
              {feedbacks.map((feedback, index) => (
                <div key={feedback.id || index} className={styles.logCard}>
                  <div className={styles.logHeader}>
                    <div className={styles.logIndex}>#{index + 1}</div>
                    <div className={styles.logDate}>
                       {formatDate(feedback.created_at)}
                    </div>
                  </div>
                  
                  <div className={styles.logUserInfo}>
                    <h4>User</h4>
                    <div className={styles.logUser}>
                      {feedback.user_email || 'Guest'}
                    </div>
                  </div>
                  
                  {feedback.submission_id && (
                    <div className={styles.logUserInfo}>
                      <h4>Submission ID</h4>
                      <div className={styles.logUser}>
                        {feedback.submission_id}
                      </div>
                    </div>
                  )}
                  
                  <div className={styles.logContent}>
                    <div className={styles.logSection}>
                      <h4>Original Feedback</h4>
                      <div className={styles.logText}>
                        {feedback.input_text || 'No input text'}
                      </div>
                    </div>
                    
                    <div className={styles.logSection}>
                      <h4>Options Used</h4>
                      <div className={styles.logOptions}>
                        {formatOptions(feedback.methods[0])}
                      </div>
                    </div>
                    
                    <div className={styles.logSection}>
                      <h4>Generated Output</h4>
                      <div className={styles.logText}>
                        {feedback.output_text || 'No output generated'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
