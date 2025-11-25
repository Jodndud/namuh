import ActionButton from './ActionButton'

export default function QuickActionButtons() {
  const actions = [
    { label: 'Manual Capture', color: 'cyan' as const },
    { label: 'Pause Recording', color: 'purple' as const },
    { label: 'Settings', color: 'gray' as const }
  ]

  return (
    <div className="space-y-2">
      {actions.map((action, index) => (
        <ActionButton
          key={index}
          color={action.color}
          variant="full"
        >
          {action.label}
        </ActionButton>
      ))}
    </div>
  )
}