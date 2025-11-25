import { useNavigate } from 'react-router-dom'
export default function DiaryButton() {
  const navigate = useNavigate()
  const handleDiaryClick = () => {
    navigate('/diary')
  }
  return (
    <button
      className="flex w-full bg-white/80 rounded-2xl px-8
      justify-between items-center
      active:border active:border-gray-300 select-none [-webkit-touch-callout:none]"
      onClick={handleDiaryClick}>
      <div className="flex flex-col space-y-2 py-6 items-start">
        <h1 className="text-2xl font-bold">일기</h1>
        <p className="text-left text-xs text-gray-600">
          Tori와 대화한 내용을<br />AI가 정리해줍니다.</p>
      </div>
      <img src="/icons/DiaryIcon.png" alt="DiaryIcon" className="w-12 h-12" />
    </button>
  )
}