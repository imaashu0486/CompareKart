import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAppTheme } from '../context/ThemeContext';

export default function CompareKartLogo({ compact = false, onDark = true }) {
  const { colors, spacing, radius, typography } = useAppTheme();

  const styles = StyleSheet.create({
    row: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: spacing.xs,
    },
    mark: {
      width: compact ? 30 : 38,
      height: compact ? 30 : 38,
      borderRadius: radius.md,
      backgroundColor: onDark ? 'rgba(255,255,255,0.18)' : colors.infoSurface,
      borderWidth: 1,
      borderColor: onDark ? 'rgba(255,255,255,0.26)' : colors.borderSubtle,
      alignItems: 'center',
      justifyContent: 'center',
    },
    innerMark: {
      width: compact ? 18 : 22,
      height: compact ? 18 : 22,
      borderRadius: 999,
      backgroundColor: '#FFFFFF',
      alignItems: 'center',
      justifyContent: 'center',
    },
    title: {
      ...typography.body,
      color: onDark ? '#FFFFFF' : colors.textPrimary,
      fontWeight: '800',
      letterSpacing: 0.45,
    },
    sub: {
      ...typography.caption,
      color: onDark ? 'rgba(255,255,255,0.86)' : colors.textSecondary,
      marginTop: -2,
    },
  });

  return (
    <View style={styles.row}>
      <View style={styles.mark}>
        <View style={styles.innerMark}>
          <MaterialCommunityIcons name="scale-balance" size={compact ? 11 : 13} color={colors.primary} />
        </View>
      </View>
      <View>
        <Text style={styles.title}>CompareKart</Text>
        {!compact ? <Text style={styles.sub}>Compare. Decide. Save.</Text> : null}
      </View>
    </View>
  );
}
