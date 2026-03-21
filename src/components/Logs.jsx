import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import styles from '../App.module.css'

export default function Logs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuth()

  useEffect(() => {
    fetchLogs()
  }, [])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/feedback-records')
      if (response.ok) {
        const data = await response.json()
        setLogs(data)
      } else {
        setError('Failed to fetch logs')
      }
    } catch (err) {
      setError('Network error. Please check your connection.')
    } finally {
      setLoading(false)
    }
  }

  const deleteLog = async (logId) => {
    if (!window.confirm('Are you sure you want to delete this log?')) {
      return
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/feedback-records/${logId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setLogs(logs.filter(log => log.id !== logId))
      } else {
        alert('Failed to delete log')
      }
    } catch (err) {
      alert('Error deleting log')
    }
  }

  const deleteAllLogs = async () => {
    if (!window.confirm('Are you sure you want to delete ALL logs? This action cannot be undone!')) {
      return
    }
    
    try {
      const deletePromises = logs.map(log => 
        fetch(`http://localhost:8000/api/feedback-records/${log.id}`, {
          method: 'DELETE'
        })
      )
      
      await Promise.all(deletePromises)
      setLogs([])
    } catch (err) {
      alert('Error deleting logs')
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    const options = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }
    
    return date.toLocaleString('en-US', options)
  }

  const formatOptions = (options) => {
    if (!options) return 'None'
    const selected = []
    if (options === "simplify") selected.push('Simplify')
    if (options === "soften") selected.push('Soften')
    if (options === "caseSupport") selected.push('Case Support')
    return selected.length > 0 ? selected.join(', ') : 'None'
  }

  const isAdmin = user && user.role === 'admin'

  if (loading) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.pageContent}>
          <h1 className={styles.pageTitle}>Feedback Logs</h1>
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner}></div>
            <p>Loading feedback records...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.pageContent}>
          <h1 className={styles.pageTitle}>Feedback Logs</h1>
          <div className={styles.errorContainer}>
            <p className={styles.errorMessage}>Error: {error}</p>
            <button className={styles.retryButton} onClick={fetchLogs}>
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageContent}>
        <h1 className={styles.pageTitle}>Feedback Logs</h1>
        <p className={styles.pageDescription}>
          View all feedback interpretation records and their results.
        </p>

        <div className={styles.logsContainer}>
            <div className={styles.logsHeader}>
              <h2>Recent Feedback Records ({logs.length})</h2>
              <div className={styles.headerActions}>
                {isAdmin && (
                  <button 
                    onClick={deleteAllLogs}
                    className={styles.deleteButton}
                  >
                    Delete All Logs
                  </button>
                )}
                <button className={styles.refreshButton} onClick={fetchLogs}>
                   Refresh
                </button>
              </div>
            </div>
            
            {logs.length === 0 ? (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>📋</div>
                <h3>No feedback records found</h3>
                <p>No feedback has been processed yet. Start by submitting some feedback!</p>
              </div>
            ) : (
              <div className={styles.logsGrid}>
                {logs.map((log, index) => (
                <div key={log._id || index} className={styles.logCard}>
                  <div className={styles.logHeader}>
                    <div className={styles.logIndex}>#{index + 1}</div>
                    <div className={styles.logDate}>
                       {formatDate(log.created_at)}
                    </div>
                  </div>
                  
                  <div className={styles.logUserInfo}>
                    <h4>User</h4>
                    <div className={styles.logUser}>
                      {log.user_email || 'Guest'}
                    </div>
                  </div>
                  
                  {log.submission_id && (
                    <div className={styles.logUserInfo}>
                      <h4>Submission ID</h4>
                      <div className={styles.logUser}>
                        {log.submission_id}
                      </div>
                    </div>
                  )}
                  
                  {isAdmin && (
                    <div className={styles.logActions}>
                      <button 
                        onClick={() => deleteLog(log._id)}
                        className={styles.deleteButton}
                        title="Delete log"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  )}
                  
                  <div className={styles.logContent}>
                    <div className={styles.logSection}>
                      <h4>Original Feedback</h4>
                      <div className={styles.logText}>
                        {log.input_text || 'No input text'}
                      </div>
                    </div>
                    
                    <div className={styles.logSection}>
                      <h4>Options Used</h4>
                      <div className={styles.logOptions}>
                        {formatOptions(log.methods[0])}
                      </div>
                    </div>
                    
                    <div className={styles.logSection}>
                      <h4>Generated Output</h4>
                      <div className={styles.logText}>
                        {log.output_text || 'No output generated'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}