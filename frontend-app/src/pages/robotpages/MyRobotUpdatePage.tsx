import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import MyRobotButton from '../../components/HomePage/MyRobotButton'
import MyRobotDeleteModal from '../../components/robot/MyRobotDeleteModal'
import FootNavbar from '../../components/footernavbar/FootNavbar'
import BackButton from '../../components/Common/BackButton'

export default function MyRobotUpdatePage() {
  const navigate = useNavigate()
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [robotnickname, setRobotNickname] = useState('')
  const [selectedCallWord, setSelectedCallWord] = useState('')
  const handleSaveClick = () => {
    navigate('/home')
  }
  const handleWifiChangeClick = () => {
    navigate('/robot/wifi/finding')
  }
  const handleMyRobotDeleteClick = () => {
    setIsDeleteOpen(true)
  }
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold">나의 휴머노이드 로봇</h1>
      </header>

      <main className="flex-1 flex flex-col justify-between px-4 pb-28">
        
        <div className="flex flex-col space-y-4">
          <MyRobotButton disabled={true} />
          {/* 연결된 휴머노이드 로봇 S/N */}
          <div className="flex flex-col space-y-2">
            <p className="pl-2 text-left text-md select-none">연결된 휴머노이드 로봇 S/N</p>
            <input
              type="text" className="w-full p-4 border border-gray-300 rounded-2xl theme-card select-none"
              value="SN-24K9-7H3Q-8M2A"
              disabled
            />
          </div>

          {/* 연결된 Wi-Fi */}
          <div className="flex flex-col space-y-2">
            <p className="pl-2 text-left text-md select-none">연결된 Wi-Fi</p>
            <div className="flex gap-2 justify-between items-center">
              <input
                type="text" className="flex-2 w-full p-4 border border-gray-300 rounded-2xl theme-card select-none"
                value="SSAFY_201"
                disabled />
              <button
                type="button"
                className="flex-1 w-full text-sm p-4 rounded-2xl border
                active:bg-gray-300 select-none theme-button cursor-pointer"
                onClick={handleWifiChangeClick}>
                변경하기
              </button>
            </div>
          </div>

          {/* 나의 로봇 별명 */}
          <div className="flex flex-col space-y-2">
            <p className="pl-2 text-left text-md select-none">나의 로봇 별명</p>
            <input
              type="text"
              className="w-full p-4 border border-gray-300 rounded-2xl"
              value={robotnickname}
              placeholder="로봇 별명을 입력하세요"
              onChange={(e) => setRobotNickname(e.target.value)}
            />
          </div>

          {/* 호출어 설정 */}
          <div className="flex flex-col space-y-2">
            <p className="pl-2 text-left text-md select-none">호출어 설정</p>
            <select
              className={`w-full p-4 border border-gray-300 rounded-2xl ${selectedCallWord ? 'text-black' : 'text-gray-400'}`}
              value={selectedCallWord}
              onChange={(e) => setSelectedCallWord(e.target.value)}
            >
              <option value="" disabled>토리야</option>
              <option value="호출어 1">토리야</option>
            </select>
          </div>
          
          {/* 로봇 연동 해제 버튼 */}
          <button className="w-full pr-2 pb-3 text-right text-sm active:text-red-500 active:font-bold cursor-pointer select-none"
          onClick={handleMyRobotDeleteClick}>연동 해제
          </button>
        </div>

        {/* 저장하기 버튼 */}
        <button
          className="w-full rounded-2xl p-4 active:bg-lime-500 active:font-bold active:text-white theme-button cursor-pointer border select-none"
          onClick={handleSaveClick}>
          저장하기
        </button>
      </main>
      <FootNavbar />
      <MyRobotDeleteModal isOpen={isDeleteOpen} onClose={() => setIsDeleteOpen(false)} />
    </div>
  )
}