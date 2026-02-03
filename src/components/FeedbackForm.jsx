import styles from './FeedbackForm.module.css'

export default function FeedbackForm({
  inputText,
  onInputChange,
  options,
  onOptionsChange,
  onGenerate,
  onClear,
  canGenerate,
  isLoading
}) {
  function handleOptionChange(e) {
    const { name, checked } = e.target
    onOptionsChange(prev => ({ ...prev, [name]: checked }))
  }

  return (
    <section className={styles.card}>
      <h2 className={styles.heading}>Input</h2>

      <label className={styles.label} htmlFor="feedback">
        Paste feedback
      </label>
      <textarea
        id="feedback"
        className={styles.textarea}
        value={inputText}
        onChange={e => onInputChange(e.target.value)}
        placeholder="Paste written feedback here..."
      />

      <div className={styles.options}>
        <label className={styles.checkbox}>
          <input
            type="checkbox"
            name="simplify"
            checked={options.simplify}
            onChange={handleOptionChange}
          />
          Simplify language
        </label>

        <label className={styles.checkbox}>
          <input type="checkbox" name="soften" checked={options.soften} onChange={handleOptionChange} />
          Soften tone
        </label>

        <label className={styles.checkbox}>
          <input
            type="checkbox"
            name="caseSupport"
            checked={options.caseSupport}
            onChange={handleOptionChange}
          />
          Add case support
        </label>
      </div>

      <div className={styles.actions}>
        <button className={styles.primary} onClick={onGenerate} disabled={!canGenerate || isLoading}>
          Generate
        </button>
        <button className={styles.secondary} onClick={onClear}>
          Clear
        </button>
      </div>

      {!canGenerate && <p className={styles.hint}>Tip: paste some feedback text to enable Generate.</p>}
    </section>
  )
}
