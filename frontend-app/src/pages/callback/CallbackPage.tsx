import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../lib/api'
// import { jwtDecode } from 'jwt-decode'

export default function CallbackPage() {
  const navigate = useNavigate()
  // const payload = jwtDecode(localStorage.getItem('accessToken')!)
  // console.log('payload',payload)
  
  useEffect(() => {
    const handleCallback = async () => {
      try {
        const res = await api.post('/auth/refresh', {}, { withCredentials: true })

        const status = res.status
        if (status < 200 || status >= 300) throw new Error(`HTTP ${status}`)

        const authHeader = res.headers['authorization'] || res.headers['Authorization']
        if (!authHeader) {
          throw new Error('Authorization 헤더가 없습니다.')
        }

        const issuedAccessToken = String(authHeader).replace(/^Bearer\s+/i, '').trim()
        if (!issuedAccessToken) {
          throw new Error('Authorization 헤더에서 토큰을 파싱하지 못했습니다.')
        }

        localStorage.setItem('accessToken', issuedAccessToken)
        navigate('/home', { replace: true })
      } catch (error) {
        navigate('/signin', { replace: true })
      }
    }

    handleCallback()
  }, [navigate])

  return (
    <div className="flex items-center justify-center h-screen text-lg font-semibold">
      로그인 완료! 잠시만 기다려주세요...
    </div>
  )
}
