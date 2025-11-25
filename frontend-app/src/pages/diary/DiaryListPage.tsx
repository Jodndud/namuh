import { useNavigate } from 'react-router-dom'
import FootNavbar from '../../components/footernavbar/FootNavbar'

export default function DiaryListPage() {
  const navigate = useNavigate()
  const handleDiaryClick = () => {
    navigate('/diary/detail')
  }
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      {/* 헤더 영역 */}
      <header className="flex justify-between items-center pl-4 pr-6 py-4 select-none">
        <button type="button" aria-label="뒤로가기" className="text-black active:text-gray-500" onClick={() => navigate(-1)}>
          <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <h1 className="text-2xl font-bold">일기 목록</h1>
      </header>

      <main className="flex-1 flex flex-col px-4 gap-4">
        {/* 일기 목록 배너 */}
        <div className="relative select-none">
          <img src="/images/DiaryListBannerImage.png" alt="DiaryListBannerImage"
            className="w-full h-full object-cover rounded-2xl"></img>
          <div className="absolute inset-0 px-8 py-6 flex flex-col items-start justify-end">
            <p className="text-white text-2xl font-bold drop-shadow">대화를 하면 위로가 됩니다</p>
            <p className="text-white text-xs drop-shadow">아이와 휴머노이드 로봇의 대화는 AI가 요약해드립니다.</p>
          </div>
        </div>
        {/* 일기 목록 아이템 */}
        <button 
          className="flex flex-col space-y-2 items-start px-8 py-6 bg-white/80 rounded-2xl
          active:bg-gray-200 select-none"
          onClick={handleDiaryClick}>
          <p className="text-sm text-gray-500">생성된 날짜</p>
          <h1 className="text-2xl font-bold">일기 제목</h1>
          <p>간략한 일기 내용</p>
        </button>
      </main>
      <FootNavbar />
    </div>
  )
}

