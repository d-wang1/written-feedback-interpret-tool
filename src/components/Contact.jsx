import styles from '../App.module.css'

export default function Contact() {
  return (
    <div className={styles.pageContainer}>
      <div className={styles.pageContent}>
        <h1 className={styles.pageTitle}>Contact Us</h1>
        <p className={styles.pageDescription}>
          Get in touch with the EchoAI team for questions, feedback, or support.
        </p>
        
        <div className={styles.contactGrid}>
          <div className={styles.contactCard}>
            <h3>📧 Email</h3>
            <p>Yang: yl4367@cornell.edu</p>
            <p>Jiarui: jz2495@cornell.edu</p>
            <p>David: dw682@cornell.edu</p>
          </div>
          
          {/* <div className={styles.contactCard}>
            <h3>💬 Support</h3>
            <p>Available 24/7 for technical assistance</p>
          </div> */}
        </div>
      </div>
    </div>
  )
}