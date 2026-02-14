import type { Metadata } from 'next';
import { ThemeProvider } from '@/providers/theme-provider';
import { ThemeToggle } from '@/components/theme-toggle';
import './globals.css';

export const metadata: Metadata = {
  title: 'Your App Name',
  description: 'Your app description',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* 
          Blocking script to prevent FOUC (Flash of Unstyled Content).
          This runs before React hydrates and sets the theme immediately.
        */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('theme') || 'dark';
                  document.documentElement.setAttribute('data-theme', theme);
                } catch (e) {
                  // If localStorage is not available, default to dark
                  document.documentElement.setAttribute('data-theme', 'dark');
                }
              })();
            `,
          }}
        />
      </head>
      <body>
        <ThemeProvider>
          <ThemeToggle />
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
