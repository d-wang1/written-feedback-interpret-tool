import { useState, useEffect } from 'react'
import styles from '../App.module.css'

export default function Logs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchLogs()
    console.log('HI')
  }, [])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/feedback-records')
      
      if (!response.ok) {
        throw new Error('Failed to fetch logs')
      }
      
      const data = await response.json()
      console.log("Here's the logs", data)
      setLogs(data || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
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
    if (options.simplify) selected.push('Simplify')
    if (options.soften) selected.push('Soften')
    if (options.caseSupport) selected.push('Case Support')
    return selected.length > 0 ? selected.join(', ') : 'None'
  }

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

        {logs.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>📋</div>
            <h3>No feedback records found</h3>
            <p>No feedback has been processed yet. Start by submitting some feedback!</p>
          </div>
        ) : (
          <div className={styles.logsContainer}>
            <div className={styles.logsHeader}>
              <h2>Recent Feedback Records ({logs.length})</h2>
              <button className={styles.refreshButton} onClick={fetchLogs}>
                🔄 Refresh
              </button>
            </div>
            
            <div className={styles.logsGrid}>
              {logs.map((log, index) => (
                <div key={log._id || index} className={styles.logCard}>
                  <div className={styles.logHeader}>
                    <div className={styles.logIndex}>#{index + 1}</div>
                    <div className={styles.logDate}>
                      📅 {formatDate(log.created_at)}
                    </div>
                  </div>
                  
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
                        {formatOptions(log.options)}
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
          </div>
        )}
      </div>
    </div>
  )
}