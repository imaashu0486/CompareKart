import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  bool _isAuthenticated = false;
  String? _error;

  String? _userId;
  String? _fullName;
  String? _email;

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  String? get error => _error;
  String? get userId => _userId;
  String? get fullName => _fullName;
  String? get email => _email;

  AuthProvider() {
    _restoreSession();
  }

  Future<void> _restoreSession() async {
    final prefs = await SharedPreferences.getInstance();
    final storedUserId = prefs.getString('auth.user_id');
    if (storedUserId == null || storedUserId.isEmpty) return;

    _userId = storedUserId;
    _fullName = prefs.getString('auth.full_name');
    _email = prefs.getString('auth.email');
    _isAuthenticated = true;
    notifyListeners();
  }

  Future<bool> login({required String userId, required String password}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.loginUser(userId: userId, password: password);
      final user = (response['user'] as Map<String, dynamic>?) ?? <String, dynamic>{};

      _userId = user['user_id']?.toString() ?? userId;
      _fullName = user['full_name']?.toString();
      _email = user['email']?.toString();
      _isAuthenticated = true;

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth.user_id', _userId!);
      if (_fullName != null) await prefs.setString('auth.full_name', _fullName!);
      if (_email != null) await prefs.setString('auth.email', _email!);

      return true;
    } catch (e) {
      _error = e.toString().replaceFirst('ApiException: ', '');
      _isAuthenticated = false;
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> register({
    required String userId,
    required String password,
    String? fullName,
    String? email,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.registerUser(
        userId: userId,
        password: password,
        fullName: fullName,
        email: email,
      );

      final user = (response['user'] as Map<String, dynamic>?) ?? <String, dynamic>{};
      _userId = user['user_id']?.toString() ?? userId;
      _fullName = user['full_name']?.toString() ?? fullName;
      _email = user['email']?.toString() ?? email;
      _isAuthenticated = true;

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth.user_id', _userId!);
      if (_fullName != null && _fullName!.isNotEmpty) {
        await prefs.setString('auth.full_name', _fullName!);
      }
      if (_email != null && _email!.isNotEmpty) {
        await prefs.setString('auth.email', _email!);
      }

      return true;
    } catch (e) {
      _error = e.toString().replaceFirst('ApiException: ', '');
      _isAuthenticated = false;
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth.user_id');
    await prefs.remove('auth.full_name');
    await prefs.remove('auth.email');

    _isAuthenticated = false;
    _userId = null;
    _fullName = null;
    _email = null;
    _error = null;
    notifyListeners();
  }
}
