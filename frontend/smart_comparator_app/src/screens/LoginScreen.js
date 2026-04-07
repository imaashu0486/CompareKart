import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useAppTheme } from '../context/ThemeContext';
import GradientButton from '../components/GradientButton';
import CompareKartLogo from '../components/CompareKartLogo';
import { getApiErrorMessage } from '../utils/apiError';

export default function LoginScreen({ navigation }) {
  const { colors, spacing, radius, typography, shadows } = useAppTheme();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onLogin = async () => {
    const cleanEmail = email.trim();
    if (!cleanEmail || !password) {
      setError('Please enter email and password.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      await login(cleanEmail, password);
    } catch (e) {
      setError(getApiErrorMessage(e, 'Login failed'));
    } finally {
      setLoading(false);
    }
  };

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    scrollContent: { padding: spacing.md, paddingTop: spacing.lg, paddingBottom: spacing.lg },
    hero: {
      borderRadius: radius.lg,
      overflow: 'hidden',
      marginBottom: spacing.md,
      ...shadows.card,
    },
    heroInner: { padding: spacing.md },
    heroTitle: { ...typography.headingSmall, color: '#FFFFFF', marginTop: spacing.sm },
    heroSubtitle: { ...typography.body, color: '#CBD5E1', marginTop: spacing.xxs },
    heroRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, marginTop: spacing.sm },
    heroChip: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: 'rgba(255,255,255,0.14)',
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: 'rgba(255,255,255,0.2)',
      paddingHorizontal: spacing.sm,
      paddingVertical: spacing.xs,
      gap: spacing.xxs,
    },
    heroChipText: { color: '#FFFFFF', fontWeight: '700', fontSize: 12 },
    card: {
      backgroundColor: colors.card,
      borderRadius: radius.md,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      padding: spacing.md,
      ...shadows.card,
    },
    title: { ...typography.title, fontSize: 22 },
    subtitle: { ...typography.body, color: colors.textSecondary, marginTop: spacing.xxs, marginBottom: spacing.md },
    inputWrap: {
      flexDirection: 'row',
      alignItems: 'center',
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      borderRadius: radius.md,
      backgroundColor: colors.inputBg,
      paddingHorizontal: spacing.sm,
      marginBottom: spacing.sm,
    },
    input: {
      flex: 1,
      color: colors.textPrimary,
      paddingVertical: spacing.sm,
      paddingHorizontal: spacing.xs,
      fontSize: 14,
    },
    helperRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: spacing.xxs, marginBottom: spacing.sm },
    helperText: { ...typography.caption, color: colors.textSecondary },
    primaryBtn: { borderRadius: radius.md, marginTop: spacing.xs },
    linkWrap: { alignItems: 'center', marginTop: spacing.sm },
    link: { color: colors.primary, fontWeight: '600' },
    errorWrap: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: spacing.xs,
      marginBottom: spacing.xs,
      backgroundColor: 'rgba(220,38,38,0.08)',
      borderWidth: 1,
      borderColor: 'rgba(220,38,38,0.22)',
      borderRadius: radius.sm,
      paddingHorizontal: spacing.sm,
      paddingVertical: spacing.xs,
    },
    error: { color: colors.danger, flex: 1 },
  });

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={styles.scrollContent}>
        <View style={styles.hero}>
          <LinearGradient
            colors={[colors.headerGradientStart, colors.headerGradientEnd]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.heroInner}
          >
            <CompareKartLogo />
            <Text style={styles.heroTitle}>Welcome back</Text>
            <Text style={styles.heroSubtitle}>Track live prices and compare smarter in seconds.</Text>
            <View style={styles.heroRow}>
              <View style={styles.heroChip}>
                <MaterialCommunityIcons name="shield-check" size={14} color="#FFFFFF" />
                <Text style={styles.heroChipText}>Secure</Text>
              </View>
              <View style={styles.heroChip}>
                <MaterialCommunityIcons name="speedometer" size={14} color="#FFFFFF" />
                <Text style={styles.heroChipText}>Fast</Text>
              </View>
            </View>
          </LinearGradient>
        </View>

        <View style={styles.card}>
          <Text style={styles.title}>Sign in to CompareKart</Text>
          <Text style={styles.subtitle}>Continue your premium shopping experience.</Text>

          <View style={styles.inputWrap}>
            <MaterialCommunityIcons name="email-outline" size={18} color={colors.textSecondary} />
            <TextInput
              style={styles.input}
              placeholder="Email address"
              placeholderTextColor={colors.textSecondary}
              autoCapitalize="none"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
            />
          </View>

          <View style={styles.inputWrap}>
            <MaterialCommunityIcons name="lock-outline" size={18} color={colors.textSecondary} />
            <TextInput
              style={styles.input}
              placeholder="Password"
              placeholderTextColor={colors.textSecondary}
              value={password}
              secureTextEntry
              onChangeText={setPassword}
            />
          </View>

          <View style={styles.helperRow}>
            <Text style={styles.helperText}>Trusted by price-savvy shoppers</Text>
          </View>

          {!!error && (
            <View style={styles.errorWrap}>
              <MaterialCommunityIcons name="alert-circle-outline" size={16} color={colors.danger} />
              <Text style={styles.error}>{error}</Text>
            </View>
          )}

          <GradientButton style={styles.primaryBtn} onPress={onLogin} disabled={loading} title={loading ? 'Signing in...' : 'Login'} />

          <Pressable onPress={() => navigation.navigate('Signup')} style={styles.linkWrap}>
            <Text style={styles.link}>Create new account</Text>
          </Pressable>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
