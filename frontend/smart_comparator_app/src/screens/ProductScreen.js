import React, { useEffect, useMemo, useState } from 'react';
import { FlatList, Image, Linking, ScrollView, StyleSheet, Text, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { api } from '../services/api';
import { getFixedPhoneSpecificationRows } from '../utils/specifications';
import { useAppStore } from '../store/AppStore';
import { useAppTheme } from '../context/ThemeContext';
import ScalePressable from '../components/ScalePressable';
import GradientButton from '../components/GradientButton';
import EmptyState from '../components/EmptyState';
import { radius } from '../theme/colors';
import { getPrimaryProductName, getVariantBadgeText } from '../utils/productName';

const PLACEHOLDER_IMAGE = 'https://placehold.co/1000x700/f0f3f8/9da7b6.png';
const hasValidPrice = (value) => typeof value === 'number' && Number.isFinite(value) && value > 0;

const parseServerDate = (value) => {
  if (!value) return null;
  const raw = String(value).trim();
  if (!raw) return null;

  // Some stored datetimes may arrive without timezone info; treat them as UTC.
  const normalized = /(Z|[+\-]\d{2}:?\d{2})$/.test(raw) ? raw : `${raw}Z`;
  const dt = new Date(normalized);
  return Number.isNaN(dt.getTime()) ? null : dt;
};

const formatIndianDateTime = (value) => {
  const dt = parseServerDate(value);
  if (!dt) return 'Unknown';

  return new Intl.DateTimeFormat('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  }).format(dt) + ' IST';
};

const getBestLink = (item) => {
  if (item?.best_platform === 'amazon') return item?.amazon_url;
  if (item?.best_platform === 'flipkart') return item?.flipkart_url;
  if (item?.best_platform === 'croma') return item?.croma_url;
  return null;
};

export default function ProductScreen({ route, navigation }) {
  const { colors, shadows, spacing, typography } = useAppTheme();
  const { id } = route.params;
  const { products, isWishlisted, toggleWishlist } = useAppStore();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retrying, setRetrying] = useState(false);
  const [retryingPlatform, setRetryingPlatform] = useState({ amazon: false, flipkart: false, croma: false });

  const loadProduct = async () => {
    try {
      setLoading(true);
      setError(null);
      const { data } = await api.get(`/product/${id}`);
      setItem(data);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load product details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProduct();
  }, [id]);

  const retryScrape = async () => {
    try {
      setRetrying(true);
      await api.post(`/product/${id}/retry-prices`);
      await loadProduct();
    } catch {
      await loadProduct();
    } finally {
      setRetrying(false);
    }
  };

  const retryPlatformScrape = async (platform) => {
    try {
      setRetryingPlatform((prev) => ({ ...prev, [platform]: true }));
      await api.post(`/product/${id}/retry-platform/${platform}`);
      await loadProduct();
    } catch {
      await loadProduct();
    } finally {
      setRetryingPlatform((prev) => ({ ...prev, [platform]: false }));
    }
  };

  const bestLink = useMemo(() => getBestLink(item), [item]);
  const specRows = useMemo(() => getFixedPhoneSpecificationRows(item), [item]);
  const gallery = useMemo(() => {
    const image = item?.image_url || PLACEHOLDER_IMAGE;
    return [image, image, image];
  }, [item?.image_url]);
  const similar = useMemo(() => {
    if (!item) return [];
    return products.filter((p) => p.id !== item.id && p.brand === item.brand).slice(0, 8);
  }, [item, products]);
  const canOpenBestDeal = hasValidPrice(item?.best_price) && !!bestLink;
  const primaryName = getPrimaryProductName(item);
  const variantBadge = getVariantBadgeText(item);
  const refreshedAtLabel = formatIndianDateTime(item?.last_updated);

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background },
    content: { padding: spacing.md, paddingBottom: spacing.xl },
    centered: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.md },
    loadingText: { ...typography.body, color: colors.textSecondary },
    image: { width: 330, height: 290, borderRadius: radius.md, marginRight: spacing.sm, backgroundColor: colors.infoSurface, ...shadows.soft },
    heroCard: { borderRadius: radius.md, marginTop: spacing.sm, backgroundColor: colors.elevated, borderWidth: 1, borderColor: colors.borderSubtle, padding: spacing.md, ...shadows.card },
    titleRow: { flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between' },
    iconBtn: { borderRadius: radius.pill },
    title: { ...typography.headingSmall },
    subtitle: { ...typography.body, color: colors.textSecondary, marginTop: spacing.xxs },
    bestPrice: { marginTop: spacing.sm, fontWeight: '700', color: colors.success, fontSize: 30 },
    bestLabel: { color: colors.success, fontWeight: '600' },
    refreshRow: { flexDirection: 'row', alignItems: 'center', marginTop: spacing.xs },
    refreshDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.success, marginRight: spacing.xs },
    refreshText: { ...typography.caption, color: colors.textSecondary },
    sectionTitle: { ...typography.title, marginTop: spacing.md, marginBottom: spacing.xs },
    platformRow: { backgroundColor: colors.elevated, borderRadius: radius.sm, borderWidth: 1, borderColor: colors.borderSubtle, padding: spacing.sm, marginBottom: spacing.xs, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
    platformName: { color: colors.textPrimary, fontWeight: '700' },
    platformPrice: { color: colors.success, fontWeight: '700', marginTop: 4 },
    rowBtn: { backgroundColor: colors.chipBg, borderRadius: radius.pill, paddingHorizontal: spacing.sm, paddingVertical: spacing.xs },
    rowBtnRetry: { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.borderSubtle },
    rowBtnText: { color: colors.primary, fontWeight: '700' },
    primaryBtn: { marginTop: spacing.sm, borderRadius: radius.lg },
    primaryBtnText: { color: '#fff', fontWeight: '700' },
    secondaryBtn: { borderRadius: radius.sm, borderWidth: 1, borderColor: colors.primary, alignItems: 'center', paddingVertical: spacing.sm, marginTop: spacing.xs },
    compareText: { color: colors.primary, fontWeight: '700' },
    retryText: { color: colors.primary, fontWeight: '700' },
    buyBtnDisabled: { opacity: 0.5 },
    specRow: {
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      borderRadius: radius.sm,
      padding: spacing.sm,
      marginBottom: spacing.xs,
      backgroundColor: colors.elevated,
    },
    specKey: { color: colors.textSecondary, marginBottom: spacing.xxs, fontWeight: '600' },
    specVal: { color: colors.textPrimary },
    similarCard: { width: 150, backgroundColor: colors.elevated, borderRadius: radius.sm, borderWidth: 1, borderColor: colors.borderSubtle, padding: spacing.xs, marginRight: spacing.sm },
    simImage: { width: '100%', height: 90, borderRadius: radius.sm, backgroundColor: colors.infoSurface },
    simTitle: { color: colors.textPrimary, fontWeight: '600', fontSize: 12, marginTop: spacing.xs, minHeight: 34 },
    simPrice: { color: colors.success, fontWeight: '700', marginTop: 3 },
  });

  if (loading) return <View style={styles.centered}><Text style={styles.loadingText}>Loading product details...</Text></View>;

  if (error) {
    return (
      <View style={styles.centered}>
        <EmptyState icon="alert-circle-outline" title="Could not load product" subtitle={error} />
        <GradientButton style={styles.primaryBtn} onPress={loadProduct} title="Retry" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <FlatList
        data={gallery}
        horizontal
        pagingEnabled
        keyExtractor={(_, idx) => `${idx}`}
        showsHorizontalScrollIndicator={false}
        renderItem={({ item: image }) => <Image source={{ uri: image }} style={styles.image} resizeMode="contain" />}
      />

      <View style={styles.heroCard}>
        <View style={styles.titleRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>{primaryName}</Text>
            {variantBadge ? <Text style={styles.subtitle}>{variantBadge}</Text> : null}
            <Text style={styles.subtitle}>{item?.brand} • {item?.category}</Text>
          </View>
          <ScalePressable onPress={() => toggleWishlist(item.id)} style={styles.iconBtn} scaleTo={0.9}>
            <MaterialCommunityIcons name={isWishlisted(item.id) ? 'heart' : 'heart-outline'} size={24} color={isWishlisted(item.id) ? '#EF4444' : '#64748B'} />
          </ScalePressable>
        </View>

        <Text style={styles.bestPrice}>{hasValidPrice(item?.best_price) ? `₹${Number(item.best_price).toLocaleString('en-IN')}` : 'Price unavailable'}</Text>
        <Text style={styles.bestLabel}>{item?.best_platform ? `Best on ${String(item.best_platform).toUpperCase()}` : 'Best deal unavailable'}</Text>
        <View style={styles.refreshRow}>
          <View style={styles.refreshDot} />
          <Text style={styles.refreshText}>Last refreshed: {refreshedAtLabel}</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Platform Prices</Text>
      {[
        { label: 'Amazon', key: 'amazon', price: item?.prices?.amazon, url: item?.amazon_url },
        { label: 'Flipkart', key: 'flipkart', price: item?.prices?.flipkart, url: item?.flipkart_url },
        { label: 'Croma', key: 'croma', price: item?.prices?.croma, url: item?.croma_url },
      ].map((p) => (
        <View key={p.label} style={styles.platformRow}>
          <View>
            <Text style={styles.platformName}>{p.label}</Text>
            <Text style={styles.platformPrice}>{typeof p.price === 'number' ? `₹${Number(p.price).toLocaleString('en-IN')}` : 'N/A'}</Text>
          </View>
          <View style={{ flexDirection: 'row', gap: spacing.xs }}>
            <ScalePressable style={[styles.rowBtn, !p.url && styles.buyBtnDisabled]} disabled={!p.url} onPress={() => p.url && Linking.openURL(p.url)}>
              <Text style={styles.rowBtnText}>Open</Text>
            </ScalePressable>
            <ScalePressable style={[styles.rowBtn, styles.rowBtnRetry]} onPress={() => retryPlatformScrape(p.key)}>
              <Text style={styles.rowBtnText}>{retryingPlatform[p.key] ? 'Retrying...' : 'Retry'}</Text>
            </ScalePressable>
          </View>
        </View>
      ))}

      <GradientButton style={[styles.primaryBtn, !canOpenBestDeal && styles.buyBtnDisabled]} disabled={!canOpenBestDeal} onPress={() => bestLink && Linking.openURL(bestLink)} title="Go to Best Deal" />

      <ScalePressable style={styles.secondaryBtn} onPress={() => navigation.navigate('Compare')}>
        <Text style={styles.compareText}>Open Compare</Text>
      </ScalePressable>

      <ScalePressable style={styles.secondaryBtn} onPress={retryScrape}>
        <Text style={styles.retryText}>{retrying ? 'Retrying scrape...' : 'Retry Scrape'}</Text>
      </ScalePressable>

      <Text style={styles.sectionTitle}>Specifications</Text>
      {specRows.map(({ key, label, value }) => (
        <View key={key} style={styles.specRow}>
          <Text style={styles.specKey}>{label}</Text>
          <Text style={styles.specVal}>{String(value)}</Text>
        </View>
      ))}

      <Text style={styles.sectionTitle}>Similar Products</Text>
      <FlatList
        data={similar}
        horizontal
        keyExtractor={(p) => p.id}
        showsHorizontalScrollIndicator={false}
        renderItem={({ item: sim }) => (
          <ScalePressable style={styles.similarCard} onPress={() => navigation.push('ProductDetails', { id: sim.id })}>
            <Image source={{ uri: sim.image_url || PLACEHOLDER_IMAGE }} style={styles.simImage} />
            <Text style={styles.simTitle} numberOfLines={2}>{getPrimaryProductName(sim)}</Text>
            <Text style={styles.simPrice}>{typeof sim.best_price === 'number' ? `₹${sim.best_price.toLocaleString('en-IN')}` : 'N/A'}</Text>
          </ScalePressable>
        )}
      />
    </ScrollView>
  );
}
