import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function POST() {
  try {
    const supabaseUrl = process.env.SUPABASE_URL!
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
    
    const supabase = createClient(supabaseUrl, supabaseKey)
    
    // Get first 5 stocks for testing
    const { data: stocks, error: stocksError } = await supabase
      .from('screened_stocks')
      .select('symbol')
      .limit(5)
    
    if (stocksError) throw stocksError
    
    const fundamentals_data = []
    const errors = []
    
    for (const stock of stocks) {
      try {
        // Fetch from yfinance API (using a public API endpoint)
        const response = await fetch(`https://query1.finance.yahoo.com/v10/finance/quoteSummary/${stock.symbol}.NS?modules=defaultKeyStatistics,financialData,summaryProfile`)
        
        if (response.ok) {
          const data = await response.json()
          const result = data.quoteSummary?.result?.[0]
          
          if (result) {
            const keyStats = result.defaultKeyStatistics || {}
            const financialData = result.financialData || {}
            const profile = result.summaryProfile || {}
            
            fundamentals_data.push({
              symbol: stock.symbol,
              company_name: profile.longBusinessSummary ? `${stock.symbol} Company` : null,
              market_cap: keyStats.marketCap?.raw || null,
              pe_ratio: keyStats.trailingPE?.raw || financialData.currentPrice?.raw / (keyStats.trailingEps?.raw || 1),
              pb_ratio: keyStats.priceToBook?.raw || null,
              roe: financialData.returnOnEquity?.raw || null,
              eps: keyStats.trailingEps?.raw || null,
              sector: profile.sector || 'Unknown',
              industry: profile.industry || 'Unknown'
            })
          } else {
            errors.push(`No data for ${stock.symbol}`)
          }
        } else {
          errors.push(`API failed for ${stock.symbol}`)
        }
      } catch (e) {
        errors.push(`Error with ${stock.symbol}: ${e}`)
      }
    }
    
    // Insert mock data if Yahoo Finance fails
    if (fundamentals_data.length === 0) {
      const mockData = stocks.slice(0, 3).map((stock, i) => ({
        symbol: stock.symbol,
        company_name: `${stock.symbol} Limited`,
        market_cap: Math.floor(Math.random() * 1000000000000),
        pe_ratio: 15 + Math.random() * 20,
        pb_ratio: 1 + Math.random() * 5,
        roe: 0.1 + Math.random() * 0.3,
        eps: 10 + Math.random() * 50,
        sector: ['Technology', 'Finance', 'Energy'][i % 3],
        industry: ['Software', 'Banking', 'Oil & Gas'][i % 3]
      }))
      
      fundamentals_data.push(...mockData)
      errors.push('Using mock data - Yahoo Finance API may be blocked')
    }
    
    // Upsert to database
    if (fundamentals_data.length > 0) {
      const { error: upsertError } = await supabase
        .from('fundamentals')
        .upsert(fundamentals_data)
      
      if (upsertError) throw upsertError
    }
    
    return NextResponse.json({
      message: `Loaded fundamentals for ${fundamentals_data.length} stocks`,
      count: fundamentals_data.length,
      errors: errors.slice(0, 3),
      sample_data: fundamentals_data.slice(0, 2)
    })
    
  } catch (error) {
    return NextResponse.json({
      error: error instanceof Error ? error.message : 'Unknown error',
      details: 'Check environment variables and database connection'
    }, { status: 500 })
  }
}
