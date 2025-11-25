import { useNavigate } from 'react-router-dom'
export default function VideoButton() {
  const navigate = useNavigate()
  const handleVideoClick = () => {
    navigate('/video')
  }
  return (
    <button
      className="flex w-full bg-white/80 rounded-2xl px-8
      justify-between items-center theme-button select-none cursor-pointer
      active:border active:border-gray-300 select-none border"
      onClick={handleVideoClick}>
      <div className="flex flex-col space-y-2 py-6 items-start">
        <h1 className="text-2xl font-bold">영상</h1>
        <p className="text-left text-xs">
          우리 아이의 미소를<br />
          영상으로 담아드립니다</p>
      </div>
      <img src="/icons/VideoCameraIcon.png" alt="VideoCameraIcon" className="w-12 h-12" />
    </button>
  )
}