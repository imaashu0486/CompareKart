import React, { createContext, useContext, useMemo, useState } from 'react';
import { buildTheme } from '../theme/colors';

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [mode, setMode] = useState('light');

  const value = useMemo(() => {
    const theme = buildTheme(mode);
    return {
      ...theme,
      isDark: mode === 'dark',
      setMode,
      toggleTheme: () => setMode((prev) => (prev === 'light' ? 'dark' : 'light')),
    };
  }, [mode]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useAppTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useAppTheme must be used inside ThemeProvider');
  return ctx;
}
