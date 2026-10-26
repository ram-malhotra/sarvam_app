import React from 'react';
import { Link } from 'react-router-dom';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 via-white to-orange-50/40 text-gray-900 flex flex-col justify-between">
      {/* Navigation */}
      <header className="max-w-5xl mx-auto w-full px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-2xl bg-orange-600 text-white flex items-center justify-center font-black text-xl shadow-md shadow-orange-500/20">
            🎙️
          </div>
          <div>
            <span className="text-xl font-black tracking-tight text-gray-900">
              VoiceMenu <span className="text-orange-600">AI</span>
            </span>
            <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest">
              Multilingual Dining
            </span>
          </div>
        </div>

        <Link
          to="/kitchen/demo-restaurant"
          className="text-xs font-bold text-gray-700 hover:text-orange-600 bg-white border border-gray-200 px-4 py-2 rounded-xl shadow-xs transition-colors"
        >
          Kitchen Login →
        </Link>
      </header>

      {/* Hero Section */}
      <main className="max-w-4xl mx-auto px-6 py-10 text-center flex-1 flex flex-col justify-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-100 text-orange-800 text-xs font-bold mx-auto mb-6">
          <span>🇮🇳</span> Powered by Sarvam AI Indic Voice Tech
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-black text-gray-950 tracking-tight leading-tight">
          Speak your order. <br className="hidden sm:inline" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-amber-600">
            In any Indian language.
          </span>
        </h1>

        <p className="mt-5 text-base sm:text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
          Voice-first QR dining system for Indian restaurants. Guests speak naturally in
          <strong className="text-gray-900"> Hindi, Tamil, Telugu, or English</strong>, and AI updates the cart & sends orders straight to the kitchen.
        </p>

        {/* Demo Action Buttons */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/r/demo-restaurant/table-1"
            className="min-h-[50px] px-8 py-3.5 bg-orange-600 hover:bg-orange-500 active:bg-orange-700 text-white font-extrabold rounded-2xl shadow-lg shadow-orange-500/30 transition-all transform hover:-translate-y-0.5 active:translate-y-0 text-base inline-flex items-center gap-2"
          >
            <span>Try Table 1 Demo</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </Link>

          <Link
            to="/r/demo-restaurant/table-2"
            className="min-h-[50px] px-6 py-3.5 bg-white hover:bg-gray-50 border-2 border-gray-200 text-gray-800 font-bold rounded-2xl shadow-xs transition-colors text-base inline-flex items-center gap-2"
          >
            <span>Table 2 Demo</span>
          </Link>

          <Link
            to="/kitchen/demo-restaurant/qr"
            className="min-h-[50px] px-6 py-3.5 bg-amber-50 hover:bg-amber-100 text-amber-900 font-bold rounded-2xl border border-amber-200 transition-colors text-base inline-flex items-center gap-2"
          >
            <span>Generate QR Standees</span>
          </Link>
        </div>

        {/* Feature Cards Grid */}
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 text-left">
          <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center text-xl mb-4">
              🗣️
            </div>
            <h3 className="font-bold text-gray-900 text-base mb-1">
              Multilingual Voice
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Real-time voice recognition and speech synthesis across Hindi, Tamil, Telugu, and English.
            </p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl mb-4">
              🛒
            </div>
            <h3 className="font-bold text-gray-900 text-base mb-1">
              Conversational Cart
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Understands multi-item additions, spicy/mild customizations, and instant quantity adjustments.
            </p>
          </div>

          <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center text-xl mb-4">
              👨‍🍳
            </div>
            <h3 className="font-bold text-gray-900 text-base mb-1">
              Live Kitchen Screen
            </h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Auto-updating KDS with PIN security, table numbers, preparation timers, and one-tap status updates.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-5xl mx-auto w-full px-6 py-8 border-t border-gray-200/60 text-center text-xs text-gray-400">
        VoiceMenu AI — Multilingual Voice-First Dining Platform
      </footer>
    </div>
  );
};

export default LandingPage;
