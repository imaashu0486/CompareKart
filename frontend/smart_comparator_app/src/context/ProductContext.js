import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { api } from '../services/api';

const ProductContext = createContext(null);

export function ProductProvider({ children }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const loadProducts = useCallback(async ({ isRefresh = false } = {}) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      const { data } = await api.get('/products');
      setProducts(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load products');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  const value = useMemo(
    () => ({
      products,
      loading,
      refreshing,
      error,
      loadProducts,
      setProducts,
    }),
    [products, loading, refreshing, error, loadProducts]
  );

  return <ProductContext.Provider value={value}>{children}</ProductContext.Provider>;
}

export function useProducts() {
  const ctx = useContext(ProductContext);
  if (!ctx) {
    throw new Error('useProducts must be used inside ProductProvider');
  }
  return ctx;
}
