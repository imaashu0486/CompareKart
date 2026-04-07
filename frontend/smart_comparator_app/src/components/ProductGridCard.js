import React, { memo } from 'react';
import { Image, StyleSheet, Text, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import ScalePressable from './ScalePressable';
import { useAppTheme } from '../context/ThemeContext';
import { getPrimaryProductName } from '../utils/productName';

const PLACEHOLDER_IMAGE = 'https://placehold.co/800x800/f2f4f8/9aa2af.png';

function ProductGridCard({ item, wishlisted, compared, onToggleWish, onToggleCompare, onPress }) {
  const { colors, radius, shadows, spacing, typography } = useAppTheme();
  const displayName = getPrimaryProductName(item);
  const price = typeof item?.best_price === 'number' ? `₹${Number(item.best_price).toLocaleString('en-IN')}` : 'Price unavailable';

  const styles = StyleSheet.create({
    wrap: { flex: 1, marginBottom: spacing.sm },
    cardWrap: { marginHorizontal: spacing.xs },
    card: {
      backgroundColor: colors.elevated,
      borderRadius: 18,
      padding: spacing.md,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      ...shadows.card,
    },
    cardSelected: {
      borderColor: colors.primary,
      borderWidth: 2,
      transform: [{ scale: 0.995 }],
    },
    topRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.xs },
    rightIcons: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs },
    platformPill: {
      backgroundColor: colors.chipBg,
      borderRadius: radius.pill,
      paddingHorizontal: spacing.xs,
      paddingVertical: 3,
    },
    platformPillText: { fontSize: 10, fontWeight: '700', color: colors.primary },
    iconButton: {
      width: 30,
      height: 30,
      borderRadius: 15,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#111827',
      borderWidth: 1,
      borderColor: 'rgba(255,255,255,0.22)',
    },
    checkBadge: {
      position: 'absolute',
      left: spacing.xs,
      top: spacing.xs,
      width: 22,
      height: 22,
      borderRadius: 11,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colors.success,
      borderWidth: 2,
      borderColor: '#FFFFFF',
      zIndex: 2,
    },
    imageWrap: {
      borderRadius: radius.sm,
      backgroundColor: colors.card,
      marginBottom: spacing.sm,
      ...shadows.soft,
    },
    image: {
      width: '100%',
      aspectRatio: 1,
      borderRadius: radius.sm,
      backgroundColor: colors.infoSurface,
    },
    title: {
      ...typography.body,
      fontWeight: '600',
      lineHeight: 20,
      minHeight: 40,
      marginBottom: spacing.xs,
    },
    price: {
      ...typography.price,
      fontSize: 22,
      marginBottom: spacing.xs,
    },
    footerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
    bestTag: {
      backgroundColor: '#EAF8EF',
      borderRadius: radius.pill,
      paddingHorizontal: spacing.xs,
      paddingVertical: spacing.xxs,
    },
    bestTagText: { color: colors.success, fontWeight: '700', fontSize: 11 },
  });

  return (
    <View style={styles.wrap}>
      <ScalePressable onPress={onPress} style={styles.cardWrap} scaleTo={0.975}>
        <View style={[styles.card, compared && styles.cardSelected]}>
          {compared ? (
            <View style={styles.checkBadge}>
              <MaterialCommunityIcons name="check" size={12} color="#FFFFFF" />
            </View>
          ) : null}

          <View style={styles.topRow}>
            <View style={styles.platformPill}>
              <Text style={styles.platformPillText}>{String(item?.best_platform || 'N/A').toUpperCase()}</Text>
            </View>
            <View style={styles.rightIcons}>
              <ScalePressable onPress={onToggleCompare} scaleTo={0.9} style={styles.iconButton}>
                <MaterialCommunityIcons name={compared ? 'scale-balance' : 'scale-unbalanced'} size={17} color={compared ? '#60A5FA' : '#FFFFFF'} />
              </ScalePressable>
              <ScalePressable onPress={onToggleWish} scaleTo={0.9} style={styles.iconButton}>
                <MaterialCommunityIcons name={wishlisted ? 'heart' : 'heart-outline'} size={18} color={wishlisted ? '#F87171' : '#FFFFFF'} />
              </ScalePressable>
            </View>
          </View>

            <View style={styles.imageWrap}>
              <Image source={{ uri: item?.image_url || PLACEHOLDER_IMAGE }} style={styles.image} resizeMode="contain" />
            </View>

          <Text numberOfLines={2} ellipsizeMode="tail" style={styles.title}>{displayName}</Text>
          <Text style={styles.price}>{price}</Text>

          <View style={styles.footerRow}>
            <View style={styles.bestTag}><Text style={styles.bestTagText}>Best deal</Text></View>
            <View style={{ width: 30 }} />
          </View>
        </View>
      </ScalePressable>
    </View>
  );
}

export default memo(ProductGridCard);

const styles = StyleSheet.create({
  wrap: {},
});
