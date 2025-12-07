import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ChatMessage from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import StatsCard from "@/components/admin/StatsCard";
import { ImageUpload } from "@/components/ui/image-upload";
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
  Loader2,
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

import { adminAPI, productsAPI } from "@/lib/api";

// ... existing imports ...

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

  // Stats State
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalRevenue: 0,
    ordersToday: 0,
    lowStockItems: 0
  });

  const [categoryStats, setCategoryStats] = useState<any[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [isStatsLoading, setIsStatsLoading] = useState(false);

  // Products State
  const [products, setProducts] = useState<any[]>([]);
  const [isProductLoading, setIsProductLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false); // For add product
  const [deletingId, setDeletingId] = useState<number | null>(null); // For delete product
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [newProduct, setNewProduct] = useState({
    title: "",
    price: "",
    stock: "",
    category: "",
    description: "",
  });
  const [imageFile, setImageFile] = useState<File | null>(null);

  // Chat State
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello Admin! 👋 I'm your analytics assistant. Ask me anything about your store's performance.",
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

  const fetchStats = async (storeId?: number) => {
    if (!storeId && admin?.storeId) storeId = admin.storeId;
    if (!storeId) return;

    setIsStatsLoading(true);

    const { data } = await adminAPI.getStats(storeId);
    if (data) setStats(data);

    const { data: catData } = await adminAPI.getCategoryPerformance(storeId);
    if (catData) setCategoryStats(catData);

    const { data: actData } = await adminAPI.getRecentActivity(storeId);
    if (actData) setRecentActivity(actData);

    setIsStatsLoading(false);
  };

  /* Fetch Products */
  const fetchProducts = async (storeId?: number) => {
    if (!storeId && admin?.storeId) storeId = admin.storeId;
    if (!storeId) return;

    // Only set loading on initial fetch if products are empty
    if (products.length === 0) setIsProductLoading(true);

    const { data } = await productsAPI.getAll(storeId);
    if (data) {
      setProducts(data);
    }
    setIsProductLoading(false);
  };

  useEffect(() => {
    const storedAdmin = localStorage.getItem('admin');
    if (storedAdmin) {
      const parsedAdmin = JSON.parse(storedAdmin);
      setAdmin(parsedAdmin);
      // Fetch data only after we have the admin
      if (parsedAdmin.storeId) {
        fetchStats(parsedAdmin.storeId);
        fetchProducts(parsedAdmin.storeId);
      }
    }
  }, []);

  /* AI Logic */
  const handleSendMessage = async (content: string) => {
    const userMessage: Message = { id: Date.now().toString(), content, role: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const { data, error } = await adminAPI.nlpQuery(content, admin?.storeId);

      let aiResponse = "I couldn't process that.";
      if (error) {
        aiResponse = `Error: ${error}`;
      } else if (data) {
        aiResponse = data.answer;
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: aiResponse,
        role: "assistant"
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (e) {
      setMessages((prev) => [...prev, { id: Date.now().toString(), content: "Network Error", role: "assistant" }]);
    }
    setIsLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin');
    toast({ title: "Logged out", description: "See you next time!" });
    navigate("/");
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return; // Prevent double submit

    if (!imageFile) {
      toast({ title: "Image Required", description: "Please upload a product image", variant: "destructive" });
      return;
    }

    setIsSubmitting(true);

    const formData = new FormData();
    formData.append("title", newProduct.title);
    formData.append("price", newProduct.price);
    formData.append("stock", newProduct.stock);
    formData.append("category", newProduct.category);
    formData.append("description", newProduct.description);

    if (admin?.storeId) {
      formData.append("store_id", admin.storeId.toString());
    } else {
      toast({ title: "Error", description: "Admin State Missing. Please relogin.", variant: "destructive" });
      setIsSubmitting(false);
      return;
    }
    formData.append("image", imageFile);

    const { error } = await productsAPI.create(formData);
    if (error) {
      toast({ title: "Error", description: error, variant: "destructive" });
    } else {
      toast({ title: "Success", description: "Product added successfully" });
      setShowAddProduct(false);
      setNewProduct({ title: "", price: "", stock: "", category: "", description: "" });
      setImageFile(null);
      fetchProducts(admin.storeId);
      fetchStats(admin.storeId); // Update stats after adding product
    }
    setIsSubmitting(false);
  };

  const handleDeleteProduct = async (id: number) => {
    if (deletingId) return; // Prevent concurrent deletes? Or allow parallel? Better safe.
    if (!confirm("Are you sure?")) return;

    setDeletingId(id);
    const { error } = await productsAPI.delete(id);
    if (error) {
      toast({ title: "Error", description: error, variant: "destructive" });
    } else {
      toast({ title: "Deleted", description: "Product removed" });
      fetchProducts(admin.storeId);
      fetchStats(admin.storeId);
    }
    setDeletingId(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      {/* ... Header Content ... (Keep existing Header) */}
      <header className="sticky top-0 z-50 border-b border-border bg-card/95 backdrop-blur">
        <div className="flex items-center justify-between px-4 lg:px-6 h-16">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 text-foreground"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <Link to="/admin/dashboard" className="flex items-center gap-2">
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
          {isStatsLoading ? (
            Array(4).fill(0).map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-8 bg-muted rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-muted rounded w-1/4"></div>
                </CardContent>
              </Card>
            ))
          ) : (
            <>
              <StatsCard
                title="Total Users"
                value={stats.totalUsers.toLocaleString()}
                icon={Users}
                trend={{ value: 12.5, isPositive: true }}
              />
              <StatsCard
                title="Total Revenue"
                value={`₹${stats.totalRevenue.toLocaleString()}`}
                icon={TrendingUp}
                trend={{ value: 8.2, isPositive: true }}
              />
              <StatsCard
                title="Orders Today"
                value={stats.ordersToday.toString()}
                icon={ShoppingBag}
                trend={{ value: 3.1, isPositive: true }}
              />
              <StatsCard
                title="Low Stock Items"
                value={stats.lowStockItems.toString()}
                icon={AlertTriangle}
                trend={{ value: 5, isPositive: false }}
              />
            </>
          )}
        </div>

        {/* INVENTORY MANAGEMENT SECTION */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Inventory Management</h2>
            <Button onClick={() => setShowAddProduct(!showAddProduct)}>
              {showAddProduct ? <X className="h-4 w-4 mr-2" /> : <TrendingUp className="h-4 w-4 mr-2" />}
              {showAddProduct ? "Cancel" : "Add Product"}
            </Button>
          </div>

          {/* Add Product Form */}
          {showAddProduct && (
            <Card className="mb-6 animate-fade-up">
              <CardHeader>
                <CardTitle>Add New Product</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleCreateProduct} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Product Title</label>
                      <input
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                        placeholder="e.g. Organic Brown Rice"
                        value={newProduct.title}
                        onChange={(e) => setNewProduct({ ...newProduct, title: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Price (₹)</label>
                      <input
                        type="number"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                        placeholder="e.g. 120"
                        value={newProduct.price}
                        onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Stock Quantity</label>
                      <input
                        type="number"
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                        placeholder="e.g. 50"
                        value={newProduct.stock}
                        onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Category</label>
                      <input
                        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                        placeholder="e.g. Grains"
                        value={newProduct.category}
                        onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Description</label>
                    <textarea
                      className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                      placeholder="Product details..."
                      value={newProduct.description}
                      onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Product Image</label>
                    <ImageUpload
                      value={imageFile}
                      onChange={(file) => setImageFile(file)}
                    />
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit" disabled={isSubmitting}>
                      {isSubmitting ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Adding...
                        </>
                      ) : (
                        "Add Product"
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Product List */}
          <Card>
            <CardHeader>
              <CardTitle>Current Inventory</CardTitle>
            </CardHeader>
            <CardContent>
              {isProductLoading ? (
                <div className="text-center py-8 text-muted-foreground">Loading inventory...</div>
              ) : products.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No products found. Start by adding one!
                </div>
              ) : (
                <div className="rounded-md border">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50 transition-colors hover:bg-muted/50">
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Image</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Name</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Category</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Price</th>
                        <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Stock</th>
                        <th className="h-12 px-4 text-right align-middle font-medium text-muted-foreground">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map((p) => (
                        <tr key={p.id} className="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                          <td className="p-4 align-middle">
                            <img
                              src={p.image_url || "https://placehold.co/50"}
                              alt={p.title}
                              className="h-10 w-10 rounded object-cover"
                            />
                          </td>
                          <td className="p-4 align-middle font-medium">{p.title}</td>
                          <td className="p-4 align-middle">{p.category}</td>
                          <td className="p-4 align-middle">₹{p.price}</td>
                          <td className="p-4 align-middle">
                            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 ${p.stock < 10 ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"
                              }`}>
                              {p.stock} units
                            </span>
                          </td>
                          <td className="p-4 align-middle text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteProduct(p.id)}
                              disabled={deletingId === p.id}
                            >
                              {deletingId === p.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <TrendingUp className="h-4 w-4 rotate-180" />}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
        {/* Skipping inventory part for brevity in this replace block, resuming at grid */}

        <div className="grid lg:grid-cols-2 gap-6">
          {/* ... AI Section ... */}
          {/* AI Query Section */}
          <Card className="lg:col-span-1 flex flex-col h-[600px]">
            <CardHeader className="border-b">
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                AI Analytics Assistant
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[400px]">
              {messages.map((msg) => (
                <ChatMessage
                  key={msg.id}
                  content={msg.content}
                  role={msg.role}
                />
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-muted-foreground text-sm p-2 bg-secondary/50 rounded-lg w-fit">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing store data...
                </div>
              )}
              <div ref={messagesEndRef} />
            </CardContent>
            <div className="p-4 border-t bg-secondary/10">
              <ChatInput
                onSendMessage={handleSendMessage}
                disabled={isLoading}
                placeholder="Ask about revenue, users, or top products..."
              />
            </div>
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
                  {isStatsLoading ? (
                    Array(3).fill(0).map((_, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg animate-pulse">
                        <div className="space-y-2 w-1/2">
                          <div className="h-4 bg-muted rounded w-2/3"></div>
                          <div className="h-3 bg-muted rounded w-1/3"></div>
                        </div>
                        <div className="h-6 bg-muted rounded w-16"></div>
                      </div>
                    ))
                  ) : categoryStats.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No category data yet.</p>
                  ) : categoryStats.map((category) => (
                    <div key={category.name} className="flex items-center justify-between p-3 bg-secondary/50 rounded-lg">
                      <div>
                        <p className="font-medium text-foreground">{category.name}</p>
                        <p className="text-sm text-muted-foreground">{category.orders} orders</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-foreground">₹{category.revenue?.toLocaleString() ?? 0}</p>
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
                  {isStatsLoading ? (
                    Array(4).fill(0).map((_, i) => (
                      <div key={i} className="flex items-center justify-between py-2 border-b border-border last:border-0 animate-pulse">
                        <div className="flex items-center gap-3 w-3/4">
                          <div className="h-2 w-2 rounded-full bg-muted"></div>
                          <div className="h-4 bg-muted rounded w-full"></div>
                        </div>
                        <div className="h-3 bg-muted rounded w-12"></div>
                      </div>
                    ))
                  ) : recentActivity.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No recent activity.</p>
                  ) : recentActivity.map((activity, index) => (
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
