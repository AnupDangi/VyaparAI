import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Loader2, Camera, Upload, Check, X, AlertCircle } from "lucide-react";
import { useCart } from "@/context/CartContext";
import { toast } from "@/hooks/use-toast";
import { Product } from "@/lib/api";

interface ShoppingListUploadProps {
    allProducts: Product[];
}

interface OCRItem {
    product: string;
    quantity: number;
}

interface OCRResponse {
    items: OCRItem[];
    total_items: number;
}

interface MatchedItem {
    original: string;
    matchedProduct: Product | null;
    quantity: number;
}

export function ShoppingListUpload({ allProducts }: ShoppingListUploadProps) {
    const [open, setOpen] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [matches, setMatches] = useState<MatchedItem[]>([]);
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { addToCart } = useCart();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const f = e.target.files[0];
            setFile(f);
            setPreview(URL.createObjectURL(f));
            setMatches([]);
        }
    };

    const processImage = async () => {
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
            const response = await fetch(`${API_URL}/ocr/extract`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) throw new Error("OCR Failed");

            const data: OCRResponse = await response.json();

            // Perform Frontend Matching
            const matched: MatchedItem[] = data.items.map((item) => {
                const searchTerm = item.product.toLowerCase();

                // Simple fuzzy match logic
                const found = allProducts.find((p) => {
                    const title = p.title.toLowerCase();
                    const category = p.category.toLowerCase();
                    // Check if product title contains the OCR term OR OCR term contains product title (partial match)
                    // or category match
                    return title.includes(searchTerm) || searchTerm.includes(title) || category.includes(searchTerm);
                });

                return {
                    original: item.product,
                    matchedProduct: found || null,
                    quantity: item.quantity,
                };
            });

            setMatches(matched);

            if (matched.length === 0) {
                toast({ title: "No items found", description: "We couldn't identify any products from the image." });
            } else {
                toast({ title: "List Processed", description: `Found ${matched.length} items.` });
            }

        } catch (error) {
            console.error("OCR Error:", error);
            toast({ title: "Upload Failed", description: "Could not process image. Please try again.", variant: "destructive" });
        } finally {
            setUploading(false);
        }
    };

    const handleAddAll = () => {
        let addedCount = 0;
        matches.forEach((m) => {
            if (m.matchedProduct) {
                addToCart(m.matchedProduct, m.quantity);
                addedCount++;
            }
        });
        setOpen(false);
        setFile(null);
        setPreview(null);
        setMatches([]);
        toast({ title: "Items Added", description: `Added ${addedCount} items to your cart.` });
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button className="gap-2 bg-white text-black hover:bg-gray-100 border-none transition-colors">
                    <Camera className="h-4 w-4" />
                    <span className="hidden sm:inline">Upload List</span>
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>Upload Shopping List</DialogTitle>
                </DialogHeader>

                <div className="space-y-4">
                    <div
                        className="flex flex-col items-center justify-center border-2 border-dashed border-muted-foreground/25 rounded-xl p-8 bg-muted/10 hover:bg-muted/30 hover:border-primary/50 transition-all duration-300 cursor-pointer group"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        {preview ? (
                            <div className="relative w-full">
                                <img src={preview} alt="Upload" className="w-full max-h-60 rounded-lg object-contain shadow-sm" />
                                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center rounded-lg">
                                    <p className="text-white font-medium">Click to change</p>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center gap-3 text-center py-4">
                                <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                                    <Camera className="h-8 w-8 text-primary" />
                                </div>
                                <div>
                                    <p className="text-base font-semibold text-foreground">Tap to Scan List</p>
                                    <p className="text-sm text-muted-foreground mt-1">Supports PNG, JPG, JPEG</p>
                                </div>
                            </div>
                        )}
                        <input
                            type="file"
                            ref={fileInputRef}
                            className="hidden"
                            accept=".png, .jpeg, .jpg"
                            onChange={handleFileChange}
                        />
                    </div>

                    {!matches.length && (
                        <Button onClick={processImage} disabled={!file || uploading} className="w-full">
                            {uploading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...
                                </>
                            ) : (
                                "Scan List"
                            )}
                        </Button>
                    )}

                    {matches.length > 0 && (
                        <div className="space-y-3">
                            <h3 className="font-semibold text-sm">Identified Items</h3>
                            <div className="space-y-2 max-h-60 overflow-y-auto border rounded-md p-2">
                                {matches.map((m, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-2 bg-card rounded border text-sm">
                                        <div className="flex-1">
                                            <p className="font-medium text-foreground">{m.original}</p>
                                            {m.matchedProduct ? (
                                                <p className="text-xs text-green-600 flex items-center gap-1">
                                                    <Check className="h-3 w-3" /> Found: {m.matchedProduct.title}
                                                </p>
                                            ) : (
                                                <p className="text-xs text-red-500 flex items-center gap-1">
                                                    <AlertCircle className="h-3 w-3" /> Not found in store
                                                </p>
                                            )}
                                        </div>
                                        <div className="font-bold flex items-center gap-1">
                                            x{m.quantity}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="flex gap-2">
                                <Button variant="outline" className="flex-1" onClick={() => { setMatches([]); setFile(null); setPreview(null); }}>
                                    Reset
                                </Button>
                                <Button className="flex-1 bg-[#f08804] hover:bg-[#d07300] text-black" onClick={handleAddAll}>
                                    Add All to Cart
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
