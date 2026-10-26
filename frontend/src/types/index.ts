export interface MenuItem {
  id: string;
  restaurant_id: string;
  category: string;
  canonical_name: string;
  localized_names: Record<string, string>;
  description: string;
  localized_descriptions: Record<string, string>;
  price: number;
  is_veg: boolean;
  ingredients: string[];
  spice_level: 'mild' | 'medium' | 'spicy' | 'very_spicy';
  available: boolean;
  customizations: Array<{ name: string; options: string[] }>;
}

export interface CartItem {
  menu_item_id: string;
  item_name: string;
  quantity: number;
  customizations: Record<string, string>;
  unit_price: number;
  subtotal: number;
}

export interface Order {
  id: string;
  restaurant_id: string;
  table_id: string;
  status: 'pending' | 'accepted' | 'preparing' | 'ready' | 'completed' | 'cancelled';
  items: CartItem[];
  total_amount: number;
  created_at: string;
  language: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  audioUrl?: string;
}

export interface ConversationResponse {
  response_text: string;
  cart_updates: CartItem[];
  action: string;
}

export interface Restaurant {
  id: string;
  name: string;
  description: string;
}

export type Language = 'hi-IN' | 'en-IN' | 'ta-IN' | 'te-IN';

export const LANGUAGE_LABELS: Record<Language, string> = {
  'hi-IN': 'हिंदी',
  'en-IN': 'English',
  'ta-IN': 'தமிழ்',
  'te-IN': 'తెలుగు',
};

export const SPICE_LABELS: Record<string, { label: string; emoji: string }> = {
  'mild': { label: 'Mild', emoji: '🌶️' },
  'medium': { label: 'Medium', emoji: '🌶️🌶️' },
  'spicy': { label: 'Spicy', emoji: '🌶️🌶️🌶️' },
  'very_spicy': { label: 'Very Spicy', emoji: '🌶️🌶️🌶️🌶️' },
};
