import { useState } from 'react'

export default function App() {
  const [inputText, setInputText] = useState('')
  const [outputText, setOutputText] = useState('')
  const [options, setOptions] = useState({
    simplify: false,
    soften: false,
    caseSupport: false,
  })

  function handleOptionChange(e) {
    const { name, checked } = e.target
    setOptions(prev => ({ ...prev, [name]: checked }))
  }

  function handleGenerate() {
    // setOutputText('Hello! Generate works.')
    console.log('Generate clicked', inputText, options, " at \n", new Date().toString())
    let result = inputText

    if (options.simplify) {
      result = result.replace(/utilize/g, 'use')
      result = result.replace(/demonstrate/g, 'show')
    }

    if (options.soften) {
      result = `Consider the following suggestion:\n\n${result}`
    }

    if (options.caseSupport) {
      result += `\n\n• You may want to include a specific example to support this point.`
    }

    setOutputText(result || '(No input provided)')
  }

  return (
    <div style={styles.container}>
      <h1>Written Feedback Interpretation Tool</h1>

      <label style={styles.label}>Paste feedback</label>
      <textarea
        style={styles.textarea}
        value={inputText}
        onChange={e => setInputText(e.target.value)}
        placeholder="Paste written feedback here..."
      />

      <div style={styles.options}>
        <label>
          <input
            type="checkbox"
            name="simplify"
            checked={options.simplify}
            onChange={handleOptionChange}
          />
          Simplify language
        </label>

        <label>
          <input
            type="checkbox"
            name="soften"
            checked={options.soften}
            onChange={handleOptionChange}
          />
          Soften tone
        </label>

        <label>
          <input
            type="checkbox"
            name="caseSupport"
            checked={options.caseSupport}
            onChange={handleOptionChange}
          />
          Add case support
        </label>
      </div>

      <button style={styles.button} onClick={handleGenerate}>
        Generate
      </button>

      <label style={styles.label}>Output</label>
      <textarea
        style={{
          ...styles.textarea,
          backgroundColor: '#f7f7f7',
          color: '#111',
          WebkitTextFillColor: '#111',
        }}
        value={outputText}
        readOnly
      />
    </div>
  )
}

const styles = {
  container: {
    maxWidth: '800px',
    margin: '40px auto',
    padding: '20px',
    fontFamily: 'sans-serif',
  },
  label: {
    fontWeight: 'bold',
    display: 'block',
    marginBottom: '8px',
  },
  textarea: {
    width: '100%',
    minHeight: '140px',
    padding: '10px',
    marginBottom: '20px',
    fontSize: '14px',
  },
  options: {
    display: 'flex',
    gap: '20px',
    marginBottom: '20px',
  },
  button: {
    padding: '10px 16px',
    fontSize: '16px',
    cursor: 'pointer',
    marginBottom: '20px',
  },
}
