import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import LoadingRobot from '../../components/Common/LoadingRobot'
import BackButton from '../../components/Common/BackButton'

export default function RobotFindingPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const timerId = setTimeout(() => {
      navigate('/robot/select')
    }, 1500)

    return () => clearTimeout(timerId)
  }, [navigate])
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold">휴머노이드 로봇 연결</h1>
      </header>

      <main className="flex px-4 pb-4">
        <div className="">
          <LoadingRobot />
          <h1>연결 가능한 휴머노이드 로봇을 찾는 중입니다...</h1>
        </div>
      </main>
    </div>
  )
}