import React from 'react';
import type { Order } from '../types';

interface OrderConfirmationProps {
  order: Order;
  onDismiss: () => void;
}

export const OrderConfirmation: React.FC<OrderConfirmationProps> = ({
  order,
  onDismiss,
}) => {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="order-success-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fade-in"
    >
      <div className="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 text-center shadow-2xl transform transition-all animate-scale-up">
        {/* Animated Success Checkmark Badge */}
        <div className="w-20 h-20 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-4 ring-8 ring-emerald-50">
          <svg
            className="w-10 h-10 animate-bounce"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={3}
              d="M5 13l4 4L19 7"
            />
          </svg>
        </div>

        <h2 id="order-success-title" className="text-2xl font-black text-gray-900">
          Order Placed!
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Your order has been sent directly to the kitchen.
        </p>

        {/* Order Details Card */}
        <div className="mt-6 p-4 rounded-2xl bg-gray-50 border border-gray-100 text-left space-y-3">
          <div className="flex items-center justify-between text-xs text-gray-500 pb-2 border-b border-gray-200">
            <span>Order Reference:</span>
            <span className="font-mono font-bold text-gray-800">
              #{order.id.slice(-6).toUpperCase()}
            </span>
          </div>

          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Table Number:</span>
            <span className="font-bold text-gray-800">{order.table_id}</span>
          </div>

          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Estimated Preparation:</span>
            <span className="font-bold text-orange-600">~15-20 mins</span>
          </div>

          {/* Items Summary */}
          <div className="pt-2 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-1.5">Ordered Items:</p>
            <div className="max-h-36 overflow-y-auto space-y-1 pr-1">
              {order.items.map((item, idx) => (
                <div
                  key={`${item.menu_item_id}-${idx}`}
                  className="flex items-center justify-between text-xs text-gray-600"
                >
                  <span className="truncate pr-2">
                    {item.quantity}x {item.item_name}
                  </span>
                  <span className="font-medium text-gray-900 shrink-0">
                    ₹{item.subtotal.toFixed(0)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Total */}
          <div className="pt-2 border-t border-gray-200 flex items-center justify-between font-bold text-sm text-gray-900">
            <span>Total Paid/Payable:</span>
            <span className="text-base text-emerald-700">₹{order.total_amount.toFixed(0)}</span>
          </div>
        </div>

        {/* Action Button */}
        <div className="mt-6">
          <button
            type="button"
            onClick={onDismiss}
            className="w-full min-h-[48px] py-3 px-6 bg-orange-600 hover:bg-orange-700 active:bg-orange-800 text-white font-bold rounded-xl shadow-md shadow-orange-600/20 transition-all focus:outline-none focus:ring-4 focus:ring-orange-200"
          >
            Done / Order More
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrderConfirmation;
