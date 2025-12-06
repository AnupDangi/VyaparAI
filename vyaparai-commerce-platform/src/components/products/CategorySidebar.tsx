import { cn } from "@/lib/utils";

interface Category {
  id: string;
  name: string;
  icon?: string;
  count?: number;
}

interface CategorySidebarProps {
  categories: Category[];
  selectedCategory: string | null;
  onSelectCategory: (categoryId: string | null) => void;
}

const CategorySidebar = ({
  categories,
  selectedCategory,
  onSelectCategory,
}: CategorySidebarProps) => {
  return (
    <aside className="w-64 bg-card border-r border-border p-4 space-y-2">
      <h2 className="font-serif font-semibold text-foreground mb-4">Categories</h2>
      
      <button
        onClick={() => onSelectCategory(null)}
        className={cn(
          "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors",
          selectedCategory === null
            ? "bg-primary text-primary-foreground"
            : "text-muted-foreground hover:bg-secondary hover:text-foreground"
        )}
      >
        All Products
      </button>

      {categories.map((category) => (
        <button
          key={category.id}
          onClick={() => onSelectCategory(category.id)}
          className={cn(
            "w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between",
            selectedCategory === category.id
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-secondary hover:text-foreground"
          )}
        >
          <span className="flex items-center gap-2">
            {category.icon && <span>{category.icon}</span>}
            {category.name}
          </span>
          {category.count !== undefined && (
            <span className="text-xs opacity-70">{category.count}</span>
          )}
        </button>
      ))}
    </aside>
  );
};

export default CategorySidebar;
