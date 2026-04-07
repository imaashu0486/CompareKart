import React from 'react';
import { StyleSheet, View } from 'react-native';

export default function ProductSkeleton() {
  return (
    <View style={styles.card}>
      <View style={styles.image} />
      <View style={styles.lineLong} />
      <View style={styles.lineShort} />
      <View style={styles.badge} />
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: '#fff',
    margin: 8,
    borderRadius: 18,
    padding: 12,
    borderWidth: 1,
    borderColor: '#EEF2F7',
  },
  image: {
    width: '100%',
    height: 120,
    borderRadius: 12,
    backgroundColor: '#EDF2F7',
    marginBottom: 10,
  },
  lineLong: {
    width: '100%',
    height: 14,
    borderRadius: 8,
    backgroundColor: '#EDF2F7',
    marginBottom: 8,
  },
  lineShort: {
    width: '62%',
    height: 14,
    borderRadius: 8,
    backgroundColor: '#EDF2F7',
    marginBottom: 10,
  },
  badge: {
    width: '50%',
    height: 28,
    borderRadius: 14,
    backgroundColor: '#EDF2F7',
  },
});
