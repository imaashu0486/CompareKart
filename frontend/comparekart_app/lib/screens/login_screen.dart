import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _loginFormKey = GlobalKey<FormState>();
  final _registerFormKey = GlobalKey<FormState>();

  final _loginUserController = TextEditingController();
  final _loginPasswordController = TextEditingController();

  final _registerUserController = TextEditingController();
  final _registerPasswordController = TextEditingController();
  final _registerNameController = TextEditingController();
  final _registerEmailController = TextEditingController();

  @override
  void dispose() {
    _loginUserController.dispose();
    _loginPasswordController.dispose();
    _registerUserController.dispose();
    _registerPasswordController.dispose();
    _registerNameController.dispose();
    _registerEmailController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin(AuthProvider auth) async {
    if (!_loginFormKey.currentState!.validate()) return;
    await auth.login(
      userId: _loginUserController.text.trim(),
      password: _loginPasswordController.text,
    );
    if (!mounted || auth.error == null) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(auth.error!)));
  }

  Future<void> _handleRegister(AuthProvider auth) async {
    if (!_registerFormKey.currentState!.validate()) return;
    await auth.register(
      userId: _registerUserController.text.trim(),
      password: _registerPasswordController.text,
      fullName: _registerNameController.text.trim(),
      email: _registerEmailController.text.trim(),
    );
    if (!mounted || auth.error == null) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(auth.error!)));
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        return Scaffold(
          body: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [Color(0xFF0F172A), Color(0xFF1D4ED8), Color(0xFF38BDF8)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: SafeArea(
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 480),
                  child: Card(
                    margin: const EdgeInsets.all(16),
                    elevation: 14,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: DefaultTabController(
                        length: 2,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Text(
                              'CompareKart',
                              style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Smart comparison, smarter shopping',
                              style: TextStyle(color: Colors.grey[600]),
                            ),
                            const SizedBox(height: 16),
                            const TabBar(
                              tabs: [
                                Tab(text: 'Login'),
                                Tab(text: 'Register'),
                              ],
                            ),
                            const SizedBox(height: 12),
                            SizedBox(
                              height: 380,
                              child: TabBarView(
                                children: [
                                  Form(
                                    key: _loginFormKey,
                                    child: Column(
                                      children: [
                                        TextFormField(
                                          controller: _loginUserController,
                                          decoration: const InputDecoration(
                                            labelText: 'User ID',
                                            prefixIcon: Icon(Icons.person_outline),
                                          ),
                                          validator: (v) => (v == null || v.trim().length < 4)
                                              ? 'User ID must be at least 4 characters'
                                              : null,
                                        ),
                                        const SizedBox(height: 12),
                                        TextFormField(
                                          controller: _loginPasswordController,
                                          obscureText: true,
                                          decoration: const InputDecoration(
                                            labelText: 'Password',
                                            prefixIcon: Icon(Icons.lock_outline),
                                          ),
                                          validator: (v) => (v == null || v.length < 6)
                                              ? 'Password must be at least 6 characters'
                                              : null,
                                        ),
                                        const SizedBox(height: 18),
                                        SizedBox(
                                          width: double.infinity,
                                          child: ElevatedButton.icon(
                                            onPressed: auth.isLoading ? null : () => _handleLogin(auth),
                                            icon: auth.isLoading
                                                ? const SizedBox(
                                                    height: 16,
                                                    width: 16,
                                                    child: CircularProgressIndicator(strokeWidth: 2),
                                                  )
                                                : const Icon(Icons.login),
                                            label: const Text('Login'),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Form(
                                    key: _registerFormKey,
                                    child: ListView(
                                      children: [
                                        TextFormField(
                                          controller: _registerNameController,
                                          decoration: const InputDecoration(
                                            labelText: 'Full Name (optional)',
                                            prefixIcon: Icon(Icons.badge_outlined),
                                          ),
                                        ),
                                        const SizedBox(height: 10),
                                        TextFormField(
                                          controller: _registerEmailController,
                                          decoration: const InputDecoration(
                                            labelText: 'Email (optional)',
                                            prefixIcon: Icon(Icons.email_outlined),
                                          ),
                                        ),
                                        const SizedBox(height: 10),
                                        TextFormField(
                                          controller: _registerUserController,
                                          decoration: const InputDecoration(
                                            labelText: 'User ID',
                                            prefixIcon: Icon(Icons.person_outline),
                                          ),
                                          validator: (v) => (v == null || v.trim().length < 4)
                                              ? 'User ID must be at least 4 characters'
                                              : null,
                                        ),
                                        const SizedBox(height: 10),
                                        TextFormField(
                                          controller: _registerPasswordController,
                                          obscureText: true,
                                          decoration: const InputDecoration(
                                            labelText: 'Password',
                                            prefixIcon: Icon(Icons.lock_outline),
                                          ),
                                          validator: (v) => (v == null || v.length < 6)
                                              ? 'Password must be at least 6 characters'
                                              : null,
                                        ),
                                        const SizedBox(height: 18),
                                        SizedBox(
                                          width: double.infinity,
                                          child: ElevatedButton.icon(
                                            onPressed: auth.isLoading ? null : () => _handleRegister(auth),
                                            icon: auth.isLoading
                                                ? const SizedBox(
                                                    height: 16,
                                                    width: 16,
                                                    child: CircularProgressIndicator(strokeWidth: 2),
                                                  )
                                                : const Icon(Icons.person_add_alt_1),
                                            label: const Text('Create Account'),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
