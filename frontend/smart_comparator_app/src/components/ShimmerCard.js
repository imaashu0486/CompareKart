import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, View } from 'react-native';
import { useAppTheme } from '../context/ThemeContext';

export default function ShimmerCard() {
  const { colors, radius, spacing } = useAppTheme();
  const opacity = useRef(new Animated.Value(0.45)).current;

  const styles = StyleSheet.create({
    card: {
      flex: 1,
      backgroundColor: colors.card,
      borderRadius: radius.md,
      padding: spacing.sm,
      marginHorizontal: spacing.xs,
      marginBottom: spacing.sm,
      overflow: 'hidden',
      borderWidth: 1,
      borderColor: colors.border,
    },
    image: { height: 132, borderRadius: radius.sm, backgroundColor: colors.infoSurface },
    lineLg: { height: 12, borderRadius: 6, backgroundColor: colors.infoSurface, marginTop: spacing.sm, width: '90%' },
    lineSm: { height: 12, borderRadius: 6, backgroundColor: colors.infoSurface, marginTop: spacing.xs, width: '60%' },
    price: { height: 16, borderRadius: 8, backgroundColor: colors.infoSurface, marginTop: spacing.sm, width: '50%' },
  });

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 650, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.45, duration: 650, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [opacity]);

  return (
    <Animated.View style={[styles.card, { opacity }]}>
      <View style={styles.image} />
      <View style={styles.lineLg} />
      <View style={styles.lineSm} />
      <View style={styles.price} />
    </Animated.View>
  );
}
