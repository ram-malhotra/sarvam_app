import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { Order, Restaurant } from '../types';
import { fetchKitchenOrders, updateOrderStatus, fetchRestaurant } from '../api/client';
import OrderCard from '../components/OrderCard';
import Loading from '../components/Loading';
import ErrorDisplay from '../components/ErrorDisplay';

type KitchenFilterTab = 'all' | 'pending' | 'accepted' | 'preparing' | 'ready';

export const KitchenDashboard: React.FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();

  const [pin, setPin] = useState<string>(() => {
    return sessionStorage.getItem(`kitchen_pin_${restaurantId}`) || '';
  });
  const [pinInput, setPinInput] = useState<string>('');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return !!sessionStorage.getItem(`kitchen_pin_${restaurantId}`);
  });
  const [authError, setAuthError] = useState<string | null>(null);

  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<KitchenFilterTab>('all');
  const [updatingOrderId, setUpdatingOrderId] = useState<string | null>(null);

  const pollIntervalRef = useRef<number | null>(null);

  // Load restaurant metadata
  useEffect(() => {
    if (!restaurantId) return;
    fetchRestaurant(restaurantId)
      .then((data) => setRestaurant(data))
      .catch((err) => console.warn('Could not load restaurant info:', err));
  }, [restaurantId]);

  // Load kitchen orders
  const loadOrders = useCallback(async (currentPin: string, isSilent = false) => {
    if (!restaurantId || !currentPin) return;
    if (!isSilent) setLoading(true);
    setRefreshError(null);

    try {
      const data = await fetchKitchenOrders(restaurantId, currentPin);
      setOrders(data);
      setIsAuthenticated(true);
      sessionStorage.setItem(`kitchen_pin_${restaurantId}`, currentPin);
    } catch (err: unknown) {
      const errorMsg = (err as Error).message || 'Failed to fetch orders';
      if (/pin|unauthorized|forbidden|401|403/i.test(errorMsg)) {
        setIsAuthenticated(false);
        sessionStorage.removeItem(`kitchen_pin_${restaurantId}`);
        setAuthError('Invalid Kitchen PIN. Please enter the correct 4-digit PIN.');
      } else {
        setRefreshError(errorMsg);
      }
    } finally {
      if (!isSilent) setLoading(false);
    }
  }, [restaurantId]);

  // Handle PIN form submission
  const handlePinSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (pinInput.trim().length < 4) {
      setAuthError('Please enter a 4-digit numeric PIN.');
      return;
    }
    setPin(pinInput);
    setAuthError(null);
    loadOrders(pinInput, false);
  };

  // Auto-refresh orders every 10 seconds when authenticated
  useEffect(() => {
    if (isAuthenticated && pin) {
      loadOrders(pin, false);

      pollIntervalRef.current = window.setInterval(() => {
        loadOrders(pin, true);
      }, 10000);

      return () => {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
        }
      };
    }
  }, [isAuthenticated, pin, loadOrders]);

  // Update order status
  const handleUpdateStatus = async (orderId: string, newStatus: Order['status']) => {
    if (!restaurantId || !pin) return;
    setUpdatingOrderId(orderId);
    try {
      const updated = await updateOrderStatus(restaurantId, orderId, newStatus, pin);
      setOrders((prev) =>
        prev.map((o) => (o.id === orderId ? updated : o))
      );
    } catch (err: unknown) {
      alert(`Could not update order status: ${(err as Error).message || 'Error'}`);
    } finally {
      setUpdatingOrderId(null);
    }
  };

  const filteredOrders = orders.filter((order) => {
    if (activeTab === 'all') return true;
    return order.status.toLowerCase() === activeTab.toLowerCase();
  });

  const activeOrdersCount = orders.filter(
    (o) => o.status !== 'completed' && o.status !== 'cancelled'
  ).length;

  if (!restaurantId) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
        <ErrorDisplay title="Missing Restaurant ID" message="Access via /kitchen/:restaurantId" />
      </div>
    );
  }

  // PIN Entry Screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center p-4">
        <div className="bg-gray-900 border border-gray-800 rounded-3xl p-8 max-w-sm w-full shadow-2xl text-center">
          <div className="w-16 h-16 bg-orange-600/20 text-orange-400 border border-orange-500/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>

          <h1 className="text-xl font-black text-gray-100 mb-1">
            Kitchen Display System
          </h1>
          <p className="text-xs text-gray-400 mb-6">
            Enter 4-digit kitchen security PIN to unlock orders
          </p>

          {authError && (
            <div className="mb-4 p-3 bg-red-950/50 border border-red-800 text-red-300 text-xs rounded-xl">
              {authError}
            </div>
          )}

          <form onSubmit={handlePinSubmit} className="space-y-4">
            <input
              type="password"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={6}
              value={pinInput}
              onChange={(e) => setPinInput(e.target.value)}
              placeholder="••••"
              aria-label="Kitchen PIN"
              className="w-full text-center text-3xl font-mono tracking-widest px-4 py-3 bg-gray-950 border border-gray-700 rounded-xl text-white focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/50"
              autoFocus
            />

            <button
              type="submit"
              className="w-full min-h-[46px] py-3 bg-orange-600 hover:bg-orange-500 active:bg-orange-700 text-white font-bold rounded-xl transition-all shadow-md shadow-orange-600/30 text-sm"
            >
              Unlock Dashboard
            </button>
          </form>

          <p className="mt-4 text-[11px] text-gray-500">
            Default Demo PIN: <code className="text-orange-400 font-mono">1234</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col font-sans">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 sticky top-0 z-20 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-orange-600 flex items-center justify-center font-bold text-white shadow-xs">
              👨‍🍳
            </div>
            <div>
              <h1 className="text-lg font-black text-gray-100 leading-tight">
                {restaurant?.name || 'Kitchen Live Display'}
              </h1>
              <p className="text-xs text-gray-400">
                Restaurant ID: <span className="font-mono text-orange-400">{restaurantId}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-gray-800 border border-gray-700 px-3 py-1.5 rounded-xl text-xs font-semibold text-gray-300">
              Active: <span className="text-orange-400 font-black">{activeOrdersCount}</span>
            </div>

            <Link
              to={`/kitchen/${restaurantId}/qr`}
              className="min-h-[40px] px-3.5 py-1.5 bg-gray-800 hover:bg-gray-700 active:bg-gray-600 border border-gray-700 text-xs font-bold text-gray-200 rounded-xl inline-flex items-center gap-1.5 transition-colors"
            >
              <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
              </svg>
              <span>QR Codes</span>
            </Link>

            <button
              type="button"
              onClick={() => {
                sessionStorage.removeItem(`kitchen_pin_${restaurantId}`);
                setIsAuthenticated(false);
                setPin('');
              }}
              title="Lock screen"
              className="min-h-[40px] px-3 py-1.5 bg-red-950/40 hover:bg-red-900/60 border border-red-800/50 text-red-400 text-xs font-semibold rounded-xl transition-colors"
            >
              Lock
            </button>
          </div>
        </div>
      </header>

      {/* Filter Tabs */}
      <div className="bg-gray-900/80 border-b border-gray-800/80 px-6 py-2.5">
        <div className="max-w-7xl mx-auto flex items-center gap-2 overflow-x-auto no-scrollbar">
          {(['all', 'pending', 'accepted', 'preparing', 'ready'] as KitchenFilterTab[]).map((tab) => {
            const isSelected = activeTab === tab;
            const count =
              tab === 'all'
                ? orders.length
                : orders.filter((o) => o.status === tab).length;

            return (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`min-h-[40px] px-4 py-1.5 rounded-xl text-xs font-bold capitalize transition-all flex items-center gap-2 ${
                  isSelected
                    ? 'bg-orange-600 text-white shadow-xs'
                    : 'bg-gray-800 text-gray-400 hover:text-gray-100 hover:bg-gray-700'
                }`}
              >
                <span>{tab}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                    isSelected ? 'bg-orange-800 text-white' : 'bg-gray-900 text-gray-300'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Order Grid */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {refreshError && (
          <div className="mb-6">
            <ErrorDisplay
              title="Connection Warning"
              message={refreshError}
              onRetry={() => loadOrders(pin, false)}
            />
          </div>
        )}

        {loading && orders.length === 0 ? (
          <div className="py-20 flex justify-center">
            <Loading message="Syncing with kitchen queue..." size="lg" />
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-3xl p-12 text-center text-gray-500 max-w-md mx-auto my-12">
            <div className="w-16 h-16 rounded-full bg-gray-800 text-gray-400 flex items-center justify-center mx-auto mb-4 text-2xl">
              🍳
            </div>
            <h3 className="text-lg font-bold text-gray-200">No Orders in this view</h3>
            <p className="text-xs text-gray-400 mt-1">
              New customer orders placed from table QR codes will appear here in real-time.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredOrders.map((order) => (
              <OrderCard
                key={order.id}
                order={order}
                onUpdateStatus={handleUpdateStatus}
                isUpdating={updatingOrderId === order.id}
              />
            ))}
          </div>
        )}
      </main>

      {/* Footer Status Bar */}
      <footer className="bg-gray-900 border-t border-gray-800 px-6 py-2.5 text-xs text-gray-500 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span>Live sync active (refreshes every 10s)</span>
        </div>
        <span>VoiceMenu AI Kitchen Display</span>
      </footer>
    </div>
  );
};

export default KitchenDashboard;
