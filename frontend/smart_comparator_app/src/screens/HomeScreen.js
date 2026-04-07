import React, { useMemo, useState } from 'react';
import { FlatList, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import { Snackbar } from 'react-native-paper';
import { useAuth } from '../context/AuthContext';
import { useAppTheme } from '../context/ThemeContext';
import useDebouncedValue from '../hooks/useDebouncedValue';
import ProductGridCard from '../components/ProductGridCard';
import BrandChips from '../components/BrandChips';
import FeaturedCarousel from '../components/FeaturedCarousel';
import ShimmerCard from '../components/ShimmerCard';
import EmptyState from '../components/EmptyState';
import ScalePressable from '../components/ScalePressable';
import CompareSelectionBar from '../components/CompareSelectionBar';
import CompareKartLogo from '../components/CompareKartLogo';
import { useAppStore } from '../store/AppStore';

function normalizeText(value) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, ' ')
    .toLowerCase();
}

export default function HomeScreen({ navigation }) {
  const { colors, radius, shadows, spacing, typography } = useAppTheme();
  const { user } = useAuth();
  const {
    products,
    loading,
    refreshing,
    error,
    selectedBrand,
    brands,
    loadProducts,
    setBrand,
    isWishlisted,
    isCompared,
    toggleWishlist,
    toggleCompare,
    compareIds,
    compareProducts,
    removeCompare,
  } = useAppStore();

  const [search, setSearch] = useState('');
  const [visibleCount, setVisibleCount] = useState(16);
  const [sortBy, setSortBy] = useState('best');
  const [feedback, setFeedback] = useState('');
  const [snackVisible, setSnackVisible] = useState(false);
  const debouncedSearch = useDebouncedValue(search, 300);

  const filtered = useMemo(() => {
    const query = normalizeText(debouncedSearch);
    const activeBrand = normalizeText(selectedBrand);

    return products.filter((p) => {
      const searchable = normalizeText(`${p.brand} ${p.model} ${p.variant_name}`);
      const byBrand =
        activeBrand === 'all' ||
        searchable.includes(activeBrand) ||
        normalizeText(p.brand) === activeBrand;
      const byQuery = !query || searchable.includes(query);
      return byBrand && byQuery;
    });
  }, [products, debouncedSearch, selectedBrand]);

  const sorted = useMemo(() => {
    const data = [...filtered];
    if (sortBy === 'price_asc') {
      return data.sort((a, b) => (a.best_price ?? Number.MAX_SAFE_INTEGER) - (b.best_price ?? Number.MAX_SAFE_INTEGER));
    }
    if (sortBy === 'price_desc') {
      return data.sort((a, b) => (b.best_price ?? -1) - (a.best_price ?? -1));
    }
    if (sortBy === 'name_asc') {
      return data.sort((a, b) => (`${a.brand} ${a.model}`.localeCompare(`${b.brand} ${b.model}`)));
    }
    return data.sort((a, b) => (a.best_price ?? Number.MAX_SAFE_INTEGER) - (b.best_price ?? Number.MAX_SAFE_INTEGER));
  }, [filtered, sortBy]);

  const visibleData = useMemo(() => sorted.slice(0, visibleCount), [sorted, visibleCount]);
  const activeBrandTitle = useMemo(() => {
    return normalizeText(selectedBrand) === 'all' ? 'Recommended phones' : `${selectedBrand} phones`;
  }, [selectedBrand]);

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
      paddingHorizontal: spacing.md,
      paddingTop: spacing.sm,
    },
    headerRow: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: spacing.md,
      borderRadius: 20,
      overflow: 'hidden',
    },
    greeting: {
      ...typography.headingSmall,
      color: '#F8FAFC',
      marginTop: spacing.xxs,
    },
    subtitle: {
      ...typography.body,
      color: '#CBD5E1',
      marginTop: spacing.xxs,
    },
    rightActions: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: spacing.xs,
    },
    iconBtn: {
      width: 36,
      height: 36,
      borderRadius: 18,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'rgba(255,255,255,0.14)',
      borderWidth: 1,
      borderColor: 'rgba(255,255,255,0.2)',
    },
    avatar: {
      width: 36,
      height: 36,
      borderRadius: 18,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'rgba(255,255,255,0.22)',
      borderWidth: 1,
      borderColor: 'rgba(255,255,255,0.2)',
    },
    avatarText: {
      color: '#FFFFFF',
      fontWeight: '700',
    },
    searchWrap: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.elevated,
      borderRadius: radius.lg,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      paddingHorizontal: spacing.sm,
      ...shadows.soft,
    },
    searchInput: {
      flex: 1,
      paddingVertical: spacing.sm,
      paddingHorizontal: spacing.xs,
      color: colors.textPrimary,
      fontSize: 14,
    },
    listContent: {
      paddingBottom: spacing.xl,
    },
    headerInner: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.md,
      width: '100%',
    },
    sectionHead: {
      marginTop: spacing.xs,
      marginBottom: spacing.sm,
      paddingHorizontal: spacing.xs,
    },
    sectionTitle: {
      ...typography.headingSmall,
      color: colors.textPrimary,
      fontSize: 18,
    },
    sectionSubtitle: {
      ...typography.caption,
      color: colors.textSecondary,
      marginTop: spacing.xxs,
    },
    sortRow: { flexDirection: 'row', gap: spacing.xs, marginBottom: spacing.sm, paddingHorizontal: spacing.xs },
    sortChip: {
      paddingHorizontal: spacing.sm,
      paddingVertical: spacing.xs,
      borderRadius: radius.pill,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      backgroundColor: colors.elevated,
    },
    sortChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
    sortChipText: { ...typography.caption, color: colors.textPrimary, fontWeight: '700' },
    sortChipTextActive: { color: '#FFFFFF' },
  });

  const notify = (message) => {
    setFeedback(message);
    setSnackVisible(true);
  };

  const handleToggleCompare = async (id) => {
    const already = isCompared(id);
    if (!already && compareIds.length >= 4) {
      notify('You can compare up to 4 phones');
      try { await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning); } catch {}
      return;
    }
    toggleCompare(id);
    notify(already ? 'Removed from compare' : 'Added to compare');
    try { await Haptics.selectionAsync(); } catch {}
  };

  const handleToggleWishlist = async (id) => {
    const already = isWishlisted(id);
    toggleWishlist(id);
    notify(already ? 'Removed from wishlist' : 'Saved to wishlist');
    try { await Haptics.selectionAsync(); } catch {}
  };

  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <LinearGradient
          colors={[colors.headerGradientStart, colors.headerGradientEnd]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.headerInner}
        >
          <View>
            <CompareKartLogo compact />
            <Text style={styles.greeting}>Hello, {user?.name || 'Anish'}</Text>
            <Text style={styles.subtitle}>Smart price discovery across trusted stores</Text>
          </View>
          <View style={styles.rightActions}>
            <ScalePressable style={styles.iconBtn} scaleTo={0.9}>
              <MaterialCommunityIcons name="bell-outline" size={20} color="#FFFFFF" />
            </ScalePressable>
            <View style={styles.avatar}><Text style={styles.avatarText}>{String(user?.name || 'A').slice(0, 1).toUpperCase()}</Text></View>
          </View>
        </LinearGradient>
      </View>

      <View style={styles.searchWrap}>
        <MaterialCommunityIcons name="magnify" size={20} color={colors.textSecondary} />
        <TextInput
          value={search}
          onChangeText={setSearch}
          placeholder="Search brand, model or variant"
          placeholderTextColor={colors.textSecondary}
          style={styles.searchInput}
        />
      </View>

      <BrandChips brands={brands} selectedBrand={selectedBrand} onSelect={(brand) => { setBrand(brand); setVisibleCount(16); }} />

      {loading && !products.length ? (
        <FlatList
          data={Array.from({ length: 6 }, (_, i) => ({ id: String(i) }))}
          keyExtractor={(item) => item.id}
          numColumns={2}
          showsVerticalScrollIndicator={false}
          renderItem={() => <ShimmerCard />}
          contentContainerStyle={[styles.listContent, compareIds.length ? { paddingBottom: 190 } : null]}
        />
      ) : (
        <FlatList
          data={visibleData}
          keyExtractor={(item) => item.id}
          numColumns={2}
          refreshing={refreshing}
          onRefresh={() => loadProducts({ refreshing: true })}
          onEndReached={() => {
            if (visibleCount < filtered.length) setVisibleCount((prev) => prev + 8);
          }}
          onEndReachedThreshold={0.5}
          maxToRenderPerBatch={8}
          showsVerticalScrollIndicator={false}
          columnWrapperStyle={{ paddingHorizontal: spacing.xxs }}
          ListHeaderComponent={(
            <>
              <FeaturedCarousel items={filtered} onPressItem={(item) => navigation.navigate('ProductDetails', { id: item.id })} />
              <View style={styles.sectionHead}>
                <Text style={styles.sectionTitle}>{activeBrandTitle}</Text>
                <Text style={styles.sectionSubtitle}>
                  {normalizeText(selectedBrand) === 'all'
                    ? 'Curated picks from top brands'
                    : 'Handpicked models for this brand'}
                </Text>
              </View>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.sortRow}>
                {[
                  { key: 'best', label: 'Best deals' },
                  { key: 'price_asc', label: 'Price ↑' },
                  { key: 'price_desc', label: 'Price ↓' },
                  { key: 'name_asc', label: 'A-Z' },
                ].map((opt) => (
                  <ScalePressable
                    key={opt.key}
                    style={[styles.sortChip, sortBy === opt.key && styles.sortChipActive]}
                    onPress={() => {
                      setSortBy(opt.key);
                      setVisibleCount(16);
                    }}
                    scaleTo={0.94}
                  >
                    <Text style={[styles.sortChipText, sortBy === opt.key && styles.sortChipTextActive]}>{opt.label}</Text>
                  </ScalePressable>
                ))}
              </ScrollView>
            </>
          )}
          renderItem={({ item }) => (
            <ProductGridCard
              item={item}
              wishlisted={isWishlisted(item.id)}
              compared={isCompared(item.id)}
              onToggleWish={() => handleToggleWishlist(item.id)}
              onToggleCompare={() => handleToggleCompare(item.id)}
              onPress={() => navigation.navigate('ProductDetails', { id: item.id })}
            />
          )}
          ListEmptyComponent={
            <EmptyState
              icon="magnify-close"
              title={error ? 'Something went wrong' : 'No products found'}
              subtitle={error || 'Try another brand or clear the search filters.'}
            />
          }
          contentContainerStyle={[styles.listContent, compareIds.length ? { paddingBottom: 190 } : null]}
        />
      )}

      <CompareSelectionBar
        selected={compareProducts}
        maxCount={4}
        onRemove={removeCompare}
        onOpenCompare={() => navigation.navigate('Compare')}
      />

      <Snackbar
        visible={snackVisible}
        onDismiss={() => setSnackVisible(false)}
        duration={1400}
        style={{ backgroundColor: colors.elevated, borderWidth: 1, borderColor: colors.borderSubtle }}
      >
        <Text style={{ color: colors.textPrimary, fontWeight: '600' }}>{feedback}</Text>
      </Snackbar>
    </View>
  );
}
