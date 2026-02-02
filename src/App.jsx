import { useMemo, useState } from 'react'
import FeedbackForm from './components/FeedbackForm'
import OutputPanel from './components/OutputPanel'
import styles from './App.module.css'

export default function App() {
  const [inputText, setInputText] = useState('')
  const [outputText, setOutputText] = useState('')
  const [options, setOptions] = useState({
    simplify: false,
    soften: false,
    caseSupport: false,
  })

  const canGenerate = useMemo(() => inputText.trim().length > 0, [inputText])

  async function handleGenerate() {
    const res = await fetch("/api/interpret", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputText,
        options,
      }),
    })

    const data = await res.json()
    setOutputText(data.output || data.detail || "")
  }

  function handleClear() {
    setInputText('')
    setOutputText('')
    setOptions({ simplify: false, soften: false, caseSupport: false })
  }

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <header className={styles.header}>
          <h1 className={styles.title}>Written Feedback Interpretation Tool</h1>
          <p className={styles.subtitle}>
            Demo: paste feedback, choose options, and generate an improved version.
          </p>
        </header>

        <div className={styles.grid}>
          <FeedbackForm
            inputText={inputText}
            onInputChange={setInputText}
            options={options}
            onOptionsChange={setOptions}
            onGenerate={handleGenerate}
            onClear={handleClear}
            canGenerate={canGenerate}
          />

          <OutputPanel outputText={outputText} />
        </div>
      </div>
    </div>
  )
}
