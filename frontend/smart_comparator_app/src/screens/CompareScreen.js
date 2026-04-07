import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Animated, Easing, Image, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import EmptyState from '../components/EmptyState';
import ScalePressable from '../components/ScalePressable';
import CompareKartLogo from '../components/CompareKartLogo';
import { useAppStore } from '../store/AppStore';
import { useAppTheme } from '../context/ThemeContext';
import BrandChips from '../components/BrandChips';
import { getPrimaryProductName, getVariantBadgeText } from '../utils/productName';

const PLACEHOLDER_IMAGE = 'https://placehold.co/800x800/f0f3f8/9da7b6.png';

const metricRows = [
  { key: 'platform', label: 'Best platform', icon: 'trophy-outline', get: (p) => String(p.best_platform || 'N/A').toUpperCase() },
  { key: 'amazon', label: 'Amazon', icon: 'shopping', get: (p) => (typeof p?.prices?.amazon === 'number' ? `₹${p.prices.amazon.toLocaleString('en-IN')}` : 'N/A') },
  { key: 'flipkart', label: 'Flipkart', icon: 'cart-outline', get: (p) => (typeof p?.prices?.flipkart === 'number' ? `₹${p.prices.flipkart.toLocaleString('en-IN')}` : 'N/A') },
  { key: 'croma', label: 'Croma', icon: 'storefront-outline', get: (p) => (typeof p?.prices?.croma === 'number' ? `₹${p.prices.croma.toLocaleString('en-IN')}` : 'N/A') },
];

const normalizeId = (value) => String(value ?? '');

export default function CompareScreen() {
  const theme = useAppTheme();
  const { colors, spacing, radius, typography, shadows } = theme;
  const { compareProducts, compareIds, products, toggleCompare, removeCompare, clearCompare } = useAppStore();
  const [query, setQuery] = useState('');
  const [pickerBrand, setPickerBrand] = useState('All');

  const normalizedQuery = useMemo(
    () => String(query || '').trim().replace(/\s+/g, ' ').toLowerCase(),
    [query]
  );

  const pickerBrands = useMemo(() => {
    const set = new Set(products.map((p) => p?.brand).filter(Boolean));
    return ['All', ...Array.from(set).sort((a, b) => String(a).localeCompare(String(b)))];
  }, [products]);

  const availableToAdd = useMemo(() => {
    const activeBrand = String(pickerBrand || 'All').toLowerCase();
    const comparedIdSet = new Set(compareIds.map((id) => normalizeId(id)));
    return products
      .filter((p) => !comparedIdSet.has(normalizeId(p.id)))
      .filter((p) => {
        const searchable = `${p.brand || ''} ${p.model || ''} ${p.variant_name || ''}`.toLowerCase();
        const byBrand = activeBrand === 'all' || String(p.brand || '').toLowerCase() === activeBrand;
        const byQuery = !normalizedQuery || searchable.includes(normalizedQuery);
        return byBrand && byQuery;
      })
      .sort((a, b) => {
        const ap = typeof a.best_price === 'number' ? a.best_price : Number.MAX_SAFE_INTEGER;
        const bp = typeof b.best_price === 'number' ? b.best_price : Number.MAX_SAFE_INTEGER;
        return ap - bp;
      })
      .slice(0, 24);
  }, [products, compareIds, pickerBrand, normalizedQuery]);

  const canAddMore = compareProducts.length < 4;
  const emptySlots = Math.max(0, 4 - compareProducts.length);
  const heroPulse = useRef(new Animated.Value(1)).current;
  const compareOpacity = useRef(new Animated.Value(compareProducts.length ? 1 : 0)).current;
  const compareTranslateY = useRef(new Animated.Value(compareProducts.length ? 0 : 14)).current;

  const compareStats = useMemo(() => {
    const priced = compareProducts.filter((p) => typeof p.best_price === 'number');
    if (!priced.length) {
      return { spread: null };
    }
    const sorted = [...priced].sort((a, b) => a.best_price - b.best_price);
    const spread = sorted[sorted.length - 1].best_price - sorted[0].best_price;
    return { spread };
  }, [compareProducts]);

  const platformMin = useMemo(() => {
    const mins = { amazon: null, flipkart: null, croma: null };
    compareProducts.forEach((p) => {
      if (typeof p?.prices?.amazon === 'number') {
        mins.amazon = mins.amazon === null ? p.prices.amazon : Math.min(mins.amazon, p.prices.amazon);
      }
      if (typeof p?.prices?.flipkart === 'number') {
        mins.flipkart = mins.flipkart === null ? p.prices.flipkart : Math.min(mins.flipkart, p.prices.flipkart);
      }
      if (typeof p?.prices?.croma === 'number') {
        mins.croma = mins.croma === null ? p.prices.croma : Math.min(mins.croma, p.prices.croma);
      }
    });
    return mins;
  }, [compareProducts]);

  const insights = useMemo(() => {
    const priced = compareProducts.filter((p) => typeof p.best_price === 'number');
    if (!priced.length) {
      return { cheapest: null, maxSaving: null, avg: null };
    }
    const sorted = [...priced].sort((a, b) => a.best_price - b.best_price);
    const cheapest = sorted[0];
    const avg = Math.round(sorted.reduce((sum, p) => sum + p.best_price, 0) / sorted.length);
    const maxSaving = sorted.length > 1 ? sorted[sorted.length - 1].best_price - sorted[0].best_price : null;
    return { cheapest, maxSaving, avg };
  }, [compareProducts]);

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: { flex: 1, backgroundColor: colors.background, paddingHorizontal: spacing.md, paddingTop: spacing.sm },
        hero: {
          borderRadius: radius.md,
          overflow: 'hidden',
          marginBottom: spacing.md,
          ...shadows.card,
        },
        heroInner: {
          paddingHorizontal: spacing.md,
          paddingVertical: spacing.md,
        },
        heroTitle: { ...typography.title, color: '#FFFFFF' },
        heroSub: { ...typography.caption, color: 'rgba(255,255,255,0.86)', marginTop: spacing.xxs },
        heroStatsRow: { flexDirection: 'row', gap: spacing.xs, marginTop: spacing.sm },
        heroStatPill: {
          backgroundColor: 'rgba(255,255,255,0.17)',
          borderWidth: 1,
          borderColor: 'rgba(255,255,255,0.22)',
          borderRadius: radius.pill,
          paddingHorizontal: spacing.sm,
          paddingVertical: spacing.xs,
        },
        heroStatText: { color: '#FFFFFF', fontWeight: '700', fontSize: 12 },
        slotsRow: { flexDirection: 'row', gap: spacing.xs, marginTop: spacing.xs },
        slotItem: {
          width: 36,
          height: 36,
          borderRadius: 18,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          backgroundColor: colors.card,
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
        },
        slotItemEmpty: {
          borderStyle: 'dashed',
          backgroundColor: colors.infoSurface,
        },
        slotImage: { width: 30, height: 30, borderRadius: 15, backgroundColor: colors.infoSurface },
        row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
        title: { ...typography.headingSmall },
        subtitle: { ...typography.body, color: colors.textSecondary, marginTop: spacing.xxs, marginBottom: spacing.md },
        addCard: {
          backgroundColor: colors.elevated,
          borderRadius: radius.md,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          padding: spacing.sm,
          marginBottom: spacing.md,
          ...shadows.card,
        },
        addTopRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.xs },
        addTitle: { ...typography.title },
        addHint: { ...typography.caption, color: colors.textSecondary },
        searchWrap: {
          flexDirection: 'row',
          alignItems: 'center',
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          borderRadius: radius.lg,
          paddingHorizontal: spacing.sm,
          marginBottom: spacing.xs,
        },
        searchInput: {
          flex: 1,
          color: colors.textPrimary,
          paddingVertical: spacing.sm,
          paddingHorizontal: spacing.xs,
          fontSize: 14,
        },
        pickList: { marginTop: spacing.xs },
        pickCard: {
          width: 176,
          marginRight: spacing.sm,
          borderRadius: radius.md,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          backgroundColor: colors.card,
          padding: spacing.sm,
        },
        pickImage: {
          width: '100%',
          aspectRatio: 1,
          borderRadius: radius.sm,
          backgroundColor: colors.infoSurface,
          marginBottom: spacing.xs,
        },
        pickName: { ...typography.body, fontWeight: '600', minHeight: 36 },
        pickBrand: { ...typography.caption, marginTop: spacing.xxs },
        pickPrice: { ...typography.price, fontSize: 18, marginTop: spacing.xs },
        addBtn: {
          marginTop: spacing.sm,
          alignSelf: 'flex-start',
          backgroundColor: colors.primary,
          borderRadius: radius.pill,
          paddingHorizontal: spacing.sm,
          paddingVertical: spacing.xs,
        },
        addBtnText: { color: '#FFFFFF', fontWeight: '700', fontSize: 12 },
        clearBtn: {
          backgroundColor: colors.chipBg,
          borderRadius: radius.pill,
          paddingHorizontal: spacing.sm,
          paddingVertical: spacing.xs,
        },
        clearText: { color: colors.primary, fontWeight: '600', fontSize: 13 },
        compareStrip: { marginBottom: spacing.md },
        compareStripHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.xs },
        compareStripTitle: { ...typography.title },
        compareStripHint: { ...typography.caption, color: colors.textSecondary },
        compareCard: {
          width: 220,
          borderRadius: radius.md,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          overflow: 'hidden',
          marginRight: spacing.sm,
          ...shadows.card,
        },
        compareCardInner: { padding: spacing.sm },
        compareCardCheapest: {
          borderColor: colors.success,
          ...shadows.glow,
        },
        compareTopRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: spacing.xs },
        brandPill: {
          backgroundColor: colors.infoSurface,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          borderRadius: radius.pill,
          paddingHorizontal: spacing.xs,
          paddingVertical: spacing.xxs,
        },
        brandPillText: { ...typography.caption, fontWeight: '700' },
        removeIconBtn: {
          width: 28,
          height: 28,
          borderRadius: 14,
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
        },
        cardImage: { width: '100%', aspectRatio: 1, borderRadius: radius.sm, backgroundColor: colors.infoSurface, marginBottom: spacing.xs, ...shadows.soft },
        name: { ...typography.body, fontWeight: '600', minHeight: 40 },
        price: { ...typography.price, fontSize: 20, marginTop: spacing.xs },
        lowestTag: {
          alignSelf: 'flex-start',
          backgroundColor: 'rgba(22,163,74,0.20)',
          borderRadius: radius.pill,
          paddingHorizontal: spacing.xs,
          paddingVertical: spacing.xxs,
          marginTop: spacing.xs,
        },
        lowestText: { color: colors.success, fontSize: 12, fontWeight: '600' },
        metricCard: {
          backgroundColor: colors.elevated,
          borderRadius: radius.md,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          padding: spacing.sm,
          marginBottom: spacing.sm,
        },
        metricHeader: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs, marginBottom: spacing.xs },
        metricLabel: { ...typography.caption, marginBottom: spacing.xxs },
        metricValuePill: {
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          borderRadius: radius.sm,
          backgroundColor: colors.card,
          paddingHorizontal: spacing.xs,
          paddingVertical: spacing.xs,
          minHeight: 40,
          justifyContent: 'center',
        },
        metricValuePillBest: {
          borderColor: colors.success,
          backgroundColor: 'rgba(22,163,74,0.12)',
        },
        metricValue: { ...typography.body, fontWeight: '700' },
        sectionTitle: { ...typography.title, marginBottom: spacing.sm },
        insightCard: {
          borderRadius: radius.md,
          overflow: 'hidden',
          marginBottom: spacing.md,
          ...shadows.card,
        },
        insightInner: {
          paddingHorizontal: spacing.md,
          paddingVertical: spacing.md,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          borderRadius: radius.md,
        },
        insightHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: spacing.xs },
        insightTitle: { ...typography.title, marginLeft: spacing.xs, color: colors.textPrimary },
        insightRow: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs, marginTop: spacing.xs },
        insightPill: {
          backgroundColor: colors.card,
          borderWidth: 1,
          borderColor: colors.borderSubtle,
          borderRadius: radius.pill,
          paddingHorizontal: spacing.sm,
          paddingVertical: spacing.xs,
        },
        insightPillText: { ...typography.caption, color: colors.textPrimary, fontWeight: '700' },
      }),
    [colors, spacing, radius, typography, shadows]
  );

  const lowestId = useMemo(() => {
    const priced = compareProducts.filter((p) => typeof p.best_price === 'number');
    if (!priced.length) return null;
    return [...priced].sort((a, b) => a.best_price - b.best_price)[0].id;
  }, [compareProducts]);

  useEffect(() => {
    Animated.parallel([
      Animated.timing(compareOpacity, {
        toValue: compareProducts.length ? 1 : 0,
        duration: 280,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.timing(compareTranslateY, {
        toValue: compareProducts.length ? 0 : 14,
        duration: 280,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();
  }, [compareProducts.length, compareOpacity, compareTranslateY]);

  const pulseHero = () => {
    Animated.sequence([
      Animated.timing(heroPulse, { toValue: 0.985, duration: 80, useNativeDriver: true }),
      Animated.spring(heroPulse, { toValue: 1, speed: 18, bounciness: 6, useNativeDriver: true }),
    ]).start();
  };

  const handleAddCompare = async (id) => {
    if (!canAddMore) {
      try {
        await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
      } catch {
        // ignore haptics failure on unsupported devices
      }
      return;
    }
    toggleCompare(id);
    try {
      await Haptics.selectionAsync();
    } catch {
      // ignore haptics failure on unsupported devices
    }
    pulseHero();
  };

  const handleRemoveCompare = async (id) => {
    removeCompare(id);
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    } catch {
      // ignore haptics failure on unsupported devices
    }
  };

  const handleClearCompare = async () => {
    clearCompare();
    try {
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    } catch {
      // ignore haptics failure on unsupported devices
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={{ paddingBottom: spacing.md }}
      showsVerticalScrollIndicator={false}
    >
      <Animated.View style={[styles.hero, { transform: [{ scale: heroPulse }] }]}>
        <LinearGradient
          colors={[colors.headerGradientStart, colors.headerGradientEnd]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.heroInner}
        >
          <CompareKartLogo />
          <Text style={styles.heroTitle}>Advanced comparison</Text>
          <Text style={styles.heroSub}>Pick up to 4 phones and compare platform-wise prices instantly</Text>
          <View style={styles.heroStatsRow}>
            <View style={styles.heroStatPill}>
              <Text style={styles.heroStatText}>{compareProducts.length}/4 selected</Text>
            </View>
            <View style={styles.heroStatPill}>
              <Text style={styles.heroStatText}>
                {compareStats.spread && compareStats.spread > 0
                  ? `Price spread ₹${compareStats.spread.toLocaleString('en-IN')}`
                  : 'Price spread N/A'}
              </Text>
            </View>
          </View>

          <View style={styles.slotsRow}>
            {compareProducts.map((p) => (
              <View key={`slot-${p.id}`} style={styles.slotItem}>
                <Image source={{ uri: p.image_url || PLACEHOLDER_IMAGE }} style={styles.slotImage} resizeMode="contain" />
              </View>
            ))}
            {Array.from({ length: emptySlots }, (_, idx) => (
              <View key={`slot-empty-${idx}`} style={[styles.slotItem, styles.slotItemEmpty]}>
                <MaterialCommunityIcons name="plus" size={16} color={colors.textSecondary} />
              </View>
            ))}
          </View>
        </LinearGradient>
      </Animated.View>

      <View style={styles.row}>
        <Text style={styles.title}>Compare Products</Text>
        <ScalePressable style={styles.clearBtn} onPress={handleClearCompare}>
          <Text style={styles.clearText}>Clear all</Text>
        </ScalePressable>
      </View>
      <Text style={styles.subtitle}>Selected products comparison. Lowest price is highlighted.</Text>

      <View style={styles.addCard}>
        <View style={styles.addTopRow}>
          <Text style={styles.addTitle}>Add phones to compare</Text>
          <Text style={styles.addHint}>{canAddMore ? 'Select up to 4 phones' : 'Remove one phone to add another'}</Text>
        </View>

        <View style={styles.searchWrap}>
          <MaterialCommunityIcons name="magnify" size={20} color={colors.textSecondary} />
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Search by brand, model or variant"
            placeholderTextColor={colors.textSecondary}
            style={styles.searchInput}
          />
        </View>

        <BrandChips brands={pickerBrands} selectedBrand={pickerBrand} onSelect={setPickerBrand} />

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.pickList}>
          {availableToAdd.length ? (
            availableToAdd.map((p) => (
              <ScalePressable key={`add-${p.id}`} style={styles.pickCard} onPress={() => handleAddCompare(p.id)} scaleTo={0.97}>
                <Image source={{ uri: p.image_url || PLACEHOLDER_IMAGE }} style={styles.pickImage} resizeMode="contain" />
                <Text numberOfLines={2} style={styles.pickName}>{getPrimaryProductName(p)}</Text>
                <Text numberOfLines={1} style={styles.pickBrand}>{getVariantBadgeText(p) || p.brand}</Text>
                <Text style={styles.pickPrice}>{typeof p.best_price === 'number' ? `₹${p.best_price.toLocaleString('en-IN')}` : 'N/A'}</Text>
                <View style={[styles.addBtn, !canAddMore && { opacity: 0.55 }]}>
                  <Text style={styles.addBtnText}>{canAddMore ? 'Add to compare' : 'Limit reached'}</Text>
                </View>
              </ScalePressable>
            ))
          ) : (
            <View style={[styles.pickCard, { width: 260 }]}>
              <Text style={styles.pickName}>No matching phones found</Text>
              <Text style={styles.pickBrand}>Try another brand or clear search</Text>
            </View>
          )}
        </ScrollView>
      </View>

      {compareProducts.length ? (
        <Animated.View style={{ opacity: compareOpacity, transform: [{ translateY: compareTranslateY }] }}>
          <View style={styles.compareStripHeader}>
            <Text style={styles.compareStripTitle}>Side-by-side cards</Text>
            <Text style={styles.compareStripHint}>Best deal is highlighted</Text>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.compareStrip}>
          {compareProducts.map((p) => (
            <View key={p.id} style={[styles.compareCard, lowestId === p.id && styles.compareCardCheapest]}>
              <LinearGradient
                colors={lowestId === p.id ? ['rgba(22,163,74,0.14)', 'rgba(22,163,74,0.03)'] : [colors.card, colors.elevated]}
                style={styles.compareCardInner}
              >
                <View style={styles.compareTopRow}>
                  <View style={styles.brandPill}>
                    <Text style={styles.brandPillText} numberOfLines={1}>{p.brand || 'Phone'}</Text>
                  </View>
                  <ScalePressable style={styles.removeIconBtn} onPress={() => handleRemoveCompare(p.id)}>
                    <MaterialCommunityIcons name="close" size={16} color={colors.textSecondary} />
                  </ScalePressable>
                </View>

                <Image source={{ uri: p.image_url || PLACEHOLDER_IMAGE }} style={styles.cardImage} resizeMode="contain" />
                <Text numberOfLines={2} style={styles.name}>{getPrimaryProductName(p)}</Text>
                {getVariantBadgeText(p) ? <Text numberOfLines={1} style={styles.metricLabel}>{getVariantBadgeText(p)}</Text> : null}
                <Text style={styles.price}>{typeof p.best_price === 'number' ? `₹${p.best_price.toLocaleString('en-IN')}` : 'N/A'}</Text>
                {lowestId === p.id ? (
                  <View style={styles.lowestTag}><Text style={styles.lowestText}>Lowest price</Text></View>
                ) : null}
              </LinearGradient>
            </View>
          ))}
          </ScrollView>
        </Animated.View>
      ) : (
        <EmptyState icon="scale-balance" title="No compared products" subtitle="Select products from Home, Search or Saved to compare here." />
      )}

      {compareProducts.length ? (
        <View style={styles.insightCard}>
          <LinearGradient
            colors={[colors.elevated, colors.card]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.insightInner}
          >
            <View style={styles.insightHeader}>
              <MaterialCommunityIcons name="lightbulb-on-outline" size={18} color={colors.warning} />
              <Text style={styles.insightTitle}>Smart insights</Text>
            </View>
            <View style={styles.insightRow}>
              <View style={styles.insightPill}>
                <Text style={styles.insightPillText}>
                  Cheapest: {insights.cheapest?.brand || 'N/A'}
                </Text>
              </View>
              <View style={styles.insightPill}>
                <Text style={styles.insightPillText}>
                  {typeof insights.avg === 'number' ? `Avg ₹${insights.avg.toLocaleString('en-IN')}` : 'Avg N/A'}
                </Text>
              </View>
              <View style={styles.insightPill}>
                <Text style={styles.insightPillText}>
                  {typeof insights.maxSaving === 'number' && insights.maxSaving > 0
                    ? `Max save ₹${insights.maxSaving.toLocaleString('en-IN')}`
                    : 'Max save N/A'}
                </Text>
              </View>
            </View>
          </LinearGradient>
        </View>
      ) : null}

      {compareProducts.length ? (
        <View style={{ marginBottom: spacing.md }}>
          {metricRows.map((row) => (
            <View key={row.key} style={styles.metricCard}>
              <View style={styles.metricHeader}>
                <MaterialCommunityIcons name={row.icon} size={18} color={colors.textSecondary} />
                <Text style={styles.sectionTitle}>{row.label}</Text>
              </View>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={{ flexDirection: 'row', gap: spacing.sm }}>
                  {compareProducts.map((p) => (
                    <View key={`${row.key}-${p.id}`} style={{ width: 170 }}>
                      <Text style={styles.metricLabel} numberOfLines={1}>{getPrimaryProductName(p)}</Text>
                      <View
                        style={[
                          styles.metricValuePill,
                          row.key === 'amazon' && typeof p?.prices?.amazon === 'number' && platformMin.amazon !== null && p.prices.amazon === platformMin.amazon && styles.metricValuePillBest,
                          row.key === 'flipkart' && typeof p?.prices?.flipkart === 'number' && platformMin.flipkart !== null && p.prices.flipkart === platformMin.flipkart && styles.metricValuePillBest,
                          row.key === 'croma' && typeof p?.prices?.croma === 'number' && platformMin.croma !== null && p.prices.croma === platformMin.croma && styles.metricValuePillBest,
                        ]}
                      >
                        <Text style={styles.metricValue}>{row.get(p)}</Text>
                      </View>
                    </View>
                  ))}
                </View>
              </ScrollView>
            </View>
          ))}
        </View>
      ) : null}
    </ScrollView>
  );
}
