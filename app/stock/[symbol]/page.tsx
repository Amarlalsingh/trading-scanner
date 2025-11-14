'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import StockChart from '../../components/StockChart'
import InsightsList from '../../components/InsightsList'
import { supabase } from '../../lib/supabase'

interface Insight {
  id: number
  signal_type: string
  price: number
  score: number
  detected_on: string
  attributes: any
  insight_types: {
    code: string
    name: string
    category: string
  }
}

export default function StockDetail() {
  const params = useParams()
  const symbol = params.symbol as string
  const [insights, setInsights] = useState<Insight[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (symbol) {
      fetchInsights()
    }
  }, [symbol])

  const fetchInsights = async () => {
    try {
      const { data, error } = await supabase
        .from('insights')
        .select(`
          *,
          insight_types(code, name, category),
          insight_images(img_url, meta)
        `)
        .eq('symbol', symbol)
        .order('detected_on', { ascending: false })
        .limit(50)

      if (error) throw error
      setInsights(data || [])
    } catch (error) {
      console.error('Error fetching insights:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">{symbol}</h1>
        <p className="text-gray-600">Stock Analysis & Insights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-4">Price Chart</h2>
            <StockChart symbol={symbol} />
          </div>
        </div>

        {/* Insights Section */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-xl font-semibold mb-4">Recent Insights</h2>
            {loading ? (
              <div className="text-center py-8">Loading insights...</div>
            ) : (
              <InsightsList insights={insights} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
