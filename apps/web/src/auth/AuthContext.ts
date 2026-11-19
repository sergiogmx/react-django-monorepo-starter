import { createContext, useContext } from 'react';

// The app's own view of authentication. Components use `useAuth()` and never
// import the Auth0 SDK, so the provider can change without touching them.

export type AuthStatus = 'unconfigured' | 'loading' | 'anonymous' | 'authenticated';

export interface AuthUser {
  name?: string;
  email?: string;
}

export interface LoginOptions {
  /** Path to come back to after login. */
  returnTo?: string;
  /** Open Universal Login on the sign-up screen. */
  signUp?: boolean;
}

export interface AuthState {
  status: AuthStatus;
  user: AuthUser | null;
  /** Message from the identity provider, e.g. a misconfigured audience. */
  error?: string;
  login(options?: LoginOptions): void;
  logout(): void;
  getAccessToken(): Promise<string>;
}

export const AuthContext = createContext<AuthState | null>(null);

export const unconfiguredAuth: AuthState = {
  status: 'unconfigured',
  user: null,
  login: () => {},
  logout: () => {},
  getAccessToken: () => Promise.reject(new Error('Auth0 is not configured')),
};

export function useAuth(): AuthState {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error('useAuth must be used inside <AuthProvider>');
  return auth;
}
