interface ActionButtonProps {
  children: React.ReactNode
  color: 'cyan' | 'purple' | 'gray' | 'red' | 'blue' | 'green'
  variant?: 'default' | 'full'
  onClick?: () => void
}

export default function ActionButton({ 
  children, 
  color, 
  variant = 'default',
  onClick 
}: ActionButtonProps) {
  const getColorClasses = (color: string) => {
    const colorMap: Record<string, string> = {
      cyan: 'bg-cyan-500/20 hover:bg-cyan-500/30 border-cyan-500/50 text-cyan-300',
      purple: 'bg-purple-500/20 hover:bg-purple-500/30 border-purple-500/50 text-purple-300',
      gray: 'bg-gray-500/20 hover:bg-gray-500/30 border-gray-500/50 text-gray-300',
      red: 'bg-red-500/20 hover:bg-red-500/30 border-red-500/50 text-red-300',
      blue: 'bg-blue-500/20 hover:bg-blue-500/30 border-blue-500/50 text-blue-300',
      green: 'bg-green-500/20 hover:bg-green-500/30 border-green-500/50 text-green-300'
    }
    return colorMap[color] || colorMap.gray
  }

  const getWidthClass = () => {
    return variant === 'full' ? 'w-full' : ''
  }

  return (
    <button
      className={`py-3 px-4 border rounded text-sm transition-all ${getColorClasses(color)} ${getWidthClass()}`}
      onClick={onClick}
    >
      {children}
    </button>
  )
}