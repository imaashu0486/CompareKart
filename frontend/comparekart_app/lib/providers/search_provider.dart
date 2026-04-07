/// Search Provider
/// Manages search state and results

import 'package:flutter/material.dart';
import '../models/product_model.dart';
import '../services/api_service.dart';

class SearchProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  /// State variables
  ComparisonResult? _searchResult;
  bool _isLoading = false;
  String? _error;
  String _lastQuery = '';

  /// Getters
  ComparisonResult? get searchResult => _searchResult;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String get lastQuery => _lastQuery;

  /// Check if has results
  bool get hasResults => _searchResult != null && _searchResult!.products.isNotEmpty;

  /// Get result count
  int get resultCount => _searchResult?.totalResults ?? 0;

  /// Get platform count
  int get platformCount => _searchResult?.platformCount ?? 0;

  bool _hasStorageHint(String query) {
    final q = query.toLowerCase();
    return RegExp(r'\d+\s?gb').hasMatch(q);
  }

  /// Search products
  Future<void> searchProducts(String query) async {
    final normalizedQuery = query.trim();

    if (normalizedQuery.isEmpty) {
      _error = 'Please enter a search query';
      notifyListeners();
      return;
    }

    if (!_hasStorageHint(normalizedQuery)) {
      _error = 'Please include storage in query (e.g., iPhone 16 Pro 256GB).';
      notifyListeners();
      return;
    }

    _isLoading = true;
    _error = null;
    _lastQuery = normalizedQuery;
    notifyListeners();

    try {
      _searchResult = await _apiService.searchProducts(query: normalizedQuery);
      if (_searchResult == null || _searchResult!.products.isEmpty) {
        _searchResult = await _apiService.compareProducts(query: normalizedQuery);
      }
      _error = null;
    } catch (e) {
      _error = e.toString();
      _searchResult = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Compare products (more detailed search)
  Future<void> compareProducts(String query) async {
    if (query.trim().isEmpty) {
      _error = 'Please enter a search query';
      notifyListeners();
      return;
    }

    _isLoading = true;
    _error = null;
    _lastQuery = query;
    notifyListeners();

    try {
      _searchResult = await _apiService.compareProducts(query: query);
      _error = null;
    } catch (e) {
      _error = e.toString();
      _searchResult = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Clear search results
  void clearSearch() {
    _searchResult = null;
    _error = null;
    _lastQuery = '';
    notifyListeners();
  }

  /// Retry last search
  Future<void> retrySearch() async {
    if (_lastQuery.isEmpty) return;
    await searchProducts(_lastQuery);
  }

  /// Get best deal product
  Product? getBestDeal() => _searchResult?.bestDeal;

  /// Get products sorted by price
  List<Product> getProductsSortedByPrice() {
    if (_searchResult == null) return [];
    return List.from(_searchResult!.products)
      ..sort((a, b) => a.price.compareTo(b.price));
  }

  /// Get products by platform
  Map<String, List<Product>> getProductsByPlatform() {
    if (_searchResult == null) return {};
    
    final grouped = <String, List<Product>>{};
    for (final product in _searchResult!.products) {
      grouped.putIfAbsent(product.platform, () => []);
      grouped[product.platform]!.add(product);
    }
    return grouped;
  }

  /// Get lowest price
  double? getLowestPrice() => _searchResult?.lowestPrice;

  /// Get highest price
  double? getHighestPrice() => _searchResult?.highestPrice;

  /// Get price range
  double? getPriceRange() => _searchResult?.priceRange;
}
