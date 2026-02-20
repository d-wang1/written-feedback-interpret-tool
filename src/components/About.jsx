import styles from '../App.module.css'

export default function About() {
  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageContent}>
        <h1 className={styles.pageTitle}>About EchoAI</h1>
        <p className={styles.pageDescription}>
          We're dedicated to making educational feedback more accessible and actionable for students.
        </p>
        
        <div className={styles.aboutSection}>
          <h2>Our Mission</h2>
          <p>
            EchoAI helps turn confusing academic feedback into plain English explanations students can
             actually use. We use AI to break down written comments into clear, practical guidance so you
              know what to fix, why it matters, and how to improve.
          </p>
        </div>
      </div>
    </div>
  )
}