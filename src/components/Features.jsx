import styles from '../App.module.css'

export default function Features() {
  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageContent}>
        <h1 className={styles.pageTitle}>Features</h1>
        <p className={styles.pageDescription}>
          Discover what makes EchoAI the perfect tool for transforming educational feedback.
        </p>
        
        <div className={styles.featuresGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔄</div>
            <h3>Language Simplification</h3>
            <p>Complex academic feedback made simple and easy to understand.</p>
          </div>
          
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>💬</div>
            <h3>Tone Softening</h3>
            <p>Transform harsh criticism into constructive, encouraging feedback.</p>
          </div>
          
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📚</div>
            <h3>Case-Based Support</h3>
            <p>Add relevant examples and case studies to clarify feedback.</p>
          </div>
        </div>
      </div>
    </div>
  )
}