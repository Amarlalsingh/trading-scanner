import Link from 'next/link'
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'

interface Stock {
  symbol: string
  exchange: string
  combined_score?: number
  last_signal?: string
  fundamentals?: {
    market_cap?: number
    pe_ratio?: number
    sector?: string
  }
}

interface StockCardProps {
  stock: Stock
}

export default function StockCard({ stock }: StockCardProps) {
  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-500'
    if (score > 0.3) return 'text-bull'
    if (score < -0.3) return 'text-bear'
    return 'text-yellow-500'
  }

  const getScoreIcon = (score?: number) => {
    if (!score) return null
    if (score > 0) return <ArrowUpIcon className="w-4 h-4" />
    return <ArrowDownIcon className="w-4 h-4" />
  }

  return (
    <Link href={`/stock/${stock.symbol}`}>
      <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow cursor-pointer border">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="font-semibold text-lg">{stock.symbol}</h3>
            <p className="text-sm text-gray-500">{stock.exchange}</p>
          </div>
          <div className={`flex items-center ${getScoreColor(stock.combined_score)}`}>
            {getScoreIcon(stock.combined_score)}
            <span className="ml-1 font-medium">
              {stock.combined_score ? stock.combined_score.toFixed(2) : 'N/A'}
            </span>
          </div>
        </div>
        
        <div className="mt-3 pt-3 border-t">
          {stock.fundamentals?.sector && (
            <div className="text-xs text-blue-600 mb-1">
              {stock.fundamentals.sector}
            </div>
          )}
          <div className="text-xs text-gray-500">
            Last Signal: {stock.last_signal || 'None'}
          </div>
          {stock.fundamentals?.pe_ratio && (
            <div className="text-xs text-gray-500">
              PE: {stock.fundamentals.pe_ratio.toFixed(1)}
            </div>
          )}
        </div>
      </div>
    </Link>
  )
}
