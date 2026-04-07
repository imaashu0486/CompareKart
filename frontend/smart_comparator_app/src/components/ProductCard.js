import React, { memo, useRef } from 'react';
import { Animated, Image, Pressable, StyleSheet, View } from 'react-native';
import { Chip, Text } from 'react-native-paper';
import { getPrimaryProductName } from '../utils/productName';

const PLACEHOLDER_IMAGE = 'https://placehold.co/600x400/png?text=No+Image';
const hasValidPrice = (value) => typeof value === 'number' && Number.isFinite(value) && value > 0;

function ProductCard({ item, onPress }) {
  const scale = useRef(new Animated.Value(1)).current;
  const fade = useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    Animated.timing(fade, {
      toValue: 1,
      duration: 260,
      useNativeDriver: true,
    }).start();
  }, [fade]);

  const runScale = (toValue) => {
    Animated.spring(scale, {
      toValue,
      useNativeDriver: true,
      speed: 25,
      bounciness: 4,
    }).start();
  };

  return (
    <Animated.View style={{ opacity: fade, transform: [{ scale }] }}>
      <Pressable onPressIn={() => runScale(0.98)} onPressOut={() => runScale(1)} onPress={onPress}>
        <View style={styles.card}>
          <View style={styles.imageWrap}>
            <Image source={{ uri: item.image_url || PLACEHOLDER_IMAGE }} style={styles.image} resizeMode="cover" />
            <View style={styles.bestTag}><Text style={styles.bestTagText}>Best Deal</Text></View>
          </View>

          <Text variant="titleMedium" numberOfLines={2} style={styles.title}>
            {getPrimaryProductName(item)}
          </Text>

          <Text style={styles.price}>{hasValidPrice(item.best_price) ? `₹${Number(item.best_price).toLocaleString('en-IN')}` : 'Price unavailable'}</Text>

          <Chip compact style={styles.platformChip} textStyle={styles.platformChipText}>
            {(item.best_platform || 'Not Available').toUpperCase()}
          </Chip>
        </View>
      </Pressable>
    </Animated.View>
  );
}

export default memo(ProductCard);

const styles = StyleSheet.create({
  card: {
    width: 170,
    backgroundColor: '#fff',
    borderRadius: 18,
    padding: 10,
    borderWidth: 1,
    borderColor: '#E8EEF8',
    shadowColor: '#1F2937',
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 12,
    elevation: 2,
  },
  imageWrap: {
    borderRadius: 14,
    overflow: 'hidden',
    marginBottom: 10,
  },
  image: {
    width: '100%',
    height: 122,
    backgroundColor: '#F1F5F9',
  },
  bestTag: {
    position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: '#0EA75A',
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  bestTagText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '700',
  },
  title: {
    color: '#111827',
    fontWeight: '700',
    minHeight: 44,
  },
  price: {
    color: '#0B8A4D',
    fontSize: 20,
    fontWeight: '800',
    marginTop: 4,
    marginBottom: 6,
  },
  platformChip: {
    alignSelf: 'flex-start',
    backgroundColor: '#E8EEFF',
  },
  platformChipText: {
    color: '#1E40AF',
    fontWeight: '700',
    fontSize: 11,
  },
});
