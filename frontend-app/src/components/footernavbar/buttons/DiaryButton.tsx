import { useNavigate } from 'react-router-dom'

export default function DiaryButton() {
  const navigate = useNavigate()
  const handleDiaryClick = () => {
    navigate('/diary')
  }
  return (
    <button type="button" aria-label="일기"
      className="group flex flex-col items-center text-gray-400 py-2 px-4
      active:text-black active:bg-gray-200 rounded-2xl select-none cursor-pointer"
      onClick={handleDiaryClick}>
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 transition-transform duration-150 ease-out group-active:scale-80" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M3 5a2 2 0 0 1 2-2h6v16H5a2 2 0 0 1-2-2V5z" />
        <path fill="currentColor" d="M13 3h6a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-6V3z" />
      </svg>
      <h1 className="text-xs transition-transform duration-150 ease-out group-active:scale-80">일기</h1>
    </button>
  )
}