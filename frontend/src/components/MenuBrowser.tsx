import React, { useState, useEffect } from 'react';
import type { Language, MenuItem } from '../types';
import { SPICE_LABELS } from '../types';
import { fetchMenu } from '../api/client';
import Loading from './Loading';
import ErrorDisplay from './ErrorDisplay';

interface MenuBrowserProps {
  restaurantId: string;
  language: Language;
  onAddToCart: (item: MenuItem) => void;
}

const DEFAULT_CATEGORIES = ['All', 'Dosa', 'Idli', 'Rice', 'Snacks', 'Beverages'];

export const MenuBrowser: React.FC<MenuBrowserProps> = ({
  restaurantId,
  language,
  onAddToCart,
}) => {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadMenu = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchMenu(restaurantId, language);
      setItems(data);
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to load menu items.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMenu();
  }, [restaurantId, language]);

  // Collect unique categories from items, keeping standard order
  const categories = Array.from(
    new Set([
      ...DEFAULT_CATEGORIES,
      ...items.map((i) => i.category).filter(Boolean),
    ])
  );

  const filteredItems = items.filter((item) => {
    if (selectedCategory === 'All') return true;
    return item.category.toLowerCase() === selectedCategory.toLowerCase();
  });

  if (loading) {
    return <Loading message="Loading delicious menu..." />;
  }

  if (error) {
    return <ErrorDisplay message={error} onRetry={loadMenu} title="Could not load menu" />;
  }

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Category Tabs */}
      <div className="overflow-x-auto no-scrollbar py-1">
        <div className="flex gap-2 min-w-max px-4">
          {categories.map((category) => {
            const isSelected = selectedCategory.toLowerCase() === category.toLowerCase();
            return (
              <button
                key={category}
                type="button"
                onClick={() => setSelectedCategory(category)}
                className={`min-h-[44px] px-4 py-2 text-sm font-semibold rounded-full transition-all focus:outline-none focus:ring-2 focus:ring-orange-500 ${
                  isSelected
                    ? 'bg-orange-600 text-white shadow-xs'
                    : 'bg-white text-gray-700 border border-gray-200 hover:bg-orange-50 hover:text-orange-900'
                }`}
              >
                {category}
              </button>
            );
          })}
        </div>
      </div>

      {/* Menu Grid */}
      <div className="flex-1 overflow-y-auto px-4 pb-6">
        {filteredItems.length === 0 ? (
          <div className="text-center py-12 text-gray-500 bg-white rounded-2xl border border-gray-100 p-6">
            <svg
              className="w-12 h-12 mx-auto text-gray-400 mb-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <p className="text-sm font-medium">No items found in this category.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredItems.map((item) => {
              const localizedName = item.localized_names?.[language] || item.canonical_name;
              const hasDiffName = localizedName && localizedName !== item.canonical_name;
              const localizedDesc = item.localized_descriptions?.[language] || item.description;
              const spice = SPICE_LABELS[item.spice_level] || { label: item.spice_level, emoji: '🌶️' };

              return (
                <div
                  key={item.id}
                  className={`flex flex-col justify-between bg-white rounded-2xl p-4 border transition-all duration-200 shadow-xs hover:shadow-md ${
                    item.available
                      ? 'border-gray-200/80 hover:border-orange-300'
                      : 'border-gray-200 bg-gray-50/70 opacity-75'
                  }`}
                >
                  <div>
                    {/* Header: Veg/Non-veg & Spice & Availability */}
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        {/* FSSAI Veg / Non-veg indicator */}
                        <div
                          title={item.is_veg ? 'Vegetarian' : 'Non-Vegetarian'}
                          className={`w-4 h-4 border flex items-center justify-center p-0.5 rounded-xs ${
                            item.is_veg ? 'border-green-600' : 'border-red-600'
                          }`}
                        >
                          <div
                            className={`w-2 h-2 rounded-full ${
                              item.is_veg ? 'bg-green-600' : 'bg-red-600'
                            }`}
                          />
                        </div>

                        {/* Spice Level */}
                        <span
                          className="text-xs text-gray-500 inline-flex items-center"
                          title={`Spice level: ${spice.label}`}
                        >
                          {spice.emoji}
                        </span>
                      </div>

                      {!item.available && (
                        <span className="text-[11px] font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full">
                          Unavailable
                        </span>
                      )}
                    </div>

                    {/* Item Title */}
                    <h3 className="text-base font-bold text-gray-900 leading-tight">
                      {localizedName}
                    </h3>
                    {hasDiffName && (
                      <p className="text-xs text-gray-500 font-medium mt-0.5">
                        ({item.canonical_name})
                      </p>
                    )}

                    {/* Description */}
                    {localizedDesc && (
                      <p className="text-xs text-gray-600 mt-2 line-clamp-2 leading-relaxed">
                        {localizedDesc}
                      </p>
                    )}
                  </div>

                  {/* Price & Add Button */}
                  <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
                    <span className="text-base font-extrabold text-gray-900">
                      ₹{item.price.toFixed(0)}
                    </span>

                    <button
                      type="button"
                      disabled={!item.available}
                      onClick={() => onAddToCart(item)}
                      aria-label={`Add ${localizedName} to cart for ₹${item.price}`}
                      className="min-h-[44px] min-w-[76px] px-4 py-2 bg-orange-600 hover:bg-orange-700 active:bg-orange-800 disabled:bg-gray-200 disabled:text-gray-400 text-white text-xs sm:text-sm font-bold rounded-xl shadow-xs transition-all active:scale-95 disabled:scale-100 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-orange-500"
                    >
                      + Add
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default MenuBrowser;
