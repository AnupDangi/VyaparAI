// API utilities for VyaparAI
// These functions are placeholders that will be connected to FastAPI backend

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Generic fetch wrapper with error handling
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<{ data: T | null; error: string | null }> {
  try {
    const isFormData = options?.body instanceof FormData;
    const headers = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...options?.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers,
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return { data: null, error: errorData.message || errorData.detail || `HTTP error ${response.status}` };
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    return { data: null, error: error instanceof Error ? error.message : 'Unknown error' };
  }
}

// Types
export interface Product {
  id: string;
  title: string;
  price: number;
  stock: number;
  image: string;
  category: string;
  description?: string;
  image_url?: string; // Add optional backend field compatibility
}

export interface Category {
  id: string;
  name: string;
  icon?: string;
  count?: number;
}

export interface CartItem {
  productId: string;
  quantity: number;
  product?: Product;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
}

export interface NLPQueryResponse {
  message: string;
  products?: Product[];
  analytics?: Record<string, unknown>;
  chart?: {
    type: 'bar' | 'line' | 'pie';
    data: Record<string, unknown>;
  };
}

// Authentication APIs
export const authAPI = {
  // User login with email/password
  login: async (email: string, password: string) => {
    return fetchAPI<{ user: User; token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  // User registration
  register: async (name: string, email: string, password: string) => {
    return fetchAPI<{ user: User; token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  // Admin login with credentials
  adminLogin: async (adminId: string, password: string) => {
    return fetchAPI<{ user: User; token: string }>('/auth/admin/login', {
      method: 'POST',
      body: JSON.stringify({ adminId, password }),
    });
  },

  // Logout
  logout: async () => {
    return fetchAPI('/auth/logout', { method: 'POST' });
  },

  // Get current user
  getCurrentUser: async () => {
    return fetchAPI<User>('/auth/me');
  },
};

// Products APIs
export const productsAPI = {
  // Get all products
  getAll: async () => {
    return fetchAPI<Product[]>('/products/');
  },

  // Get single product
  getById: async (id: string | number) => {
    return fetchAPI<Product>(`/products/${id}`);
  },

  // Create Product (Admin)
  create: async (productData: FormData) => {
    return fetchAPI<{ success: boolean; product: Product }>('/products/', {
      method: 'POST',
      body: productData
    });
  },

  // Update Product (Admin)
  update: async (id: number, productData: FormData) => {
    return fetchAPI<{ success: boolean; product: Product }>(`/products/${id}`, {
      method: 'PUT',
      body: productData
    });
  },

  // Delete Product (Admin)
  delete: async (id: number) => {
    return fetchAPI<{ success: boolean; message: string }>(`/products/${id}`, {
      method: 'DELETE'
    });
  },

  // Search products with natural language
  nlpSearch: async (query: string) => {
    return fetchAPI<NLPQueryResponse>('/products/nlp-search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  },
};

// Categories APIs
export const categoriesAPI = {
  // Get all categories
  getAll: async () => {
    return fetchAPI<Category[]>('/categories');
  },
};

// Cart APIs
export const cartAPI = {
  // Get cart
  getCart: async () => {
    return fetchAPI<{ items: CartItem[]; total: number }>('/cart');
  },

  // Add to cart
  addItem: async (productId: string, quantity: number) => {
    return fetchAPI<CartItem>('/cart/add', {
      method: 'POST',
      body: JSON.stringify({ productId, quantity }),
    });
  },

  // Update cart item
  updateItem: async (productId: string, quantity: number) => {
    return fetchAPI<CartItem>('/cart/update', {
      method: 'PUT',
      body: JSON.stringify({ productId, quantity }),
    });
  },

  // Remove from cart
  removeItem: async (productId: string) => {
    return fetchAPI('/cart/remove', {
      method: 'DELETE',
      body: JSON.stringify({ productId }),
    });
  },

  // Clear cart
  clearCart: async () => {
    return fetchAPI('/cart/clear', { method: 'DELETE' });
  },
};

// Admin APIs
export const adminAPI = {
  // Get dashboard stats
  getStats: async () => {
    return fetchAPI<{
      totalUsers: number;
      totalRevenue: number;
      ordersToday: number;
      lowStockItems: number;
    }>('/admin/stats');
  },

  // NLP query for analytics
  nlpQuery: async (query: string) => {
    return fetchAPI<NLPQueryResponse>('/admin/nlp-query', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  },

  // Get category performance
  getCategoryPerformance: async () => {
    return fetchAPI<{
      name: string;
      revenue: number;
      orders: number;
      growth: number;
    }[]>('/admin/categories/performance');
  },

  // Get recent activity
  getRecentActivity: async () => {
    return fetchAPI<{
      action: string;
      time: string;
      type: 'order' | 'user' | 'alert' | 'success';
    }[]>('/admin/activity');
  },

  // Get low stock items
  getLowStockItems: async () => {
    return fetchAPI<Product[]>('/admin/inventory/low-stock');
  },

  // Update product stock
  updateStock: async (productId: string, stock: number) => {
    return fetchAPI<Product>(`/admin/products/${productId}/stock`, {
      method: 'PUT',
      body: JSON.stringify({ stock }),
    });
  },

  // Setup store details
  setupStore: async (storeDetails: {
    name: string;
    description: string;
    category: string;
    address: string;
    phone: string;
  }) => {
    return fetchAPI<{ success: boolean; message: string }>('/admin/store/setup', {
      method: 'POST',
      body: JSON.stringify(storeDetails),
    });
  },
};

// Orders APIs
export const ordersAPI = {
  create: async (orderData: { items: any[], total_amount: number, clerk_id: string, shipping_address: string }) => {
    return fetchAPI<{ success: boolean; orderId: number; message: string }>('/orders/', {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  },
  getUserOrders: async (clerkId: string) => {
    return fetchAPI<{ id: number; total: number; status: string; date: string; items: any[] }[]>(`/orders/${clerkId}`);
  }
};

export default {
  auth: authAPI,
  products: productsAPI,
  categories: categoriesAPI,
  cart: cartAPI,
  admin: adminAPI,
  orders: ordersAPI,
};
