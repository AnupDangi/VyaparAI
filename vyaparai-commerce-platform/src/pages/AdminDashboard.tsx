import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ChatMessage from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import StatsCard from "@/components/admin/StatsCard";
import {
  Shield,
  LogOut,
  Users,
  ShoppingBag,
  TrendingUp,
  Package,
  AlertTriangle,
  BarChart3,
  Menu,
  X,
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

import { productsAPI } from "@/lib/api";

// ... existing imports

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  chart?: boolean;
}

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [admin, setAdmin] = useState<any>(null);

  useEffect(() => {
    const storedAdmin = localStorage.getItem('admin');
    if (storedAdmin) {
      setAdmin(JSON.parse(storedAdmin));
    }
  }, []);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello Admin! 👋 I'm your analytics assistant. Ask me anything about your store's performance:\n\n• \"How many users bought dairy items this week?\"\n• \"Show me revenue for snacks category\"\n• \"Which product sold the most today?\"\n• \"What's the average order value?\"",
      role: "assistant",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (content: string) => {
    // ... logic ...
    const userMessage: Message = { id: Date.now().toString(), content, role: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setTimeout(() => {
      // ... simple response logic for now ...
      const assistantMessage: Message = { id: (Date.now() + 1).toString(), content: "AI is processing...", role: "assistant" };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin');
    toast({ title: "Logged out", description: "See you next time!" });
    navigate("/");
  };

  // Products State
  const [products, setProducts] = useState<any[]>([]);
  const [isProductLoading, setIsProductLoading] = useState(false);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [newProduct, setNewProduct] = useState({
    title: "",
    price: "",
    stock: "",
    category: "",
    description: "",
  });
  const [imageFile, setImageFile] = useState<File | null>(null);

  // Fetch Products
  const fetchProducts = async () => {
    setIsProductLoading(true);
    const { data } = await productsAPI.getAll();
    if (data) setProducts(data);
    setIsProductLoading(false);
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imageFile) {
      toast({ title: "Image Required", description: "Please upload a product image", variant: "destructive" });
      return;
    }

    const formData = new FormData();
    formData.append("title", newProduct.title);
    formData.append("price", newProduct.price);
    formData.append("stock", newProduct.stock);
    formData.append("category", newProduct.category);
    formData.append("description", newProduct.description);
    formData.append("image", imageFile);

    const { error } = await productsAPI.create(formData);
    if (error) {
      toast({ title: "Error", description: error, variant: "destructive" });
    } else {
      toast({ title: "Success", description: "Product added successfully" });
      setShowAddProduct(false);
      setNewProduct({ title: "", price: "", stock: "", category: "", description: "" });
      setImageFile(null);
      fetchProducts();
    }
  };

  const handleDeleteProduct = async (id: number) => {
    if (!confirm("Are you sure?")) return;
    const { error } = await productsAPI.delete(id);
    if (error) {
      toast({ title: "Error", description: error, variant: "destructive" });
    } else {
      toast({ title: "Deleted", description: "Product removed" });
      fetchProducts();
    }
  };

  // ... existing code ...

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-card/95 backdrop-blur">
        {/* ... Header Content ... */}
        <div className="flex items-center justify-between px-4 lg:px-6 h-16">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 text-foreground"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <Link to="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Shield className="h-4 w-4" />
              </div>
              <span className="font-serif text-lg font-bold text-foreground">
                {admin?.storeName || "Admin Dashboard"}
              </span>
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden sm:inline">
              Welcome, {admin?.name || "Admin"}
            </span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="container py-6 lg:py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {/* ... Existing Stats ... */}
          <StatsCard
            title="Total Users"
            value="12,543"
            icon={Users}
            trend={{ value: 12.5, isPositive: true }}
          />
          <StatsCard
            title="Total Revenue"
            value="₹4.2L"
            icon={TrendingUp}
            trend={{ value: 8.2, isPositive: true }}
          />
          <StatsCard
            title="Orders Today"
            value="847"
            icon={ShoppingBag}
            trend={{ value: 3.1, isPositive: true }}
          />
          <StatsCard
            title="Low Stock Items"
            value="23"
            icon={AlertTriangle}
            trend={{ value: 5, isPositive: false }}
          />
        </div>

        {/* INVENTORY MANAGEMENT SECTION */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Inventory Management</h2>
            <Button onClick={() => setShowAddProduct(!showAddProduct)}>
              {showAddProduct ? "Cancel" : "Add New Product"}
            </Button>
          </div>

          {showAddProduct && (
            <Card className="mb-6 border-primary/50">
              <CardHeader><CardTitle>Add New Product</CardTitle></CardHeader>
              <CardContent>
                <form onSubmit={handleCreateProduct} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <input className="p-2 border rounded bg-background" placeholder="Product Title" value={newProduct.title} onChange={e => setNewProduct({ ...newProduct, title: e.target.value })} required />
                    <input className="p-2 border rounded bg-background" placeholder="Price (₹)" type="number" value={newProduct.price} onChange={e => setNewProduct({ ...newProduct, price: e.target.value })} required />
                    <input className="p-2 border rounded bg-background" placeholder="Stock Quantity" type="number" value={newProduct.stock} onChange={e => setNewProduct({ ...newProduct, stock: e.target.value })} required />
                    <input className="p-2 border rounded bg-background" placeholder="Category" value={newProduct.category} onChange={e => setNewProduct({ ...newProduct, category: e.target.value })} required />
                    <input className="p-2 border rounded bg-background col-span-2" placeholder="Image File" type="file" onChange={e => setImageFile(e.target.files?.[0] || null)} accept="image/*" required />
                    <textarea className="p-2 border rounded bg-background col-span-2" placeholder="Description" value={newProduct.description} onChange={e => setNewProduct({ ...newProduct, description: e.target.value })} required />
                  </div>
                  <Button type="submit" disabled={isProductLoading}>
                    {isProductLoading ? "Uploading..." : "Save Product"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader><CardTitle>Product List</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs uppercase bg-muted/50">
                    <tr>
                      <th className="px-4 py-3">Image</th>
                      <th className="px-4 py-3">Title</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Price</th>
                      <th className="px-4 py-3">Stock</th>
                      <th className="px-4 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.length === 0 ? (
                      <tr><td colSpan={6} className="text-center py-4">No products found. Add one!</td></tr>
                    ) : products.map((prod: any) => (
                      <tr key={prod.id} className="border-b hover:bg-muted/50">
                        <td className="px-4 py-3">
                          <img src={prod.image_url} alt={prod.title} className="w-10 h-10 object-cover rounded" />
                        </td>
                        <td className="px-4 py-3 font-medium">{prod.title}</td>
                        <td className="px-4 py-3">{prod.category}</td>
                        <td className="px-4 py-3">₹{prod.price}</td>
                        <td className="px-4 py-3">{prod.stock}</td>
                        <td className="px-4 py-3">
                          <Button variant="destructive" size="sm" onClick={() => handleDeleteProduct(prod.id)}>Delete</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* ... Existing AI & Recent Activity ... */}
          {/* AI Query Section */}
          <Card className="lg:col-span-1">
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                AI Analytics Assistant
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] flex flex-col">
                <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                  {messages.map((message) => (
                    <ChatMessage
                      key={message.id}
                      content={message.content}
                      role={message.role}
                    />
                  ))}
                  {isLoading && (
                    <ChatMessage content="" role="assistant" isLoading />
                  )}
                  <div ref={messagesEndRef} />
                </div>
                <ChatInput
                  onSendMessage={handleSendMessage}
                  disabled={isLoading}
                  placeholder="Ask about sales, users, revenue..."
                />
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <div className="space-y-6">
            {/* Category Performance */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  Category Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { name: "Grocery", revenue: "₹1.2L", orders: 324, growth: 12 },
                    { name: "Dairy & Eggs", revenue: "₹85K", orders: 247, growth: 8 },
                    { name: "Snacks", revenue: "₹67K", orders: 189, growth: 15 },
                    { name: "Beverages", revenue: "₹45K", orders: 156, growth: -3 },
                    { name: "Personal Care", revenue: "₹32K", orders: 98, growth: 6 },
                  ].map((category) => (
                    <div key={category.name} className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
                      <div>
                        <p className="font-medium text-foreground">{category.name}</p>
                        <p className="text-sm text-muted-foreground">{category.orders} orders</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-foreground">{category.revenue}</p>
                        <p className={`text-sm ${category.growth >= 0 ? 'text-success' : 'text-destructive'}`}>
                          {category.growth >= 0 ? '+' : ''}{category.growth}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { action: "New order #1234", time: "2 min ago", type: "order" },
                    { action: "User registered", time: "5 min ago", type: "user" },
                    { action: "Low stock: Amul Milk", time: "12 min ago", type: "alert" },
                    { action: "Order #1233 delivered", time: "18 min ago", type: "success" },
                    { action: "New order #1232", time: "25 min ago", type: "order" },
                  ].map((activity, index) => (
                    <div key={index} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                      <div className="flex items-center gap-3">
                        <div className={`h-2 w-2 rounded-full ${activity.type === 'alert' ? 'bg-warning' :
                          activity.type === 'success' ? 'bg-success' :
                            'bg-primary'
                          }`} />
                        <span className="text-sm text-foreground">{activity.action}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AdminDashboard;
