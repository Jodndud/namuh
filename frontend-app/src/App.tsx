import { Routes, Route, Navigate } from 'react-router-dom'
import WelcomePage from './pages/WelcomePage'
import SignInPage from './pages/user/SignInPage'
import VideoListPage from './pages/video/VideoListPage'
import DiaryListPage from './pages/diary/DiaryListPage'
import DiaryDetailPage from './pages/diary/DiaryDetailPage'
import MyRobotListPage from './pages/robotpages/MyRobotListPage'
import MyRobotDetailPage from './pages/robotpages/MyRobotDetailPage'
import MyRobotUpdatePage from './pages/robotpages/MyRobotUpdatePage'
import RobotFindingPage from './pages/robotpages/RobotFindingPage'
import RobotSelectPage from './pages/robotpages/RobotSelectPage'
import WiFiFindingPage from './pages/robotpages/WiFiFindingPage'
import WiFiListPage from './pages/robotpages/WiFiListPage'
import HomePage from './pages/HomePage'
import MyPage from './pages/user/MyPage'
import CallbackPage from './pages/callback/CallbackPage'

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/home" element={<HomePage />} />

        {/* Login Callback */}
        <Route path="/callback" element={<CallbackPage />} />

        {/* Func. Video */}
        <Route path="/video" element={<VideoListPage />} />

        {/* Func. Diary */}
        <Route path="/diary" element={<DiaryListPage />} />
        <Route path="/diary/detail" element={<DiaryDetailPage />} />
        
        {/* Humanoid Robot */}
        <Route path="/robot/finding" element={<RobotFindingPage />} />
        <Route path="/robot/list" element={<MyRobotListPage />} />
        <Route path="/robot/detail" element={<MyRobotDetailPage />} />
        <Route path="/robot/update" element={<MyRobotUpdatePage />} />
        <Route path="/robot/select" element={<RobotSelectPage />} />

        {/* Robot Wi-Fi */}
        <Route path="/robot/wifi/finding" element={<WiFiFindingPage />} />
        <Route path="/robot/wifi/list" element={<WiFiListPage />} />
        <Route path="/my-page" element={<MyPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default App