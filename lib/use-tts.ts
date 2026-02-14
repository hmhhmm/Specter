"use client";

import { useState, useCallback, useRef, useEffect } from "react";

export interface TTSOptions {
  voice?: string;
  speed?: number;
  enabled?: boolean;
}

/**
 * Hook for handling Text-to-Speech narration via the backend Kokoro TTS service.
 * Manages an audio queue to ensure narrations play sequentially.
 */
export function useTTS(enabled: boolean = true) {
  const [isPlaying, setIsPlaying] = useState(false);
  const queueRef = useRef<string[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const isProcessingRef = useRef(false);

  /**
   * Smart filter to determine if a string is narratable human-like text.
   * Filters out system logs, URLs, and very short fragments.
   */
  const isNarratable = useCallback((text: string): boolean => {
    if (!text || text.length < 5) return false;
    
    const lowerText = text.toLowerCase();
    
    // Filter out common system log prefixes that aren't human-like
    const systemPrefixes = ["step ", "test id:", "connected to ", "initializing ", "re-attaching ", "reattaching "];
    if (systemPrefixes.some(prefix => lowerText.startsWith(prefix))) return false;
    
    // Filter out URLs
    if (lowerText.includes("http://") || lowerText.includes("https://")) return false;
    
    // Filter out raw JSON-like strings
    if (text.trim().startsWith("{") && text.trim().endsWith("}")) return false;
    
    return true;
  }, []);

  const processQueue = useCallback(async () => {
    if (isProcessingRef.current || queueRef.current.length === 0 || !enabled) {
      return;
    }

    isProcessingRef.current = true;
    const text = queueRef.current.shift();

    if (!text) {
      isProcessingRef.current = false;
      return;
    }

    try {
      setIsPlaying(true);
      
      const response = await fetch("http://localhost:8000/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch audio from TTS service");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      if (audioRef.current) {
        audioRef.current.pause();
        URL.revokeObjectURL(audioRef.current.src);
      }

      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        isProcessingRef.current = false;
        URL.revokeObjectURL(url);
        processQueue(); // Process next item in queue
      };

      audio.onerror = (e) => {
        console.error("Audio playback error:", e);
        setIsPlaying(false);
        isProcessingRef.current = false;
        processQueue();
      };

      await audio.play();
    } catch (error) {
      console.error("TTS Error:", error);
      setIsPlaying(false);
      isProcessingRef.current = false;
      processQueue();
    }
  }, [enabled]);

  const speak = useCallback((text: string) => {
    if (!enabled || !text) return;
    
    // Only narrate if it passes the human-like text filter
    if (!isNarratable(text)) {
      return;
    }

    // Add to queue and process
    queueRef.current.push(text);
    processQueue();
  }, [enabled, isNarratable, processQueue]);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
    queueRef.current = [];
    isProcessingRef.current = false;
  }, []);

  // Handle toggle off
  useEffect(() => {
    if (!enabled) {
      stop();
    }
  }, [enabled, stop]);

  return { speak, stop, isPlaying };
}
