import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

type UserDeleteModalProps = {
  isOpen: boolean
  onClose: () => void
}

export default function UserDeleteModal({ isOpen, onClose }: UserDeleteModalProps) {
  const [agreed, setAgreed] = useState(false)
  const navigate = useNavigate()
  const handleUserDeleteClick = () => {
    navigate('/')
    onClose()
  }
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-center items-end" onClick={onClose}>
      <div className="absolute inset-0 bg-black/40 z-0" />
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative z-10 w-full max-w-md theme-card select-none p-6 rounded-t-4xl border border-gray-300 transform transition-transform duration-300 ease-out translate-y-0"
      >
        {/* 드래그 바 */}
        <div className="flex justify-center py-2">
          <div className="h-1.5 w-12 rounded-full dragbar" />
        </div>
        
        {/* 회원탈퇴 안내 */}
        <div className="py-2 space-y-4">
          <h2 className="text-3xl font-bold text-center">회원탈퇴</h2>
          <p className="text-left text-lg"> 탈퇴 시 저장한 데이터가 영구 삭제되며 복구할 수 없습니다.</p>
        </div>

        {/* 탈퇴 동의 체크박스*/}
        <div className="flex py-4 justify-start items-center space-x-2 select-none">
          <input
            id="agree"
            type="checkbox"
            className="w-5 h-5 cursor-pointer"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
          />
          <label htmlFor="agree" className="cursor-pointer">회원 탈퇴 및 데이터 삭제에 동의합니다.</label>
        </div>

        {/* 회원탈퇴 버튼 */}
        <button
          type="button"
          disabled={!agreed}
          onClick={handleUserDeleteClick}
          className="w-full rounded-2xl p-4 select-none bg-gray-300 active:bg-red-500 active:font-bold active:text-white
          disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed
          theme-button border select-none cursor-pointer">
          회원탈퇴
        </button>
      </div>
    </div>
  )
}