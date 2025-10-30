import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
      setSuccess(false)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file')
      return
    }

    setLoading(true)
    setProgress(0)
    setError(null)
    setSuccess(false)

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) return prev
        return prev + 2
      })
    }, 500)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Use relative path in production, absolute in development
      const apiUrl = import.meta.env.PROD 
        ? '/format' 
        : 'http://localhost:8000/format'
      
      // Simple retry for transient 502/504/network errors
      const doRequest = async (): Promise<Response> => {
        let attempt = 0
        let lastErr: any
        while (attempt < 3) {
          try {
            const resp = await fetch(apiUrl, { method: 'POST', body: formData })
            if (resp.status === 502 || resp.status === 504) {
              throw new Error(`Upstream ${resp.status}`)
            }
            return resp
          } catch (e) {
            lastErr = e
            attempt++
            const delay = 500 * Math.pow(2, attempt - 1)
            await new Promise((r) => setTimeout(r, delay))
          }
        }
        throw lastErr ?? new Error('Network error')
      }

      const response = await doRequest()

      if (!response.ok) {
        let details = ''
        try {
          details = await response.text()
        } catch {}
        throw new Error(`Failed to format transcript (${response.status})${details ? `: ${details.slice(0, 300)}` : ''}`)
      }

      setProgress(95)
      // Download the formatted file
      const blob = await response.blob()
      setProgress(100)
      
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `formatted_${file.name.replace('.txt', '')}.docx`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setSuccess(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      clearInterval(progressInterval)
      setProgress(100)
      setTimeout(() => setLoading(false), 1000)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ORU Transcript Formatter
          </h1>
          <p className="text-lg text-gray-600">
            Upload your raw transcript and get a professionally formatted Word document
          </p>
        </div>

        {/* Upload Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            {!file ? (
              <div>
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-4h12m-4 4v12m0 0l-4-4m4 4l4-4"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="mt-4">
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold inline-block transition-colors"
                  >
                    Select a transcript file
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".txt"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    Choose a .txt file to format
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <svg
                  className="mx-auto h-12 w-12 text-green-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="mt-4 text-lg font-semibold text-gray-900">
                  {file.name}
                </p>
                <p className="mt-2 text-sm text-gray-500">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
                <button
                  onClick={() => setFile(null)}
                  className="mt-4 text-sm text-red-600 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {file && (
            <div className="mt-6 flex gap-4">
              <button
                onClick={handleUpload}
                disabled={loading}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                  loading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {loading ? 'Formatting...' : 'Format & Download'}
              </button>
            </div>
          )}

          {/* Progress Bar */}
          {loading && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Formatting transcript...</span>
                <span className="text-sm font-medium text-blue-600">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-2">This may take 2-3 minutes. Please don't close this page.</p>
            </div>
          )}

          {/* Messages */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800">
                ✅ Transcript formatted successfully! Download started.
              </p>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Professional Formatting</h3>
            <p className="text-sm text-gray-600">Industry-standard transcript layout</p>
          </div>

          <div className="text-center">
            <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">AI-Powered</h3>
            <p className="text-sm text-gray-600">Claude AI ensures perfect readability</p>
          </div>

          <div className="text-center">
            <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m6.364-6.364L19 5m-7-7l2.879 2.879M5 19l2.879-2.879m0 0L5 13.121m2.879 2.879L13.121 19M9.121 9.121l-2.879 2.879" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">ORU Branding</h3>
            <p className="text-sm text-gray-600">Preserves World Impact branding</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App