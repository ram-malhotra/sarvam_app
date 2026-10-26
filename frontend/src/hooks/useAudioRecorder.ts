import { useState, useRef, useEffect, useCallback } from 'react';

export interface UseAudioRecorderReturn {
  isRecording: boolean;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  audioBlob: Blob | null;
  error: string | null;
  isSupported: boolean;
}

export function useAudioRecorder(): UseAudioRecorderReturn {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const resolveStopPromiseRef = useRef<((blob: Blob | null) => void) | null>(null);

  const isSupported = typeof window !== 'undefined' &&
    typeof navigator?.mediaDevices?.getUserMedia === 'function' &&
    typeof window.MediaRecorder !== 'undefined';

  const stopTracks = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);
    setAudioBlob(null);
    chunksRef.current = [];

    if (!isSupported) {
      setError('Voice recording is not supported in this browser. Please use text input or Chrome/Edge/Safari.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;

      // Determine supported mime type
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        mimeType = 'audio/webm';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
      } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
        mimeType = 'audio/ogg';
      } else {
        mimeType = '';
      }

      const recorderOptions = mimeType ? { mimeType } : undefined;
      const mediaRecorder = new MediaRecorder(stream, recorderOptions);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const type = mimeType || 'audio/webm';
        const blob = new Blob(chunksRef.current, { type });
        setAudioBlob(blob);
        setIsRecording(false);
        stopTracks();

        if (resolveStopPromiseRef.current) {
          resolveStopPromiseRef.current(blob);
          resolveStopPromiseRef.current = null;
        }
      };

      mediaRecorder.onerror = (event: Event) => {
        console.error('MediaRecorder error:', event);
        setError('Audio recording failed. Please try again.');
        setIsRecording(false);
        stopTracks();
        if (resolveStopPromiseRef.current) {
          resolveStopPromiseRef.current(null);
          resolveStopPromiseRef.current = null;
        }
      };

      // Request data every 250ms
      mediaRecorder.start(250);
      setIsRecording(true);
    } catch (err: unknown) {
      const errorMsg = (err as Error).name === 'NotAllowedError' || (err as Error).name === 'PermissionDeniedError'
        ? 'Microphone permission was denied. Please allow microphone access to use voice ordering.'
        : `Could not access microphone: ${(err as Error).message || 'Unknown error'}`;
      setError(errorMsg);
      setIsRecording(false);
      stopTracks();
    }
  }, [isSupported, stopTracks]);

  const stopRecording = useCallback((): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
        setIsRecording(false);
        stopTracks();
        resolve(null);
        return;
      }

      resolveStopPromiseRef.current = resolve;
      try {
        mediaRecorderRef.current.stop();
      } catch (err) {
        console.error('Error stopping MediaRecorder:', err);
        stopTracks();
        setIsRecording(false);
        resolve(null);
      }
    });
  }, [stopTracks]);

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        try {
          mediaRecorderRef.current.stop();
        } catch {
          // ignore
        }
      }
      stopTracks();
    };
  }, [stopTracks]);

  return {
    isRecording,
    startRecording,
    stopRecording,
    audioBlob,
    error,
    isSupported,
  };
}
