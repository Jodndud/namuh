import { useNavigate } from 'react-router-dom'

export default function HomeButton() {
  const navigate = useNavigate()
  const handleHomeClick = () => {
    navigate('/home')
  }
  return (
    <button type="button" aria-label="홈"
      className="group flex flex-col items-center text-gray-400 py-2 px-4
      active:text-black active:bg-gray-200 rounded-2xl select-none cursor-pointer"
      onClick={handleHomeClick}>
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 transition-transform duration-150 ease-out group-active:scale-80" viewBox="0 0 24 24" aria-hidden="true">
        <path fill="currentColor" d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
      </svg>
      <h1 className="text-xs transition-transform duration-150 ease-out group-active:scale-80">홈</h1>
    </button>
  )
}