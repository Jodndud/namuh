import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MyRobotButton from '../components/HomePage/MyRobotButton'
// import DiaryButton from '../components/HomePage/DiaryButton'
import VideoButton from '../components/HomePage/VideoButton'
import MyPageButton from '../components/HomePage/MyPageButton'
import FootNavbar from '../components/footernavbar/FootNavbar'


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

export default function HomePage() {
  const navigate = useNavigate()
  const [nickname, setNickname] = useState<string>('')

  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    const parsedNickname = parseNicknameFromAccessToken(token)
    if (parsedNickname) {
      setNickname(parsedNickname)
    }
  }, [])

  const handleMyRobotListClick = () => {
    navigate('/robot/list')
  }
  return (
    <section className="relative min-h-screen w-full bg-cover bg-center bg-no-repeat">
      {/* 나의 휴머노이드 로봇 */}
      <div className="bg-lime-500 pt-4 pb-2 px-4 space-y-1">
      <h1 className="flex items-start justify-center text-4xl font-bold text-white select-none [-webkit-touch-callout:none]">
        NAMUH
        <span className="border border-white rounded-full text-sm px-1">S</span>
      </h1>
        {/* 나의 휴머노이드 목록 버튼 */}
        <MyRobotButton />
        <button
          className="text-white text-right w-full text-sm select-none select-none cursor-pointer"
          onClick={handleMyRobotListClick}>로봇 목록 <span>&gt;</span></button>
      </div>
      {/* 일기/영상/마이페이지 Button */}
      <div className="flex flex-col px-4">
        <h1 className="text-xl py-4 px-1 text-left select-none [-webkit-touch-callout:none]">
          <strong>{nickname || 'nickname'}</strong>님, 안녕하세요!</h1>
        <div className="flex flex-col space-y-4">
          {/* 일기 버튼
          <DiaryButton /> */}
          {/* 영상 버튼 */}
          <VideoButton />
          {/* 마이페이지 버튼 */}
          <MyPageButton />
        </div>
      </div>
      <FootNavbar />
    </section>
  )
}

