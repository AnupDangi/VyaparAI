import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "@/context/CartContext";
import { useUser } from "@clerk/clerk-react";
import { ordersAPI } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { Loader2 } from "lucide-react";

export default function Checkout() {
    const { items, cartTotal, clearCart } = useCart();
    const { user } = useUser();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        fullName: user?.fullName || "",
        address: "",
        city: "",
        zip: "",
        card: "" // Mock payment
    });

    const shipping = 50;
    const total = cartTotal + shipping;

    if (items.length === 0) {
        navigate("/dashboard");
        return null;
    }

    const handlePlaceOrder = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!user) {
            toast({ title: "Login Required", description: "Please login to place an order", variant: "destructive" });
            return;
        }

        setLoading(true);

        const orderData = {
            items: items.map(item => ({
                product_id: parseInt(item.id),
                quantity: item.quantity,
                price: item.price
            })),
            total_amount: total,
            clerk_id: user.id,
            shipping_address: `${formData.address}, ${formData.city}, ${formData.zip}`
        };

        const { data, error } = await ordersAPI.create(orderData);

        if (data?.success) {
            toast({ title: "Order Placed! 🎉", description: "Thank you for shopping with us." });
            clearCart();
            navigate("/orders");
        } else {
            toast({ title: "Order Failed", description: error || "Something went wrong", variant: "destructive" });
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-background p-4 md:p-8">
            <h1 className="text-3xl font-bold mb-8 max-w-4xl mx-auto">Checkout</h1>

            <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Shipping Form */}
                <Card className="md:col-span-2">
                    <CardHeader><CardTitle>Shipping Details</CardTitle></CardHeader>
                    <CardContent>
                        <form id="checkout-form" onSubmit={handlePlaceOrder} className="space-y-4">
                            <div className="space-y-2">
                                <Label>Full Name</Label>
                                <Input value={formData.fullName} onChange={e => setFormData({ ...formData, fullName: e.target.value })} required />
                            </div>
                            <div className="space-y-2">
                                <Label>Address</Label>
                                <Input value={formData.address} onChange={e => setFormData({ ...formData, address: e.target.value })} required placeholder="123 Main St" />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>City</Label>
                                    <Input value={formData.city} onChange={e => setFormData({ ...formData, city: e.target.value })} required />
                                </div>
                                <div className="space-y-2">
                                    <Label>ZIP Code</Label>
                                    <Input value={formData.zip} onChange={e => setFormData({ ...formData, zip: e.target.value })} required />
                                </div>
                            </div>

                            <div className="space-y-2 pt-4 border-t">
                                <Label>Payment Method</Label>
                                <div className="p-3 border rounded bg-secondary/20 text-sm">
                                    Mock Payment Gateway (Cash on Delivery / Card)
                                </div>
                            </div>
                        </form>
                    </CardContent>
                </Card>

                {/* Order Summary */}
                <Card>
                    <CardHeader><CardTitle>Order Summary</CardTitle></CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            {items.map(item => (
                                <div key={item.id} className="flex justify-between text-sm">
                                    <span className="truncate w-32">{item.title} (x{item.quantity})</span>
                                    <span>₹{(item.price * item.quantity).toLocaleString()}</span>
                                </div>
                            ))}
                        </div>
                        <div className="border-t my-2 pt-2 space-y-2">
                            <div className="flex justify-between text-sm">
                                <span>Subtotal</span>
                                <span>₹{cartTotal.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span>Shipping</span>
                                <span>₹{shipping}</span>
                            </div>
                            <div className="flex justify-between font-bold text-lg pt-2">
                                <span>Total</span>
                                <span>₹{total.toLocaleString()}</span>
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button type="submit" form="checkout-form" className="w-full" disabled={loading}>
                            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {loading ? "Processing..." : "Place Order"}
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}
