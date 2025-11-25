import { useNavigate } from 'react-router-dom'
import BackButton from '../../components/Common/BackButton'


export default function RobotSelectPage() {
  const navigate = useNavigate()
  const handleRobotSelectClick = () => {
    navigate('/robot/wifi/finding')
  }
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold">휴머노이드 로봇 연결</h1>
      </header>

      <main className="flex-1 flex flex-col px-4 pb-4">
        <button
          className="flex items-center justify-start border-b border-gray-300 p-4
          active:bg-gray-200 select-none cursor-pointer"
          onClick={handleRobotSelectClick}>
          <p>SN-24K9-7H3Q-8M2A</p>
        </button>
      </main>
    </div>
  )
}