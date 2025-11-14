import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from '@heroicons/react/24/solid'

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

interface InsightsListProps {
  insights: Insight[]
}

export default function InsightsList({ insights }: InsightsListProps) {
  const getSignalIcon = (signalType: string) => {
    switch (signalType) {
      case 'BUY':
        return <ArrowUpIcon className="w-4 h-4 text-bull" />
      case 'SELL':
        return <ArrowDownIcon className="w-4 h-4 text-bear" />
      default:
        return <MinusIcon className="w-4 h-4 text-gray-500" />
    }
  }

  const getSignalColor = (signalType: string) => {
    switch (signalType) {
      case 'BUY':
        return 'text-bull'
      case 'SELL':
        return 'text-bear'
      default:
        return 'text-gray-500'
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'FORMULA':
        return 'bg-blue-100 text-blue-800'
      case 'PATTERN':
        return 'bg-purple-100 text-purple-800'
      case 'SENTIMENT':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (insights.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No insights found
      </div>
    )
  }

  // Group insights by category
  const groupedInsights = insights.reduce((acc, insight) => {
    const category = insight.insight_types.category
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(insight)
    return acc
  }, {} as Record<string, Insight[]>)

  return (
    <div className="space-y-4">
      {Object.entries(groupedInsights).map(([category, categoryInsights]) => (
        <div key={category}>
          <h3 className="font-medium text-sm text-gray-700 mb-2">
            {category.charAt(0) + category.slice(1).toLowerCase()}
          </h3>
          <div className="space-y-2">
            {categoryInsights.map((insight) => (
              <div key={insight.id} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getSignalIcon(insight.signal_type)}
                    <span className={`font-medium ${getSignalColor(insight.signal_type)}`}>
                      {insight.signal_type || 'NEUTRAL'}
                    </span>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${getCategoryColor(insight.insight_types.category)}`}>
                    {insight.insight_types.category}
                  </span>
                </div>
                
                <div className="text-sm">
                  <div className="font-medium">{insight.insight_types.name}</div>
                  <div className="text-gray-600 mt-1">
                    Price: ₹{insight.price?.toFixed(2) || 'N/A'}
                  </div>
                  <div className="text-gray-600">
                    Score: {insight.score?.toFixed(3) || 'N/A'}
                  </div>
                  <div className="text-gray-500 text-xs mt-1">
                    {new Date(insight.detected_on).toLocaleDateString()}
                  </div>
                </div>

                {insight.attributes && Object.keys(insight.attributes).length > 0 && (
                  <details className="mt-2">
                    <summary className="text-xs text-gray-500 cursor-pointer">
                      View Details
                    </summary>
                    <div className="mt-1 text-xs text-gray-600 bg-white p-2 rounded">
                      <pre className="whitespace-pre-wrap">
                        {JSON.stringify(insight.attributes, null, 2)}
                      </pre>
                    </div>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
