import styles from './OutputPanel.module.css'

export default function OutputPanel({ outputText }) {
  return (
    <section className={styles.card}>
      <h2 className={styles.heading}>Output</h2>

      <label className={styles.label} htmlFor="output">
        Generated text
      </label>

      <textarea
        id="output"
        className={styles.textarea}
        value={outputText}
        readOnly
        placeholder="Your generated output will appear here..."
      />
    </section>
  )
}
