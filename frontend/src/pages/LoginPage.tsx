import LoginForm from '../components/LoginForm'

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold text-center text-gray-900">
          AI_code_assisstant
        </h2>
        <p className="mt-2 text-center text-gray-500">登录你的账户</p>
        <div className="mt-6">
          <LoginForm />
        </div>
      </div>
    </div>
  )
}