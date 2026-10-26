import type {
  MenuItem,
  CartItem,
  Order,
  ConversationMessage,
  ConversationResponse,
  Restaurant,
  Language,
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || '';

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data && typeof data === 'object') {
        errorDetail = data.detail || data.message || data.error || JSON.stringify(data);
      }
    } catch {
      try {
        const text = await res.text();
        if (text) errorDetail = text;
      } catch {
        // Fallback to status text
        errorDetail = res.statusText || errorDetail;
      }
    }
    throw new ApiError(errorDetail, res.status);
  }
  return res.json() as Promise<T>;
}

export async function fetchRestaurant(restaurantId: string): Promise<Restaurant> {
  try {
    const res = await fetch(`${BASE_URL}/api/restaurants/${encodeURIComponent(restaurantId)}`);
    return await handleResponse<Restaurant>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to load restaurant details: ${(err as Error).message || 'Network error'}`);
  }
}

export async function fetchMenu(
  restaurantId: string,
  language: Language,
  category?: string
): Promise<MenuItem[]> {
  try {
    const query = new URLSearchParams({ language });
    if (category && category !== 'All') {
      query.set('category', category);
    }
    const res = await fetch(
      `${BASE_URL}/api/restaurants/${encodeURIComponent(restaurantId)}/menu?${query.toString()}`
    );
    return await handleResponse<MenuItem[]>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to load menu: ${(err as Error).message || 'Network error'}`);
  }
}

export async function transcribeAudio(
  audioBlob: Blob
): Promise<{ transcript: string; language_code: string }> {
  try {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('file', audioBlob, 'recording.webm');

    const res = await fetch(`${BASE_URL}/api/voice/transcribe`, {
      method: 'POST',
      body: formData,
    });
    return await handleResponse<{ transcript: string; language_code: string }>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Speech transcription failed: ${(err as Error).message || 'Network error'}`);
  }
}

export async function sendMessage(
  text: string,
  language: Language,
  restaurantId: string,
  tableId: string,
  conversationHistory: ConversationMessage[],
  currentCart: CartItem[]
): Promise<ConversationResponse> {
  try {
    const res = await fetch(`${BASE_URL}/api/conversation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        language,
        restaurant_id: restaurantId,
        table_id: tableId,
        history: conversationHistory.map((m) => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp.toISOString(),
        })),
        cart: currentCart,
      }),
    });
    return await handleResponse<ConversationResponse>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to process message: ${(err as Error).message || 'Network error'}`);
  }
}

export async function synthesizeSpeech(text: string, languageCode: string): Promise<string> {
  try {
    const res = await fetch(`${BASE_URL}/api/voice/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        language_code: languageCode,
      }),
    });

    if (!res.ok) {
      return '';
    }

    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const data = await res.json();
      if (data.audio_base64) {
        return `data:audio/wav;base64,${data.audio_base64}`;
      }
      if (data.audio_url) {
        return data.audio_url;
      }
      return '';
    } else {
      // Audio stream or binary blob
      const blob = await res.blob();
      return URL.createObjectURL(blob);
    }
  } catch (err) {
    console.warn('Speech synthesis skipped or failed:', err);
    return '';
  }
}

export async function createOrder(
  restaurantId: string,
  tableId: string,
  items: CartItem[],
  language: Language
): Promise<Order> {
  try {
    const res = await fetch(`${BASE_URL}/api/orders`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        restaurant_id: restaurantId,
        table_id: tableId,
        items,
        language,
      }),
    });
    return await handleResponse<Order>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to create order: ${(err as Error).message || 'Network error'}`);
  }
}

export async function updateOrder(orderId: string, items: CartItem[]): Promise<Order> {
  try {
    const res = await fetch(`${BASE_URL}/api/orders/${encodeURIComponent(orderId)}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ items }),
    });
    return await handleResponse<Order>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to update order: ${(err as Error).message || 'Network error'}`);
  }
}

export async function confirmOrder(orderId: string): Promise<Order> {
  try {
    const res = await fetch(`${BASE_URL}/api/orders/${encodeURIComponent(orderId)}/confirm`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return await handleResponse<Order>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to confirm order: ${(err as Error).message || 'Network error'}`);
  }
}

export async function fetchKitchenOrders(
  restaurantId: string,
  pin: string = '',
  statuses?: string[]
): Promise<Order[]> {
  try {
    const query = new URLSearchParams({ pin });
    if (statuses && statuses.length > 0) {
      query.set('statuses', statuses.join(','));
    }
    const res = await fetch(
      `${BASE_URL}/api/kitchen/${encodeURIComponent(restaurantId)}/orders?${query.toString()}`,
      {
        headers: {
          'X-Kitchen-PIN': pin,
        },
      }
    );
    return await handleResponse<Order[]>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to fetch kitchen orders: ${(err as Error).message || 'Network error'}`);
  }
}

export async function updateOrderStatus(
  restaurantId: string,
  orderId: string,
  status: string,
  pin: string = ''
): Promise<Order> {
  try {
    const res = await fetch(
      `${BASE_URL}/api/kitchen/${encodeURIComponent(restaurantId)}/orders/${encodeURIComponent(orderId)}/status`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-Kitchen-PIN': pin,
        },
        body: JSON.stringify({ status, pin }),
      }
    );
    return await handleResponse<Order>(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new Error(`Failed to update order status: ${(err as Error).message || 'Network error'}`);
  }
}
