import { useNavigate } from 'react-router-dom'
import BackButton from '../../components/Common/BackButton'

export default function WiFiListPage() {
  const navigate = useNavigate()
  const handleWiFiSelectClick = () => {
    navigate('/robot/detail')
  }
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold">Wi-Fi 연결</h1>
      </header>

      <main className="flex-1 flex flex-col items-start px-4 pb-4">
        <button
          className="flex items-center justify-between w-full border-b border-gray-300 p-4
          active:bg-gray-200 select-none cursor-pointer select-none"
          onClick={handleWiFiSelectClick}>
          <p className="text-lg">SSAFY_201</p>
          <div className="flex items-center gap-3">
            <img src="/icons/LockIcon.png" alt="Lock" className="w-5 h-5" />
            <img src="/icons/WiFiIcon.png" alt="WiFi" className="w-5 h-5" />
          </div>
        </button>
        <button
          className="flex items-center justify-between w-full border-b border-gray-300 p-4
          active:bg-gray-200 select-none cursor-pointer select-none"
          onClick={handleWiFiSelectClick}>
          <p className="text-lg">SSAFY_202</p>
          <div className="flex items-center gap-3">
            <img src="/icons/LockIcon.png" alt="Lock" className="w-5 h-5" />
            <img src="/icons/WiFiIcon.png" alt="WiFi" className="w-5 h-5" />
          </div>
        </button>
        <button
          className="flex items-center justify-between w-full border-b border-gray-300 p-4
          active:bg-gray-200 select-none cursor-pointer select-none"
          onClick={handleWiFiSelectClick}>
          <p className="text-lg">SSAFY_GUEST</p>
          <div className="flex items-center gap-3">
            <img src="/icons/LockIcon.png" alt="Lock" className="w-5 h-5" />
            <img src="/icons/WiFiIcon.png" alt="WiFi" className="w-5 h-5" />
          </div>
        </button>
      </main>
    </div>
  )
}

