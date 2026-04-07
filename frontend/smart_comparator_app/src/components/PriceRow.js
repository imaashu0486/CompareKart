import React from 'react';
import { StyleSheet, View } from 'react-native';
import { Button, Text } from 'react-native-paper';

const hasValidPrice = (value) => typeof value === 'number' && Number.isFinite(value) && value > 0;
const formatPrice = (value) => (hasValidPrice(value) ? `₹${value.toLocaleString('en-IN')}` : 'Price unavailable');

export default function PriceRow({ label, price, isBest, onPress, disabled }) {
  const isDisabled = disabled || !hasValidPrice(price);

  return (
    <View style={[styles.container, isBest && styles.bestContainer]}>
      <View>
        <Text variant="titleMedium" style={styles.platform}>{label}</Text>
        <Text variant="bodyLarge" style={[styles.price, isBest && styles.bestPrice]}>{formatPrice(price)}</Text>
      </View>
      <Button mode={isBest ? 'contained' : 'outlined'} buttonColor={isBest ? '#0EA75A' : undefined} onPress={onPress} disabled={isDisabled}>
        {isDisabled ? 'Unavailable' : `Buy on ${label}`}
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  bestContainer: {
    borderColor: '#0EA75A',
    backgroundColor: '#ECFDF3',
  },
  platform: {
    fontWeight: '700',
    color: '#111827',
  },
  price: {
    marginTop: 2,
    color: '#374151',
    fontWeight: '700',
  },
  bestPrice: {
    color: '#0EA75A',
  },
});
