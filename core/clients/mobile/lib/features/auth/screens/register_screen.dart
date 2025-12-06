import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/auth/auth_service.dart';
import '../../../core/theme/colors.dart';
import '../../../core/router/app_router.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _passwordConfirmController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;
  bool _obscurePasswordConfirm = true;
  bool _acceptedTerms = false;
  String? _errorMessage;
  double _passwordStrength = 0;

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _passwordConfirmController.dispose();
    super.dispose();
  }

  void _updatePasswordStrength(String password) {
    double strength = 0;
    if (password.length >= 8) strength += 0.25;
    if (password.contains(RegExp(r'[a-z]')) &&
        password.contains(RegExp(r'[A-Z]'))) strength += 0.25;
    if (password.contains(RegExp(r'[0-9]'))) strength += 0.25;
    if (password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) strength += 0.25;

    setState(() {
      _passwordStrength = strength;
    });
  }

  Color _getStrengthColor() {
    if (_passwordStrength <= 0.25) return UnibosColors.danger;
    if (_passwordStrength <= 0.5) return UnibosColors.warning;
    if (_passwordStrength <= 0.75) return UnibosColors.orange;
    return UnibosColors.success;
  }

  String _getStrengthText() {
    if (_passwordStrength <= 0.25) return 'weak';
    if (_passwordStrength <= 0.5) return 'fair';
    if (_passwordStrength <= 0.75) return 'good';
    return 'strong';
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    if (!_acceptedTerms) {
      setState(() {
        _errorMessage = 'please accept the terms and conditions';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final authService = ref.read(authServiceProvider);
    final result = await authService.register(
      username: _usernameController.text.trim(),
      email: _emailController.text.trim(),
      password: _passwordController.text,
      passwordConfirm: _passwordConfirmController.text,
    );

    if (!mounted) return;

    setState(() {
      _isLoading = false;
    });

    if (result.isSuccess) {
      // Show success message and navigate to dashboard
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('account created successfully!'),
          backgroundColor: UnibosColors.success,
        ),
      );
      // AuthService auto-logs in after registration, so go to dashboard
      context.go(AppRoutes.dashboard);
    } else {
      setState(() {
        _errorMessage = result.errorMessage;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),

              // logo and title
              const Center(
                child: Text(
                  '🦄',
                  style: TextStyle(fontSize: 56),
                ),
              ),
              const SizedBox(height: 12),
              Text(
                'unibos',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                      color: UnibosColors.orange,
                      letterSpacing: 2,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'create your account',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: UnibosColors.gray,
                    ),
              ),
              const SizedBox(height: 32),

              // register form
              Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // error message
                    if (_errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: UnibosColors.danger.withValues(alpha: 0.1),
                          border: Border.all(color: UnibosColors.danger),
                          borderRadius: BorderRadius.circular(3),
                        ),
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(
                            color: UnibosColors.danger,
                            fontSize: 13,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // username field
                    Text(
                      'username',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _usernameController,
                      decoration: const InputDecoration(
                        hintText: 'choose a username',
                        prefixIcon: Icon(Icons.person_outline),
                      ),
                      textInputAction: TextInputAction.next,
                      autocorrect: false,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'username is required';
                        }
                        if (value.trim().length < 3) {
                          return 'username must be at least 3 characters';
                        }
                        if (!RegExp(r'^[a-zA-Z0-9_]+$').hasMatch(value)) {
                          return 'only letters, numbers, and underscore';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),

                    // email field
                    Text(
                      'email',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _emailController,
                      decoration: const InputDecoration(
                        hintText: 'your@email.com',
                        prefixIcon: Icon(Icons.email_outlined),
                      ),
                      textInputAction: TextInputAction.next,
                      keyboardType: TextInputType.emailAddress,
                      autocorrect: false,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'email is required';
                        }
                        if (!RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
                            .hasMatch(value)) {
                          return 'please enter a valid email';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 20),

                    // password field
                    Text(
                      'password',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _passwordController,
                      decoration: InputDecoration(
                        hintText: 'create a strong password',
                        prefixIcon: const Icon(Icons.lock_outline),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword
                                ? Icons.visibility_off
                                : Icons.visibility,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePassword = !_obscurePassword;
                            });
                          },
                        ),
                      ),
                      obscureText: _obscurePassword,
                      textInputAction: TextInputAction.next,
                      onChanged: _updatePasswordStrength,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'password is required';
                        }
                        if (value.length < 8) {
                          return 'password must be at least 8 characters';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 8),

                    // password strength indicator
                    if (_passwordController.text.isNotEmpty) ...[
                      Row(
                        children: [
                          Expanded(
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(2),
                              child: LinearProgressIndicator(
                                value: _passwordStrength,
                                backgroundColor:
                                    UnibosColors.gray.withValues(alpha: 0.3),
                                valueColor: AlwaysStoppedAnimation<Color>(
                                    _getStrengthColor()),
                                minHeight: 4,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            _getStrengthText(),
                            style: TextStyle(
                              fontSize: 12,
                              color: _getStrengthColor(),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                    ],
                    const SizedBox(height: 8),

                    // confirm password field
                    Text(
                      'confirm password',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _passwordConfirmController,
                      decoration: InputDecoration(
                        hintText: 'confirm your password',
                        prefixIcon: const Icon(Icons.lock_outline),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePasswordConfirm
                                ? Icons.visibility_off
                                : Icons.visibility,
                          ),
                          onPressed: () {
                            setState(() {
                              _obscurePasswordConfirm =
                                  !_obscurePasswordConfirm;
                            });
                          },
                        ),
                      ),
                      obscureText: _obscurePasswordConfirm,
                      textInputAction: TextInputAction.done,
                      onFieldSubmitted: (_) => _handleRegister(),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'please confirm your password';
                        }
                        if (value != _passwordController.text) {
                          return 'passwords do not match';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 20),

                    // terms checkbox
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SizedBox(
                          width: 24,
                          height: 24,
                          child: Checkbox(
                            value: _acceptedTerms,
                            onChanged: (value) {
                              setState(() {
                                _acceptedTerms = value ?? false;
                              });
                            },
                            activeColor: UnibosColors.orange,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: GestureDetector(
                            onTap: () {
                              setState(() {
                                _acceptedTerms = !_acceptedTerms;
                              });
                            },
                            child: Text(
                              'i agree to the terms of service and privacy policy',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(
                                    color: UnibosColors.gray,
                                  ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // register button
                    SizedBox(
                      height: 48,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _handleRegister,
                        child: _isLoading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: UnibosColors.bgBlack,
                                ),
                              )
                            : const Text('create account'),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // login link
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'already have an account?',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        TextButton(
                          onPressed: () {
                            context.go(AppRoutes.login);
                          },
                          child: const Text(
                            'login here',
                            style: TextStyle(
                              fontSize: 14,
                              color: UnibosColors.orange,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // server info
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.cloud_outlined,
                          size: 16,
                          color: UnibosColors.gray,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'recaria.org',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
