import { useNavigate } from 'react-router-dom'
import MyRobotButton from '../../components/HomePage/MyRobotButton'
import FootNavbar from '../../components/footernavbar/FootNavbar'
import OpenViduViewer from '../../components/video/OpenViduViewer'
import BackButton from '../../components/Common/BackButton'

export default function MyRobotDetailPage() {
  const navigate = useNavigate()

  const handleMyRobotUpdateClick = () => {
    navigate('/robot/update')
  }
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold select-none">나의 휴머노이드 로봇</h1>
      </header>

      <main className="flex-1 flex flex-col justify-between px-4 pb-4">
        
        <div className="flex flex-col space-y-4">
          <MyRobotButton disabled={true} />
          <div className="w-full rounded-2xl overflow-hidden">
            <OpenViduViewer className="min-h-[240px]" />
          </div>
          <button className="w-full bg-white p-4 rounded-2xl border border-gray-200
          active:bg-gray-200 active:font-bold select-none cursor-pointer theme-button select-none"
          onClick={handleMyRobotUpdateClick}>
            로봇 정보 수정
          </button>
        </div>
      </main>
      <FootNavbar />
    </div>
  )
}