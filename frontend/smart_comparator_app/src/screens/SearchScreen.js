import React, { useMemo, useState } from 'react';
import { FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { Snackbar } from 'react-native-paper';
import { useAppStore } from '../store/AppStore';
import { useAppTheme } from '../context/ThemeContext';
import useDebouncedValue from '../hooks/useDebouncedValue';
import ProductGridCard from '../components/ProductGridCard';
import ShimmerCard from '../components/ShimmerCard';
import EmptyState from '../components/EmptyState';
import CompareSelectionBar from '../components/CompareSelectionBar';

export default function SearchScreen({ navigation }) {
  const { colors, radius, shadows, spacing, typography } = useAppTheme();
  const {
    products,
    loading,
    recentSearches,
    trendingProducts,
    addRecentSearch,
    isWishlisted,
    isCompared,
    toggleWishlist,
    toggleCompare,
    compareIds,
    compareProducts,
    removeCompare,
  } = useAppStore();

  const [query, setQuery] = useState('');
  const [feedback, setFeedback] = useState('');
  const [snackVisible, setSnackVisible] = useState(false);
  const debounced = useDebouncedValue(query, 250);

  const results = useMemo(() => {
    const q = String(debounced || '').toLowerCase().trim();
    if (!q) return [];
    return products.filter((p) => `${p.brand} ${p.model} ${p.variant_name}`.toLowerCase().includes(q));
  }, [debounced, products]);

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background, paddingHorizontal: spacing.md, paddingTop: spacing.sm },
    searchWrap: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.card,
      borderRadius: radius.lg,
      borderWidth: 1,
      borderColor: colors.border,
      paddingHorizontal: spacing.sm,
      marginBottom: spacing.md,
      ...shadows.soft,
    },
    input: { flex: 1, color: colors.textPrimary, paddingHorizontal: spacing.xs, paddingVertical: spacing.sm },
    sectionTitle: { ...typography.title, marginBottom: spacing.xs },
    chips: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.xs, marginBottom: spacing.md },
    chip: { backgroundColor: colors.chipBg, borderRadius: radius.pill, paddingHorizontal: spacing.sm, paddingVertical: spacing.xs },
    chipText: { color: colors.primary, fontWeight: '700' },
    empty: { ...typography.caption, marginBottom: spacing.sm },
  });

  const notify = (msg) => {
    setFeedback(msg);
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
      <View style={styles.searchWrap}>
        <MaterialCommunityIcons name="magnify" size={20} color={colors.textSecondary} />
        <TextInput
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={() => addRecentSearch(query)}
          placeholder="Search products"
          placeholderTextColor={colors.textSecondary}
          style={styles.input}
          returnKeyType="search"
        />
      </View>

      {loading && !products.length ? (
        <FlatList
          data={Array.from({ length: 6 }, (_, idx) => ({ id: String(idx) }))}
          keyExtractor={(item) => item.id}
          numColumns={2}
          renderItem={() => <ShimmerCard />}
          contentContainerStyle={{ paddingBottom: compareIds.length ? 190 : spacing.xl }}
        />
      ) : !debounced ? (
        <>
          <Text style={styles.sectionTitle}>Recent Searches</Text>
          <View style={styles.chips}>
            {recentSearches.length ? recentSearches.map((term) => (
              <Pressable key={term} style={styles.chip} onPress={() => setQuery(term)}>
                <Text style={styles.chipText}>{term}</Text>
              </Pressable>
            )) : <Text style={styles.empty}>No recent searches yet.</Text>}
          </View>

          <Text style={styles.sectionTitle}>Trending Products</Text>
          <FlatList
            data={trendingProducts}
            keyExtractor={(item) => item.id}
            numColumns={2}
            renderItem={({ item, index }) => (
              <ProductGridCard
                item={item}
                wishlisted={isWishlisted(item.id)}
                compared={isCompared(item.id)}
                onToggleWish={() => handleToggleWishlist(item.id)}
                onToggleCompare={() => handleToggleCompare(item.id)}
                onPress={() => {
                  addRecentSearch(item.variant_name || `${item.brand} ${item.model}`);
                  navigation.navigate('ProductDetails', { id: item.id });
                }}
              />
            )}
            contentContainerStyle={{ paddingBottom: compareIds.length ? 190 : spacing.xl }}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={<EmptyState title="No trending products" subtitle="Pull to refresh and try again." />}
          />
        </>
      ) : (
        <FlatList
          data={results}
          keyExtractor={(item) => item.id}
          numColumns={2}
          ListHeaderComponent={<Text style={styles.sectionTitle}>Results ({results.length})</Text>}
          renderItem={({ item, index }) => (
            <ProductGridCard
              item={item}
              wishlisted={isWishlisted(item.id)}
              compared={isCompared(item.id)}
              onToggleWish={() => handleToggleWishlist(item.id)}
              onToggleCompare={() => handleToggleCompare(item.id)}
              onPress={() => {
                addRecentSearch(query);
                navigation.navigate('ProductDetails', { id: item.id });
              }}
            />
          )}
          ListEmptyComponent={<EmptyState icon="magnify-close" title="No products found" subtitle="Try a different keyword or remove filters." />}
          contentContainerStyle={{ paddingBottom: compareIds.length ? 190 : spacing.xl }}
          showsVerticalScrollIndicator={false}
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
