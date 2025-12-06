import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { productsAPI, Product } from "@/lib/api";
import { useCart } from "@/context/CartContext";
import { Button } from "@/components/ui/button";
import { ShoppingCart, ArrowLeft, Truck, ShieldCheck, Zap } from "lucide-react";
import { toast } from "@/hooks/use-toast";

const ProductDetails = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const { addToCart } = useCart();

    const [product, setProduct] = useState<Product | null>(null);
    const [loading, setLoading] = useState(true);
    const [mainImage, setMainImage] = useState("");

    useEffect(() => {
        const fetchProduct = async () => {
            if (!id) return;
            setLoading(true);
            const { data, error } = await productsAPI.getById(id);
            if (data) {
                setProduct(data);
                setMainImage(data.image_url || data.image || "");
            } else {
                toast({ title: "Error", description: error || "Product not found", variant: "destructive" });
                navigate("/dashboard");
            }
            setLoading(false);
        };
        fetchProduct();
    }, [id, navigate]);

    const handleBuyNow = () => {
        if (product) {
            addToCart(product, 1);
            navigate("/checkout");
        }
    };

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
    }

    if (!product) return null;

    return (
        <div className="min-h-screen bg-background p-4 md:p-8">
            <Button variant="ghost" onClick={() => navigate(-1)} className="mb-6 gap-2">
                <ArrowLeft className="h-4 w-4" /> Back
            </Button>

            <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12">
                {/* Product Image */}
                <div className="space-y-4">
                    <div className="aspect-square bg-white rounded-xl border overflow-hidden flex items-center justify-center p-8 relative group">
                        <img src={mainImage} alt={product.title} className="max-h-full max-w-full object-contain transition-transform group-hover:scale-105" />
                    </div>
                </div>

                {/* Product Info */}
                <div className="space-y-6">
                    <div>
                        <h1 className="text-3xl font-bold text-foreground mb-2">{product.title}</h1>
                        <p className="text-muted-foreground">{product.category}</p>
                    </div>

                    <div className="text-4xl font-bold text-primary">
                        ₹{product.price.toLocaleString()}
                    </div>

                    <div className="bg-secondary/30 p-4 rounded-lg space-y-3">
                        <div className="flex items-center gap-3 text-sm">
                            <Truck className="h-4 w-4 text-primary" />
                            <span>Free Delivery by <strong>Tomorrow, 4 PM</strong></span>
                        </div>
                        <div className="flex items-center gap-3 text-sm">
                            <ShieldCheck className="h-4 w-4 text-success" />
                            <span>1 Year Warranty</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm">
                            <Zap className="h-4 w-4 text-yellow-500" />
                            <span>Best Seller in {product.category}</span>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <Button
                            size="lg"
                            className="flex-1 gap-2 bg-[#ffd814] text-black hover:bg-[#f7ca00]"
                            onClick={() => addToCart(product, 1)}
                        >
                            <ShoppingCart className="h-5 w-5" /> Add to Cart
                        </Button>
                        <Button
                            size="lg"
                            className="flex-1 gap-2 bg-[#ffa41c] text-black hover:bg-[#fa8900]"
                            onClick={handleBuyNow}
                        >
                            Buy Now
                        </Button>
                    </div>

                    <div className="border-t pt-6">
                        <h3 className="font-semibold mb-2">Description</h3>
                        <p className="text-muted-foreground leading-relaxed">
                            {product.description || "No description available for this product."}
                        </p>
                    </div>

                    {/* Specs / Details Placeholder */}
                    <div className="border-t pt-6">
                        <h3 className="font-semibold mb-4">Product Specifications</h3>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="text-muted-foreground">Stock Status</span>
                                <p className="font-medium">{product.stock > 0 ? "In Stock" : "Out of Stock"}</p>
                            </div>
                            <div>
                                <span className="text-muted-foreground">Manufacturer</span>
                                <p className="font-medium">VyaparAI Generic</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductDetails;
