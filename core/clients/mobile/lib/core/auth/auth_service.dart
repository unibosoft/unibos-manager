import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';
import 'token_storage.dart';
import 'auth_provider.dart';

/// auth service provider
final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(ref);
});

/// authentication service
class AuthService {
  final Ref _ref;

  AuthService(this._ref);

  ApiClient get _apiClient => _ref.read(apiClientProvider);
  TokenStorage get _tokenStorage => _ref.read(tokenStorageProvider);

  /// login with username and password
  Future<AuthResult> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
        Endpoints.login,
        data: {
          'username': username,
          'password': password,
        },
      );

      final accessToken = response['access'] as String?;
      final refreshToken = response['refresh'] as String?;
      final userId = response['user_id']?.toString();

      if (accessToken == null || refreshToken == null) {
        return AuthResult.failure('invalid response from server');
      }

      // save tokens
      await _tokenStorage.saveTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
        userId: userId,
        username: username,
      );

      // update auth state
      _ref.read(authStateProvider.notifier).setAuthenticated(
            userId: userId ?? '',
            username: username,
          );

      return AuthResult.success();
    } on ApiException catch (e) {
      return AuthResult.failure(e.message);
    } catch (e) {
      return AuthResult.failure('login failed: $e');
    }
  }

  /// register new user
  Future<AuthResult> register({
    required String username,
    required String email,
    required String password,
    required String passwordConfirm,
  }) async {
    try {
      await _apiClient.post<Map<String, dynamic>>(
        Endpoints.register,
        data: {
          'username': username,
          'email': email,
          'password': password,
          'password_confirm': passwordConfirm,
        },
      );

      // auto-login after registration
      return await login(username: username, password: password);
    } on ApiException catch (e) {
      return AuthResult.failure(e.message);
    } catch (e) {
      return AuthResult.failure('registration failed: $e');
    }
  }

  /// logout
  Future<void> logout() async {
    try {
      // try to logout on server (optional)
      await _apiClient.post(Endpoints.logout);
    } catch (e) {
      // ignore errors, clear local state anyway
    }

    // clear tokens
    await _tokenStorage.clearTokens();

    // update auth state
    _ref.read(authStateProvider.notifier).setUnauthenticated();
  }

  /// check if user is authenticated
  Future<bool> isAuthenticated() async {
    return await _tokenStorage.hasValidToken();
  }

  /// restore auth state from storage
  Future<void> restoreAuthState() async {
    final hasToken = await _tokenStorage.hasValidToken();
    if (hasToken) {
      final userId = await _tokenStorage.getUserId();
      final username = await _tokenStorage.getUsername();
      _ref.read(authStateProvider.notifier).setAuthenticated(
            userId: userId ?? '',
            username: username ?? '',
          );
    }
  }
}

/// result of auth operations
class AuthResult {
  final bool isSuccess;
  final String? errorMessage;

  AuthResult._({required this.isSuccess, this.errorMessage});

  factory AuthResult.success() => AuthResult._(isSuccess: true);
  factory AuthResult.failure(String message) =>
      AuthResult._(isSuccess: false, errorMessage: message);
}
