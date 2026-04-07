/// Comparison Provider
/// Manages detailed product comparison

import 'package:flutter/material.dart';
import '../models/product_model.dart';
import '../services/api_service.dart';

class ComparisonProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  /// State variables
  DetailedComparison? _comparison;
  bool _isLoading = false;
  String? _error;
  int? _currentProductId;

  /// Getters
  DetailedComparison? get comparison => _comparison;
  bool get isLoading => _isLoading;
  String? get error => _error;
  int? get currentProductId => _currentProductId;

  /// Check if has comparison
  bool get hasComparison => _comparison != null;

  /// Get product count
  int get productCount => _comparison?.resultsCount ?? 0;

  /// Get platform count
  int get platformCount => _comparison?.platformsAvailable ?? 0;

  /// Load detailed comparison
  Future<void> loadComparison(int productId) async {
    _isLoading = true;
    _error = null;
    _currentProductId = productId;
    notifyListeners();

    try {
      _comparison = await _apiService.getProductComparison(productId);
      _error = null;
    } catch (e) {
      _error = e.toString();
      _comparison = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Clear comparison
  void clearComparison() {
    _comparison = null;
    _error = null;
    _currentProductId = null;
    notifyListeners();
  }

  /// Get average price
  double? getAveragePrice() => _comparison?.getAveragePrice();

  /// Get min price
  double? getMinPrice() => _comparison?.getMinPrice();

  /// Get max price
  double? getMaxPrice() => _comparison?.getMaxPrice();

  /// Get price savings
  double? getPriceSavings() {
    if (_comparison == null) return null;
    final minPrice = _comparison!.getMinPrice();
    final maxPrice = _comparison!.getMaxPrice();
    return maxPrice - minPrice;
  }

  /// Get discount percentage
  double? getDiscountPercentage() {
    if (_comparison == null) return null;
    final minPrice = _comparison!.getMinPrice();
    final maxPrice = _comparison!.getMaxPrice();
    if (maxPrice == 0) return 0;
    return ((maxPrice - minPrice) / maxPrice) * 100;
  }

  /// Get products by platform
  Map<String, Product?> getProductsByPlatform() {
    if (_comparison == null) return {};
    
    final mapped = <String, Product?>{};
    for (final product in _comparison!.products) {
      mapped[product.platform] = product;
    }
    return mapped;
  }

  /// Get cheapest product
  Product? getCheapestProduct() {
    if (_comparison == null || _comparison!.products.isEmpty) return null;
    
    Product cheapest = _comparison!.products.first;
    for (final product in _comparison!.products) {
      if (product.price < cheapest.price) {
        cheapest = product;
      }
    }
    return cheapest;
  }

  /// Get most expensive product
  Product? getMostExpensiveProduct() {
    if (_comparison == null || _comparison!.products.isEmpty) return null;
    
    Product mostExpensive = _comparison!.products.first;
    for (final product in _comparison!.products) {
      if (product.price > mostExpensive.price) {
        mostExpensive = product;
      }
    }
    return mostExpensive;
  }
}
