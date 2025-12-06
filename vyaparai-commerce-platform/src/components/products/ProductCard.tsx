import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Minus, ShoppingCart } from "lucide-react";
import { useState } from "react";

interface ProductCardProps {
  id: string;
  title: string;
  price: number;
  stock: number;
  image: string;
  category?: string;
  onAddToCart?: (id: string, quantity: number) => void;
}

const ProductCard = ({
  id,
  title,
  price,
  stock,
  image,
  category,
  onAddToCart,
}: ProductCardProps) => {
  const [quantity, setQuantity] = useState(1);

  const handleIncrement = () => {
    if (quantity < stock) {
      setQuantity(quantity + 1);
    }
  };

  const handleDecrement = () => {
    if (quantity > 1) {
      setQuantity(quantity - 1);
    }
  };

  const handleAddToCart = () => {
    onAddToCart?.(id, quantity);
    setQuantity(1);
  };

  const isOutOfStock = stock === 0;

  return (
    <Card className="overflow-hidden hover:shadow-card-hover group">
      <div className="aspect-square relative overflow-hidden bg-secondary">
        <img
          src={image}
          alt={title}
          className="object-cover w-full h-full transition-transform duration-300 group-hover:scale-105"
        />
        {category && (
          <span className="absolute top-2 left-2 px-2 py-1 text-xs font-medium bg-card/90 text-foreground rounded-md">
            {category}
          </span>
        )}
        {isOutOfStock && (
          <div className="absolute inset-0 bg-background/80 flex items-center justify-center">
            <span className="text-sm font-medium text-destructive">Out of Stock</span>
          </div>
        )}
      </div>

      <div className="p-4 space-y-3">
        <div>
          <h3 className="font-medium text-foreground line-clamp-2 leading-snug">{title}</h3>
          <p className="text-lg font-semibold text-foreground mt-1">₹{price.toLocaleString()}</p>
        </div>

        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{stock > 0 ? `${stock} in stock` : "Out of stock"}</span>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center border border-border rounded-lg">
            <button
              onClick={handleDecrement}
              disabled={quantity <= 1 || isOutOfStock}
              className="p-2 hover:bg-secondary transition-colors disabled:opacity-50"
            >
              <Minus className="h-4 w-4" />
            </button>
            <span className="px-3 text-sm font-medium min-w-[2rem] text-center">
              {quantity}
            </span>
            <button
              onClick={handleIncrement}
              disabled={quantity >= stock || isOutOfStock}
              className="p-2 hover:bg-secondary transition-colors disabled:opacity-50"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>
          <Button
            onClick={handleAddToCart}
            disabled={isOutOfStock}
            variant="accent"
            className="flex-1"
            size="sm"
          >
            <ShoppingCart className="h-4 w-4" />
            Add
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default ProductCard;
