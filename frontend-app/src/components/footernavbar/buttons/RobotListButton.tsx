import { useNavigate } from 'react-router-dom'

export default function RobotListButton() {
  const navigate = useNavigate()
  const handleRobotListClick = () => {
    navigate('/robot/list')
  }
  return (
    <button type="button" aria-label="로봇 목록"
      className="group flex flex-col items-center text-gray-400 py-2 px-4
      active:text-black active:bg-gray-200 rounded-2xl select-none cursor-pointer"
      onClick={handleRobotListClick}>
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 transition-transform duration-150 ease-out group-active:scale-80" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M11 2h2v2h3a2 2 0 0 1 2 2v8a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V6a2 2 0 0 1 2-2h3V2z" />
        <circle cx="9.5" cy="12" r="1.2" fill="white" />
        <circle cx="14.5" cy="12" r="1.2" fill="white" />
      </svg>
      <h1 className="text-xs transition-transform duration-150 ease-out group-active:scale-80">로봇</h1>
    </button>
  )
}