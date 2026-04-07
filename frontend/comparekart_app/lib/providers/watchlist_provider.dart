import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/product_model.dart';

class WatchlistProvider extends ChangeNotifier {
  final List<Product> _items = [];

  List<Product> get items => List.unmodifiable(_items);
  int get count => _items.length;

  WatchlistProvider() {
    _load();
  }

  bool contains(Product product) {
    final url = product.productUrl;
    return _items.any((p) => p.productUrl == url);
  }

  Future<void> toggle(Product product) async {
    final existingIndex = _items.indexWhere((p) => p.productUrl == product.productUrl);
    if (existingIndex >= 0) {
      _items.removeAt(existingIndex);
    } else {
      _items.insert(0, product);
    }
    await _persist();
    notifyListeners();
  }

  Future<void> remove(Product product) async {
    _items.removeWhere((p) => p.productUrl == product.productUrl);
    await _persist();
    notifyListeners();
  }

  Future<void> clear() async {
    _items.clear();
    await _persist();
    notifyListeners();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString('watchlist.items');
    if (raw == null || raw.isEmpty) return;

    try {
      final decoded = jsonDecode(raw) as List<dynamic>;
      _items
        ..clear()
        ..addAll(
          decoded
              .whereType<Map<String, dynamic>>()
              .map(Product.fromJson),
        );
      notifyListeners();
    } catch (_) {
      // Ignore malformed cache and continue.
    }
  }

  Future<void> _persist() async {
    final prefs = await SharedPreferences.getInstance();
    final payload = _items.map((e) => e.toJson()).toList();
    await prefs.setString('watchlist.items', jsonEncode(payload));
  }
}
