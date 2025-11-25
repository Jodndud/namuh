import { useEffect, useState } from 'react'

export type ThemeMode = 'system' | 'light' | 'dark'

export function applyTheme(mode: ThemeMode) {
  const root = document.documentElement

  if (mode === 'system') {
    const prefersDark = window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    const resolved = prefersDark ? 'dark' : 'light'
    root.setAttribute('data-theme', resolved)
    root.style.setProperty('color-scheme', resolved)
    return
  }

  root.setAttribute('data-theme', mode)
  // Inline style to help built-in UI elements (dropdowns, form controls) match theme
  root.style.setProperty('color-scheme', mode)
}

type Props = {
  value?: ThemeMode
  onChange?: (mode: ThemeMode) => void
  persist?: boolean
}

export default function SystemTheme({ value, onChange, persist = true }: Props) {
  const [internalMode, setInternalMode] = useState<ThemeMode>('system')
  const isControlled = value !== undefined
  const mode = isControlled ? (value as ThemeMode) : internalMode

  useEffect(() => {
    if (isControlled) return
    const saved = (localStorage.getItem('theme-preference') as ThemeMode | null) || 'system'
    setInternalMode(saved)
    applyTheme(saved)
  }, [isControlled])

  // Keep system theme in sync with OS preference changes
  useEffect(() => {
    if (mode !== 'system') return
    const media = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e: MediaQueryListEvent) => {
      applyTheme(e.matches ? 'dark' : 'light')
    }
    // Ensure immediate alignment on mount
    applyTheme(media.matches ? 'dark' : 'light')
    if (typeof media.addEventListener === 'function') {
      media.addEventListener('change', handleChange)
    } else {
      ;(media as any).addListener?.(handleChange)
    }
    return () => {
      if (typeof media.removeEventListener === 'function') {
        media.removeEventListener('change', handleChange)
      } else {
        ;(media as any).removeListener?.(handleChange)
      }
    }
  }, [mode])

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const next = e.target.value as ThemeMode
    if (!isControlled) {
      setInternalMode(next)
      if (persist) {
        localStorage.setItem('theme-preference', next)
      }
    }
    if (persist) {
      applyTheme(next)
    }
    onChange?.(next)
  }

  return (
    <select
      aria-label="테마 선택"
      className="w-full p-4 border cursor-pointer select-none border-gray-300 rounded-2xl bg-white"
      value={mode}
      onChange={handleChange}
    >
      <option value="system" className="cursor-pointer">시스템 설정</option>
      <option value="light" className="cursor-pointer">라이트 모드</option>
      <option value="dark" className="cursor-pointer">다크 모드</option>
    </select>
  )
}

