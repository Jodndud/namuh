import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import BrandLogo from '../components/Common/BrandLogo'

export default function WelcomePage() {
  const navigate = useNavigate()

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      navigate('/signin')
    }, 1500)
    return () => clearTimeout(timeoutId)
  }, [navigate])

  return (
    <section
      className="relative min-h-screen w-full bg-cover bg-center bg-no-repeat"
      style={{
        backgroundImage: "url('/backgrounds/WelcomePageBG.png')",
      }}
    >
      <div className="absolute left-1/2 top-[40vh] -translate-x-1/2 -translate-y-1/2">
        <BrandLogo />
      </div>
    </section>
  )
}

