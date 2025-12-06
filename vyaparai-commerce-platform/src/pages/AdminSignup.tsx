import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Store, Building2, MapPin, Phone, ArrowRight, User, Mail, Lock, Shield } from "lucide-react";

import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import MainLayout from "@/components/layout/MainLayout";
import { toast } from "@/hooks/use-toast";
import { adminAPI } from "@/lib/api";

const adminSignupSchema = z.object({
    // Admin Credentials
    adminId: z.string().min(3, "Admin ID must be at least 3 characters"),
    fullName: z.string().min(2, "Name is required"),
    email: z.string().email("Invalid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),

    // Store Details
    storeName: z.string().min(2, "Store name must be at least 2 characters"),
    description: z.string().min(10, "Description must be at least 10 characters"),
    category: z.string({
        required_error: "Please select a category",
    }),
    address: z.string().min(5, "Address is required"),
    phone: z.string().min(10, "Phone number must be at least 10 digits"),
});

type AdminSignupValues = z.infer<typeof adminSignupSchema>;

export default function AdminSignup() {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);

    const form = useForm<AdminSignupValues>({
        resolver: zodResolver(adminSignupSchema),
        defaultValues: {
            adminId: "",
            fullName: "",
            email: "",
            password: "",
            storeName: "",
            description: "",
            address: "",
            phone: "",
        },
    });

    const onSubmit = async (data: AdminSignupValues) => {
        setIsSubmitting(true);

        try {
            const response = await fetch('http://localhost:8000/admin/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const resData = await response.json();

            if (!response.ok) {
                throw new Error(resData.detail || "Signup failed");
            }

            toast({
                title: "Account Created!",
                description: "Your admin account has been set up. Please login.",
            });

            navigate("/admin/login");
        } catch (error) {
            toast({
                title: "Signup Failed",
                description: error instanceof Error ? error.message : "Something went wrong",
                variant: "destructive",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <MainLayout showFooter={false}>
            <div className="min-h-[calc(100vh-4rem)] bg-secondary/30 py-12 px-4">
                <div className="mx-auto max-w-3xl space-y-8 animate-fade-up">
                    <div className="text-center space-y-2">
                        <div className="inline-flex items-center justify-center h-12 w-12 rounded-xl bg-primary text-primary-foreground mb-4">
                            <Shield className="h-6 w-6" />
                        </div>
                        <h1 className="text-3xl font-serif font-bold">Admin Registration</h1>
                        <p className="text-muted-foreground">
                            Create your admin account and set up your store in one go.
                        </p>
                    </div>

                    <Card>
                        <CardHeader>
                            <CardTitle>Account & Store Details</CardTitle>
                            <CardDescription>
                                Please fill in all the information below to get started.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <Form {...form}>
                                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">

                                    {/* Admin Credentials Section */}
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-medium">Admin Credentials</h3>
                                        <div className="grid md:grid-cols-2 gap-4">
                                            <FormField
                                                control={form.control}
                                                name="adminId"
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Admin ID (Username)</FormLabel>
                                                        <FormControl>
                                                            <div className="relative">
                                                                <User className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                                                <Input placeholder="store_admin_01" className="pl-9" {...field} />
                                                            </div>
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                            <FormField
                                                control={form.control}
                                                name="fullName"
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Full Name</FormLabel>
                                                        <FormControl>
                                                            <Input placeholder="John Doe" {...field} />
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                        </div>
                                        <div className="grid md:grid-cols-2 gap-4">
                                            <FormField
                                                control={form.control}
                                                name="email"
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Email Address</FormLabel>
                                                        <FormControl>
                                                            <div className="relative">
                                                                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                                                <Input placeholder="admin@example.com" type="email" className="pl-9" {...field} />
                                                            </div>
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                            <FormField
                                                control={form.control}
                                                name="password"
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Password</FormLabel>
                                                        <FormControl>
                                                            <div className="relative">
                                                                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                                                <Input placeholder="••••••••" type="password" className="pl-9" {...field} />
                                                            </div>
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                        </div>
                                    </div>

                                    <div className="h-px bg-border" />

                                    {/* Store Details Section */}
                                    <div className="space-y-4">
                                        <h3 className="text-lg font-medium">Store Information</h3>
                                        <FormField
                                            control={form.control}
                                            name="storeName"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel>Store Name</FormLabel>
                                                    <FormControl>
                                                        <div className="relative">
                                                            <Store className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                                            <Input placeholder="My Awesome Store" className="pl-9" {...field} />
                                                        </div>
                                                    </FormControl>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <div className="grid gap-6 md:grid-cols-2">
                                            <FormField
                                                control={form.control}
                                                name="category"
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Category</FormLabel>
                                                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                                                            <FormControl>
                                                                <SelectTrigger>
                                                                    <SelectValue placeholder="Select business type" />
                                                                </SelectTrigger>
                                                            </FormControl>
                                                            <SelectContent>
                                                                <SelectItem value="retail">Retail & Fashion</SelectItem>
                                                                <SelectItem value="electronics">Electronics</SelectItem>
                                                                <SelectItem value="food">Food & Beverage</SelectItem>
                                                                <SelectItem value="services">Services</SelectItem>
                                                                <SelectItem value="digital">Digital Products</SelectItem>
                                                                <SelectItem value="other">Other</SelectItem>
                                                            </SelectContent>
                                                        </Select>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />

                                            <FormField
                                                control={form.control}
                                                name="phone"
                                                render={({ field }) => (
                                                    <FormItem>
                                                        <FormLabel>Business Phone</FormLabel>
                                                        <FormControl>
                                                            <div className="relative">
                                                                <Phone className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                                                                <Input placeholder="+91 98765 43210" className="pl-9" {...field} />
                                                            </div>
                                                        </FormControl>
                                                        <FormMessage />
                                                    </FormItem>
                                                )}
                                            />
                                        </div>

                                        <FormField
                                            control={form.control}
                                            name="address"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel>Business Address</FormLabel>
                                                    <FormControl>
                                                        <div className="relative">
                                                            <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                                                            <Textarea
                                                                placeholder="Full business address for verification"
                                                                className="pl-9 min-h-[80px]"
                                                                {...field}
                                                            />
                                                        </div>
                                                    </FormControl>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <FormField
                                            control={form.control}
                                            name="description"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel>Store Description</FormLabel>
                                                    <FormControl>
                                                        <Textarea
                                                            placeholder="Describe your store..."
                                                            className="min-h-[100px]"
                                                            {...field}
                                                        />
                                                    </FormControl>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />
                                    </div>

                                    <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
                                        {isSubmitting ? (
                                            <span className="flex items-center gap-2">
                                                <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                                Creating Account...
                                            </span>
                                        ) : (
                                            <span className="flex items-center gap-2">
                                                Create Account & Store <ArrowRight className="h-4 w-4" />
                                            </span>
                                        )}
                                    </Button>
                                </form>
                            </Form>
                        </CardContent>
                    </Card>

                    <div className="text-center">
                        <Link
                            to="/admin/login"
                            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                        >
                            Already have an account? <span className="text-primary font-medium">Log in</span>
                        </Link>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}
