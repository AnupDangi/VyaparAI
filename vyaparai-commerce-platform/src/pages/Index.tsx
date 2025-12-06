import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  ShoppingBag,
  ArrowRight,
  Sparkles,
  ScanLine,
  BarChart3,
  MessageSquare,
  TrendingUp,
  Brain
} from "lucide-react";
import { useUser } from "@clerk/clerk-react";
import { useEffect } from "react";

const Index = () => {
  const navigate = useNavigate();
  const { isSignedIn } = useUser();

  // Redirect if logged in
  useEffect(() => {
    if (isSignedIn) {
      navigate("/dashboard");
    }
  }, [isSignedIn, navigate]);

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans">
      {/* Navbar */}
      <nav className="border-b bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 md:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingBag className="h-6 w-6 text-primary" />
            <span className="font-serif text-xl font-bold tracking-tight">VyaparAI</span>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" onClick={() => navigate("/login")}>
              Login
            </Button>
            <Button onClick={() => navigate("/signup")} className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-lg shadow-primary/20">
              Get Started
            </Button>
          </div>
        </div>
      </nav>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-24 md:py-32 px-4 relative overflow-hidden bg-gradient-to-b from-primary/5 to-background">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl opacity-30 pointer-events-none">
            <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl mix-blend-multiply animate-blob" />
            <div className="absolute top-20 right-10 w-72 h-72 bg-purple-500/20 rounded-full blur-3xl mix-blend-multiply animate-blob animation-delay-2000" />
            <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500/20 rounded-full blur-3xl mix-blend-multiply animate-blob animation-delay-4000" />
          </div>

          <div className="max-w-4xl mx-auto text-center relative z-10 space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium animate-in fade-in slide-in-from-bottom-4 duration-700">
              <Sparkles className="h-4 w-4" />
              <span>AI-Powered Commerce for Everyone</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-tight animate-in fade-in slide-in-from-bottom-6 duration-1000 delay-100">
              Shopping understood <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-purple-500 to-blue-600">
                in your own words.
              </span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-200">
              Experience the future of shopping. Upload handwritten lists, chat naturally, and get smart insights on your spending.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
              <Button size="lg" className="h-14 px-8 text-lg gap-2 shadow-xl shadow-primary/20 hover:scale-105 transition-transform" onClick={() => navigate("/signup")}>
                Try VyaparAI Now <ArrowRight className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </section>

        {/* Feature 1: Natural Language */}
        <section className="py-24 bg-card border-y">
          <div className="max-w-7xl mx-auto px-4 md:px-8 grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="h-12 w-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center">
                <MessageSquare className="h-6 w-6" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold">Just ask like a human.</h2>
              <p className="text-lg text-muted-foreground">
                Done with complex filters? Just say <span className="text-foreground font-semibold">"Show me snacks under ₹50"</span> or <span className="text-foreground font-semibold">"I need milk and eggs"</span>. Our AI understands your intent and finds exactly what you need.
              </p>
              <ul className="space-y-3">
                {['"Suggest tailored products"', '"Show me healthy breakfast options"', '"Filter by price and category instantly"'].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-muted-foreground">
                    <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative p-8 bg-secondary/50 rounded-3xl border shadow-lg transform md:rotate-2 hover:rotate-0 transition-transform duration-500">
              <div className="bg-background rounded-xl p-4 shadow-sm border space-y-4">
                <div className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary/20 flex-shrink-0" />
                  <div className="bg-secondary p-3 rounded-lg rounded-tl-none text-sm">
                    Show me fresh fruits under ₹100 🍎
                  </div>
                </div>
                <div className="flex gap-3 flex-row-reverse">
                  <div className="h-8 w-8 rounded-full bg-blue-500 flex-shrink-0" />
                  <div className="bg-blue-600 text-white p-3 rounded-lg rounded-tr-none text-sm">
                    Here are 5 fresh fruit options for you!
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div className="h-24 bg-muted rounded-md animate-pulse" />
                  <div className="h-24 bg-muted rounded-md animate-pulse delay-75" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature 2: Smart OCR */}
        <section className="py-24 bg-background">
          <div className="max-w-7xl mx-auto px-4 md:px-8 grid md:grid-cols-2 gap-12 items-center md:flex-row-reverse">
            <div className="order-2 md:order-1 relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 to-emerald-500/10 blur-2xl rounded-full transform group-hover:scale-110 transition-transform duration-700" />
              <div className="relative bg-card p-2 rounded-2xl border shadow-2xl transform md:-rotate-2 hover:rotate-0 transition-transform duration-500">
                <div className="aspect-[4/3] bg-muted rounded-xl flex items-center justify-center border-2 border-dashed border-muted-foreground/20">
                  <div className="text-center space-y-2">
                    <ScanLine className="h-10 w-10 mx-auto text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">Scanning List...</p>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg">
                    <span className="text-sm font-medium">Apple (1kg)</span>
                    <span className="text-green-600 text-xs font-bold">MATCHED</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-secondary/30 rounded-lg">
                    <span className="text-sm font-medium">Milk (2L)</span>
                    <span className="text-green-600 text-xs font-bold">MATCHED</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="order-1 md:order-2 space-y-6">
              <div className="h-12 w-12 rounded-xl bg-green-100 text-green-600 flex items-center justify-center">
                <ScanLine className="h-6 w-6" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold">Upload. Click. Shop.</h2>
              <p className="text-lg text-muted-foreground">
                Still writing lists on paper? Just snap a photo of your handwritten note. Our extensive **OCR** tech extracts items and fills your cart instantly.
              </p>
              <Button variant="outline" className="gap-2" onClick={() => navigate("/login")}>
                Try Image Upload <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </section>

        {/* Feature 3: Analytics */}
        <section className="py-24 bg-accent/5">
          <div className="max-w-7xl mx-auto px-4 md:px-8 text-center space-y-12">
            <div className="space-y-4 max-w-3xl mx-auto">
              <div className="h-12 w-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mx-auto">
                <BarChart3 className="h-6 w-6" />
              </div>
              <h2 className="text-3xl md:text-4xl font-bold">Deep Insights for Everyone</h2>
              <p className="text-lg text-muted-foreground">
                Whether you're a shopper or a seller, we give you the data you need.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {/* User Analytics */}
              <div className="bg-background p-8 rounded-3xl border shadow-sm hover:shadow-lg transition-all text-left space-y-4 group">
                <div className="flex items-center gap-3 mb-2">
                  <Brain className="h-6 w-6 text-indigo-500 group-hover:scale-110 transition-transform" />
                  <h3 className="text-xl font-bold">For Shoppers</h3>
                </div>
                <p className="text-muted-foreground">
                  "How much did I spend last week?"<br />
                  Get instant answers to your spending habits naturally.
                </p>
                <div className="h-32 w-full bg-secondary/50 rounded-xl flex items-end justify-around pb-4 px-4 gap-2">
                  {[40, 70, 45, 90, 60].map((h, i) => (
                    <div key={i} className="w-full bg-indigo-500/20 rounded-t-sm relative group-hover:bg-indigo-500/40 transition-colors" style={{ height: `${h}%` }}>
                      <div className="absolute bottom-0 w-full bg-indigo-500 h-1 rounded-sm" />
                    </div>
                  ))}
                </div>
              </div>

              {/* Admin Analytics */}
              <div className="bg-background p-8 rounded-3xl border shadow-sm hover:shadow-lg transition-all text-left space-y-4 group">
                <div className="flex items-center gap-3 mb-2">
                  <TrendingUp className="h-6 w-6 text-emerald-500 group-hover:scale-110 transition-transform" />
                  <h3 className="text-xl font-bold">For Sellers</h3>
                </div>
                <p className="text-muted-foreground">
                  Track inventory, sales growth, and popular categories in real-time.
                </p>
                <div className="h-32 w-full bg-secondary/50 rounded-xl flex items-center justify-center">
                  <div className="text-2xl font-bold text-foreground">
                    +124% <span className="text-sm text-muted-foreground font-normal">Growth</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>

      <footer className="border-t py-12 bg-card">
        <div className="max-w-7xl mx-auto px-4 md:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <ShoppingBag className="h-5 w-5 text-primary" />
            <span className="font-bold">VyaparAI</span>
          </div>
          <p className="text-muted-foreground text-sm">© 2024 VyaparAI. Built for the Future.</p>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground">Privacy</a>
            <a href="#" className="hover:text-foreground">Terms</a>
            <a href="#" className="hover:text-foreground">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
