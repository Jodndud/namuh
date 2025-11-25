import { useNavigate } from 'react-router-dom'

type MyRobotButtonProps = {
  disabled?: boolean
}

export default function MyRobotButton({ disabled = false }: MyRobotButtonProps) {
  const navigate = useNavigate()
  const handleMyRobotClick = () => {
    if (disabled) return
    navigate('/robot/detail')
  }
  return (
    <button
      type="button"
      className="flex w-full justify-between items-center bg-white/80 rounded-2xl pl-8 pr-4 active:bg-white select-none border border-gray-300
      theme-card select-none cursor-pointer"
      onClick={handleMyRobotClick}
      disabled={disabled}
      aria-disabled={disabled}>
          <div className="flex flex-col space-y-2 py-6 items-start the">
            <p className="text-sm">나의 휴머노이드 로봇</p>
            <h1 className="font-bold text-3xl">Tori</h1>
          </div>
          <img src="/images/RobotImage.png" alt="RobotImage" className="w-28 h-28 pt-3" />
        </button>
  )
}