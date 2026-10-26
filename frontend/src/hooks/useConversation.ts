import { useState, useCallback, useRef } from 'react';
import type { CartItem, ConversationMessage, Language, MenuItem } from '../types';
import { sendMessage, transcribeAudio, synthesizeSpeech } from '../api/client';

export interface UseConversationReturn {
  messages: ConversationMessage[];
  cart: CartItem[];
  isProcessing: boolean;
  error: string | null;
  sendVoiceMessage: (audioBlob: Blob) => Promise<void>;
  sendTextMessage: (text: string) => Promise<void>;
  addToCart: (item: MenuItem, quantity?: number) => void;
  removeFromCart: (menuItemId: string) => void;
  updateQuantity: (menuItemId: string, quantity: number) => void;
  clearCart: () => void;
  setCart: React.Dispatch<React.SetStateAction<CartItem[]>>;
  addWelcomeMessage: (restaurantName: string, lang: Language) => void;
  clearError: () => void;
}

const WELCOME_MESSAGES: Record<Language, (name: string) => string> = {
  'en-IN': (name) => `Welcome to ${name}! I can help you order. Speak or type your order.`,
  'hi-IN': (name) => `${name} में आपका स्वागत है! मैं आपका ऑर्डर लेने में मदद कर सकता हूं।`,
  'ta-IN': (name) => `${name} க்கு வரவேற்கிறோம்! நான் உங்கள் ஆர்டரில் உதவ முடியும்.`,
  'te-IN': (name) => `${name} కి స్వాగతం! నేను మీ ఆర్డర్లో సహాయం చేయగలను.`,
};

export function useConversation(
  restaurantId: string,
  tableId: string,
  language: Language
): UseConversationReturn {
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cartRef = useRef<CartItem[]>(cart);
  cartRef.current = cart;

  const messagesRef = useRef<ConversationMessage[]>(messages);
  messagesRef.current = messages;

  const clearError = useCallback(() => setError(null), []);

  const addWelcomeMessage = useCallback((restaurantName: string, lang: Language) => {
    const textGen = WELCOME_MESSAGES[lang] || WELCOME_MESSAGES['en-IN'];
    const welcomeText = textGen(restaurantName);
    setMessages([
      {
        role: 'assistant',
        content: welcomeText,
        timestamp: new Date(),
      },
    ]);
  }, []);

  const processUserText = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      const userMessage: ConversationMessage = {
        role: 'user',
        content: text.trim(),
        timestamp: new Date(),
      };

      const updatedHistory = [...messagesRef.current, userMessage];
      setMessages(updatedHistory);
      setIsProcessing(true);
      setError(null);

      try {
        const response = await sendMessage(
          text,
          language,
          restaurantId,
          tableId,
          updatedHistory,
          cartRef.current
        );

        // Update cart if cart_updates provided
        if (response.cart_updates && Array.isArray(response.cart_updates)) {
          setCart(response.cart_updates);
        }

        // Synthesize speech for assistant response in background
        let audioUrl: string | undefined = undefined;
        try {
          const synthesized = await synthesizeSpeech(response.response_text, language);
          if (synthesized) {
            audioUrl = synthesized;
          }
        } catch {
          // Non-blocking: TTS failure shouldn't stop text flow
        }

        const assistantMessage: ConversationMessage = {
          role: 'assistant',
          content: response.response_text,
          timestamp: new Date(),
          audioUrl,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err: unknown) {
        const message = (err as Error).message || 'Failed to process message';
        setError(message);

        // Add a visible notification in the conversation if needed
        const errorMessage: ConversationMessage = {
          role: 'assistant',
          content: `Sorry, I encountered an issue: ${message}. Please try again or tap an item on the menu.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsProcessing(false);
      }
    },
    [language, restaurantId, tableId]
  );

  const sendVoiceMessage = useCallback(
    async (audioBlob: Blob) => {
      setIsProcessing(true);
      setError(null);
      try {
        const { transcript } = await transcribeAudio(audioBlob);
        if (!transcript || !transcript.trim()) {
          throw new Error('Could not understand speech. Please speak clearly and try again.');
        }
        await processUserText(transcript);
      } catch (err: unknown) {
        setError((err as Error).message || 'Voice transcription failed.');
        setIsProcessing(false);
      }
    },
    [processUserText]
  );

  const sendTextMessage = useCallback(
    async (text: string) => {
      await processUserText(text);
    },
    [processUserText]
  );

  const addToCart = useCallback((item: MenuItem, quantity: number = 1) => {
    setCart((prev) => {
      const existingIndex = prev.findIndex((c) => c.menu_item_id === item.id);
      if (existingIndex >= 0) {
        const updated = [...prev];
        const existing = updated[existingIndex];
        const newQty = existing.quantity + quantity;
        updated[existingIndex] = {
          ...existing,
          quantity: newQty,
          subtotal: Math.round(newQty * existing.unit_price * 100) / 100,
        };
        return updated;
      } else {
        const newCartItem: CartItem = {
          menu_item_id: item.id,
          item_name: item.canonical_name,
          quantity,
          customizations: {},
          unit_price: item.price,
          subtotal: Math.round(quantity * item.price * 100) / 100,
        };
        return [...prev, newCartItem];
      }
    });
  }, []);

  const removeFromCart = useCallback((menuItemId: string) => {
    setCart((prev) => prev.filter((item) => item.menu_item_id !== menuItemId));
  }, []);

  const updateQuantity = useCallback((menuItemId: string, quantity: number) => {
    if (quantity <= 0) {
      setCart((prev) => prev.filter((item) => item.menu_item_id !== menuItemId));
      return;
    }
    setCart((prev) =>
      prev.map((item) => {
        if (item.menu_item_id === menuItemId) {
          return {
            ...item,
            quantity,
            subtotal: Math.round(quantity * item.unit_price * 100) / 100,
          };
        }
        return item;
      })
    );
  }, []);

  const clearCart = useCallback(() => {
    setCart([]);
  }, []);

  return {
    messages,
    cart,
    isProcessing,
    error,
    sendVoiceMessage,
    sendTextMessage,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    setCart,
    addWelcomeMessage,
    clearError,
  };
}
