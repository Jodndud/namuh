import { useNavigate } from 'react-router-dom'

export default function BackButton() {
  const navigate = useNavigate()
  return (
    <button type="button" aria-label="뒤로가기" className="back-button cursor-pointer" onClick={() => navigate(-1)}>
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M15 18l-6-6 6-6" />
      </svg>
    </button>
  )
}