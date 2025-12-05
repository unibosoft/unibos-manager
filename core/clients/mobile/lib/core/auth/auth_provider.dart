import 'package:flutter_riverpod/flutter_riverpod.dart';

/// auth state
enum AuthStatus {
  initial,
  authenticated,
  unauthenticated,
  loading,
}

class AuthState {
  final AuthStatus status;
  final String? userId;
  final String? username;
  final String? errorMessage;

  const AuthState({
    required this.status,
    this.userId,
    this.username,
    this.errorMessage,
  });

  const AuthState.initial()
      : status = AuthStatus.initial,
        userId = null,
        username = null,
        errorMessage = null;

  const AuthState.loading()
      : status = AuthStatus.loading,
        userId = null,
        username = null,
        errorMessage = null;

  AuthState copyWith({
    AuthStatus? status,
    String? userId,
    String? username,
    String? errorMessage,
  }) {
    return AuthState(
      status: status ?? this.status,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      errorMessage: errorMessage,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
}

/// auth state provider
final authStateProvider = StateNotifierProvider<AuthStateNotifier, AuthState>(
  (ref) => AuthStateNotifier(),
);

class AuthStateNotifier extends StateNotifier<AuthState> {
  AuthStateNotifier() : super(const AuthState.initial());

  void setLoading() {
    state = const AuthState.loading();
  }

  void setAuthenticated({
    required String userId,
    required String username,
  }) {
    state = AuthState(
      status: AuthStatus.authenticated,
      userId: userId,
      username: username,
    );
  }

  void setUnauthenticated({String? errorMessage}) {
    state = AuthState(
      status: AuthStatus.unauthenticated,
      errorMessage: errorMessage,
    );
  }

  void clearError() {
    state = state.copyWith(errorMessage: null);
  }
}
