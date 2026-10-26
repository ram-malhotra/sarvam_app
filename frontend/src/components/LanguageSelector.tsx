import React from 'react';
import type { Language } from '../types';
import { LANGUAGE_LABELS } from '../types';

interface LanguageSelectorProps {
  currentLanguage: Language;
  onLanguageChange: (lang: Language) => void;
  disabled?: boolean;
}

const LANGUAGES: Language[] = ['hi-IN', 'en-IN', 'ta-IN', 'te-IN'];

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  currentLanguage,
  onLanguageChange,
  disabled = false,
}) => {
  return (
    <div
      role="group"
      aria-label="Select Language"
      className="inline-flex items-center bg-orange-950/10 backdrop-blur-xs p-1 rounded-xl border border-orange-200/50"
    >
      {LANGUAGES.map((lang) => {
        const isSelected = currentLanguage === lang;
        return (
          <button
            key={lang}
            type="button"
            disabled={disabled}
            onClick={() => onLanguageChange(lang)}
            aria-pressed={isSelected}
            className={`min-h-[38px] px-3 py-1.5 text-xs sm:text-sm font-semibold rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-orange-500 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed ${
              isSelected
                ? 'bg-orange-600 text-white shadow-xs'
                : 'text-gray-700 hover:text-orange-900 hover:bg-orange-100/60'
            }`}
          >
            {LANGUAGE_LABELS[lang]}
          </button>
        );
      })}
    </div>
  );
};

export default LanguageSelector;
