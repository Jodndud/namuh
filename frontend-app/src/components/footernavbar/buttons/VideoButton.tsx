import { useNavigate } from 'react-router-dom'

export default function VideoButton() {
  const navigate = useNavigate()
  const handleVideoClick = () => {
    navigate('/video')
  }
  return (
    <button type="button" aria-label="영상"
      className="group flex flex-col items-center text-gray-400 py-2 px-4
      active:text-black active:bg-gray-200 rounded-2xl select-none cursor-pointer"
      onClick={handleVideoClick}>
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 transition-transform duration-150 ease-out group-active:scale-80" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M3 7a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2l4-2v8l-4-2v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z" />
      </svg>
      <h1 className="text-xs transition-transform duration-150 ease-out group-active:scale-80">영상</h1>
    </button>
  )
}