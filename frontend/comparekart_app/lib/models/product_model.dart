/// Data models for CompareKart API responses

class Product {
  final int? id;
  final String name;
  final String platform;
  final double price;
  final String? imageUrl;
  final String productUrl;
  final double? rating;
  final int? ratingCount;
  final String? description;
  final String? lastUpdated;
  final String? createdAt;

  Product({
    this.id,
    required this.name,
    required this.platform,
    required this.price,
    this.imageUrl,
    required this.productUrl,
    this.rating,
    this.ratingCount,
    this.description,
    this.lastUpdated,
    this.createdAt,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    final dynamic rawId = json['id'];
    final dynamic rawName = json['name'] ?? json['title'];
    final dynamic rawUrl = json['product_url'] ?? json['url'] ?? '';
    final dynamic rawPrice = json['price'];
    final dynamic rawRating = json['rating'];
    final dynamic rawRatingCount = json['rating_count'];

    return Product(
      id: rawId is int ? rawId : int.tryParse('$rawId'),
      name: (rawName ?? '').toString(),
      platform: (json['platform'] ?? '').toString(),
      price: rawPrice is num ? rawPrice.toDouble() : double.tryParse('$rawPrice') ?? 0,
      imageUrl: (json['image_url'] ?? json['imageUrl'])?.toString(),
      productUrl: rawUrl.toString(),
      rating: rawRating is num ? rawRating.toDouble() : double.tryParse('$rawRating'),
      ratingCount: rawRatingCount is int ? rawRatingCount : int.tryParse('$rawRatingCount'),
      description: json['description']?.toString(),
      lastUpdated: json['last_updated']?.toString(),
      createdAt: json['created_at']?.toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'platform': platform,
        'price': price,
        'image_url': imageUrl,
        'product_url': productUrl,
        'rating': rating,
        'rating_count': ratingCount,
        'description': description,
        'last_updated': lastUpdated,
        'created_at': createdAt,
      };

  /// Get platform color for UI badges
  String getPlatformColor() {
    switch (platform.toLowerCase()) {
      case 'amazon':
        return '#FF9800';
      case 'flipkart':
        return '#2874F0';
      case 'croma':
        return '#E12432';
      case 'ebay':
        return '#E53238';
      default:
        return '#666666';
    }
  }

  /// Check if product is best deal (lowest price)
  bool isBestDeal(double lowestPrice) => price == lowestPrice;
}

class ComparisonResult {
  final String query;
  final int totalResults;
  final int platformCount;
  final double lowestPrice;
  final double highestPrice;
  final double priceRange;
  final Product? bestDeal;
  final List<Product> products;

  ComparisonResult({
    required this.query,
    required this.totalResults,
    required this.platformCount,
    required this.lowestPrice,
    required this.highestPrice,
    required this.priceRange,
    this.bestDeal,
    required this.products,
  });

  factory ComparisonResult.fromJson(Map<String, dynamic> json) {
    final productsList = (json['products'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(Product.fromJson)
        .toList();

    final dynamic bestDealJson = json['best_deal'];

    return ComparisonResult(
      query: (json['query'] ?? '').toString(),
      totalResults: (json['total_results'] as num?)?.toInt() ?? productsList.length,
      platformCount: (json['platform_count'] as num?)?.toInt() ??
          productsList.map((p) => p.platform.toLowerCase()).toSet().length,
      lowestPrice: (json['lowest_price'] as num?)?.toDouble() ??
          (productsList.isEmpty ? 0 : productsList.map((p) => p.price).reduce((a, b) => a < b ? a : b)),
      highestPrice: (json['highest_price'] as num?)?.toDouble() ??
          (productsList.isEmpty ? 0 : productsList.map((p) => p.price).reduce((a, b) => a > b ? a : b)),
      priceRange: (json['price_range'] as num?)?.toDouble() ?? 0,
      bestDeal: bestDealJson is Map<String, dynamic> ? Product.fromJson(bestDealJson) : null,
      products: productsList,
    );
  }

  factory ComparisonResult.fromApiResponse(Map<String, dynamic> json) {
    // New grouped response shape from /api/products/search
    if (json['product_groups'] is List) {
      final groups = json['product_groups'] as List<dynamic>;
      final products = <Product>[];
      for (final group in groups) {
        if (group is Map<String, dynamic>) {
          final offers = group['offers'];
          if (offers is List) {
            for (final offer in offers.whereType<Map<String, dynamic>>()) {
              products.add(Product.fromJson(offer));
            }
          }
        }
      }

      products.sort((a, b) => a.price.compareTo(b.price));
      final lowest = products.isEmpty ? 0.0 : products.first.price;
      final highest = products.isEmpty ? 0.0 : products.last.price;

      return ComparisonResult(
        query: (json['query'] ?? '').toString(),
        totalResults: (json['total_offers'] as num?)?.toInt() ?? products.length,
        platformCount: products.map((p) => p.platform.toLowerCase()).toSet().length,
        lowestPrice: lowest,
        highestPrice: highest,
        priceRange: highest - lowest,
        bestDeal: products.isEmpty ? null : products.first,
        products: products,
      );
    }

    // Flat response shape from /api/products/compare
    return ComparisonResult.fromJson(json);
  }

  Map<String, dynamic> toJson() => {
        'query': query,
        'total_results': totalResults,
        'platform_count': platformCount,
        'lowest_price': lowestPrice,
        'highest_price': highestPrice,
        'price_range': priceRange,
        'best_deal': bestDeal?.toJson(),
        'products': products.map((p) => p.toJson()).toList(),
      };

  /// Get price difference between highest and lowest
  double getSavings(Product product) => highestPrice - product.price;

  /// Get discount percentage
  double getDiscountPercentage(Product product) {
    if (highestPrice == 0) return 0;
    return ((highestPrice - product.price) / highestPrice) * 100;
  }
}

class DetailedComparison {
  final String productName;
  final int resultsCount;
  final int platformsAvailable;
  final Map<String, dynamic> priceStats;
  final List<Product> products;

  DetailedComparison({
    required this.productName,
    required this.resultsCount,
    required this.platformsAvailable,
    required this.priceStats,
    required this.products,
  });

  factory DetailedComparison.fromJson(Map<String, dynamic> json) {
    final productsList = (json['products'] as List<dynamic>? ?? const [])
        .whereType<Map<String, dynamic>>()
        .map(Product.fromJson)
        .toList();

    return DetailedComparison(
      productName: (json['product_name'] ?? '').toString(),
      resultsCount: (json['results_count'] as num?)?.toInt() ?? productsList.length,
      platformsAvailable: (json['platforms_available'] as num?)?.toInt() ??
          productsList.map((p) => p.platform.toLowerCase()).toSet().length,
      priceStats: (json['price_stats'] as Map<String, dynamic>?) ?? <String, dynamic>{},
      products: productsList,
    );
  }

  Map<String, dynamic> toJson() => {
        'product_name': productName,
        'results_count': resultsCount,
        'platforms_available': platformsAvailable,
        'price_stats': priceStats,
        'products': products.map((p) => p.toJson()).toList(),
      };

  /// Get average price
  double getAveragePrice() =>
      (priceStats['avg'] as num?)?.toDouble() ?? 0.0;

  /// Get min price
  double getMinPrice() => (priceStats['min'] as num?)?.toDouble() ?? 0.0;

  /// Get max price
  double getMaxPrice() => (priceStats['max'] as num?)?.toDouble() ?? 0.0;
}

class SearchHistoryItem {
  final int id;
  final String query;
  final String timestamp;
  final int? resultsCount;

  SearchHistoryItem({
    required this.id,
    required this.query,
    required this.timestamp,
    this.resultsCount,
  });

  factory SearchHistoryItem.fromJson(Map<String, dynamic> json) => SearchHistoryItem(
        id: (json['id'] as num?)?.toInt() ?? 0,
        query: (json['query'] ?? '').toString(),
        timestamp: (json['timestamp'] ?? '').toString(),
        resultsCount: (json['results_count'] as num?)?.toInt(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'query': query,
        'timestamp': timestamp,
        'results_count': resultsCount,
      };
}

class ApiError {
  final bool error;
  final String detail;
  final int statusCode;

  ApiError({
    required this.error,
    required this.detail,
    required this.statusCode,
  });

  factory ApiError.fromJson(Map<String, dynamic> json) => ApiError(
        error: json['error'] == true,
        detail: (json['detail'] ?? '').toString(),
        statusCode: (json['status_code'] as num?)?.toInt() ?? 500,
      );

  Map<String, dynamic> toJson() => {
        'error': error,
        'detail': detail,
        'status_code': statusCode,
      };
}
