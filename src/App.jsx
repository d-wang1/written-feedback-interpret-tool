import { useMemo, useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import FeedbackForm from './components/FeedbackForm'
import OutputPanel from './components/OutputPanel'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Features from './components/Features'
import About from './components/About'
import Contact from './components/Contact'
import styles from './App.module.css'
import Login from './components/Login'


function HomePage() {
  const [inputText, setInputText] = useState('')
  const [outputText, setOutputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [options, setOptions] = useState({
    simplify: false,
    soften: false,
    caseSupport: false,
  })

  useEffect(() => {
    document.title = 'EchoAI - Written Feedback Interpretation Tool'
  }, [])

  const canGenerate = useMemo(() => inputText.trim().length > 0, [inputText])

  async function handleGenerate() {
    setIsLoading(true)
    const res = await fetch("/api/interpret", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputText,
        options,
      }),
    })

    const data = await res.json()
    setIsLoading(false)
    setOutputText(data.output || data.detail || "")
  }

  function handleClear() {
    setInputText('')
    setOutputText('')
    setOptions({ simplify: false, soften: false, caseSupport: false })
  }

  return (
    <>
      <div className={styles.hero}>
        <div className={styles.heroContent}>
          <h1 className={styles.title}>EchoAI</h1>
          <p className={styles.subtitle}>
            Transform written feedback into clear, actionable insights
          </p>
        </div>
      </div>

      <div className={styles.container}>
        <div className={styles.grid}>
          <FeedbackForm
            inputText={inputText}
            onInputChange={setInputText}
            options={options}
            onOptionsChange={setOptions}
            onGenerate={handleGenerate}
            onClear={handleClear}
            canGenerate={canGenerate}
            isLoading={isLoading}
          />

          <OutputPanel outputText={outputText} />
        </div>
      </div>
    </>
  )
}

export default function App() {
  return (
    <Router>
      <div className={styles.app}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={
            <>
              <Navbar />
              <main className={styles.main}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/features" element={<Features />} />
                  <Route path="/about" element={<About />} />
                  <Route path="/contact" element={<Contact />} />
                </Routes>
              </main>
              <Footer />
            </>
          } />
        </Routes>
      </div>
    </Router>
  )
}