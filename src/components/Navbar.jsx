import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import styles from '../App.module.css'

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()
  const { user, logout } = useAuth()

  // Debug logging
  console.log('Navbar - user state:', user)
  console.log('Navbar - localStorage token:', localStorage.getItem('access_token'))
  console.log('Navbar - localStorage user_id:', localStorage.getItem('user_id'))
  console.log('Navbar - localStorage email:', localStorage.getItem('user_email'))

  const isActive = (path) => location.pathname === path

  const handleLogout = () => {
    logout()
    // Redirect to login page
    window.location.href = '/login'
  }

  return (
    <nav className={styles.navbar}>
      <div className={styles.navContainer}>
        <div className={styles.navLeft}>
          <Link to="/" className={styles.logoLink}>
            <div className={styles.logoContainer}>
              <div className={styles.logoIcon}>
                <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                  <circle cx="16" cy="16" r="14" stroke="#4F46E5" strokeWidth="2"/>
                  <path d="M12 12L20 20M20 12L12 20" stroke="#4F46E5" strokeWidth="2"/>
                  <circle cx="16" cy="16" r="3" fill="#4F46E5"/>
                </svg>
              </div>
              <div className={styles.logoText}>
                <span className={styles.echo}>Echo</span>
                <span className={styles.ai}>AI</span>
              </div>
            </div>
          </Link>
        </div>
        
        <div className={styles.navCenter}>
          <Link 
            to="/features" 
            className={`${styles.navLink} ${isActive('/features') ? styles.activeLink : ''}`}
          >
            Features
          </Link>
          <Link 
            to="/about" 
            className={`${styles.navLink} ${isActive('/about') ? styles.activeLink : ''}`}
          >
            About
          </Link>
          <Link 
            to="/contact" 
            className={`${styles.navLink} ${isActive('/contact') ? styles.activeLink : ''}`}
          >
            Contact
          </Link>
          <Link 
            to="/logs" 
            className={`${styles.navLink} ${isActive('/logs') ? styles.activeLink : ''}`}
          >
            Logs
          </Link>
          <Link 
            to="/users" 
            className={`${styles.navLink} ${isActive('/users') ? styles.activeLink : ''}`}
          >
            Users
          </Link>
          <Link 
            to="/profile" 
            className={`${styles.navLink} ${isActive('/profile') ? styles.activeLink : ''}`}
          >
            Profile
          </Link>
        </div>

        <div className={styles.navRight}>
          {user ? (
            <>
              <span className={styles.userInfo}>
                 {user.email}
              </span>
              <button onClick={handleLogout} className={styles.logoutButton}>
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className={styles.loginButton}>
              <span className={styles.loginIcon}>👤</span>
              Login
            </Link>
          )}
          <button 
            className={styles.mobileMenuButton}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <span className={styles.hamburger}></span>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className={styles.mobileMenu}>
          <Link to="/features" className={styles.mobileNavLink}>Features</Link>
          <Link to="/about" className={styles.mobileNavLink}>About</Link>
          <Link to="/contact" className={styles.mobileNavLink}>Contact</Link>
          <Link to="/logs" className={styles.mobileNavLink}>Logs</Link>
          <Link to="/users" className={styles.mobileNavLink}>Users</Link>
          <Link to="/profile" className={styles.mobileNavLink}>Profile</Link>
          {user ? (
            <>
              <span className={styles.userInfo}>
                 {user.email}
              </span>
              <button onClick={handleLogout} className={styles.mobileLogoutButton}>
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className={styles.mobileLoginButton}>
              <span className={styles.loginIcon}>👤</span>
              Login
            </Link>
          )}
        </div>
      )}
    </nav>
  )
}