import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import type { Language, Order, Restaurant } from '../types';
import { fetchRestaurant, createOrder } from '../api/client';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { useConversation } from '../hooks/useConversation';
import LanguageSelector from '../components/LanguageSelector';
import ConversationArea from '../components/ConversationArea';
import MicrophoneButton from '../components/MicrophoneButton';
import TextInput from '../components/TextInput';
import MenuBrowser from '../components/MenuBrowser';
import CartSummary from '../components/CartSummary';
import OrderConfirmation from '../components/OrderConfirmation';
import Loading from '../components/Loading';
import ErrorDisplay from '../components/ErrorDisplay';

type TabType = 'chat' | 'menu' | 'cart';

export const CustomerPage: React.FC = () => {
  const { restaurantId, tableId } = useParams<{ restaurantId: string; tableId: string }>();

  const [language, setLanguage] = useState<Language>('en-IN');
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [loadingRestaurant, setLoadingRestaurant] = useState<boolean>(true);
  const [restaurantError, setRestaurantError] = useState<string | null>(null);

  const [confirmedOrder, setConfirmedOrder] = useState<Order | null>(null);
  const [isSubmittingOrder, setIsSubmittingOrder] = useState<boolean>(false);
  const [orderError, setOrderError] = useState<string | null>(null);

  // Audio Recorder Hook
  const {
    isRecording,
    startRecording,
    stopRecording,
    isSupported: isMicSupported,
    error: micError,
  } = useAudioRecorder();

  // Conversation Hook
  const {
    messages,
    cart,
    isProcessing,
    error: conversationError,
    sendVoiceMessage,
    sendTextMessage,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    addWelcomeMessage,
    clearError: clearConvError,
  } = useConversation(restaurantId || '', tableId || '', language);

  // Load restaurant details
  const loadRestaurant = useCallback(async () => {
    if (!restaurantId) {
      setRestaurantError('Missing restaurant identifier in the URL.');
      setLoadingRestaurant(false);
      return;
    }

    setLoadingRestaurant(true);
    setRestaurantError(null);
    try {
      const data = await fetchRestaurant(restaurantId);
      setRestaurant(data);
      addWelcomeMessage(data.name, language);
    } catch (err: unknown) {
      setRestaurantError((err as Error).message || 'Failed to load restaurant.');
    } finally {
      setLoadingRestaurant(false);
    }
  }, [restaurantId, language, addWelcomeMessage]);

  useEffect(() => {
    loadRestaurant();
  }, [loadRestaurant]);

  // Handle language switch
  const handleLanguageChange = (newLang: Language) => {
    setLanguage(newLang);
    if (restaurant) {
      addWelcomeMessage(restaurant.name, newLang);
    }
  };

  // Voice recording toggle
  const handleStartRecording = async () => {
    clearConvError();
    await startRecording();
  };

  const handleStopRecording = async () => {
    const blob = await stopRecording();
    if (blob && blob.size > 0) {
      await sendVoiceMessage(blob);
    }
  };

  // Submit cart order
  const handleConfirmOrder = async () => {
    if (!restaurantId || !tableId || cart.length === 0) return;
    setIsSubmittingOrder(true);
    setOrderError(null);
    try {
      const order = await createOrder(restaurantId, tableId, cart, language);
      setConfirmedOrder(order);
      clearCart();
    } catch (err: unknown) {
      setOrderError((err as Error).message || 'Failed to submit order. Please try again.');
    } finally {
      setIsSubmittingOrder(false);
    }
  };

  const cartItemsCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  if (!restaurantId || !tableId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
        <ErrorDisplay
          title="Invalid Table Link"
          message="Please scan a valid table QR code or access via /r/:restaurantId/:tableId"
        />
      </div>
    );
  }

  if (loadingRestaurant) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loading message="Connecting to table..." size="lg" />
      </div>
    );
  }

  if (restaurantError || !restaurant) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
        <ErrorDisplay
          title="Restaurant Not Available"
          message={restaurantError || 'Restaurant could not be loaded.'}
          onRetry={loadRestaurant}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-gray-50 text-gray-900 overflow-hidden shadow-2xl border-x border-gray-200">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 shrink-0 shadow-xs">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-orange-600 text-white flex items-center justify-center shrink-0 font-black text-lg shadow-xs">
              🍽️
            </div>
            <div className="truncate">
              <h1 className="text-base font-extrabold text-gray-900 leading-tight truncate">
                {restaurant.name}
              </h1>
              <p className="text-xs font-semibold text-orange-600">
                Table {tableId}
              </p>
            </div>
          </div>

          {/* Language Selector */}
          <div className="shrink-0">
            <LanguageSelector
              currentLanguage={language}
              onLanguageChange={handleLanguageChange}
              disabled={isRecording || isProcessing}
            />
          </div>
        </div>
      </header>

      {/* Tabs Navigation */}
      <nav
        role="tablist"
        aria-label="Dining options"
        className="flex border-b border-gray-200 bg-white shrink-0"
      >
        <button
          role="tab"
          aria-selected={activeTab === 'chat'}
          onClick={() => setActiveTab('chat')}
          className={`flex-1 py-3 text-sm font-bold text-center border-b-2 transition-all min-h-[44px] flex items-center justify-center gap-1.5 ${
            activeTab === 'chat'
              ? 'border-orange-600 text-orange-600 bg-orange-50/50'
              : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-50'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <span>Voice Chat</span>
        </button>

        <button
          role="tab"
          aria-selected={activeTab === 'menu'}
          onClick={() => setActiveTab('menu')}
          className={`flex-1 py-3 text-sm font-bold text-center border-b-2 transition-all min-h-[44px] flex items-center justify-center gap-1.5 ${
            activeTab === 'menu'
              ? 'border-orange-600 text-orange-600 bg-orange-50/50'
              : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-50'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
            />
          </svg>
          <span>Menu</span>
        </button>

        <button
          role="tab"
          aria-selected={activeTab === 'cart'}
          onClick={() => setActiveTab('cart')}
          className={`flex-1 py-3 text-sm font-bold text-center border-b-2 transition-all min-h-[44px] flex items-center justify-center gap-1.5 relative ${
            activeTab === 'cart'
              ? 'border-orange-600 text-orange-600 bg-orange-50/50'
              : 'border-transparent text-gray-500 hover:text-gray-900 hover:bg-gray-50'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
          <span>Cart</span>
          {cartItemsCount > 0 && (
            <span className="bg-orange-600 text-white text-[10px] font-extrabold px-1.5 py-0.5 rounded-full">
              {cartItemsCount}
            </span>
          )}
        </button>
      </nav>

      {/* Main Tab Content */}
      <main className="flex-1 overflow-y-auto flex flex-col relative bg-gradient-to-b from-orange-50/30 to-gray-50">
        {/* Banner Error Notifications */}
        {(micError || conversationError || orderError) && (
          <div className="p-3">
            <ErrorDisplay
              message={(micError || conversationError || orderError) as string}
              onRetry={clearConvError}
            />
          </div>
        )}

        {/* Tab 1: Voice & Chat */}
        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col justify-between overflow-hidden">
            <ConversationArea
              messages={messages}
              isProcessing={isProcessing}
              language={language}
            />

            {/* Voice & Text Interaction Bar */}
            <div className="p-4 bg-white/95 backdrop-blur-xs border-t border-gray-200/80 shadow-lg space-y-3 shrink-0">
              <MicrophoneButton
                isRecording={isRecording}
                isProcessing={isProcessing}
                isSupported={isMicSupported}
                onStartRecording={handleStartRecording}
                onStopRecording={handleStopRecording}
              />

              <TextInput
                language={language}
                onSend={sendTextMessage}
                disabled={isRecording || isProcessing}
              />
            </div>
          </div>
        )}

        {/* Tab 2: Menu Browser */}
        {activeTab === 'menu' && (
          <div className="flex-1 p-2 sm:p-4 overflow-y-auto">
            <MenuBrowser
              restaurantId={restaurantId}
              language={language}
              onAddToCart={(item) => {
                addToCart(item);
              }}
            />
          </div>
        )}

        {/* Tab 3: Cart Summary */}
        {activeTab === 'cart' && (
          <div className="flex-1 p-4 overflow-y-auto">
            <CartSummary
              cart={cart}
              onUpdateQuantity={updateQuantity}
              onRemoveItem={removeFromCart}
              onClearCart={clearCart}
              onConfirmOrder={handleConfirmOrder}
              isSubmitting={isSubmittingOrder}
            />
          </div>
        )}
      </main>

      {/* Confirmation Modal */}
      {confirmedOrder && (
        <OrderConfirmation
          order={confirmedOrder}
          onDismiss={() => {
            setConfirmedOrder(null);
            setActiveTab('chat');
          }}
        />
      )}
    </div>
  );
};

export default CustomerPage;
