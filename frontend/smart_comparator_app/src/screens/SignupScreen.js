import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useAppTheme } from '../context/ThemeContext';
import GradientButton from '../components/GradientButton';
import CompareKartLogo from '../components/CompareKartLogo';
import { getApiErrorMessage } from '../utils/apiError';

export default function SignupScreen({ navigation }) {
  const { colors, spacing, radius, typography, shadows } = useAppTheme();
  const { signup } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onSignup = async () => {
    const cleanName = name.trim();
    const cleanEmail = email.trim();

    if (!cleanName || !cleanEmail || !password) {
      setError('Please fill all fields.');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      await signup(cleanName, cleanEmail, password);
    } catch (e) {
      setError(getApiErrorMessage(e, 'Signup failed'));
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
    helperRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs, marginTop: spacing.xxs, marginBottom: spacing.sm },
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
            <Text style={styles.heroTitle}>Create your account</Text>
            <Text style={styles.heroSubtitle}>Save more with intelligent price comparison.</Text>
            <View style={styles.heroRow}>
              <View style={styles.heroChip}>
                <MaterialCommunityIcons name="account-check-outline" size={14} color="#FFFFFF" />
                <Text style={styles.heroChipText}>Quick setup</Text>
              </View>
              <View style={styles.heroChip}>
                <MaterialCommunityIcons name="star-four-points-outline" size={14} color="#FFFFFF" />
                <Text style={styles.heroChipText}>Premium UI</Text>
              </View>
            </View>
          </LinearGradient>
        </View>

        <View style={styles.card}>
          <Text style={styles.title}>Sign up for CompareKart</Text>
          <Text style={styles.subtitle}>Start tracking prices across Amazon, Flipkart and Croma.</Text>

          <View style={styles.inputWrap}>
            <MaterialCommunityIcons name="account-outline" size={18} color={colors.textSecondary} />
            <TextInput style={styles.input} placeholder="Full name" placeholderTextColor={colors.textSecondary} value={name} onChangeText={setName} />
          </View>

          <View style={styles.inputWrap}>
            <MaterialCommunityIcons name="email-outline" size={18} color={colors.textSecondary} />
            <TextInput style={styles.input} placeholder="Email" placeholderTextColor={colors.textSecondary} value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" />
          </View>

          <View style={styles.inputWrap}>
            <MaterialCommunityIcons name="lock-outline" size={18} color={colors.textSecondary} />
            <TextInput style={styles.input} placeholder="Password" placeholderTextColor={colors.textSecondary} value={password} onChangeText={setPassword} secureTextEntry />
          </View>

          <View style={styles.helperRow}>
            <MaterialCommunityIcons name="shield-check-outline" size={14} color={colors.success} />
            <Text style={styles.helperText}>Use 8+ characters for stronger account security</Text>
          </View>

          {!!error && (
            <View style={styles.errorWrap}>
              <MaterialCommunityIcons name="alert-circle-outline" size={16} color={colors.danger} />
              <Text style={styles.error}>{error}</Text>
            </View>
          )}

          <GradientButton style={styles.primaryBtn} onPress={onSignup} disabled={loading} title={loading ? 'Creating account...' : 'Sign up'} />

          <Pressable onPress={() => navigation.navigate('Login')} style={styles.linkWrap}>
            <Text style={styles.link}>Already have an account? Login</Text>
          </Pressable>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
