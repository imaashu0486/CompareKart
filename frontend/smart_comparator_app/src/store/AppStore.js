import React, { createContext, useCallback, useContext, useEffect, useMemo, useReducer } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from '../services/api';

const STORE_KEY = 'comparekart_store_v2';
const MAX_COMPARE = 4;

function normalizeBrand(value) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, ' ')
    .toLowerCase();
}

function toDisplayBrand(value) {
  const cleaned = String(value || '').trim().replace(/\s+/g, ' ');
  if (!cleaned) return '';
  return cleaned
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
}

function normalizeId(value) {
  return String(value ?? '');
}

const initialState = {
  products: [],
  loading: false,
  refreshing: false,
  error: null,
  selectedBrand: 'All',
  wishlist: {},
  compareIds: [],
  recentSearches: [],
};

function reducer(state, action) {
  switch (action.type) {
    case 'LOAD_START':
      return { ...state, loading: !action.refreshing, refreshing: action.refreshing, error: null };
    case 'LOAD_SUCCESS':
      {
        const validIds = new Set((action.products || []).map((p) => normalizeId(p?.id)));
        const sanitizedCompare = state.compareIds
          .filter((id) => validIds.has(normalizeId(id)))
          .slice(0, MAX_COMPARE);
        return {
          ...state,
          loading: false,
          refreshing: false,
          products: action.products,
          compareIds: sanitizedCompare,
        };
      }
    case 'LOAD_ERROR':
      return { ...state, loading: false, refreshing: false, error: action.error || 'Failed to load products' };
    case 'SET_BRAND':
      return { ...state, selectedBrand: action.brand };
    case 'TOGGLE_WISHLIST': {
      const next = { ...state.wishlist };
      if (next[action.id]) {
        delete next[action.id];
      } else {
        next[action.id] = true;
      }
      return { ...state, wishlist: next };
    }
    case 'TOGGLE_COMPARE': {
      const actionId = normalizeId(action.id);
      const exists = state.compareIds.some((id) => normalizeId(id) === actionId);
      if (exists) {
        return { ...state, compareIds: state.compareIds.filter((id) => normalizeId(id) !== actionId) };
      }
      if (state.compareIds.length >= MAX_COMPARE) {
        return state;
      }
      return { ...state, compareIds: [...state.compareIds, action.id] };
    }
    case 'REMOVE_COMPARE':
      return { ...state, compareIds: state.compareIds.filter((id) => normalizeId(id) !== normalizeId(action.id)) };
    case 'CLEAR_COMPARE':
      return { ...state, compareIds: [] };
    case 'ADD_RECENT': {
      const term = String(action.term || '').trim();
      if (!term) return state;
      const list = [term, ...state.recentSearches.filter((v) => v.toLowerCase() !== term.toLowerCase())].slice(0, 8);
      return { ...state, recentSearches: list };
    }
    case 'SET_PERSISTED':
      return { ...state, ...action.payload };
    default:
      return state;
  }
}

const AppStore = createContext(null);

export function AppStoreProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const loadProducts = useCallback(async ({ refreshing = false } = {}) => {
    dispatch({ type: 'LOAD_START', refreshing });
    try {
      const { data } = await api.get('/products');
      dispatch({ type: 'LOAD_SUCCESS', products: Array.isArray(data) ? data : [] });
    } catch (e) {
      dispatch({ type: 'LOAD_ERROR', error: e?.response?.data?.detail || 'Could not fetch products' });
    }
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          dispatch({
            type: 'SET_PERSISTED',
            payload: {
              wishlist: parsed?.wishlist || {},
              compareIds: parsed?.compareIds || [],
              recentSearches: parsed?.recentSearches || [],
            },
          });
        }
      } catch {
        // ignore persisted state errors
      }
      loadProducts();
    })();
  }, [loadProducts]);

  useEffect(() => {
    AsyncStorage.setItem(
      STORE_KEY,
      JSON.stringify({
        wishlist: state.wishlist,
        compareIds: state.compareIds,
        recentSearches: state.recentSearches,
      })
    ).catch(() => undefined);
  }, [state.wishlist, state.compareIds, state.recentSearches]);

  const brands = useMemo(() => {
    const byKey = new Map();

    state.products.forEach((p) => {
      const raw = p?.brand;
      const key = normalizeBrand(raw);
      if (!key || byKey.has(key)) return;
      byKey.set(key, toDisplayBrand(raw));
    });

    return ['All', ...Array.from(byKey.values()).sort((a, b) => a.localeCompare(b))];
  }, [state.products]);

  const wishlistProducts = useMemo(
    () => state.products.filter((p) => state.wishlist[p.id]),
    [state.products, state.wishlist]
  );

  const compareProducts = useMemo(
    () => state.compareIds.map((id) => state.products.find((p) => normalizeId(p.id) === normalizeId(id))).filter(Boolean),
    [state.compareIds, state.products]
  );

  const trendingProducts = useMemo(() => {
    return [...state.products]
      .filter((p) => typeof p.best_price === 'number')
      .sort((a, b) => a.best_price - b.best_price)
      .slice(0, 10);
  }, [state.products]);

  const value = useMemo(
    () => ({
      ...state,
      brands,
      wishlistProducts,
      compareProducts,
      trendingProducts,
      loadProducts,
      setBrand: (brand) => dispatch({ type: 'SET_BRAND', brand }),
      toggleWishlist: (id) => dispatch({ type: 'TOGGLE_WISHLIST', id }),
      toggleCompare: (id) => dispatch({ type: 'TOGGLE_COMPARE', id }),
      removeCompare: (id) => dispatch({ type: 'REMOVE_COMPARE', id }),
      clearCompare: () => dispatch({ type: 'CLEAR_COMPARE' }),
      addRecentSearch: (term) => dispatch({ type: 'ADD_RECENT', term }),
      getProductById: (id) => state.products.find((p) => p.id === id),
      isWishlisted: (id) => !!state.wishlist[id],
      isCompared: (id) => state.compareIds.some((x) => normalizeId(x) === normalizeId(id)),
    }),
    [state, brands, wishlistProducts, compareProducts, trendingProducts, loadProducts]
  );

  return <AppStore.Provider value={value}>{children}</AppStore.Provider>;
}

export function useAppStore() {
  const ctx = useContext(AppStore);
  if (!ctx) throw new Error('useAppStore must be used inside AppStoreProvider');
  return ctx;
}
