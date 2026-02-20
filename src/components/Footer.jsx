import styles from '../App.module.css'

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.footerContainer}>
        <div className={styles.footerContent}>
          <div className={styles.footerSection}>
            <h3 className={styles.footerTitle}>What EchoAI Does</h3>
            <ul className={styles.featureList}>
              <li>🔄 Simplify complex feedback language</li>
              <li>💬 Soften harsh or critical tones</li>
              <li>📚 Add case-based examples and support</li>
              <li>⚡ Transform feedback into actionable insights</li>
            </ul>
          </div>
          
          <div className={styles.footerSection}>
            <h3 className={styles.footerTitle}>Technology</h3>
            <ul className={styles.featureList}>
              <li>🤖 Powered by advanced LLM technology</li>
              <li>🔧 Fast and reliable Groq API</li>
              <li>🛡️ Secure and private processing</li>
            </ul>
          </div>
          
          <div className={styles.footerSection}>
            <h3 className={styles.footerTitle}>Resources</h3>
            <ul className={styles.featureList}>
              <li>📖 Documentation</li>
              <li>💡 Examples & Use Cases</li>
              <li>🆘 Support & Help</li>
            </ul>
          </div>
        </div>
        
        <div className={styles.footerBottom}>
          <p>&​copy; 2024 EchoAI. Built for better learning experiences.</p>
        </div>
      </div>
    </footer>
  )
}