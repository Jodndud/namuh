import HomeButton from './buttons/HomeButton'
// import DiaryButton from './buttons/DiaryButton'
import VideoButton from './buttons/VideoButton'
import RobotListButton from './buttons/RobotListButton'
import MyPageButton from './buttons/MyPageButton'

export default function FootNavbar() {

  return (
    <footer className="fixed flex justify-between items-center px-6 pt-3 pb-4 bottom-0 left-0 rounded-t-3xl
    right-0 bg-white shadow-2xl border-gray-300">
      {/* 홈 버튼 */}
      <HomeButton />

      {/* 일기 버튼 */}
      {/* <DiaryButton /> */}

      {/* 영상 버튼 */}
      <VideoButton />

      {/* 로봇 버튼 */}
      <RobotListButton />

      {/* 마이페이지 버튼 */}
      <MyPageButton />
    </footer>
  )
}