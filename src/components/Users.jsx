import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import styles from '../App.module.css'

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { user } = useAuth()

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      setLoading(true)
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
      minute: '2-digit',
      timeZone: 'America/New_York',
      timeZoneName: 'short'
    })
  }

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return
    }
    
    try {
      const response = await fetch(`http://localhost:8000/api/auth/users/${userId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setUsers(users.filter(user => user._id !== userId))
      } else {
        alert('Failed to delete user')
      }
    } catch (err) {
      alert('Error deleting user')
    }
  }

  const deleteAllLogs = async () => {
    if (!window.confirm('Are you sure you want to delete ALL feedback logs? This action cannot be undone!')) {
      return
    }
    
    try {
      const response = await fetch('http://localhost:8000/api/feedback-records')
      if (response.ok) {
        const data = await response.json()
        // Delete each record
        for (const record of data) {
          await fetch(`http://localhost:8000/api/feedback-records/${record.id}`, {
            method: 'DELETE'
          })
        }
        setUsers([]) // Clear display after deletion
      } else {
        alert('Failed to fetch logs to delete')
      }
    } catch (err) {
      alert('Error deleting logs')
    }
  }

  const isAdmin = user && user.role === 'admin'

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
      <div className={styles.pageContent}>
        <h1 className={styles.pageTitle}>Users</h1>
        <p className={styles.pageDescription}>
          Manage user accounts and view system activity.
        </p>

        <div className={styles.logsContainer}>
            <div className={styles.logsHeader}>
              <h2>Registered Users ({users.length})</h2>
              <div className={styles.headerActions}>
                {isAdmin && (
                  <button 
                    onClick={deleteAllLogs}
                    className={styles.deleteButton}
                  >
                    Delete All Users
                  </button>
                )}
                <button className={styles.refreshButton} onClick={fetchUsers}>
                   Refresh
                </button>
              </div>
            </div>
            
            {users.length === 0 ? (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>👥</div>
                <h3>No users found</h3>
                <p>No users have registered yet.</p>
              </div>
            ) : (
              <div className={styles.logsGrid}>
                {users.map((user) => (
                <div key={user._id} className={styles.logCard}>
                  <div className={styles.logHeader}>
                    <h3 className={styles.logEmail}>{user.email}</h3>
                    {user.role === 'admin' && (
                      <span className={styles.adminBadge}>ADMIN</span>
                    )}
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
                      {user.submission_id && (
                        <p><strong>Submission ID:</strong> {user.submission_id}</p>
                      )}
                      <p><strong>Last Updated:</strong> {formatDate(user.updated_at)}</p>
                    </div>
                  </div>
                  
                  {isAdmin && (
                    <div className={styles.logActions}>
                      <button 
                        onClick={() => deleteUser(user._id)}
                        className={styles.deleteButton}
                        title="Delete user"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  )}
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
