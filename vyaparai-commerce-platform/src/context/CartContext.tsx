import React, { createContext, useContext, useState, useEffect } from "react";
import { toast } from "@/hooks/use-toast";
import { useUser } from "@clerk/clerk-react";
import { cartAPI } from "@/lib/api";

export interface CartItem {
    // This might be Product ID or CartItem ID. Be careful. Backend returns CartItem ID as 'id' and product_id as 'product_id'. 
    // Frontend expects 'id' to be product ID for some lookups?
    // Let's standardise: In Frontend Item, id should be Product ID to match addToCart logic? 
    // Or we store both.
    // The current frontend uses 'id' as product id in 'existing' check.
    // Backend GetCart returns: { id: item_id, product_id: pid, ... }
    // We need to map Backend Response to Frontend State.
    id: string;
    title: string;
    price: number;
    image: string;
    quantity: number;
    category?: string;
    stock: number;
    cartItemId?: string; // Track backend ID for removal
}

interface CartContextType {
    items: CartItem[];
    addToCart: (product: any, quantity: number) => void;
    removeFromCart: (productId: string) => void;
    updateQuantity: (productId: string, quantity: number) => void;
    clearCart: () => void;
    cartCount: number;
    cartTotal: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider = ({ children }: { children: React.ReactNode }) => {
    const [items, setItems] = useState<CartItem[]>([]);
    const { user, isLoaded } = useUser();

    // Load Cart (API or LocalStorage)
    useEffect(() => {
        if (!isLoaded) return;

        if (user) {
            // Load from Backend
            const fetchCart = async () => {
                const { data, error } = await cartAPI.getCart(user.id);
                if (data && data.items) {
                    // Map Backend Items to Frontend Shape
                    const mappedItems = data.items.map((i: any) => ({
                        id: i.product_id.toString(), // Frontend uses product ID as key often? Or Item ID? 
                        // In removeFromCart, it filters by item.id. 
                        // In addToCart, it checks existing.id === product.id. 
                        // So 'id' MUST be Product ID.
                        cartItemId: i.id.toString(), // Store backend Item ID
                        title: i.title,
                        price: i.price,
                        image: i.image_url,
                        quantity: i.quantity,
                        stock: 100, // Backend doesn't return stock in cart items yet? defaulting
                    }));
                    setItems(mappedItems);
                }
            };
            fetchCart();
        } else {
            // Load from Local Storage (Guest)
            const saved = localStorage.getItem("cart");
            if (saved) {
                try {
                    setItems(JSON.parse(saved));
                } catch (e) {
                    console.error("Failed to parse cart", e);
                }
            }
        }
    }, [user, isLoaded]);

    // Save to local storage (Guest Only)
    useEffect(() => {
        if (!user && isLoaded) {
            localStorage.setItem("cart", JSON.stringify(items));
        }
    }, [items, user, isLoaded]);

    const addToCart = async (product: any, quantity: number) => {
        // Optimistic UI Update
        const existing = items.find((item) => item.id === product.id);

        if (existing) {
            setItems(prev => prev.map((item) =>
                item.id === product.id ? { ...item, quantity: item.quantity + quantity } : item
            ));
        } else {
            setItems(prev => [...prev, {
                id: product.id, // Product ID
                title: product.title,
                price: product.price,
                image: product.image || product.image_url,
                quantity,
                category: product.category,
                stock: product.stock || 100
            }]);
        }
        toast({ title: "Added to Cart", description: `${quantity}x ${product.title} added` });

        // 2. Sync with Backend (if Auth)
        if (user) {
            try {
                const { data } = await cartAPI.addItem(product.id, quantity, user.id);
                // Update local state with the returned backend ID (cartItemId)
                if (data?.item_id) {
                    setItems(prev => prev.map((item) =>
                        item.id === product.id ? { ...item, cartItemId: data.item_id.toString() } : item
                    ));
                }
            } catch (error) {
                console.error("Failed to sync cart", error);
                toast({ title: "Sync Error", description: "Could not save to account", variant: "destructive" });
            }
        }
    };

    const removeFromCart = async (productId: string) => {
        const itemToRemove = items.find(i => i.id === productId);

        setItems((prev) => prev.filter((item) => item.id !== productId));
        toast({ title: "Removed", description: "Item removed from cart" });

        if (user && itemToRemove) {
            if (itemToRemove.cartItemId) {
                await cartAPI.removeItem(itemToRemove.cartItemId, user.id);
            } else {
                // Fallback: If ID missing, refresh cart to ensure consistency
                try {
                    const { data } = await cartAPI.getCart(user.id);
                    if (data?.items) {
                        const mappedItems = data.items.map((i: any) => ({
                            id: i.product_id.toString(),
                            cartItemId: i.id.toString(),
                            title: i.title,
                            price: i.price,
                            image: i.image_url,
                            quantity: i.quantity,
                            stock: 100,
                        }));
                        setItems(mappedItems);
                    }
                } catch (e) { console.error("Refresh failed", e); }
            }
        }
    };

    const updateQuantity = async (productId: string, quantity: number) => {
        if (quantity < 1) {
            removeFromCart(productId);
            return;
        }
        setItems((prev) => prev.map((item) => item.id === productId ? { ...item, quantity } : item));

        if (user) {
            await cartAPI.updateItem(productId, quantity, user.id);
        }
    };

    const clearCart = async () => {
        setItems([]);
        toast({ title: "Cart Cleared" });
        if (user) {
            await cartAPI.clearCart(user.id);
        }
    };

    const cartCount = items.reduce((acc, item) => acc + item.quantity, 0);
    const cartTotal = items.reduce((acc, item) => acc + item.price * item.quantity, 0);

    return (
        <CartContext.Provider
            value={{ items, addToCart, removeFromCart, updateQuantity, clearCart, cartCount, cartTotal }}
        >
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => {
    const context = useContext(CartContext);
    if (!context) throw new Error("useCart must be used within a CartProvider");
    return context;
};
