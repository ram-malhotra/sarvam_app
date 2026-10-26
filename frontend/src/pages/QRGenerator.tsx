import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';

export const QRGenerator: React.FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const [tableNumber, setTableNumber] = useState<number>(1);

  const origin = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5173';
  const tableId = `table-${tableNumber}`;
  const targetUrl = `${origin}/r/${restaurantId}/${tableId}`;

  const handlePrint = () => {
    window.print();
  };

  if (!restaurantId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
        <p className="text-red-600 font-bold">Restaurant ID is missing.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 py-8 px-4 flex flex-col items-center">
      {/* Navigation & Controls (Hidden in print) */}
      <div className="w-full max-w-md mb-6 flex items-center justify-between print:hidden">
        <Link
          to={`/kitchen/${restaurantId}`}
          className="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-600 hover:text-orange-600 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Kitchen
        </Link>

        <button
          type="button"
          onClick={handlePrint}
          className="min-h-[44px] px-5 py-2 bg-orange-600 hover:bg-orange-700 active:bg-orange-800 text-white font-bold text-sm rounded-xl shadow-md transition-all flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Print Standee
        </button>
      </div>

      {/* Table Selector Box (Hidden in print) */}
      <div className="w-full max-w-md bg-white rounded-2xl p-5 border border-gray-200 shadow-xs mb-6 print:hidden">
        <label htmlFor="table-select" className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
          Select Table Number (1 - 20)
        </label>
        <div className="flex items-center gap-3">
          <select
            id="table-select"
            value={tableNumber}
            onChange={(e) => setTableNumber(Number(e.target.value))}
            className="flex-1 min-h-[44px] px-4 py-2 border border-gray-300 rounded-xl text-base font-bold bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            {Array.from({ length: 20 }, (_, i) => i + 1).map((num) => (
              <option key={num} value={num}>
                Table {num}
              </option>
            ))}
          </select>

          <span className="text-sm font-mono text-gray-500 bg-gray-100 px-3 py-2 rounded-xl">
            {tableId}
          </span>
        </div>
      </div>

      {/* Printable QR Code Table Standee Card */}
      <div className="w-full max-w-md bg-white rounded-3xl p-8 border-2 border-orange-500/20 shadow-xl text-center print:shadow-none print:border print:m-0 print:p-6">
        {/* Brand Header */}
        <div className="flex items-center justify-center gap-2 mb-2">
          <span className="text-2xl">🎙️</span>
          <h2 className="text-xl font-black text-gray-900 tracking-tight">
            VoiceMenu AI
          </h2>
        </div>

        <p className="text-xs font-bold uppercase tracking-widest text-orange-600 mb-6">
          Scan to Speak & Order
        </p>

        {/* QR Code Container */}
        <div className="p-4 bg-white rounded-2xl inline-block border-2 border-gray-100 shadow-xs mb-6">
          <QRCodeSVG
            value={targetUrl}
            size={220}
            level="H"
            includeMargin={true}
          />
        </div>

        {/* Table Number Highlight */}
        <div className="bg-orange-50 border border-orange-200 rounded-2xl py-3 px-4 mb-4">
          <p className="text-xs text-orange-800 font-semibold uppercase">Your Table</p>
          <p className="text-3xl font-black text-orange-950 mt-0.5">
            Table {tableNumber}
          </p>
        </div>

        {/* Multilingual instructions */}
        <div className="space-y-1 text-xs text-gray-600 font-medium">
          <p>Scan with your phone camera</p>
          <p className="text-gray-500">
            हिंदी • English • தமிழ் • తెలుగు
          </p>
        </div>

        {/* URL for manual reference */}
        <div className="mt-6 pt-4 border-t border-gray-100">
          <p className="text-[10px] text-gray-400 font-mono break-all">
            {targetUrl}
          </p>
        </div>
      </div>

      {/* Note about production HTTPS (Hidden in print) */}
      <div className="w-full max-w-md mt-6 p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 print:hidden space-y-1">
        <p className="font-bold flex items-center gap-1.5">
          <span>ℹ️</span> Microphone & HTTPS Note
        </p>
        <p className="text-amber-800 leading-relaxed">
          Browsers only allow microphone access on <code className="font-mono bg-white/80 px-1 rounded">localhost</code> or secure <code className="font-mono bg-white/80 px-1 rounded">https://</code> domains. When deploying to production or testing on mobile phones over local Wi-Fi, serve over HTTPS or configure port-forwarding.
        </p>
      </div>
    </div>
  );
};

export default QRGenerator;
