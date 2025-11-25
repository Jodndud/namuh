// import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Vite PWA 플러그인이 자동으로 Service Worker를 등록합니다
// 수동 등록은 필요하지 않습니다

ReactDOM.createRoot(document.getElementById('root')!).render(
  // <React.StrictMode>
    <App />
  // </React.StrictMode>,
)
