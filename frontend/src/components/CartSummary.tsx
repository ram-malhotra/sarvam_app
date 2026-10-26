import React from 'react';
import type { CartItem } from '../types';

interface CartSummaryProps {
  cart: CartItem[];
  onUpdateQuantity: (menuItemId: string, quantity: number) => void;
  onRemoveItem: (menuItemId: string) => void;
  onClearCart: () => void;
  onConfirmOrder: () => void;
  isSubmitting?: boolean;
}

export const CartSummary: React.FC<CartSummaryProps> = ({
  cart,
  onUpdateQuantity,
  onRemoveItem,
  onClearCart,
  onConfirmOrder,
  isSubmitting = false,
}) => {
  const totalAmount = cart.reduce((sum, item) => sum + item.subtotal, 0);
  const totalItemsCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  if (cart.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-white rounded-2xl border border-gray-100 shadow-xs max-w-lg mx-auto my-4">
        <div className="w-16 h-16 rounded-full bg-orange-50 flex items-center justify-center text-orange-500 mb-4">
          <svg
            className="w-8 h-8"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-bold text-gray-900">Your cart is empty</h3>
        <p className="text-sm text-gray-500 mt-1 max-w-xs">
          Start ordering! You can speak your order using the microphone or pick dishes from the menu.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-gray-200/80 shadow-xs overflow-hidden max-w-xl mx-auto w-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 bg-gray-50/50">
        <div>
          <h2 className="text-base font-bold text-gray-900">Your Order Cart</h2>
          <p className="text-xs text-gray-500">
            {totalItemsCount} {totalItemsCount === 1 ? 'item' : 'items'} in order
          </p>
        </div>

        <button
          type="button"
          onClick={onClearCart}
          disabled={isSubmitting}
          className="min-h-[44px] px-3 py-1.5 text-xs font-semibold text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
        >
          Clear Cart
        </button>
      </div>

      {/* Cart Items List */}
      <div className="flex-1 overflow-y-auto px-5 py-3 divide-y divide-gray-100">
        {cart.map((item) => (
          <div key={item.menu_item_id} className="py-3 flex items-center justify-between gap-3">
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-bold text-gray-900 truncate">
                {item.item_name}
              </h4>
              <p className="text-xs text-gray-500">
                ₹{item.unit_price} each
              </p>

              {item.customizations && Object.keys(item.customizations).length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {Object.entries(item.customizations).map(([k, v]) => (
                    <span
                      key={k}
                      className="text-[11px] bg-orange-50 text-orange-800 px-1.5 py-0.5 rounded-sm"
                    >
                      {k}: {v}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Quantity Controls & Subtotal */}
            <div className="flex items-center gap-3">
              <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden bg-gray-50">
                <button
                  type="button"
                  onClick={() => onUpdateQuantity(item.menu_item_id, item.quantity - 1)}
                  disabled={isSubmitting}
                  aria-label={`Decrease quantity of ${item.item_name}`}
                  className="min-h-[44px] min-w-[36px] flex items-center justify-center text-gray-600 hover:bg-gray-200 active:bg-gray-300 font-bold transition-colors disabled:opacity-50"
                >
                  -
                </button>
                <span className="w-8 text-center text-sm font-bold text-gray-900">
                  {item.quantity}
                </span>
                <button
                  type="button"
                  onClick={() => onUpdateQuantity(item.menu_item_id, item.quantity + 1)}
                  disabled={isSubmitting}
                  aria-label={`Increase quantity of ${item.item_name}`}
                  className="min-h-[44px] min-w-[36px] flex items-center justify-center text-gray-600 hover:bg-gray-200 active:bg-gray-300 font-bold transition-colors disabled:opacity-50"
                >
                  +
                </button>
              </div>

              <div className="w-16 text-right font-bold text-sm text-gray-900">
                ₹{item.subtotal.toFixed(0)}
              </div>

              <button
                type="button"
                onClick={() => onRemoveItem(item.menu_item_id)}
                disabled={isSubmitting}
                aria-label={`Remove ${item.item_name} from cart`}
                className="min-h-[44px] min-w-[36px] flex items-center justify-center text-gray-400 hover:text-red-600 transition-colors"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Total & Confirm Button */}
      <div className="p-5 border-t border-gray-100 bg-gray-50/70 space-y-3">
        <div className="flex items-center justify-between text-base">
          <span className="font-medium text-gray-600">Total Amount:</span>
          <span className="text-xl font-black text-gray-900">₹{totalAmount.toFixed(0)}</span>
        </div>

        <button
          type="button"
          onClick={onConfirmOrder}
          disabled={isSubmitting || cart.length === 0}
          className="w-full min-h-[48px] py-3 px-6 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 disabled:bg-gray-300 text-white font-bold rounded-xl shadow-md shadow-emerald-600/20 transition-all flex items-center justify-center gap-2 disabled:cursor-not-allowed focus:outline-none focus:ring-4 focus:ring-emerald-200"
        >
          {isSubmitting ? (
            <>
              <svg className="w-5 h-5 animate-spin text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>Submitting Order...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
              <span>Confirm & Place Order</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default CartSummary;
