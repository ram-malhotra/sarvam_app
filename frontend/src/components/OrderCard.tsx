import React from 'react';
import type { Order } from '../types';

interface OrderCardProps {
  order: Order;
  onUpdateStatus: (orderId: string, newStatus: Order['status']) => void;
  isUpdating?: boolean;
}

const STATUS_CONFIG: Record<
  Order['status'],
  { label: string; badgeClasses: string; borderClasses: string }
> = {
  pending: {
    label: 'Pending',
    badgeClasses: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40',
    borderClasses: 'border-yellow-500/60',
  },
  accepted: {
    label: 'Accepted',
    badgeClasses: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
    borderClasses: 'border-blue-500/60',
  },
  preparing: {
    label: 'Preparing',
    badgeClasses: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
    borderClasses: 'border-orange-500/60',
  },
  ready: {
    label: 'Ready for Pickup',
    badgeClasses: 'bg-green-500/20 text-green-300 border-green-500/40',
    borderClasses: 'border-green-500/60',
  },
  completed: {
    label: 'Completed',
    badgeClasses: 'bg-gray-500/20 text-gray-300 border-gray-500/40',
    borderClasses: 'border-gray-700',
  },
  cancelled: {
    label: 'Cancelled',
    badgeClasses: 'bg-red-500/20 text-red-300 border-red-500/40',
    borderClasses: 'border-red-800',
  },
};

function formatRelativeTime(dateString: string): string {
  try {
    const diffMs = Date.now() - new Date(dateString).getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins === 1) return '1 min ago';
    if (diffMins < 60) return `${diffMins} mins ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return '1 hour ago';
    return `${diffHours} hours ago`;
  } catch {
    return 'Recently';
  }
}

export const OrderCard: React.FC<OrderCardProps> = ({
  order,
  onUpdateStatus,
  isUpdating = false,
}) => {
  const config = STATUS_CONFIG[order.status] || STATUS_CONFIG.pending;
  const relativeTime = formatRelativeTime(order.created_at);

  return (
    <div
      className={`flex flex-col justify-between bg-gray-900 text-gray-100 rounded-2xl border ${config.borderClasses} p-5 shadow-lg shadow-black/40 transition-all`}
    >
      <div>
        {/* Top bar: Table number, Status badge, Timestamp */}
        <div className="flex items-start justify-between gap-3 pb-3 border-b border-gray-800">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-black text-orange-400">
                Table {order.table_id}
              </span>
              <span className="text-xs font-mono text-gray-400">
                #{order.id.slice(-5).toUpperCase()}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">{relativeTime}</p>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wider ${config.badgeClasses}`}
          >
            {config.label}
          </span>
        </div>

        {/* Ordered items list */}
        <div className="py-4 space-y-2.5">
          {order.items.map((item, idx) => (
            <div
              key={`${item.menu_item_id}-${idx}`}
              className="flex items-start justify-between gap-2 text-sm"
            >
              <div className="flex-1">
                <div className="flex items-baseline gap-2">
                  <span className="font-bold text-orange-400 text-base">
                    {item.quantity}x
                  </span>
                  <span className="font-semibold text-gray-100">
                    {item.item_name}
                  </span>
                </div>
                {item.customizations && Object.keys(item.customizations).length > 0 && (
                  <p className="text-xs text-amber-300/80 ml-6 mt-0.5">
                    {Object.entries(item.customizations)
                      .map(([k, v]) => `${k}: ${v}`)
                      .join(', ')}
                  </p>
                )}
              </div>
              <span className="text-xs text-gray-400">
                ₹{item.subtotal.toFixed(0)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer: Total & Actions */}
      <div className="pt-3 border-t border-gray-800 space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Total:</span>
          <span className="text-lg font-black text-gray-100">
            ₹{order.total_amount.toFixed(0)}
          </span>
        </div>

        {/* Action Buttons based on status */}
        <div className="flex items-center gap-2 pt-1">
          {order.status === 'pending' && (
            <>
              <button
                type="button"
                disabled={isUpdating}
                onClick={() => onUpdateStatus(order.id, 'accepted')}
                className="flex-1 min-h-[44px] px-3 py-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 font-bold text-xs uppercase tracking-wider rounded-xl transition-colors disabled:opacity-50"
              >
                Accept Order
              </button>
              <button
                type="button"
                disabled={isUpdating}
                onClick={() => onUpdateStatus(order.id, 'cancelled')}
                className="min-h-[44px] px-3 py-2 bg-red-950/40 hover:bg-red-900/60 text-red-400 border border-red-800/60 font-semibold text-xs rounded-xl transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
            </>
          )}

          {order.status === 'accepted' && (
            <>
              <button
                type="button"
                disabled={isUpdating}
                onClick={() => onUpdateStatus(order.id, 'preparing')}
                className="flex-1 min-h-[44px] px-3 py-2 bg-orange-600 hover:bg-orange-500 active:bg-orange-700 font-bold text-xs uppercase tracking-wider rounded-xl transition-colors disabled:opacity-50"
              >
                Start Preparing
              </button>
              <button
                type="button"
                disabled={isUpdating}
                onClick={() => onUpdateStatus(order.id, 'cancelled')}
                className="min-h-[44px] px-3 py-2 bg-red-950/40 hover:bg-red-900/60 text-red-400 border border-red-800/60 font-semibold text-xs rounded-xl transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
            </>
          )}

          {order.status === 'preparing' && (
            <button
              type="button"
              disabled={isUpdating}
              onClick={() => onUpdateStatus(order.id, 'ready')}
              className="w-full min-h-[44px] px-3 py-2 bg-green-600 hover:bg-green-500 active:bg-green-700 font-bold text-xs uppercase tracking-wider rounded-xl transition-colors disabled:opacity-50"
            >
              Mark Ready for Pickup
            </button>
          )}

          {order.status === 'ready' && (
            <button
              type="button"
              disabled={isUpdating}
              onClick={() => onUpdateStatus(order.id, 'completed')}
              className="w-full min-h-[44px] px-3 py-2 bg-gray-700 hover:bg-gray-600 active:bg-gray-800 font-bold text-xs uppercase tracking-wider rounded-xl transition-colors disabled:opacity-50"
            >
              Mark Completed
            </button>
          )}

          {(order.status === 'completed' || order.status === 'cancelled') && (
            <span className="w-full text-center text-xs text-gray-500 italic py-2">
              Archived ({order.status})
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderCard;
