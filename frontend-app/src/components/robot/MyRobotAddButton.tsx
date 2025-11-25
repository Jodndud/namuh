import { useNavigate } from 'react-router-dom'

export default function MyRobotAddButton() {
  const navigate = useNavigate()
  const handleMyRobotAddClick = () => {
    navigate('/robot/finding')
  }
  return (
    <button
      className="flex w-full bg-white/80 rounded-2xl px-8
      active:bg-gray-200 select-none border border-gray-300 theme-card select-none cursor-pointer"
      onClick={handleMyRobotAddClick}>
      <div className="flex py-6 space-x-2 justify-center items-center w-full">
        <div className="border rounded-full w-6 h-6 flex items-center justify-center">+</div>
        <h1 className="text-md">휴머노이드 로봇 추가</h1>
      </div>
    </button>
  )
}