import 'react-native-gesture-handler';
import React from 'react';
import { Provider as PaperProvider, MD3LightTheme } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from './src/context/AuthContext';
import { ThemeProvider, useAppTheme } from './src/context/ThemeContext';
import { AppStoreProvider } from './src/store/AppStore';
import RootNavigator from './src/navigation/RootNavigator';

function AppContent() {
  const { colors } = useAppTheme();

  const theme = {
    ...MD3LightTheme,
    roundness: 16,
    colors: {
      ...MD3LightTheme.colors,
      primary: colors.primary,
      secondary: colors.success,
      background: colors.background,
      surface: colors.card,
      onSurface: colors.textPrimary,
      outline: colors.border,
      error: colors.danger,
    },
  };

  return (
    <PaperProvider theme={theme}>
      <AuthProvider>
        <AppStoreProvider>
          <RootNavigator />
        </AppStoreProvider>
      </AuthProvider>
    </PaperProvider>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </SafeAreaProvider>
  );
}
