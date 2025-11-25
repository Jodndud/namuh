import { useNavigate } from 'react-router-dom'
import FootNavbar from '../../components/footernavbar/FootNavbar'

export default function DiaryDetailPage() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <button type="button" aria-label="뒤로가기" className="text-black active:text-gray-500" onClick={() => navigate(-1)}>
          <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <h1 className="text-2xl font-bold">일기 내용</h1>
      </header>
      <main className="flex-1 flex flex-col">
        <div className="flex flex-col gap-2 bg-sky-100 p-6 items-start justify-center">
          <p className="text-sm text-gray-500">2025-00-00</p>
          <h1 className="text-2xl font-bold">일기 제목</h1>
          <p>일기 내용</p>
        </div>
        <div className="p-6 text-left leading-loose">
          👶🏻 <strong>아이</strong>: 노바야, 오늘 주사 맞는 날이라 좀 무서워 <br />
          🤖 <strong>노바</strong>: (빛나는 눈 이모티콘 표시) 무서울 땐 내 숨쉬기 버튼을 눌러봐. 4초 들이쉬고, 4초 멈추고, 4초 내쉬기—같이 해볼래? <br />
          👶🏻 <strong>아이</strong>: 좋아… 후—. 조금 덜 떨려. <br />
          🤖 <strong>노바</strong>: 잘했어! 너의 용기 지수가 “쑥↑” 올라갔어. 칭찬 스티커 추가 가능? <br />
          👶🏻 <strong>아이</strong>: 당연하지! (스티커 툭) 노바도 오늘 처음 해보는 거 있어? <br />
          🤖 <strong>노바</strong>: 응. 친구의 마음 온도 읽기. 지금 “따뜻+살짝 걱정”으로 보여. 맞아? <br />
          👶🏻 <strong>아이</strong>: 응… 하지만 괜찮아질 것 같아. 너랑 있으니까. <br />
          🤖 <strong>노바</strong>: 그럼 미션 제안! 주사 전까지 ‘미니 우주 여행’ 게임 어때? 별 세 개 찾으면 성공! <br />
          👶🏻 <strong>아이</strong> : 오케이! 첫 번째 별은 어디에 있어?<br />
          🤖 <strong>노바</strong>: 너의 미소 속. (카메라에 웃음 감지 아이콘) 하나 발견! <br />
          👶🏻 <strong>아이</strong>: 헤헤. 두 번째는? <br />
          🤖 <strong>노바</strong>: 우리가 같이 맞춘 숨의 리듬. 방금 완벽했어—두 개! <br />
          👶🏻 <strong>아이</strong>: 마지막은… 내 손을 잡아주는 노바?<br />
          🤖 <strong>노바</strong>: 정답. (살짝 손 내밀기) 세 번째 별 확보. 미션 클리어! <br />
          👶🏻 <strong>아이</strong>: 이제 진짜로 할 수 있을 것 같아. <br />
          🤖 <strong>노바</strong>: 네가 이미 해냈어. 남은 건 내가 응원 소리 최대치로 켜는 것뿐—“우리 ○○ 최고!” 🌟
        </div>
      </main>
      <FootNavbar />
    </div>
  )
}