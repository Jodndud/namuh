export default function TodayStatistics() {
  const stats = [
    {
      label: 'Smiles Detected',
      value: '47',
      color: 'cyan',
      gradient: true
    },
    {
      label: 'Clips Saved',
      value: '23',
      color: 'purple',
      gradient: false
    },
    {
      label: 'Avg. Confidence',
      value: '94.2%',
      color: 'green',
      gradient: false
    }
  ]

  const getCardClasses = (color: string, gradient: boolean) => {
    if (gradient) {
      return 'p-4 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 border border-cyan-500/30 rounded-lg'
    }
    
    const borderColor = {
      purple: 'border-cyan-500/20',
      green: 'border-cyan-500/20'
    }[color] || 'border-cyan-500/20'
    
    return `p-4 bg-black/40 border ${borderColor} rounded`
  }

  const getValueClasses = (color: string) => {
    const colorClasses = {
      cyan: 'text-cyan-400',
      purple: 'text-purple-400',
      green: 'text-green-400'
    }[color] || 'text-gray-400'
    
    return `text-2xl font-bold ${colorClasses}`
  }

  const getValueSize = (color: string) => {
    return color === 'cyan' ? 'text-3xl' : 'text-2xl'
  }

  return (
    <div className="space-y-3">
      {stats.map((stat, index) => (
        <div key={index} className={getCardClasses(stat.color, stat.gradient)}>
          <div className="text-xs text-gray-400 mb-1">{stat.label}</div>
          <div className={`${getValueSize(stat.color)} font-bold ${getValueClasses(stat.color)}`}>
            {stat.value}
          </div>
        </div>
      ))}
    </div>
  )
}