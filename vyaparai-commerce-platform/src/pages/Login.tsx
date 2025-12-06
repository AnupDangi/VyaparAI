import MainLayout from "@/components/layout/MainLayout";
import { SignIn } from "@clerk/clerk-react";

const Login = () => {
  return (
    <MainLayout showFooter={false}>
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-md animate-fade-up">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-serif font-bold text-foreground">
              Welcome Back
            </h1>
            <p className="text-muted-foreground mt-2">
              Sign in to continue shopping with AI
            </p>
          </div>

          <div className="flex justify-center">
            <SignIn
              signUpUrl="/signup"
              forceRedirectUrl="/dashboard"
            />
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default Login;
