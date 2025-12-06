import MainLayout from "@/components/layout/MainLayout";
import { SignUp } from "@clerk/clerk-react";

const Signup = () => {
    return (
        <MainLayout showFooter={false}>
            <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4">
                <div className="w-full max-w-md animate-fade-up">
                    <div className="text-center mb-8">
                        <h1 className="text-2xl font-serif font-bold text-foreground">
                            Join VyaparAI
                        </h1>
                        <p className="text-muted-foreground mt-2">
                            Create an account to start shopping
                        </p>
                    </div>

                    <div className="flex justify-center">
                        <SignUp
                            signInUrl="/login"
                            forceRedirectUrl="/dashboard"
                        />
                    </div>
                </div>
            </div>
        </MainLayout>
    );
};

export default Signup;
