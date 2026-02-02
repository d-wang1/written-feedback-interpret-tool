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

  function handleGenerate() {
    // Demo logic (swap this out for a real API call later)
    let result = inputText

    if (options.simplify) {
      result = result.replace(/utilize/gi, 'use')
      result = result.replace(/demonstrate/gi, 'show')
    }

    if (options.soften) {
      result = `Consider the following suggestion:\n\n${result}`
    }

    if (options.caseSupport) {
      result += `\n\n• You may want to include a specific example to support this point.`
    }

    setOutputText(result || '(No input provided)')
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
