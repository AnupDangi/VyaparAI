import { useState } from "react";
import { useAuth, useSignIn } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { toast } from "@/hooks/use-toast";
import { Mail, Lock, CheckCircle, ArrowRight } from "lucide-react";

export default function ResetPassword() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [code, setCode] = useState("");
    const [successfulCreation, setSuccessfulCreation] = useState(false);
    const [complete, setComplete] = useState(false);
    const [secondFactor, setSecondFactor] = useState(false);

    const { isSignedIn } = useAuth();
    const { isLoaded, signIn, setActive } = useSignIn();
    const navigate = useNavigate();

    if (!isLoaded) {
        return null;
    }

    // If already signed in, redirect
    if (isSignedIn) {
        navigate("/dashboard");
        return null;
    }

    async function create(e: React.FormEvent) {
        e.preventDefault();
        if (!isLoaded) return;
        try {
            await signIn.create({
                strategy: "reset_password_email_code",
                identifier: email,
            });
            setSuccessfulCreation(true);
            toast({ title: "Code Sent", description: "Check your email for the reset code." });
        } catch (err: any) {
            console.error("error", err.errors[0].longMessage);
            toast({ title: "Error", description: err.errors[0].longMessage, variant: "destructive" });
        }
    }

    async function reset(e: React.FormEvent) {
        e.preventDefault();
        if (!isLoaded) return;
        try {
            const result = await signIn.attemptFirstFactor({
                strategy: "reset_password_email_code",
                code,
                password,
            });

            if (result.status === "complete") {
                setActive({ session: result.createdSessionId });
                setComplete(true);
                toast({ title: "Password Reset", description: "You have successfully reset your password." });
                setTimeout(() => navigate("/dashboard"), 2000);
            } else {
                console.log(result);
                toast({ title: "Verification Failed", description: "Something went wrong.", variant: "destructive" });
            }
        } catch (err: any) {
            console.error("error", err.errors[0].longMessage);
            toast({ title: "Error", description: err.errors[0].longMessage, variant: "destructive" });
        }
    }

    if (complete) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background p-4">
                <Card className="w-full max-w-md text-center p-8">
                    <div className="flex justify-center mb-4">
                        <CheckCircle className="h-16 w-16 text-green-500" />
                    </div>
                    <h2 className="text-2xl font-bold mb-2">Password Reset Successful!</h2>
                    <p className="text-muted-foreground mb-4">Redirecting you to dashboard...</p>
                </Card>
            </div>
        )
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <Card className="w-full max-w-md">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold text-center">Reset Password</CardTitle>
                    <p className="text-sm text-muted-foreground text-center">
                        {!successfulCreation ? "Enter your email to receive a reset code" : "Enter the code sent to your email"}
                    </p>
                </CardHeader>
                <CardContent>
                    {!successfulCreation ? (
                        <form onSubmit={create} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="email">Email</Label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="email"
                                        placeholder="name@example.com"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="pl-10"
                                        required
                                    />
                                </div>
                            </div>
                            <Button type="submit" className="w-full">
                                Send Reset Code <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </form>
                    ) : (
                        <form onSubmit={reset} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="code">Reset Code</Label>
                                <Input
                                    id="code"
                                    type="text"
                                    placeholder="Enter 6-digit code"
                                    value={code}
                                    onChange={(e) => setCode(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="password">New Password</Label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="password"
                                        type="password"
                                        placeholder="Enter new password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="pl-10"
                                        required
                                    />
                                </div>
                            </div>
                            <Button type="submit" className="w-full">
                                Reset Password
                            </Button>
                        </form>
                    )}
                </CardContent>
                <CardFooter className="flex justify-center">
                    <Button variant="link" onClick={() => navigate("/login")}>
                        Back to Login
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
}
