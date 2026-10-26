import React, { useEffect, useRef, useState } from 'react';
import type { ConversationMessage, Language } from '../types';
import { synthesizeSpeech } from '../api/client';

interface ConversationAreaProps {
  messages: ConversationMessage[];
  isProcessing: boolean;
  language: Language;
}

export const ConversationArea: React.FC<ConversationAreaProps> = ({
  messages,
  isProcessing,
  language,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  // Auto-scroll on new message or processing state
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  // Handle TTS play
  const handlePlayAudio = async (msg: ConversationMessage, index: number) => {
    if (playingIndex === index) {
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
      setPlayingIndex(null);
      return;
    }

    // Stop current audio if playing
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
    }

    let urlToPlay = msg.audioUrl;
    if (!urlToPlay) {
      // Synthesize on the fly
      try {
        urlToPlay = await synthesizeSpeech(msg.content, language);
      } catch (err) {
        console.error('Failed to synthesize speech:', err);
      }
    }

    if (!urlToPlay) return;

    try {
      const audio = new Audio(urlToPlay);
      audioPlayerRef.current = audio;
      setPlayingIndex(index);

      audio.onended = () => {
        setPlayingIndex(null);
        audioPlayerRef.current = null;
      };

      audio.onerror = () => {
        setPlayingIndex(null);
        audioPlayerRef.current = null;
      };

      await audio.play();
    } catch (err) {
      console.warn('Playback failed:', err);
      setPlayingIndex(null);
    }
  };

  const formatTime = (date: Date) => {
    try {
      return new Intl.DateTimeFormat(undefined, {
        hour: 'numeric',
        minute: 'numeric',
      }).format(new Date(date));
    } catch {
      return '';
    }
  };

  return (
    <div
      tabIndex={0}
      aria-label="Conversation area"
      className="flex-1 overflow-y-auto px-4 py-4 space-y-4 smooth-scroll min-h-[220px] max-h-[55vh]"
    >
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center py-10 text-center text-gray-500">
          <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 mb-3">
            <svg
              className="w-6 h-6"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2H3v2a9 9 0 0 0 8 8.94V23h2v-2.06A9 9 0 0 0 21 12v-2h-2z" />
            </svg>
          </div>
          <p className="text-sm font-medium">Ready for your order!</p>
          <p className="text-xs text-gray-400 mt-1">
            Tap the microphone below to order in your language.
          </p>
        </div>
      )}

      {messages.map((msg, index) => {
        const isUser = msg.role === 'user';
        const isPlaying = playingIndex === index;

        return (
          <div
            key={index}
            className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-xs text-sm leading-relaxed ${
                isUser
                  ? 'bg-orange-600 text-white rounded-br-xs'
                  : 'bg-white text-gray-900 border border-gray-200/80 rounded-bl-xs'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>

              <div
                className={`mt-1.5 flex items-center gap-2 text-[11px] ${
                  isUser ? 'text-orange-200 justify-end' : 'text-gray-400 justify-between'
                }`}
              >
                <span>{formatTime(msg.timestamp)}</span>

                {!isUser && (
                  <button
                    type="button"
                    onClick={() => handlePlayAudio(msg, index)}
                    aria-label={isPlaying ? 'Stop audio' : 'Play response aloud'}
                    title="Listen to message"
                    className={`inline-flex items-center gap-1 p-1 rounded-md transition-colors ${
                      isPlaying
                        ? 'text-orange-600 bg-orange-50 font-medium'
                        : 'text-gray-500 hover:text-orange-600 hover:bg-gray-100'
                    }`}
                  >
                    <svg
                      className={`w-3.5 h-3.5 ${isPlaying ? 'animate-pulse' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      {isPlaying ? (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      ) : (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                        />
                      )}
                    </svg>
                    <span>{isPlaying ? 'Playing...' : 'Listen'}</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}

      {isProcessing && (
        <div className="flex items-center gap-2 text-gray-500 text-xs italic py-2 pl-2">
          <div className="flex gap-1">
            <span className="w-2 h-2 rounded-full bg-orange-500 animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 rounded-full bg-orange-500 animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 rounded-full bg-orange-500 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <span>Assistant is thinking...</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};

export default ConversationArea;
