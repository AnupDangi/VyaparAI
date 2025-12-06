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
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const lowerContent = content.toLowerCase();
      let responseContent = "";
      let showChart = false;

      if (lowerContent.includes("dairy") && (lowerContent.includes("week") || lowerContent.includes("user"))) {
        responseContent = "📊 **Dairy Category - Weekly Report**\n\n• Total users who purchased dairy: **247**\n• Most popular: Amul Butter (89 units)\n• Revenue: ₹45,230\n• Peak day: Wednesday (52 orders)\n\nWould you like me to break this down by product?";
        showChart = true;
      } else if (lowerContent.includes("revenue") && lowerContent.includes("snack")) {
        responseContent = "💰 **Snacks Category Revenue**\n\n• Today: ₹12,450\n• This week: ₹67,890\n• This month: ₹2,34,560\n\nTop performers:\n1. Lays Classic - ₹8,200\n2. Kurkure - ₹6,100\n3. Haldiram's Mixture - ₹4,300";
        showChart = true;
      } else if (lowerContent.includes("most") && (lowerContent.includes("sold") || lowerContent.includes("popular"))) {
        responseContent = "🏆 **Top Selling Products Today**\n\n1. Tata Salt 1kg - 156 units\n2. Amul Butter 500g - 89 units\n3. Aashirvaad Atta 5kg - 67 units\n4. Coca Cola 2L - 52 units\n5. Lays Classic - 48 units\n\nTotal revenue from top 5: ₹28,450";
      } else if (lowerContent.includes("average") && lowerContent.includes("order")) {
        responseContent = "📈 **Average Order Value Analysis**\n\n• Today's AOV: ₹345\n• Weekly average: ₹312\n• Monthly average: ₹298\n\n↑ 12% increase from last month!\n\nHighest AOV category: Grocery (₹456)";
      } else if (lowerContent.includes("low stock") || lowerContent.includes("stock")) {
        responseContent = "⚠️ **Low Stock Alert**\n\n• Amul Milk 1L - **OUT OF STOCK**\n• Sugar 5kg - 5 units left\n• Maggi Noodles - 8 units left\n• Surf Excel 1kg - 3 units left\n\nRecommendation: Reorder these items immediately.";
      } else {
        responseContent = "I found some insights for your query:\n\n• Total orders today: 847\n• Active users: 1,234\n• Revenue: ₹2,45,000\n• Items in cart: 3,456\n\nCan you be more specific? Try asking about specific categories, time periods, or metrics.";
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: responseContent,
        role: "assistant",
        chart: showChart,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin');
    toast({
      title: "Logged out",
      description: "See you next time, Admin!",
    });
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-card/95 backdrop-blur">
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

        <div className="grid lg:grid-cols-2 gap-6">
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
