import React from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useAppTheme } from '../context/ThemeContext';
import GradientButton from './GradientButton';
import ScalePressable from './ScalePressable';

const PLACEHOLDER_IMAGE = 'https://placehold.co/200x200/f0f3f8/9da7b6.png';

export default function CompareSelectionBar({ selected = [], maxCount = 4, onOpenCompare, onRemove }) {
  const { colors, spacing, radius, shadows, typography } = useAppTheme();

  if (!selected.length) return null;

  const styles = StyleSheet.create({
    container: {
      position: 'absolute',
      left: spacing.md,
      right: spacing.md,
      bottom: 84,
      backgroundColor: colors.elevated,
      borderRadius: radius.md,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      padding: spacing.sm,
      ...shadows.card,
    },
    topRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: spacing.xs,
    },
    label: {
      ...typography.caption,
      color: colors.textSecondary,
      fontWeight: '600',
    },
    count: {
      ...typography.body,
      color: colors.primary,
      fontWeight: '700',
    },
    list: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: spacing.xs,
      marginBottom: spacing.xs,
    },
    thumbWrap: {
      width: 42,
      height: 42,
      borderRadius: 21,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      backgroundColor: colors.card,
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
    },
    thumb: {
      width: 34,
      height: 34,
      borderRadius: 17,
      backgroundColor: colors.infoSurface,
    },
    removeBtn: {
      position: 'absolute',
      top: -3,
      right: -3,
      width: 18,
      height: 18,
      borderRadius: 9,
      backgroundColor: '#111827',
      alignItems: 'center',
      justifyContent: 'center',
      borderWidth: 1,
      borderColor: 'rgba(255,255,255,0.3)',
    },
    compareBtn: {
      borderRadius: radius.lg,
    },
  });

  return (
    <View style={styles.container}>
      <View style={styles.topRow}>
        <Text style={styles.label}>Selected for compare</Text>
        <Text style={styles.count}>{selected.length}/{maxCount}</Text>
      </View>

      <View style={styles.list}>
        {selected.map((p) => (
          <View key={p.id} style={styles.thumbWrap}>
            <Image source={{ uri: p.image_url || PLACEHOLDER_IMAGE }} style={styles.thumb} resizeMode="contain" />
            <ScalePressable style={styles.removeBtn} scaleTo={0.9} onPress={() => onRemove?.(p.id)}>
              <MaterialCommunityIcons name="close" size={10} color="#FFFFFF" />
            </ScalePressable>
          </View>
        ))}
      </View>

      <GradientButton
        style={styles.compareBtn}
        title={selected.length >= 2 ? 'Compare selected' : 'Select at least 2'}
        disabled={selected.length < 2}
        onPress={onOpenCompare}
      />
    </View>
  );
}
