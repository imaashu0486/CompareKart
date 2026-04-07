import React, { useState } from 'react';
import { FlatList, StyleSheet, Text, View } from 'react-native';
import * as Haptics from 'expo-haptics';
import { Snackbar } from 'react-native-paper';
import ProductGridCard from '../components/ProductGridCard';
import ShimmerCard from '../components/ShimmerCard';
import EmptyState from '../components/EmptyState';
import CompareSelectionBar from '../components/CompareSelectionBar';
import { useAppStore } from '../store/AppStore';
import { useAppTheme } from '../context/ThemeContext';

export default function SavedScreen({ navigation }) {
  const { colors, spacing, typography } = useAppTheme();
  const { loading, wishlistProducts, isWishlisted, isCompared, toggleWishlist, toggleCompare, compareIds, compareProducts, removeCompare } = useAppStore();
  const [feedback, setFeedback] = useState('');
  const [snackVisible, setSnackVisible] = useState(false);

  const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: colors.background, paddingHorizontal: spacing.md, paddingTop: spacing.sm },
    title: { ...typography.heading },
    subtitle: { ...typography.body, color: colors.textSecondary, marginTop: spacing.xxs, marginBottom: spacing.sm },
    skeletonWrap: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 12 },
    empty: { ...typography.caption, textAlign: 'center', marginTop: spacing.lg },
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

  if (loading && !wishlistProducts.length) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Saved Products</Text>
        <FlatList
          data={Array.from({ length: 4 }, (_, idx) => ({ id: String(idx) }))}
          keyExtractor={(item) => item.id}
          numColumns={2}
          renderItem={() => <ShimmerCard />}
          contentContainerStyle={{ paddingBottom: spacing.xl }}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Saved Products</Text>
      <Text style={styles.subtitle}>Your wishlist, synced for quick access.</Text>
      <FlatList
        data={wishlistProducts}
        keyExtractor={(item) => item.id}
        numColumns={2}
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
        ListEmptyComponent={<EmptyState icon="heart-outline" title="No saved products" subtitle="Tap the heart icon on a product card to save it here." />}
        contentContainerStyle={{ paddingBottom: compareIds.length ? 190 : spacing.xl }}
        showsVerticalScrollIndicator={false}
      />

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
