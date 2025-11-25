import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import UserDeleteButton from '../../components/user/UserDeleteButton'
import UserDeleteModal from '../../components/user/UserDeleteModal'
import FootNavbar from '../../components/footernavbar/FootNavbar'
import BackButton from '../../components/Common/BackButton'
import api from '../../lib/api'
import SystemTheme, { applyTheme, type ThemeMode } from './SystemTheme'

function parseNicknameFromAccessToken(token: string | null): string | null {
  if (!token) return null
  try {
    const parts = token.split('.')
    if (parts.length < 2) return null
    const base64Url = parts[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(base64.length + (4 - (base64.length % 4 || 4)) % 4, '=')
    const jsonString = decodeURIComponent(
      atob(padded)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    const payload = JSON.parse(jsonString)
    return payload?.member?.nickname ?? null
  } catch {
    return null
  }
}

export default function MyPage() {
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [nickname, setNickname] = useState('')
  const [originalNickname, setOriginalNickname] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [originalTheme, setOriginalTheme] = useState<ThemeMode>('system')
  const [draftTheme, setDraftTheme] = useState<ThemeMode>('system')
  const themeCommittedRef = useRef(false)
  const navigate = useNavigate()
  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    const parsed = parseNicknameFromAccessToken(token)
    if (parsed) {
      setNickname(parsed)
      setOriginalNickname(parsed)
    }
    const savedTheme = (localStorage.getItem('theme-preference') as ThemeMode | null) || 'system'
    setOriginalTheme(savedTheme)
    setDraftTheme(savedTheme)
    applyTheme(savedTheme)

    return () => {
      if (!themeCommittedRef.current) {
        applyTheme(savedTheme)
      }
    }
  }, [])
  const handleSaveClick = async () => {
    try {
      setIsSaving(true)
      setSaveError(null)
      const isNicknameChanged = nickname.trim() !== originalNickname.trim()
      if (isNicknameChanged) {
        const res = await api.patch('/member/me', { nickname })
        const status = res.status
        if (status < 200 || status >= 300) {
          throw new Error(`HTTP ${status}`)
        }
        const data = res.data
        if (data && data.isSuccess === false) {
          throw new Error(data?.message ?? '닉네임 저장에 실패했습니다.')
        }

        // 저장 후 최신 닉네임이 반영된 토큰 재발급
        const refreshRes = await api.post('/auth/refresh', {}, { withCredentials: true })
        const authHeader = refreshRes.headers['authorization'] || refreshRes.headers['Authorization']
        const newAccessToken = String(authHeader || '').replace(/^Bearer\s+/i, '').trim()
        if (newAccessToken) {
          localStorage.setItem('accessToken', newAccessToken)
          const parsed = parseNicknameFromAccessToken(newAccessToken)
          if (parsed) setNickname(parsed)
        }
        setOriginalNickname(nickname.trim())
      }
      // 테마 커밋: 저장시에만 영구 반영
      if (draftTheme !== originalTheme) {
        localStorage.setItem('theme-preference', draftTheme)
        setOriginalTheme(draftTheme)
      }
      themeCommittedRef.current = true

      navigate('/home', { replace: true })
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : '알 수 없는 오류가 발생했습니다.')
    } finally {
      setIsSaving(false)
    }
  }
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold select-none">마이페이지</h1>
      </header>
      <main className="flex flex-col justify-between px-4 pb-4 gap-3">
        {/* 구글 연동 완료 박스 */}
        <div className="flex w-full space-x-2 justify-center items-center bg-white rounded-2xl p-4 border border-gray-300 theme-card select-none">
          <img src="/icons/GoogleIcon.png" alt="GoogleIcon" className="w-5 h-5" />
          <p>구글 연동 완료</p>
        </div>

        {/* 닉네임 */}
        <div className="flex flex-col space-y-2 py-4">
          <p className="pl-2 text-left text-md font-bold select-none">닉네임</p>
          <input
            type="text"
            className="w-full p-4 border border-gray-300 rounded-2xl bg-white"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
          />
          {saveError && <p className="pl-2 text-sm text-red-600">{saveError}</p>}
        </div>
        {/* 테마 선택 */}
        <div className="flex flex-col space-y-2 py-2 cursorselect-none">
          <p className="pl-2 text-left text-md font-bold">테마</p>
          <SystemTheme
            value={draftTheme}
            onChange={(m) => {
              setDraftTheme(m)
              applyTheme(m) // 미리보기만 적용
            }}
            persist={false}
          />
        </div>
        <UserDeleteButton onClick={() => setIsDeleteOpen(true)} />

        {/* 저장하기 버튼 */}
        {(() => {
          const isNicknameChanged = nickname.trim() !== originalNickname.trim()
          const isThemeChanged = draftTheme !== originalTheme
          const isButtonDisabled =
            isSaving || !nickname.trim() || (!isNicknameChanged && !isThemeChanged)
          const base =
            'w-full bg-gray-300 rounded-2xl p-4 border select-none theme-button select-none'
          const enabled =
            'active:bg-lime-500 active:font-bold active:text-white cursor-pointer theme-button select-none'
          const disabledCls =
            'opacity-60 cursor-not-allowed pointer-events-none'
          return (
        <button
            className={`${base} ${isButtonDisabled ? disabledCls : enabled}`}
            onClick={handleSaveClick}
            disabled={isButtonDisabled}>
          {isSaving ? '저장 중...' : '저장하기'}
        </button>
          )
        })()}
      </main>
      <UserDeleteModal isOpen={isDeleteOpen} onClose={() => setIsDeleteOpen(false)} />
      <FootNavbar />
    </div>
  )
}