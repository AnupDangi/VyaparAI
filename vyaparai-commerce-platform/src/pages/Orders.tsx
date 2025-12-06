import { useEffect, useState } from "react";
import { useUser } from "@clerk/clerk-react";
import { ordersAPI } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { Package, Clock } from "lucide-react";

export default function Orders() {
    const { user } = useUser();
    const navigate = useNavigate();
    const [orders, setOrders] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrders = async () => {
            if (!user) return;
            const { data } = await ordersAPI.getUserOrders(user.id);
            if (data) {
                setOrders(data);
            }
            setLoading(false);
        };
        fetchOrders();
    }, [user]);

    if (loading) return <div className="p-8 text-center">Loading Orders...</div>;

    return (
        <div className="min-h-screen bg-background p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold">Your Orders</h1>
                    <Button variant="outline" onClick={() => navigate("/dashboard")}>Continue Shopping</Button>
                </div>

                {orders.length === 0 ? (
                    <Card>
                        <CardContent className="p-8 text-center">
                            <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                            <h3 className="text-lg font-medium">No orders yet</h3>
                            <p className="text-muted-foreground mb-4">Start shopping to see your orders here.</p>
                            <Button onClick={() => navigate("/dashboard")}>Go to Store</Button>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-6">
                        {orders.map((order) => (
                            <Card key={order.id}>
                                <CardHeader className="bg-secondary/20 pb-4">
                                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                        <div className="flex gap-6 text-sm">
                                            <div>
                                                <span className="block text-muted-foreground text-xs uppercase">Order Placed</span>
                                                <span className="font-medium">{new Date(order.date).toLocaleDateString()}</span>
                                            </div>
                                            <div>
                                                <span className="block text-muted-foreground text-xs uppercase">Total</span>
                                                <span className="font-medium">₹{order.total}</span>
                                            </div>
                                            <div>
                                                <span className="block text-muted-foreground text-xs uppercase">Order #</span>
                                                <span className="font-medium">{order.id}</span>
                                            </div>
                                        </div>
                                        <div>
                                            <Badge variant={order.status === 'Completed' ? 'default' : 'secondary'}>
                                                {order.status}
                                            </Badge>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent className="pt-6">
                                    <div className="space-y-4">
                                        {order.items.map((item: any) => (
                                            <div key={item.id} className="flex items-center gap-4">
                                                <img src={item.image_url} alt={item.title} className="w-16 h-16 object-cover rounded border" />
                                                <div className="flex-1">
                                                    <h4 className="font-medium line-clamp-1">{item.title}</h4>
                                                    <p className="text-sm text-muted-foreground">Qty: {item.quantity}</p>
                                                </div>
                                                <div className="font-medium">₹{item.price}</div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
