import React, { useEffect, useState } from 'react';
import { Image, Linking, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { api } from '../api/client';
import { getFixedPhoneSpecificationRows } from '../utils/specifications';
import { getPrimaryProductName, getVariantBadgeText } from '../utils/productName';

function parseServerDate(value) {
  if (!value) return null;
  const raw = String(value).trim();
  if (!raw) return null;

  // Some stored datetimes may arrive without timezone info; treat them as UTC.
  const normalized = /(Z|[+\-]\d{2}:?\d{2})$/.test(raw) ? raw : `${raw}Z`;
  const dt = new Date(normalized);
  return Number.isNaN(dt.getTime()) ? null : dt;
}

function formatIndianDateTime(value) {
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
}

function PriceRow({ label, value, isBest, url }) {
  return (
    <View style={[styles.priceRow, isBest && styles.bestRow]}>
      <Text style={styles.priceLabel}>{label}</Text>
      <Text style={styles.priceValue}>{value ? `₹${value}` : 'Not Available'}</Text>
      <TouchableOpacity disabled={!url} style={[styles.dealBtn, !url && styles.dealBtnDisabled]} onPress={() => url && Linking.openURL(url)}>
        <Text style={styles.dealText}>{url ? `View on ${label}` : 'Not Available'}</Text>
      </TouchableOpacity>
    </View>
  );
}

export default function ProductDetailsScreen({ route }) {
  const { id } = route.params;
  const [item, setItem] = useState(null);
  const [retrying, setRetrying] = useState(false);
  const [retryingPlatform, setRetryingPlatform] = useState({ amazon: false, flipkart: false, croma: false });

  const loadProduct = async () => {
    const { data } = await api.get(`/product/${id}`);
    setItem(data);
  };

  useEffect(() => {
    (async () => {
      await loadProduct();
    })();
  }, [id]);

  if (!item) return <View style={styles.container}><Text>Loading...</Text></View>;

  const retryScrape = async () => {
    try {
      setRetrying(true);
      await api.post(`/product/${id}/retry-prices`);
      await loadProduct();
    } finally {
      setRetrying(false);
    }
  };

  const retryPlatform = async (platform) => {
    try {
      setRetryingPlatform((prev) => ({ ...prev, [platform]: true }));
      await api.post(`/product/${id}/retry-platform/${platform}`);
      await loadProduct();
    } finally {
      setRetryingPlatform((prev) => ({ ...prev, [platform]: false }));
    }
  };

  const specRows = getFixedPhoneSpecificationRows(item);
  const refreshedAtLabel = formatIndianDateTime(item?.last_updated);

  const bestUrl = item.best_platform === 'amazon'
    ? item.amazon_url
    : item.best_platform === 'flipkart'
      ? item.flipkart_url
      : item.best_platform === 'croma'
        ? item.croma_url
        : null;

  return (
    <ScrollView style={styles.container}>
      {item.image_url ? <Image source={{ uri: item.image_url }} style={styles.image} /> : null}
      <Text style={styles.title}>{getPrimaryProductName(item)}</Text>
      {getVariantBadgeText(item) ? <Text style={styles.sub}>{getVariantBadgeText(item)}</Text> : null}
      <Text style={styles.sub}>{item.brand} • {item.category}</Text>
      <Text style={styles.refreshText}>Last refreshed: {refreshedAtLabel}</Text>

      <TouchableOpacity style={[styles.dealBtn, { marginBottom: 8 }]} onPress={retryScrape}>
        <Text style={styles.dealText}>{retrying ? 'Retrying scrape...' : 'Retry Scrape'}</Text>
      </TouchableOpacity>

      <TouchableOpacity
        disabled={!bestUrl}
        style={[styles.bestDealBtn, !bestUrl && styles.dealBtnDisabled]}
        onPress={() => bestUrl && Linking.openURL(bestUrl)}
      >
        <Text style={styles.bestDealText}>
          {bestUrl
            ? `Best Deal: ${String(item.best_platform || '').toUpperCase()} • ₹${item.best_price ?? 'N/A'}`
            : 'Best Deal Not Available'}
        </Text>
      </TouchableOpacity>

      <View style={[styles.priceRow, item.best_platform === 'amazon' && styles.bestRow]}>
        <Text style={styles.priceLabel}>Amazon</Text>
        <Text style={styles.priceValue}>{item.prices?.amazon ? `₹${item.prices.amazon}` : 'Not Available'}</Text>
        <View style={styles.priceActions}>
          <TouchableOpacity disabled={!item.amazon_url} style={[styles.dealBtn, !item.amazon_url && styles.dealBtnDisabled]} onPress={() => item.amazon_url && Linking.openURL(item.amazon_url)}>
            <Text style={styles.dealText}>{item.amazon_url ? 'Open' : 'N/A'}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.dealBtn, styles.retryBtn]} onPress={() => retryPlatform('amazon')}>
            <Text style={styles.dealText}>{retryingPlatform.amazon ? '...' : 'Retry'}</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={[styles.priceRow, item.best_platform === 'flipkart' && styles.bestRow]}>
        <Text style={styles.priceLabel}>Flipkart</Text>
        <Text style={styles.priceValue}>{item.prices?.flipkart ? `₹${item.prices.flipkart}` : 'Not Available'}</Text>
        <View style={styles.priceActions}>
          <TouchableOpacity disabled={!item.flipkart_url} style={[styles.dealBtn, !item.flipkart_url && styles.dealBtnDisabled]} onPress={() => item.flipkart_url && Linking.openURL(item.flipkart_url)}>
            <Text style={styles.dealText}>{item.flipkart_url ? 'Open' : 'N/A'}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.dealBtn, styles.retryBtn]} onPress={() => retryPlatform('flipkart')}>
            <Text style={styles.dealText}>{retryingPlatform.flipkart ? '...' : 'Retry'}</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={[styles.priceRow, item.best_platform === 'croma' && styles.bestRow]}>
        <Text style={styles.priceLabel}>Croma</Text>
        <Text style={styles.priceValue}>{item.prices?.croma ? `₹${item.prices.croma}` : 'Not Available'}</Text>
        <View style={styles.priceActions}>
          <TouchableOpacity disabled={!item.croma_url} style={[styles.dealBtn, !item.croma_url && styles.dealBtnDisabled]} onPress={() => item.croma_url && Linking.openURL(item.croma_url)}>
            <Text style={styles.dealText}>{item.croma_url ? 'Open' : 'N/A'}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.dealBtn, styles.retryBtn]} onPress={() => retryPlatform('croma')}>
            <Text style={styles.dealText}>{retryingPlatform.croma ? '...' : 'Retry'}</Text>
          </TouchableOpacity>
        </View>
      </View>

      <Text style={styles.section}>Specifications</Text>
      {specRows.map(({ key, label, value }) => (
        <View key={key} style={styles.specRow}>
          <Text style={styles.specKey}>{label}</Text>
          <Text style={styles.specVal}>{String(value)}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', padding: 12 },
  image: { width: '100%', height: 260, borderRadius: 12, marginBottom: 12 },
  title: { fontSize: 20, fontWeight: '700' },
  sub: { color: '#64748b', marginBottom: 12 },
  refreshText: { color: '#0f766e', marginBottom: 12, fontWeight: '600' },
  section: { fontSize: 16, fontWeight: '700', marginTop: 16, marginBottom: 8 },
  priceRow: { backgroundColor: '#fff', borderRadius: 10, padding: 12, marginBottom: 8, flexDirection: 'row', alignItems: 'center' },
  bestRow: { borderWidth: 1, borderColor: '#16a34a' },
  priceLabel: { width: 80, fontWeight: '700' },
  priceValue: { flex: 1 },
  priceActions: { flexDirection: 'row', gap: 6 },
  dealBtn: { backgroundColor: '#2563eb', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 7 },
  retryBtn: { backgroundColor: '#1d4ed8' },
  dealBtnDisabled: { opacity: 0.5 },
  dealText: { color: '#fff', fontWeight: '700' },
  bestDealBtn: { backgroundColor: '#16a34a', borderRadius: 10, padding: 12, marginBottom: 10 },
  bestDealText: { color: '#fff', fontWeight: '800', textAlign: 'center' },
  specRow: { backgroundColor: '#fff', padding: 10, borderRadius: 8, marginBottom: 6 },
  specKey: { color: '#334155', fontWeight: '700', textTransform: 'capitalize' },
  specVal: { color: '#0f172a' },
});
