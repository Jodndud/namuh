import { useNavigate } from 'react-router-dom'

export default function MyPageButton() {
  const navigate = useNavigate()
  const handleMyPageClick = () => {
    navigate('/my-page')
  }
  return (
    <button type="button" aria-label="마이페이지"
      className="group flex flex-col items-center text-gray-400 py-2 px-4
      active:text-black active:bg-gray-200 rounded-2xl select-none cursor-pointer"
      onClick={handleMyPageClick}>
      <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 transition-transform duration-150 ease-out group-active:scale-80" viewBox="0 0 24 24" aria-hidden="true">
       <path fill="currentColor" d="M12 12a4 4 0 1 0 0-8a4 4 0 0 0 0 8zm-7 8a7 7 0 0 1 14 0H5z" />
      </svg>
      <h1 className="text-xs transition-transform duration-150 ease-out group-active:scale-80">마이</h1>
    </button>
  )
}