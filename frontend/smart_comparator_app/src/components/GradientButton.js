import React from 'react';
import { StyleSheet, Text } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import ScalePressable from './ScalePressable';
import { useAppTheme } from '../context/ThemeContext';

export default function GradientButton({ title, onPress, disabled, style, textStyle }) {
  const { colors, radius, spacing, typography, shadows } = useAppTheme();

  const styles = StyleSheet.create({
    wrap: {
      borderRadius: radius.lg,
      overflow: 'hidden',
      ...shadows.soft,
    },
    fill: {
      paddingVertical: spacing.sm,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: radius.lg,
    },
    text: {
      ...typography.body,
      color: '#FFFFFF',
      fontWeight: '700',
      fontSize: 15,
    },
  });

  return (
    <ScalePressable onPress={onPress} disabled={disabled} style={[styles.wrap, style]} scaleTo={0.97}>
      <LinearGradient
        colors={disabled ? ['#9CA3AF', '#9CA3AF'] : [colors.primary, colors.primaryDark]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.fill}
      >
        <Text style={[styles.text, textStyle]}>{title}</Text>
      </LinearGradient>
    </ScalePressable>
  );
}
