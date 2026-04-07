/// CompareKart API Service
/// Handles all HTTP communication with the backend

import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter/foundation.dart';
import '../models/product_model.dart';
import 'package:logger/logger.dart';

class ApiService {
  late final Dio _dio;
  late final String _baseUrl;
  late final Logger _logger;

  ApiService() {
    _logger = Logger();

    // Get base URL from environment or use sensible defaults.
    // Android emulators must use 10.0.2.2 to reach host machine localhost.
    // On web, .env may be absent; avoid crashing when dotenv isn't initialized.
    var resolvedBaseUrl = 'http://127.0.0.1:8000';
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      resolvedBaseUrl = 'http://10.0.2.2:8000';
    }
    try {
      final envBaseUrl = dotenv.env['API_BASE_URL'];
      if (envBaseUrl != null && envBaseUrl.trim().isNotEmpty) {
        resolvedBaseUrl = envBaseUrl;
      }
    } catch (_) {
      // Keep default URL when dotenv is unavailable.
    }
    _baseUrl = resolvedBaseUrl.replaceAll(RegExp(r'/+$'), '');

    _dio = Dio(
      BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: const Duration(seconds: 20),
        receiveTimeout: const Duration(seconds: 60),
        sendTimeout: const Duration(seconds: 20),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add logging interceptor
    _dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        logPrint: (log) => _logger.d(log),
      ),
    );
  }

  /// Health check
  Future<bool> healthCheck() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (e) {
      _logger.e('Health check failed: $e');
      return false;
    }
  }

  /// Search products across all platforms
  Future<ComparisonResult> searchProducts({
    required String query,
    int limit = 30,
  }) async {
    try {
      _logger.i('Searching products: $query');

      final response = await _dio.get(
        '/api/products/search',
        queryParameters: {
          'query': query,
          'limit': limit,
        },
      );

      if (response.statusCode == 200) {
        return ComparisonResult.fromApiResponse(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message: 'Search failed',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      _logger.e('Search error: ${e.message}');
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Search failed'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  /// Compare products with detailed metrics
  Future<ComparisonResult> compareProducts({
    required String query,
    int limit = 20,
  }) async {
    try {
      _logger.i('Comparing products: $query');

      final response = await _dio.get(
        '/api/products/compare',
        queryParameters: {
          'query': query,
          'limit': limit,
        },
      );

      if (response.statusCode == 200) {
        return ComparisonResult.fromApiResponse(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message: 'Comparison failed',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      _logger.e('Comparison error: ${e.message}');
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Comparison failed'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  /// Get product details by ID
  Future<Product> getProductDetails(int productId) async {
    try {
      _logger.i('Getting product details: $productId');

      final response = await _dio.get('/api/products/$productId');

      if (response.statusCode == 200) {
        return Product.fromJson(response.data as Map<String, dynamic>);
      } else {
        throw ApiException(
          message: 'Failed to get product details',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      _logger.e('Get product error: ${e.message}');
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Failed to get product'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  /// Get detailed comparison for a product
  Future<DetailedComparison> getProductComparison(int productId) async {
    try {
      _logger.i('Getting product comparison: $productId');

      final response = await _dio.get('/api/products/$productId/comparison');

      if (response.statusCode == 200) {
        return DetailedComparison.fromJson(
          response.data as Map<String, dynamic>,
        );
      } else {
        throw ApiException(
          message: 'Failed to get product comparison',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      _logger.e('Get comparison error: ${e.message}');
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Failed to get comparison'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  /// Get trending products by platform
  Future<List<Product>> getTrendingByPlatform({
    required String platform,
    int limit = 10,
  }) async {
    try {
      _logger.i('Getting trending for platform: $platform');

      final response = await _dio.get(
        '/api/products/platform/$platform/trending',
        queryParameters: {'limit': limit},
      );

      if (response.statusCode == 200) {
        final list = response.data as List;
        return list.map((item) => Product.fromJson(item as Map<String, dynamic>)).toList();
      } else {
        throw ApiException(
          message: 'Failed to get trending',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      _logger.e('Get trending error: ${e.message}');
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Failed to get trending'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  /// Get search history
  Future<List<SearchHistoryItem>> getSearchHistory({int limit = 20}) async {
    try {
      _logger.i('Getting search history');

      final response = await _dio.get(
        '/api/products/stats/search-history',
        queryParameters: {'limit': limit},
      );

      if (response.statusCode == 200) {
        final list = response.data as List;
        return list.map((item) => SearchHistoryItem.fromJson(item as Map<String, dynamic>)).toList();
      } else {
        throw ApiException(
          message: 'Failed to get search history',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      _logger.e('Get history error: ${e.message}');
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Failed to get history'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  String _extractErrorMessage(DioException e, {required String fallback}) {
    if (e.type == DioExceptionType.connectionError) {
      return 'Cannot connect to backend at $_baseUrl. Ensure backend is running on port 8000.';
    }
    if (e.type == DioExceptionType.receiveTimeout) {
      return 'Search is taking longer than expected. Try a more specific query like "iPhone 16 Pro 256GB".';
    }

    final data = e.response?.data;
    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail != null && detail.toString().trim().isNotEmpty) {
        return detail.toString();
      }
    }
    if (data is String && data.trim().isNotEmpty) {
      return data;
    }
    return e.message ?? fallback;
  }

  /// Register new user account
  Future<Map<String, dynamic>> registerUser({
    required String userId,
    required String password,
    String? fullName,
    String? email,
  }) async {
    try {
      final response = await _dio.post(
        '/api/auth/register',
        data: {
          'user_id': userId,
          'password': password,
          'full_name': fullName,
          'email': email,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      }

      throw ApiException(
        message: 'Registration failed',
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Registration failed'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  /// Login user account
  Future<Map<String, dynamic>> loginUser({
    required String userId,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/api/auth/login',
        data: {
          'user_id': userId,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      }

      throw ApiException(
        message: 'Login failed',
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Login failed'),
        statusCode: e.response?.statusCode,
      );
    }
  }

  /// Fetch user profile by user ID
  Future<Map<String, dynamic>> getUserProfile(String userId) async {
    try {
      final response = await _dio.get('/api/auth/profile/$userId');
      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      }
      throw ApiException(
        message: 'Failed to fetch profile',
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      throw ApiException(
        message: _extractErrorMessage(e, fallback: 'Failed to fetch profile'),
        statusCode: e.response?.statusCode,
      );
    }
  }
}

/// Custom exception for API errors
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException({required this.message, this.statusCode});

  @override
  String toString() => 'ApiException: $message (Status: $statusCode)';
}
