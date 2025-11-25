import { useNavigate } from 'react-router-dom'

export default function MyPageButton() {
  const navigate = useNavigate()
  const handleMyPageClick = () => {
    navigate('/my-page')
  }
  return (
    <button
      className="flex w-full bg-white/80 rounded-2xl px-8
      justify-between items-center theme-button select-none cursor-pointer
      active:border active:border-gray-300 select-none border"
      onClick={handleMyPageClick}>
      <div className="flex flex-col space-y-2 py-6 items-start">
        <h1 className="text-2xl font-bold">마이페이지</h1>
        <p className="text-left text-xs">
          나의 정보를 변경하세요</p>
      </div>
      <img src="/icons/ParentsIcon.png" alt="ParentsIcon" className="w-12 h-12" />
    </button>
  )
}