import BrandLogo from '../../components/Common/BrandLogo'
import GoogleSignInButton from '../../components/SignIn/GoogleSignInButton'

export default function SignInPage() {
  return (
    <section
      className="relative min-h-screen w-full bg-cover bg-center bg-no-repeat"
      style={{
        backgroundImage: "url('/backgrounds/SignInPageBG.png')",
      }}
    >
      <div className="space-y-4 absolute left-1/2 top-[40vh] -translate-x-1/2 -translate-y-1/2">
        <BrandLogo />
        <GoogleSignInButton />
      </div>
    </section>
  )
}