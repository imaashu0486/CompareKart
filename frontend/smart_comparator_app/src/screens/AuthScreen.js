import React, { useMemo, useState } from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet, View } from 'react-native';
import { Button, HelperText, Surface, Text, TextInput } from 'react-native-paper';
import { useAuth } from '../context/AuthContext';

export default function AuthScreen({ mode = 'login', navigation }) {
  const isLogin = mode === 'login';
  const { login, signup } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const title = useMemo(() => (isLogin ? 'Welcome back' : 'Create account'), [isLogin]);

  const submit = async () => {
    setError('');
    if (!email.trim() || !password.trim() || (!isLogin && !name.trim())) {
      setError('Please fill all required fields');
      return;
    }

    try {
      setSubmitting(true);
      if (isLogin) {
        await login(email.trim(), password);
      } else {
        await signup(name.trim(), email.trim(), password);
      }
    } catch (e) {
      const apiError = e?.response?.data?.detail;
      if (apiError) {
        setError(apiError);
      } else {
        setError('Cannot reach server. Check backend is running and phone/emulator can access it.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.container}>
      <View style={styles.content}>
        <Text variant="headlineMedium" style={styles.title}>{title}</Text>
        <Text variant="bodyLarge" style={styles.subtitle}>Compare prices across Amazon, Flipkart, and Croma instantly.</Text>

        <Surface style={styles.card} elevation={1}>
          {!isLogin ? (
            <TextInput
              mode="outlined"
              label="Full Name"
              value={name}
              onChangeText={setName}
              style={styles.input}
              outlineStyle={styles.inputOutline}
            />
          ) : null}

          <TextInput
            mode="outlined"
            label="Email"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
            style={styles.input}
            outlineStyle={styles.inputOutline}
          />

          <TextInput
            mode="outlined"
            label="Password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!showPassword}
            style={styles.input}
            outlineStyle={styles.inputOutline}
            right={<TextInput.Icon icon={showPassword ? 'eye-off' : 'eye'} onPress={() => setShowPassword((p) => !p)} />}
          />

          {!!error ? <HelperText type="error" visible>{error}</HelperText> : null}

          <Button mode="contained" onPress={submit} loading={submitting} disabled={submitting} style={styles.primaryBtn} contentStyle={styles.primaryBtnContent}>
            {isLogin ? 'Login' : 'Sign up'}
          </Button>

          <Button mode="text" onPress={() => navigation.navigate(isLogin ? 'Signup' : 'Login')}>
            {isLogin ? 'New here? Create account' : 'Already have an account? Login'}
          </Button>
        </Surface>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F9FC' },
  content: { flex: 1, justifyContent: 'center', padding: 20 },
  title: { color: '#111827', fontWeight: '800', marginBottom: 8 },
  subtitle: { color: '#64748B', marginBottom: 20 },
  card: {
    borderRadius: 22,
    padding: 16,
    backgroundColor: '#fff',
  },
  input: {
    marginBottom: 12,
    backgroundColor: '#fff',
  },
  inputOutline: {
    borderRadius: 14,
  },
  primaryBtn: {
    borderRadius: 14,
    marginTop: 8,
  },
  primaryBtnContent: {
    height: 48,
  },
});
