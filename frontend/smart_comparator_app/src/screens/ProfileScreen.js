import React from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuth } from '../context/AuthContext';
import { useAppTheme } from '../context/ThemeContext';
import { useAppStore } from '../store/AppStore';
import ScalePressable from '../components/ScalePressable';
import CompareKartLogo from '../components/CompareKartLogo';
import { radius } from '../theme/colors';

export default function ProfileScreen() {
  const { colors, spacing, typography, shadows, isDark, toggleTheme } = useAppTheme();
  const { user, logout } = useAuth();
  const { wishlistProducts, compareIds, recentSearches } = useAppStore();

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    content: { padding: spacing.md, paddingBottom: spacing.xl + 30 },
    hero: { borderRadius: radius.md, overflow: 'hidden', marginBottom: spacing.md, ...shadows.card },
    heroInner: { padding: spacing.md },
    card: { borderRadius: radius.md, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, padding: spacing.md, ...shadows.card },
    headerRow: { flexDirection: 'row', alignItems: 'center' },
    avatar: { width: 64, height: 64, borderRadius: 32, backgroundColor: colors.chipBg, alignItems: 'center', justifyContent: 'center' },
    avatarText: { color: colors.primary, fontWeight: '900', fontSize: 24 },
    name: { ...typography.title, fontSize: 22 },
    email: { ...typography.subtitle, marginTop: 3 },
    tagline: { ...typography.caption, color: '#CBD5E1', marginTop: spacing.xs },
    statsRow: { flexDirection: 'row', marginTop: 18, gap: 8 },
    statItem: { flex: 1, backgroundColor: colors.infoSurface, borderRadius: 12, padding: 12, alignItems: 'center' },
    statValue: { fontWeight: '800', color: colors.primary },
    statLabel: { color: colors.textSecondary, fontSize: 12, marginTop: 4 },
    sectionTitle: { ...typography.title, marginTop: 16, marginBottom: 8 },
    settingsCard: { backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, ...shadows.soft },
    settingRow: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: 14, borderBottomWidth: 1, borderBottomColor: colors.border },
    settingLabel: { flex: 1, color: colors.textPrimary, fontWeight: '600' },
    logoutBtn: {
      marginTop: 18,
      backgroundColor: colors.danger,
      borderRadius: radius.sm,
      paddingVertical: 14,
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'row',
      gap: 8,
    },
    logoutText: { color: '#fff', fontWeight: '800' },
  });

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.hero}>
        <LinearGradient
          colors={[colors.headerGradientStart, colors.headerGradientEnd]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.heroInner}
        >
          <CompareKartLogo />
          <Text style={styles.tagline}>Your preferences and comparison workspace</Text>
        </LinearGradient>
      </View>

      <View style={styles.card}>
        <View style={styles.headerRow}>
          <View style={styles.avatar}><Text style={styles.avatarText}>{(user?.name || 'U')[0].toUpperCase()}</Text></View>
          <View style={{ marginLeft: 14 }}>
            <Text style={styles.name}>{user?.name || 'User'}</Text>
            <Text style={styles.email}>{user?.email || 'No email'}</Text>
          </View>
        </View>

        <View style={styles.statsRow}>
          <View style={styles.statItem}><Text style={styles.statValue}>{wishlistProducts.length}</Text><Text style={styles.statLabel}>Saved</Text></View>
          <View style={styles.statItem}><Text style={styles.statValue}>{compareIds.length}</Text><Text style={styles.statLabel}>Compare</Text></View>
          <View style={styles.statItem}><Text style={styles.statValue}>{recentSearches.length}</Text><Text style={styles.statLabel}>Searches</Text></View>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Settings</Text>
      <View style={styles.settingsCard}>
        {[
          { icon: 'bell-outline', label: 'Notifications' },
          { icon: 'shield-check-outline', label: 'Privacy' },
          { icon: isDark ? 'weather-night' : 'white-balance-sunny', label: isDark ? 'Dark mode' : 'Light mode', onPress: toggleTheme },
        ].map((s) => (
          <Pressable key={s.label} style={styles.settingRow} onPress={s.onPress} android_ripple={{ color: '#E2E8F0' }}>
            <MaterialCommunityIcons name={s.icon} size={20} color={colors.primary} />
            <Text style={styles.settingLabel}>{s.label}</Text>
            <MaterialCommunityIcons name="chevron-right" size={20} color="#94A3B8" />
          </Pressable>
        ))}
      </View>

      <ScalePressable onPress={logout} style={styles.logoutBtn}>
        <MaterialCommunityIcons name="logout" size={18} color="#fff" />
        <Text style={styles.logoutText}>Logout</Text>
      </ScalePressable>
    </ScrollView>
  );
}
