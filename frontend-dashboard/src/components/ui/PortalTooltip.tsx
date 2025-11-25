import { ReactNode } from 'react'
import { createPortal } from 'react-dom'

type Placement = 'right' | 'left' | 'top' | 'bottom'

export default function PortalTooltip({
  anchorRect,
  visible,
  placement = 'right',
  offset = 8,
  className,
  children,
}: {
  anchorRect: DOMRect | null
  visible: boolean
  placement?: Placement
  offset?: number
  className?: string
  children: ReactNode
}) {
  if (!visible || !anchorRect) return null

  let top = anchorRect.top + window.scrollY
  let left = anchorRect.left + window.scrollX

  switch (placement) {
    case 'right':
      left = anchorRect.right + offset + window.scrollX
      top = anchorRect.top + window.scrollY
      break
    case 'left':
      left = anchorRect.left - offset + window.scrollX
      top = anchorRect.top + window.scrollY
      break
    case 'top':
      left = anchorRect.left + window.scrollX
      top = anchorRect.top - offset + window.scrollY
      break
    case 'bottom':
      left = anchorRect.left + window.scrollX
      top = anchorRect.bottom + offset + window.scrollY
      break
  }

  return createPortal(
    <div
      className={`fixed z-[9999] ${className ?? ''}`}
      style={{ top, left }}
      role="tooltip"
      aria-hidden={!visible}
    >
      {children}
    </div>,
    document.body
  )
}


