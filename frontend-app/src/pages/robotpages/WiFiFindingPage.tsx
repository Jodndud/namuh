import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import LoadingPaperPlain from '../../components/Common/LoadingPaperPlain'
import BackButton from '../../components/Common/BackButton'

export default function WiFiFindingPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const timerId = setTimeout(() => {
      navigate('/robot/wifi/list')
    }, 1500)

    return () => clearTimeout(timerId)
  }, [navigate])
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold">Wi-Fi 연결</h1>
      </header>

      <main className="flex-1 flex flex-col justify-center items-center px-4 pb-4">
        <LoadingPaperPlain />
        <h1 className="text-lg">연결 가능한 Wi-Fi를 찾는 중입니다...</h1>
      </main>
    </div>
  )
}