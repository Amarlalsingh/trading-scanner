'use client'

import { useState, useEffect } from 'react'
import StockCard from './components/StockCard'
import { supabase } from './lib/supabase'

interface Stock {
  symbol: string
  exchange: string
  combined_score?: number
  last_signal?: string
}

export default function Dashboard() {
  const [stocks, setStocks] = useState<Stock[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStocks()
  }, [])

  const fetchStocks = async () => {
    try {
      console.log('Fetching stocks from Supabase...')
      // Get screened stocks with optional scores and fundamentals
      const { data: stocksData, error } = await supabase
        .from('screened_stocks')
        .select(`
          symbol,
          exchange,
          meta,
          stock_daily_scores(combined_score, date),
          fundamentals(market_cap, pe_ratio, sector)
        `)
        .limit(50)

      console.log('Supabase response:', { data: stocksData, error })

      if (error) {
        console.error('Supabase error:', error)
        throw error
      }

      // Process data to get latest score per stock
      const stocksMap = new Map()
      stocksData?.forEach((stock: any) => {
        if (!stocksMap.has(stock.symbol)) {
          const latestScore = stock.stock_daily_scores?.[0]
          stocksMap.set(stock.symbol, {
            symbol: stock.symbol,
            exchange: stock.exchange,
            combined_score: latestScore?.combined_score,
            fundamentals: stock.fundamentals,
            company_name: stock.meta?.company_name
          })
        }
      })

      setStocks(Array.from(stocksMap.values()))
    } catch (error) {
      console.error('Error fetching stocks:', error)
    } finally {
      setLoading(false)
    }
  }

  const testAPI = async (endpoint: string) => {
    try {
      const response = await fetch(`/api/${endpoint}`)
      const data = await response.json()
      alert(`${endpoint} API Response: ${JSON.stringify(data, null, 2)}`)
    } catch (error) {
      alert(`${endpoint} API Error: ${error}`)
    }
  }

  const loadFundamentals = async () => {
    try {
      const response = await fetch('/api/fundamentals', { method: 'POST' })
      const data = await response.json()
      alert(`Fundamentals loaded: ${JSON.stringify(data, null, 2)}`)
      fetchStocks() // Refresh the stocks list
    } catch (error) {
      alert(`Fundamentals Error: ${error}`)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading stocks...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Trading Dashboard</h1>
        <div className="text-sm text-gray-600">
          {stocks.length} stocks tracked
        </div>
      </div>

      {/* API Test Buttons */}
      <div className="mb-6 p-4 bg-gray-100 rounded-lg">
        <h2 className="text-lg font-semibold mb-3">API Testing</h2>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => testAPI('health')}
            className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
          >
            Test Health API
          </button>
          <button
            onClick={loadFundamentals}
            className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
          >
            Load Fundamentals
          </button>
          <button
            onClick={() => testAPI('ohlc?symbol=RELIANCE')}
            className="bg-purple-500 text-white px-3 py-1 rounded text-sm hover:bg-purple-600"
          >
            Test OHLC API
          </button>
        </div>
      </div>

      {stocks.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 mb-4">No stocks found</p>
          <a 
            href="/admin" 
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Upload Stock List
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {stocks.map((stock) => (
            <StockCard key={stock.symbol} stock={stock} />
          ))}
        </div>
      )}
    </div>
  )
}
