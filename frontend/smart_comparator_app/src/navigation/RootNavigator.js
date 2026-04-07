import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { ActivityIndicator } from 'react-native-paper';
import * as Haptics from 'expo-haptics';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useAppTheme } from '../context/ThemeContext';
import { useAppStore } from '../store/AppStore';
import LoginScreen from '../screens/LoginScreen';
import SignupScreen from '../screens/SignupScreen';
import HomeScreen from '../screens/HomeScreen';
import SearchScreen from '../screens/SearchScreen';
import ProductScreen from '../screens/ProductScreen';
import CompareScreen from '../screens/CompareScreen';
import SavedScreen from '../screens/SavedScreen';
import ProfileScreen from '../screens/ProfileScreen';
import CompareKartLogo from '../components/CompareKartLogo';
import { radius, spacing } from '../theme/colors';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function AppTabs() {
  const { colors, shadows } = useAppTheme();
  const { compareIds, wishlistProducts } = useAppStore();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600', marginBottom: 2 },
        tabBarStyle: [styles.tabBar, { backgroundColor: colors.elevated, borderTopColor: colors.borderSubtle, ...shadows.card }],
        tabBarIcon: ({ color, size, focused }) => {
          const iconMap = {
            Home: focused ? 'home-variant' : 'home-variant-outline',
            Search: focused ? 'magnify' : 'magnify',
            Compare: focused ? 'scale-balance' : 'scale-balance',
            Saved: focused ? 'heart' : 'heart-outline',
            Profile: focused ? 'account-circle' : 'account-circle-outline',
          };
          const icon = iconMap[route.name] || 'circle-outline';
          return <MaterialCommunityIcons name={icon} color={color} size={size} />;
        },
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        listeners={{ tabPress: async () => { try { await Haptics.selectionAsync(); } catch {} } }}
      />
      <Tab.Screen
        name="Search"
        component={SearchScreen}
        listeners={{ tabPress: async () => { try { await Haptics.selectionAsync(); } catch {} } }}
      />
      <Tab.Screen
        name="Compare"
        component={CompareScreen}
        options={{ tabBarBadge: compareIds.length ? compareIds.length : undefined }}
        listeners={{ tabPress: async () => { try { await Haptics.selectionAsync(); } catch {} } }}
      />
      <Tab.Screen
        name="Saved"
        component={SavedScreen}
        options={{ tabBarBadge: wishlistProducts.length ? wishlistProducts.length : undefined }}
        listeners={{ tabPress: async () => { try { await Haptics.selectionAsync(); } catch {} } }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        listeners={{ tabPress: async () => { try { await Haptics.selectionAsync(); } catch {} } }}
      />
    </Tab.Navigator>
  );
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false, animation: 'fade' }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Signup" component={SignupScreen} />
    </Stack.Navigator>
  );
}

function AppStack() {
  const { colors } = useAppTheme();

  return (
    <Stack.Navigator
      screenOptions={{
        headerShadowVisible: false,
        contentStyle: { backgroundColor: colors.background },
        animation: 'slide_from_right',
      }}
    >
      <Stack.Screen name="Main" component={AppTabs} options={{ headerShown: false }} />
      <Stack.Screen
        name="ProductDetails"
        component={ProductScreen}
        options={{ title: 'Product Details', headerTitleStyle: { fontWeight: '700', color: colors.textPrimary } }}
      />
    </Stack.Navigator>
  );
}

function SplashScreen() {
  const { colors, spacing, typography } = useAppTheme();

  return (
    <View style={[styles.splash, { backgroundColor: colors.background }]}>
      <View style={{ marginBottom: spacing.md }}>
        <CompareKartLogo onDark={false} />
      </View>
      <ActivityIndicator size="large" color={colors.primary} />
      <Text style={[styles.splashText, { marginTop: spacing.sm }, typography.caption]}>Loading your premium dashboard...</Text>
    </View>
  );
}

export default function RootNavigator() {
  const { colors, isDark } = useAppTheme();
  const { authLoading, token } = useAuth();

  const navTheme = {
    ...(isDark ? DarkTheme : DefaultTheme),
    colors: {
      ...(isDark ? DarkTheme.colors : DefaultTheme.colors),
      background: colors.background,
      card: colors.card,
      text: colors.textPrimary,
      primary: colors.primary,
      border: colors.border,
    },
  };

  if (authLoading) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer theme={navTheme}>
      {token ? <AppStack /> : <AuthStack />}
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    height: 72,
    paddingTop: spacing.xs,
    paddingBottom: spacing.sm,
    borderTopLeftRadius: radius.md,
    borderTopRightRadius: radius.md,
    position: 'absolute',
    borderTopWidth: 1,
  },
  splash: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  splashText: {},
});
