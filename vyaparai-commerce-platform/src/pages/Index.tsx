import MainLayout from "@/components/layout/MainLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";
import {
  MessageSquare,
  ShoppingBag,
  Users,
  TrendingUp,
  Store,
  Search,
  Sparkles,
  ArrowRight,
  BarChart3,
  Zap,
} from "lucide-react";

const Index = () => {
  return (
    <MainLayout>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-secondary via-background to-background" />
        <div className="container relative py-24 md:py-32 lg:py-40">
          <div className="max-w-3xl mx-auto text-center space-y-8 animate-fade-up">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-card border border-border text-sm font-medium text-muted-foreground">
              <Sparkles className="h-4 w-4 text-accent" />
              <span>AI-Powered Shopping Experience</span>
            </div>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-serif font-bold text-foreground leading-tight">
              Natural Language Commerce
              <span className="block text-muted-foreground">for the Modern Buyer</span>
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
              Shop the way you think. Simply tell us what you need, and our AI-powered platform
              finds exactly what you're looking for from your favorite local stores.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Button asChild variant="hero">
                <Link to="/login">
                  Get Started
                  <ArrowRight className="h-5 w-5 ml-1" />
                </Link>
              </Button>
              <Button asChild variant="hero-outline">
                <Link to="/admin/login">Admin Portal</Link>
              </Button>
            </div>

            <div className="flex items-center justify-center gap-8 pt-8 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Store className="h-5 w-5" />
                <span>500+ Stores</span>
              </div>
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                <span>10K+ Users</span>
              </div>
              <div className="flex items-center gap-2">
                <ShoppingBag className="h-5 w-5" />
                <span>50K+ Products</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* What VyaparAI Does */}
      <section className="py-20 bg-card">
        <div className="container">
          <div className="text-center mb-16 animate-fade-up" style={{ animationDelay: "100ms" }}>
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground mb-4">
              What VyaparAI Does
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              A complete commerce platform that understands natural language and connects
              customers with local inventory in real-time.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="hover:shadow-card-hover animate-fade-up" style={{ animationDelay: "150ms" }}>
              <CardContent className="p-8 space-y-4">
                <div className="h-12 w-12 rounded-xl bg-accent/10 flex items-center justify-center">
                  <MessageSquare className="h-6 w-6 text-accent" />
                </div>
                <h3 className="font-serif text-xl font-semibold text-foreground">
                  Natural Language Shopping
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  Just type "I need snacks for a kids' party" or "Show me affordable rice options" —
                  our AI understands and finds exactly what you need.
                </p>
              </CardContent>
            </Card>

            <Card className="hover:shadow-card-hover animate-fade-up" style={{ animationDelay: "200ms" }}>
              <CardContent className="p-8 space-y-4">
                <div className="h-12 w-12 rounded-xl bg-accent/10 flex items-center justify-center">
                  <Search className="h-6 w-6 text-accent" />
                </div>
                <h3 className="font-serif text-xl font-semibold text-foreground">
                  Real-Time Inventory
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  Know instantly if a product is available at your local store. No more wasted trips
                  or disappointment at empty shelves.
                </p>
              </CardContent>
            </Card>

            <Card className="hover:shadow-card-hover animate-fade-up" style={{ animationDelay: "250ms" }}>
              <CardContent className="p-8 space-y-4">
                <div className="h-12 w-12 rounded-xl bg-accent/10 flex items-center justify-center">
                  <Zap className="h-6 w-6 text-accent" />
                </div>
                <h3 className="font-serif text-xl font-semibold text-foreground">
                  Smart Recommendations
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  Get personalized suggestions based on your shopping history, preferences, and
                  seasonal trends from nearby stores.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Who We Built This For */}
      <section className="py-20 bg-background">
        <div className="container">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8 animate-fade-up">
              <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground">
                Who We Built This For
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                VyaparAI bridges the gap between local businesses and modern consumers,
                creating a seamless shopping experience for everyone.
              </p>

              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                    <Store className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">Kirana Shop Owners</h3>
                    <p className="text-muted-foreground text-sm">
                      Digitize your inventory and reach more customers without the complexity of
                      building your own e-commerce platform.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                    <Users className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">Local Shoppers</h3>
                    <p className="text-muted-foreground text-sm">
                      Find products at nearby stores instantly. Skip the crowds and know exactly
                      what's in stock before you visit.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                    <TrendingUp className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground mb-1">Small Retailers</h3>
                    <p className="text-muted-foreground text-sm">
                      Get insights into customer demand, automate bookings, and compete with
                      larger platforms on a level playing field.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative animate-fade-up" style={{ animationDelay: "200ms" }}>
              <div className="bg-gradient-to-br from-secondary to-background rounded-2xl p-8 border border-border">
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-4 bg-card rounded-xl border border-border">
                    <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center">
                      <span className="text-primary-foreground font-semibold text-sm">A</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">Amit's Kirana Store</p>
                      <p className="text-xs text-muted-foreground">23 products • Open now</p>
                    </div>
                    <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">Online</span>
                  </div>

                  <div className="flex items-center gap-3 p-4 bg-card rounded-xl border border-border">
                    <div className="h-10 w-10 rounded-full bg-accent flex items-center justify-center">
                      <span className="text-accent-foreground font-semibold text-sm">R</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">Ravi General Store</p>
                      <p className="text-xs text-muted-foreground">156 products • Open now</p>
                    </div>
                    <span className="px-2 py-1 bg-success/10 text-success text-xs rounded-full">Online</span>
                  </div>

                  <div className="flex items-center gap-3 p-4 bg-card rounded-xl border border-border">
                    <div className="h-10 w-10 rounded-full bg-secondary flex items-center justify-center">
                      <span className="text-secondary-foreground font-semibold text-sm">S</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">Sharma Supermart</p>
                      <p className="text-xs text-muted-foreground">412 products • Opens 9 AM</p>
                    </div>
                    <span className="px-2 py-1 bg-muted text-muted-foreground text-xs rounded-full">Offline</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Natural Language */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-serif font-bold mb-4">
              Why Natural Language Shopping is the Future
            </h2>
            <p className="text-lg opacity-80 max-w-2xl mx-auto">
              Traditional search boxes and endless category browsing are outdated.
              The future is conversational commerce.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-primary-foreground/10 rounded-xl p-6 backdrop-blur-sm">
              <div className="text-4xl font-serif font-bold mb-2">73%</div>
              <p className="text-sm opacity-80">
                of users prefer conversational interfaces over traditional navigation
              </p>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6 backdrop-blur-sm">
              <div className="text-4xl font-serif font-bold mb-2">2.5x</div>
              <p className="text-sm opacity-80">
                faster product discovery with natural language queries
              </p>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6 backdrop-blur-sm">
              <div className="text-4xl font-serif font-bold mb-2">45%</div>
              <p className="text-sm opacity-80">
                higher conversion rates with AI-assisted shopping
              </p>
            </div>
            <div className="bg-primary-foreground/10 rounded-xl p-6 backdrop-blur-sm">
              <div className="text-4xl font-serif font-bold mb-2">92%</div>
              <p className="text-sm opacity-80">
                customer satisfaction rate with our AI recommendations
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* AI-Powered Engine */}
      <section className="py-20 bg-background">
        <div className="container">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="order-2 lg:order-1 animate-fade-up">
              <div className="bg-card rounded-2xl border border-border p-6 space-y-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                  <BarChart3 className="h-4 w-4" />
                  <span>Admin Analytics Dashboard</span>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-secondary rounded-xl">
                    <p className="text-2xl font-serif font-bold text-foreground">₹2.4L</p>
                    <p className="text-xs text-muted-foreground">Today's Revenue</p>
                  </div>
                  <div className="p-4 bg-secondary rounded-xl">
                    <p className="text-2xl font-serif font-bold text-foreground">847</p>
                    <p className="text-xs text-muted-foreground">Orders Processed</p>
                  </div>
                  <div className="p-4 bg-secondary rounded-xl">
                    <p className="text-2xl font-serif font-bold text-foreground">23</p>
                    <p className="text-xs text-muted-foreground">Low Stock Items</p>
                  </div>
                  <div className="p-4 bg-secondary rounded-xl">
                    <p className="text-2xl font-serif font-bold text-foreground">4.8★</p>
                    <p className="text-xs text-muted-foreground">Avg Rating</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-border">
                  <p className="text-sm text-muted-foreground mb-2">Recent AI Query</p>
                  <div className="bg-secondary rounded-lg p-3">
                    <p className="text-sm text-foreground italic">
                      "Which products sold the most in dairy category this week?"
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="order-1 lg:order-2 space-y-8 animate-fade-up" style={{ animationDelay: "150ms" }}>
              <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground">
                AI-Powered Inventory & Booking Engine
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                Our intelligent backend manages stock levels, processes natural language queries
                from both customers and admins, and provides actionable insights.
              </p>

              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-success flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="h-3.5 w-3.5 text-success-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-muted-foreground">
                    Real-time stock synchronization across all connected stores
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-success flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="h-3.5 w-3.5 text-success-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-muted-foreground">
                    NLP-powered queries for both admin analytics and customer search
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-success flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="h-3.5 w-3.5 text-success-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-muted-foreground">
                    Automated low-stock alerts and demand forecasting
                  </span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-success flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="h-3.5 w-3.5 text-success-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-muted-foreground">
                    Booking management with smart scheduling
                  </span>
                </li>
              </ul>

              <Button asChild variant="accent" size="lg">
                <Link to="/admin/login">
                  Access Admin Dashboard
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-secondary">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center space-y-8">
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-foreground">
              Ready to Transform Your Shopping Experience?
            </h2>
            <p className="text-lg text-muted-foreground">
              Join thousands of users and local businesses already using VyaparAI
              to make commerce simpler, smarter, and more personal.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button asChild variant="hero">
                <Link to="/login">
                  Start Shopping Now
                  <ArrowRight className="h-5 w-5 ml-1" />
                </Link>
              </Button>
              <Button asChild variant="hero-outline">
                <Link to="/admin/login">Register Your Store</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </MainLayout>
  );
};

export default Index;
