import React, { useMemo, useRef, useState } from 'react';
import { Dimensions, FlatList, ImageBackground, StyleSheet, Text, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import ScalePressable from './ScalePressable';
import { useAppTheme } from '../context/ThemeContext';

const { width } = Dimensions.get('window');
const PLACEHOLDER_IMAGE = 'https://placehold.co/1200x600/e9edf5/8f98a8.png';

export default function FeaturedCarousel({ items = [], onPressItem }) {
  const { colors, radius, shadows, spacing, typography } = useAppTheme();
  const [active, setActive] = useState(0);
  const listRef = useRef();

  const styles = StyleSheet.create({
    wrap: { marginBottom: spacing.sm },
    title: { ...typography.title, marginBottom: spacing.sm },
    card: {
      marginRight: spacing.sm,
      borderRadius: radius.md,
      borderWidth: 1,
      borderColor: colors.borderSubtle,
      backgroundColor: colors.elevated,
      ...shadows.card,
      overflow: 'hidden',
    },
    image: {
      height: 190,
      justifyContent: 'flex-end',
      backgroundColor: colors.infoSurface,
    },
    imageRadius: { borderRadius: radius.md },
    overlay: {
      flex: 1,
      justifyContent: 'flex-end',
      paddingHorizontal: spacing.md,
      paddingVertical: spacing.sm,
    },
    caption: { color: '#FFFFFF', fontWeight: '600', fontSize: 15 },
    price: { color: '#C7F9D5', marginTop: spacing.xxs, fontWeight: '600', fontSize: 14 },
    dots: { flexDirection: 'row', justifyContent: 'center', marginTop: spacing.sm, marginBottom: spacing.xs, gap: spacing.xs },
    dot: { width: 7, height: 7, borderRadius: 7, backgroundColor: 'rgba(148,163,184,0.45)' },
    dotActive: { width: 20, backgroundColor: colors.primary },
  });

  const banners = useMemo(() => {
    if (!items?.length) return [];
    return items.slice(0, 5);
  }, [items]);

  if (!banners.length) return null;

  const cardWidth = width - 32;

  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>Best Deals Today</Text>
      <FlatList
        ref={listRef}
        data={banners}
        horizontal
        pagingEnabled
        decelerationRate="fast"
        showsHorizontalScrollIndicator={false}
        keyExtractor={(item) => item.id}
        snapToInterval={cardWidth + spacing.sm}
        snapToAlignment="start"
        disableIntervalMomentum
        onMomentumScrollEnd={(e) => {
          const idx = Math.round(e.nativeEvent.contentOffset.x / (cardWidth + spacing.sm));
          setActive(idx);
        }}
        renderItem={({ item }) => (
          <ScalePressable style={[styles.card, { width: cardWidth }]} onPress={() => onPressItem?.(item)}>
            <ImageBackground source={{ uri: item.image_url || PLACEHOLDER_IMAGE }} style={styles.image} imageStyle={styles.imageRadius}>
              <LinearGradient colors={['rgba(7,11,22,0.05)', 'rgba(7,11,22,0.72)']} style={styles.overlay}>
                <Text style={styles.caption} numberOfLines={2}>{item.variant_name}</Text>
                <Text style={styles.price}>{typeof item.best_price === 'number' ? `From ₹${Number(item.best_price).toLocaleString('en-IN')}` : 'Top value picks'}</Text>
              </LinearGradient>
            </ImageBackground>
          </ScalePressable>
        )}
      />
      <View style={styles.dots}>
        {banners.map((b, idx) => (
          <View key={b.id} style={[styles.dot, idx === active && styles.dotActive]} />
        ))}
      </View>
    </View>
  );
}
