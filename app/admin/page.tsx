'use client'

import { useState } from 'react'

export default function Admin() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a CSV file')
      return
    }

    setUploading(true)
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/upload-screened`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const result = await response.json()
      setMessage(`Success: ${result.message}`)
      setFile(null)
      
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''

    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Upload failed'}`)
    } finally {
      setUploading(false)
    }
  }

  const triggerBackfill = async () => {
    setUploading(true)
    setMessage('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/trigger_backfill`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Backfill failed')
      }

      const result = await response.json()
      setMessage(`Success: ${result.message}`)

    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Backfill failed'}`)
    } finally {
      setUploading(false)
    }
  }

  const loadFundamentals = async () => {
    setUploading(true)
    setMessage('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/load_fundamentals`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Load fundamentals failed')
      }

      const result = await response.json()
      setMessage(`Success: ${result.message}`)

    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Load fundamentals failed'}`)
    } finally {
      setUploading(false)
    }
  }

  const runScanner = async () => {
    setUploading(true)
    setMessage('')

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/run_scanner`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Scanner failed')
      }

      const result = await response.json()
      setMessage(`Success: ${result.message}`)

    } catch (error) {
      setMessage(`Error: ${error instanceof Error ? error.message : 'Scanner failed'}`)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>

      <div className="space-y-6">
        {/* Upload CSV */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Upload Screened Stocks</h2>
          <p className="text-gray-600 mb-4">
            Upload a CSV file with stock symbols. The CSV should have a 'Symbol' column.
          </p>
          
          <div className="space-y-4">
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            
            <button
              onClick={handleUpload}
              disabled={uploading || !file}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload CSV'}
            </button>
          </div>
        </div>

        {/* Data Operations */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Data Operations</h2>
          
          <div className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Load Fundamentals from EQUITY_L</h3>
              <p className="text-gray-600 text-sm mb-3">
                Load all NSE stocks from EQUITY_L.csv and fetch fundamental data using yfinance.
              </p>
              <button
                onClick={loadFundamentals}
                disabled={uploading}
                className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {uploading ? 'Loading...' : 'Load Fundamentals'}
              </button>
            </div>

            <div>
              <h3 className="font-medium mb-2">Trigger Data Backfill</h3>
              <p className="text-gray-600 text-sm mb-3">
                Fetch historical OHLC data for all screened stocks from Shoonya.
              </p>
              <button
                onClick={triggerBackfill}
                disabled={uploading}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {uploading ? 'Running...' : 'Trigger Backfill'}
              </button>
            </div>

            <div>
              <h3 className="font-medium mb-2">Run Insight Scanner</h3>
              <p className="text-gray-600 text-sm mb-3">
                Run all insight algorithms on the latest data for all stocks.
              </p>
              <button
                onClick={runScanner}
                disabled={uploading}
                className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {uploading ? 'Running...' : 'Run Scanner'}
              </button>
            </div>
          </div>
        </div>

        {/* Status Message */}
        {message && (
          <div className={`p-4 rounded-lg ${
            message.startsWith('Success') 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {message}
          </div>
        )}
      </div>
    </div>
  )
}
