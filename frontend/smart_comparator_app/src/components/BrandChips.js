import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useAppTheme } from '../context/ThemeContext';
import ScalePressable from './ScalePressable';

export default function BrandChips({ brands = [], selectedBrand = 'All', onSelect }) {
  const { colors, radius, spacing, shadows } = useAppTheme();

  const styles = StyleSheet.create({
    row: { gap: spacing.xs, paddingVertical: spacing.sm, paddingRight: spacing.xs },
    chip: {
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      backgroundColor: colors.elevated,
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.xs,
      minHeight: 34,
      minWidth: 72,
      alignItems: 'center',
      justifyContent: 'center',
      ...shadows.soft,
    },
    chipSelected: {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
      transform: [{ translateY: -1 }],
    },
    text: { color: colors.textPrimary, fontWeight: '700', fontSize: 13, letterSpacing: 0.2, includeFontPadding: false },
    textSelected: { color: '#FFFFFF' },
    activeDot: {
      width: 6,
      height: 6,
      borderRadius: 3,
      backgroundColor: '#FFFFFF',
      marginLeft: spacing.xs,
    },
    chipInner: { flexDirection: 'row', alignItems: 'center' },
  });

  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.row}>
      {brands.map((brand) => {
        const selected = brand === selectedBrand;
        return (
          <ScalePressable
            key={brand}
            onPress={() => onSelect?.(brand)}
            style={[styles.chip, selected && styles.chipSelected]}
            scaleTo={0.95}
          >
            <View style={styles.chipInner}>
              <Text numberOfLines={1} style={[styles.text, selected && styles.textSelected]}>{brand}</Text>
              {selected ? <View style={styles.activeDot} /> : null}
            </View>
          </ScalePressable>
        );
      })}
    </ScrollView>
  );
}
