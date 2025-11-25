import MyRobotAddButton from '../../components/robot/MyRobotAddButton'
import MyRobotButton from '../../components/HomePage/MyRobotButton'
import FootNavbar from '../../components/footernavbar/FootNavbar'
import BackButton from '../../components/Common/BackButton'

export default function MyRobotListPage() {
  return (
    <div className="min-h-screen flex flex-col space-y-2">
      <header className="flex justify-between items-center pl-4 pr-6 py-4">
        <BackButton />
        <h1 className="text-2xl font-bold">나의 휴머노이드 로봇</h1>
      </header>
      <main className="flex-1 flex flex-col space-y-4 px-4 pb-4">
        <MyRobotAddButton />
        <MyRobotButton />
      </main>
      <FootNavbar />
    </div>
  )
}