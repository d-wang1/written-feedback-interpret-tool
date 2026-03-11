import { useState, useEffect } from 'react'
import styles from '../App.module.css'

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/users')
      if (response.ok) {
        const data = await response.json()
        setUsers(data)
      } else {
        setError('Failed to fetch users')
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
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.spinner}></div>
          <p>Loading users...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.errorContainer}>
          <p>{error}</p>
          <button onClick={fetchUsers} className={styles.buttonPrimary}>
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.logsHeader}>
        <h1 className={styles.logsTitle}>Users</h1>
        <button onClick={fetchUsers} className={styles.refreshButton}>
          🔄 Refresh
        </button>
      </div>

      {users.length === 0 ? (
        <div className={styles.emptyState}>
          <p>No users found in the database.</p>
        </div>
      ) : (
        <div className={styles.logsGrid}>
          {users.map((user) => (
            <div key={user._id} className={styles.logCard}>
              <div className={styles.logHeader}>
                <h3 className={styles.logEmail}>{user.email}</h3>
                <span className={styles.logDate}>
                  Joined: {formatDate(user.created_at)}
                </span>
              </div>
              <div className={styles.logContent}>
                <div className={styles.logDetails}>
                  <p><strong>User ID:</strong> {user._id}</p>
                  {user.full_name && (
                    <p><strong>Name:</strong> {user.full_name}</p>
                  )}
                  <p><strong>Last Updated:</strong> {formatDate(user.updated_at)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
