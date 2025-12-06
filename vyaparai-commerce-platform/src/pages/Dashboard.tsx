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
import { productsAPI, Product } from "@/lib/api";
import { useCart } from "@/context/CartContext";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  products?: Product[];
}

// Helper to assign icons dynamically
const getCategoryIcon = (name: string) => {
  const n = name.toLowerCase();
  if (n.includes("fruit") || n.includes("veg")) return "🍎";
  if (n.includes("dairy") || n.includes("milk") || n.includes("egg")) return "🥛";
  if (n.includes("snack") || n.includes("chip")) return "🍿";
  if (n.includes("beverage") || n.includes("drink") || n.includes("juice")) return "🥤";
  if (n.includes("care") || n.includes("soap")) return "🧴";
  if (n.includes("house") || n.includes("clean")) return "🏠";
  return "📦";
};

const Dashboard = () => {
  const { user } = useUser();
  const navigate = useNavigate();

  // Products State
  const [allProducts, setAllProducts] = useState<Product[]>([]);
  const [displayedProducts, setDisplayedProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loadingProducts, setLoadingProducts] = useState(true);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Welcome to VyaparAI! 👋 I'm your AI shopping assistant. You can ask me things like:\n\n• \"Show me snacks under ₹50\"\n• \"I need milk and eggs\"\n• \"What's in stock for breakfast?\"\n• \"Any discounts today?\"\n\nHow can I help you shop today?",
      role: "assistant",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showProducts, setShowProducts] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { addToCart, cartCount } = useCart();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch Products
  useEffect(() => {
    const loadProducts = async () => {
      setLoadingProducts(true);
      const { data } = await productsAPI.getAll();
      if (data) {
        // Map backend fields to frontend if needed
        const mapped = data.map((p: any) => ({
          ...p,
          id: p.id.toString(),
          image: p.image_url || p.image || "https://placehold.co/300x300?text=No+Image"
        }));
        setAllProducts(mapped);
        setDisplayedProducts(mapped);

        // Update category counts dynamically from DB products
        const uniqueCats = Array.from(new Set(mapped.map((p: any) => p.category))).filter(Boolean);
        const newCats = uniqueCats.map((cat: any) => ({
          id: cat,
          name: cat,
          icon: getCategoryIcon(cat),
          count: mapped.filter((p: any) => p.category === cat).length
        }));
        setCategories(newCats);
      }
      setLoadingProducts(false);
    };
    loadProducts();
  }, []);

  // Sync User to Backend
  useEffect(() => {
    if (user) {
      const syncUser = async () => {
        try {
          const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
          await fetch(`${API_URL}/users/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              clerkId: user.id,
              email: user.primaryEmailAddress?.emailAddress,
              fullName: user.fullName,
              phone: user.primaryPhoneNumber?.phoneNumber,
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

    // Simulate AI response with REAL product filtering
    setTimeout(() => {
      const lowerContent = content.toLowerCase();
      let responseContent = "";
      let products: Product[] = [];

      // Simple keyword search
      const matchedProducts = allProducts.filter(p =>
        p.title.toLowerCase().includes(lowerContent) ||
        p.category.toLowerCase().includes(lowerContent) ||
        p.description?.toLowerCase().includes(lowerContent)
      );

      if (matchedProducts.length > 0) {
        responseContent = `I found ${matchedProducts.length} items matching your request!`;
        products = matchedProducts.slice(0, 5);
      } else {
        responseContent = "I couldn't find exactly what you asked for, but here are some popular items:";
        products = allProducts.slice(0, 4);
      }

      if (lowerContent.includes("snack") || lowerContent.includes("chips")) {
        responseContent = "Here are some snack options! 🍿";
        products = allProducts.filter((p) => p.category.toLowerCase().includes("snack"));
      } else if (lowerContent.includes("milk") || lowerContent.includes("dairy")) {
        responseContent = "Fresh dairy products 🥛";
        products = allProducts.filter((p) => p.category.toLowerCase().includes("dairy"));
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: responseContent,
        role: "assistant",
        products: products.length > 0 ? products : undefined,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setShowProducts(true);
      // setDisplayedProducts(products); // Don't filter the right panel solely on chat, unless desired. 
      // Let's keep right panel as "browse" or update it. 
      // The original code updated displayedProducts. I'll stick to that pattern if it makes sense, 
      // or allows the user to see what they asked for.
      if (products.length > 0) setDisplayedProducts(products);

      setIsLoading(false);
    }, 1500);
  };

  const handleAddToCart = (productId: string, quantity: number) => {
    const product = allProducts.find((p) => p.id === productId);
    if (product) {
      addToCart(product, quantity);
    }
  };

  const handleCategorySelect = (categoryId: string | null) => {
    setSelectedCategory(categoryId);
    if (categoryId) {
      // Filter Logic
      const filtered = allProducts.filter(p => {
        const catName = categories.find(c => c.id === categoryId)?.name.toLowerCase();
        return p.category.toLowerCase() === catName || p.category.toLowerCase() === categoryId;
      });
      setDisplayedProducts(filtered.length > 0 ? filtered : []);
      setShowProducts(true);
    } else {
      setDisplayedProducts(allProducts);
      setShowProducts(true);
    }
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans">
      {/* ... Header ... */}
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
                onChange={(e) => {
                  const term = e.target.value.toLowerCase();
                  setSearchQuery(term);
                  if (!term) {
                    setDisplayedProducts(allProducts);
                  } else {
                    const matches = allProducts.filter(p =>
                      p.title.toLowerCase().includes(term) ||
                      p.category.toLowerCase().includes(term) ||
                      p.description?.toLowerCase().includes(term)
                    );
                    setDisplayedProducts(matches);
                  }
                }}
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

          {categories.slice(0, 5).map(cat => (
            <span key={cat.id} onClick={() => handleCategorySelect(cat.id)} className="hover:border border-white/0 hover:border-white px-2 py-1 rounded-sm cursor-pointer whitespace-nowrap">{cat.name}</span>
          ))}
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
            categories={categories}
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
          <div className={`hidden lg:block w-[400px] xl:w-[500px] overflow-y-auto p-6 bg-secondary/30 border-l border-border ${showProducts ? '' : 'hidden'}`}>
            <h3 className="font-serif font-semibold text-foreground mb-4">
              {selectedCategory ? categories.find(c => c.id === selectedCategory)?.name : searchQuery ? "Search Results" : "Featured Categories"}
            </h3>
            {loadingProducts ? (
              <div className="text-center py-10">Loading Products...</div>
            ) : (
              <>
                {!selectedCategory && !searchQuery ? (
                  <div className="space-y-8 pb-10">
                    {categories.map(cat => {
                      const catProducts = allProducts.filter(p => p.category?.toLowerCase() === cat.name.toLowerCase() || p.category?.toLowerCase() === cat.id).slice(0, 4);
                      if (catProducts.length === 0) return null;
                      return (
                        <div key={cat.id}>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-bold flex items-center gap-2">
                              <span>{cat.icon}</span> {cat.name}
                            </h4>
                            <Button variant="link" size="sm" onClick={() => handleCategorySelect(cat.id)}>See More</Button>
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            {catProducts.map((product) => (
                              <ProductCard
                                key={product.id}
                                {...product}
                                onAddToCart={handleAddToCart}
                              />
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    {displayedProducts.length === 0 && <p className="col-span-2 text-muted-foreground">No products found.</p>}
                    {displayedProducts.map((product) => (
                      <ProductCard
                        key={product.id}
                        {...product}
                        onAddToCart={handleAddToCart}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
