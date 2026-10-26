import React, { useState } from 'react';
import type { Language } from '../types';

interface TextInputProps {
  language: Language;
  onSend: (text: string) => void;
  disabled?: boolean;
}

const PLACEHOLDERS: Record<Language, string> = {
  'en-IN': 'Type your order e.g., "1 Masala Dosa and filter coffee"...',
  'hi-IN': 'अपना ऑर्डर लिखें जैसे "1 मसाला डोसा और फिल्टर कॉफी"...',
  'ta-IN': 'உங்கள் ஆர்டரை உள்ளிடவும் எ.கா. "1 மசாலா தோசை"...',
  'te-IN': 'మీ ఆర్డర్‌ను టైప్ చేయండి ఉదా. "1 మసాలా దోస"...',
};

export const TextInput: React.FC<TextInputProps> = ({
  language,
  onSend,
  disabled = false,
}) => {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText('');
  };

  const placeholder = PLACEHOLDERS[language] || PLACEHOLDERS['en-IN'];

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2 w-full max-w-xl mx-auto px-1">
      <div className="relative flex-1">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="Text order input"
          className="w-full min-h-[46px] px-4 py-2.5 text-sm bg-white border border-gray-300 rounded-full shadow-xs focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 disabled:bg-gray-100 disabled:cursor-not-allowed placeholder:text-gray-400 text-gray-900"
        />
      </div>
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        aria-label="Send message"
        className="min-h-[46px] min-w-[46px] flex items-center justify-center bg-orange-600 hover:bg-orange-700 active:bg-orange-800 disabled:bg-gray-300 text-white rounded-full transition-colors shadow-xs disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-orange-500"
      >
        <svg
          className="w-5 h-5 transform rotate-90"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
        </svg>
      </button>
    </form>
  );
};

export default TextInput;
