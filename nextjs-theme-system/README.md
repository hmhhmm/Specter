# Next.js App Router - Light/Dark Mode Toggle System

Production-ready theme system with zero hydration issues and no FOUC.

## 🎯 Features

- ✅ Default dark theme
- ✅ Persistent theme preference (localStorage)
- ✅ No hydration mismatch errors
- ✅ Zero Flash of Unstyled Content (FOUC)
- ✅ Smooth theme transitions
- ✅ CSS variables for easy customization
- ✅ TypeScript support
- ✅ Accessible (ARIA labels)
- ✅ Responsive design
- ✅ Modern UI with sun/moon icons

## 📁 File Structure

```
app/
├── layout.tsx                    # Root layout with ThemeProvider
├── globals.css                   # CSS variables & theme styles
providers/
└── theme-provider.tsx            # Theme context & logic
components/
├── theme-toggle.tsx              # Toggle button component
└── theme-toggle.css              # Toggle button styles
```

## 🚀 Installation

1. Copy all files to your Next.js project
2. Update import paths in `layout.tsx` if needed:
   - `@/providers/theme-provider` → your providers path
   - `@/components/theme-toggle` → your components path

## 🔧 How It Works

### Preventing Hydration Mismatch

The system uses a **three-layer approach** to prevent hydration issues:

#### 1. **Blocking Script (Immediate Theme Application)**
```typescript
// In layout.tsx <head>
<script dangerouslySetInnerHTML={{...}}>
  // Runs BEFORE React hydrates
  // Sets data-theme attribute immediately
  // No flicker, no mismatch
</script>
```

**Why?** This script runs synchronously before React hydrates, setting the theme on `<html>` based on localStorage. The server and client both start with no `data-theme`, then the script adds it before React takes over.

#### 2. **suppressHydrationWarning on <html>**
```typescript
<html lang="en" suppressHydrationWarning>
```

**Why?** The blocking script modifies the `<html>` element's attributes before hydration, which would normally cause a warning. This suppresses that specific warning without hiding other hydration issues.

#### 3. **Deferred Context Mounting**
```typescript
// In ThemeProvider
const [mounted, setMounted] = useState(false);

useEffect(() => {
  // Only run on client after hydration
  const savedTheme = localStorage.getItem('theme') || 'dark';
  setThemeState(savedTheme);
  setMounted(true);
}, []);

if (!mounted) {
  return <>{children}</>;
}
```

**Why?** The ThemeProvider doesn't expose theme state until after client-side mount. This ensures:
- Server renders with no theme-dependent logic
- Client hydrates with same initial content
- Theme state becomes available after hydration completes

### Theme Persistence Flow

1. **First Visit (No Saved Preference)**
   ```
   User loads page
   → Blocking script checks localStorage (empty)
   → Sets data-theme="dark" (default)
   → Page renders in dark mode
   → User sees dark mode immediately
   ```

2. **Subsequent Visits (Saved Preference)**
   ```
   User loads page
   → Blocking script reads localStorage ("light")
   → Sets data-theme="light"
   → Page renders in light mode
   → No flash, no flicker
   ```

3. **Toggle Theme**
   ```
   User clicks toggle
   → toggleTheme() updates state
   → Updates localStorage
   → Updates data-theme attribute
   → CSS transitions smoothly
   ```

## 🎨 Customization

### Theme Colors

Edit `globals.css` to customize colors:

```css
[data-theme='dark'] {
  --bg-primary: #0a0a0a;      /* Main background */
  --text-primary: #ffffff;     /* Main text */
  --accent-primary: #3b82f6;   /* Accent color */
  /* ... add more variables */
}
```

### Toggle Position

Edit `theme-toggle.css`:

```css
.theme-toggle {
  position: fixed;
  top: 1.5rem;     /* Adjust vertical position */
  right: 1.5rem;   /* Adjust horizontal position */
}
```

### Toggle Style

Replace `SunIcon` and `MoonIcon` in `theme-toggle.tsx` with your own icons, or customize the track/thumb styles in `theme-toggle.css`.

## 🔍 Usage Examples

### Using Theme in Components

```typescript
'use client';

import { useTheme } from '@/providers/theme-provider';

export function MyComponent() {
  const { theme, setTheme, toggleTheme } = useTheme();
  
  return (
    <div>
      <p>Current theme: {theme}</p>
      <button onClick={toggleTheme}>Toggle</button>
      <button onClick={() => setTheme('light')}>Light</button>
      <button onClick={() => setTheme('dark')}>Dark</button>
    </div>
  );
}
```

### Conditional Rendering Based on Theme

```typescript
'use client';

import { useTheme } from '@/providers/theme-provider';

export function ThemeAwareComponent() {
  const { theme } = useTheme();
  
  return (
    <div>
      {theme === 'dark' ? (
        <img src="/logo-dark.png" alt="Logo" />
      ) : (
        <img src="/logo-light.png" alt="Logo" />
      )}
    </div>
  );
}
```

### Using CSS Variables in Your Components

```css
/* Your component.css */
.my-component {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.my-button {
  background-color: var(--accent-primary);
}

.my-button:hover {
  background-color: var(--accent-hover);
}
```

## ⚡ Performance Notes

- **Zero runtime overhead during SSR**: The blocking script is vanilla JS, no React involved
- **Minimal re-renders**: Theme context only updates on user toggle
- **CSS-based transitions**: Hardware-accelerated, smooth 60fps
- **localStorage only accessed client-side**: No server/client mismatch possible

## 🐛 Troubleshooting

### Issue: Theme flickers on page load

**Solution**: Ensure the blocking script is in `<head>` and runs before any stylesheets or React code.

### Issue: localStorage is not defined error

**Solution**: Check that you're only accessing localStorage in `useEffect` or client-side code (not during SSR).

### Issue: Toggle button doesn't appear

**Solution**: Ensure `ThemeToggle` is inside `ThemeProvider` and both are Client Components (`'use client'`).

### Issue: Theme doesn't persist

**Solution**: Check browser console for localStorage errors (private browsing mode blocks localStorage in some browsers).

## 📄 License

Free to use in your projects. No attribution required.

## 🎉 Credits

Built for Next.js 14+ App Router with production-grade best practices.
