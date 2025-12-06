import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ChatMessage from "@/components/chat/ChatMessage";
import ChatInput from "@/components/chat/ChatInput";
import CategorySidebar from "@/components/products/CategorySidebar";
import ProductCard from "@/components/products/ProductCard";
import { UserButton, useUser } from "@clerk/clerk-react";
import { Input } from "@/components/ui/input";
import {
  ShoppingBag,
  ShoppingCart,
  Menu,
  X,
  Sparkles,
  Search,
  MapPin,
} from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  products?: Product[];
}

interface Product {
  id: string;
  title: string;
  price: number;
  stock: number;
  image: string;
  category: string;
}

// Mock data
const mockCategories = [
  { id: "grocery", name: "Grocery", icon: "🛒", count: 145 },
  { id: "dairy", name: "Dairy & Eggs", icon: "🥛", count: 32 },
  { id: "snacks", name: "Snacks", icon: "🍿", count: 67 },
  { id: "beverages", name: "Beverages", icon: "🥤", count: 45 },
  { id: "personal-care", name: "Personal Care", icon: "🧴", count: 89 },
  { id: "household", name: "Household", icon: "🏠", count: 56 },
];

const mockProducts: Product[] = [
  { id: "1", title: "Tata Salt 1kg", price: 28, stock: 50, image: "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=300&h=300&fit=crop", category: "Grocery" },
  { id: "2", title: "Amul Butter 500g", price: 280, stock: 25, image: "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=300&h=300&fit=crop", category: "Dairy & Eggs" },
  { id: "3", title: "Lays Classic Chips", price: 20, stock: 100, image: "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=300&h=300&fit=crop", category: "Snacks" },
  { id: "4", title: "Coca Cola 2L", price: 95, stock: 40, image: "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=300&h=300&fit=crop", category: "Beverages" },
  { id: "5", title: "Aashirvaad Atta 5kg", price: 255, stock: 30, image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=300&fit=crop", category: "Grocery" },
  { id: "6", title: "Amul Milk 1L", price: 60, stock: 0, image: "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=300&fit=crop", category: "Dairy & Eggs" },
];

const Dashboard = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Welcome to VyaparAI! 👋 I'm your AI shopping assistant. You can ask me things like:\n\n• \"Show me snacks under ₹50\"\n• \"I need milk and eggs\"\n• \"What's in stock for breakfast?\"\n• \"Any discounts today?\"\n\nHow can I help you shop today?",
      role: "assistant",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showProducts, setShowProducts] = useState(false);
  const [displayedProducts, setDisplayedProducts] = useState<Product[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Sync User to Backend
  useEffect(() => {
    if (user) {
      const syncUser = async () => {
        try {
          await fetch('http://localhost:8000/api/users/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              clerkId: user.id,
              email: user.primaryEmailAddress?.emailAddress,
              fullName: user.fullName,
              phone: user.primaryPhoneNumber?.phoneNumber,
              // Add default address/city/pincode if stored in Clerk metadata or leave empty
            })
          });
          console.log("User synced to backend");
        } catch (error) {
          console.error("Failed to sync user", error);
        }
      };
      syncUser();
    }
  }, [user]);

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
      let products: Product[] = [];

      if (lowerContent.includes("snack") || lowerContent.includes("chips")) {
        responseContent = "Here are some snack options for you! 🍿";
        products = mockProducts.filter((p) => p.category === "Snacks");
      } else if (lowerContent.includes("milk") || lowerContent.includes("dairy") || lowerContent.includes("egg")) {
        responseContent = "Here are dairy products available near you 🥛";
        products = mockProducts.filter((p) => p.category === "Dairy & Eggs");
      } else if (lowerContent.includes("discount") || lowerContent.includes("offer") || lowerContent.includes("sale")) {
        responseContent = "Great news! Here are today's special offers 🎉";
        products = mockProducts.slice(0, 3);
      } else if (lowerContent.includes("show") || lowerContent.includes("all") || lowerContent.includes("product")) {
        responseContent = "Here's what's available in our store:";
        products = mockProducts;
      } else {
        responseContent = "I found some products that might interest you based on your query:";
        products = mockProducts.slice(0, 4);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: responseContent,
        role: "assistant",
        products,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setShowProducts(true);
      setDisplayedProducts(products);
      setIsLoading(false);
    }, 1500);
  };

  const handleAddToCart = (productId: string, quantity: number) => {
    const product = mockProducts.find((p) => p.id === productId);
    if (product) {
      setCartCount((prev) => prev + quantity);
      toast({
        title: "Added to cart!",
        description: `${quantity}x ${product.title} added to your cart`,
      });
    }
  };

  const handleCategorySelect = (categoryId: string | null) => {
    setSelectedCategory(categoryId);
    if (categoryId) {
      const category = mockCategories.find((c) => c.id === categoryId);
      if (category) {
        const filtered = mockProducts.filter(
          (p) => p.category.toLowerCase().replace(/[^a-z]/g, "") === categoryId.replace("-", "")
        );
        setDisplayedProducts(filtered.length > 0 ? filtered : mockProducts);
        setShowProducts(true);
      }
    } else {
      setDisplayedProducts(mockProducts);
      setShowProducts(true);
    }
    setSidebarOpen(false);
  };


  return (
    <div className="min-h-screen bg-background flex flex-col font-sans">
      {/* Amazon-like Header */}
      <header className="sticky top-0 z-50 bg-[#131921] text-white shrink-0">
        <div className="flex items-center gap-4 px-4 h-16 max-w-[1500px] mx-auto">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-1 hover:border border-white/0 hover:border-white p-1 rounded-sm">
            <ShoppingBag className="h-6 w-6 text-primary-foreground" />
            <span className="font-serif text-xl font-bold tracking-tight">VyaparAI</span>
          </Link>

          {/* Delivery Location */}
          <div className="hidden md:flex flex-col items-start leading-tight text-xs hover:border border-white/0 hover:border-white p-2 rounded-sm cursor-pointer">
            <span className="text-gray-300 ml-3">Deliver to {user?.firstName || 'User'}</span>
            <div className="flex items-center gap-1 font-bold">
              <MapPin className="h-4 w-4" />
              <span>Mumbai 400001</span>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl px-2 hidden sm:block">
            <div className="flex h-10 w-full bg-white rounded-md overflow-hidden focus-within:ring-2 ring-primary">
              <div className="flex items-center justify-center bg-gray-100 px-3 text-gray-500 text-xs border-r hover:bg-gray-200 cursor-pointer">
                All
              </div>
              <input
                type="text"
                className="flex-1 px-3 text-black text-sm outline-none"
                placeholder="Search VyaparAI..."
              />
              <button className="bg-[#febd69] hover:bg-[#f3a847] px-4 flex items-center justify-center">
                <Search className="h-5 w-5 text-black" />
              </button>
            </div>
          </div>

          <div className="flex-1 sm:hidden"></div>

          {/* Right Actions */}
          <div className="flex items-center gap-1 md:gap-4">

            {/* Returns & Orders */}
            <div className="hidden md:flex flex-col leading-tight text-xs hover:border border-white/0 hover:border-white p-2 rounded-sm cursor-pointer">
              <span className="text-gray-300">Returns</span>
              <span className="font-bold">& Orders</span>
            </div>

            {/* Profile */}
            <div className="flex items-center hover:border border-white/0 hover:border-white p-1 rounded-sm">
              <div className="text-right mr-2 hidden md:block">
                <div className="text-xs text-gray-300">Hello, {user?.firstName || 'Guest'}</div>
                <div className="text-sm font-bold">Account & Lists</div>
              </div>
              <UserButton afterSignOutUrl="/" appearance={{
                elements: {
                  avatarBox: "h-9 w-9 border-2 border-white/20"
                }
              }} />
            </div>

            {/* Cart */}
            <Link to="/cart" className="flex items-end hover:border border-white/0 hover:border-white p-2 rounded-sm relative">
              <ShoppingCart className="h-7 w-7 md:h-8 md:w-8" />
              <span className="absolute top-0 left-1/2 -translate-x-1/2 md:left-5 md:translate-x-0 font-bold text-[#f08804] text-sm bg-[#131921] px-1">
                {cartCount}
              </span>
              <span className="font-bold hidden md:inline mb-1">Cart</span>
            </Link>
          </div>
        </div>

        {/* Sub Header / Category Bar */}
        <div className="bg-[#232f3e] h-10 flex items-center px-4 gap-4 text-sm text-white font-medium overflow-x-auto">
          <button
            className="flex items-center gap-1 hover:border border-white/0 hover:border-white px-1 py-0.5 rounded-sm whitespace-nowrap"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu className="h-5 w-5" />
            All
          </button>
          <span className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap">Fresh</span>
          <span className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap">Mobiles</span>
          <span className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap">Best Sellers</span>
          <span className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap">Today's Deals</span>
          <span className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap">Electronics</span>
          <span className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap hidden sm:inline">Customer Service</span>
          <span className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap hidden sm:inline">New Releases</span>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden relative">
        {/* Sidebar Overlay */}
        {sidebarOpen && (
          <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
        )}

        {/* Sidebar */}
        <div
          className={`fixed lg:static inset-y-0 left-0 z-50 transform transition-transform duration-300 lg:transform-none bg-background border-r border-border w-64 shrink-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
            }`}
        >
          <CategorySidebar
            categories={mockCategories}
            selectedCategory={selectedCategory}
            onSelectCategory={handleCategorySelect}
          />
        </div>

        {/* Chat + Products Area */}
        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden w-full relative z-0">
          {/* Chat Section */}
          <div className="flex-1 flex flex-col h-full lg:border-r border-border relative">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4">
              {messages.map((message) => (
                <div key={message.id}>
                  <ChatMessage content={message.content} role={message.role} />
                  {message.products && message.products.length > 0 && (
                    <div className="ml-11 mt-3 grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {message.products.slice(0, 3).map((product) => (
                        <ProductCard
                          key={product.id}
                          {...product}
                          onAddToCart={handleAddToCart}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <ChatMessage content="" role="assistant" isLoading />
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input */}
            <div className="p-4 border-t border-border bg-card">
              <div className="max-w-3xl mx-auto">
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                  <Sparkles className="h-3 w-3" />
                  <span>Try: "Show me healthy breakfast options" or "I need rice and dal"</span>
                </div>
                <ChatInput
                  onSendMessage={handleSendMessage}
                  disabled={isLoading}
                  placeholder="What are you looking for today?"
                />
              </div>
            </div>
          </div>

          {/* Products Grid (Desktop Right Panel) */}
          {showProducts && (
            <div className="hidden lg:block w-[400px] xl:w-[500px] overflow-y-auto p-6 bg-secondary/30 border-l border-border">
              <h3 className="font-serif font-semibold text-foreground mb-4">
                Products ({displayedProducts.length})
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {displayedProducts.map((product) => (
                  <ProductCard
                    key={product.id}
                    {...product}
                    onAddToCart={handleAddToCart}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
