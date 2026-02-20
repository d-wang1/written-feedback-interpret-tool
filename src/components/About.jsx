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
            EchoAI was created to bridge the gap between complex academic feedback and student understanding. 
            Using advanced AI technology, we transform written feedback into clear, actionable insights that 
            help students improve their work and learning outcomes.
          </p>
        </div>
      </div>
    </div>
  )
}