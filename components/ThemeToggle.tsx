'use client';

import React, { useEffect, useState } from 'react';

export default function ThemeToggle() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Get saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') as 'dark' | 'light' | null;
    const initialTheme = savedTheme || 'dark';
    setTheme(initialTheme);
    
    // Apply theme to body element
    if (initialTheme === 'light') {
      document.body.classList.remove('dark');
    } else {
      document.body.classList.add('dark');
    }
    
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Toggle dark class on body
    if (newTheme === 'light') {
      document.body.classList.remove('dark');
    } else {
      document.body.classList.add('dark');
    }
  };

  if (!mounted) return null;

  return (
    <button
      onClick={toggleTheme}
      className="fixed top-5 right-5 z-[10000] group hover:scale-105 active:scale-95 transition-transform duration-200"
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <div className="w-16 h-8 bg-zinc-800 dark:bg-zinc-800 rounded-full p-0.5 shadow-lg shadow-black/20 border border-zinc-700/50 dark:border-zinc-700/50 transition-colors duration-300">
        <div
          className={`w-7 h-7 rounded-full flex items-center justify-center shadow-md transition-all duration-300 ease-out ${
            theme === 'dark'
              ? 'translate-x-0 bg-gradient-to-br from-blue-500 to-blue-600'
              : 'translate-x-8 bg-gradient-to-br from-amber-400 to-orange-500'
          }`}
        >
          {theme === 'dark' ? (
            <svg
              className="w-4 h-4 text-white animate-in fade-in duration-300"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          ) : (
            <svg
              className="w-4 h-4 text-white animate-in fade-in duration-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="4" fill="currentColor" />
              <line x1="12" y1="2" x2="12" y2="4" />
              <line x1="12" y1="20" x2="12" y2="22" />
              <line x1="4.93" y1="4.93" x2="6.34" y2="6.34" />
              <line x1="17.66" y1="17.66" x2="19.07" y2="19.07" />
              <line x1="2" y1="12" x2="4" y2="12" />
              <line x1="20" y1="12" x2="22" y2="12" />
              <line x1="6.34" y1="17.66" x2="4.93" y2="19.07" />
              <line x1="19.07" y1="4.93" x2="17.66" y2="6.34" />
            </svg>
          )}
        </div>
      </div>
    </button>
  );
}
