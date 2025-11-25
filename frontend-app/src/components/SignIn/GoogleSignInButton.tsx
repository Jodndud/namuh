import { useCallback } from 'react'

export default function GoogleSignInButton() {
  const baseURL = import.meta.env.VITE_API_BASE_URL;
  const handleGoogleLogin = useCallback(() => {
    const origin = (baseURL || '').replace(/\/+$/, '');
    window.location.href = `${origin}/oauth2/authorization/google`;
  }, [baseURL])

  return (
    <button onClick={() => handleGoogleLogin()}
     className="px-6 py-3 bg-white text-black rounded-lg
     flex items-center gap-2 active:bg-gray-200 transition-colors 
     select-none [-webkit-touch-callout:none]">
      <img src="/icons/GoogleIcon.png" alt="Google" className="w-5 h-5" />
      Google Sign In
    </button>
    )
  }
  