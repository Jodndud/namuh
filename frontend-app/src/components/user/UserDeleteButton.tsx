type UserDeleteButtonProps = {
  onClick?: () => void
}

export default function UserDeleteButton({ onClick }: UserDeleteButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="pr-2 w-full text-right text-gray-500 cursor-pointer hover:text-red-500 active:font-bold active:text-red-500 select-none"
    >
      회원탈퇴
    </button>
  )
}