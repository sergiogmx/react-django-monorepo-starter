import { Auth0Provider, useAuth0, type AppState } from '@auth0/auth0-react';
import { useMemo, type ReactNode } from 'react';
import { useNavigate } from 'react-router';
import { AuthContext, unconfiguredAuth, type AuthState } from './AuthContext';
import { auth0Config } from './config';

/** Must be rendered inside the router: it navigates after the login redirect. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();

  if (!auth0Config) {
    return (
      <AuthContext.Provider value={unconfiguredAuth}>{children}</AuthContext.Provider>
    );
  }

  return (
    <Auth0Provider
      domain={auth0Config.domain}
      clientId={auth0Config.clientId}
      authorizationParams={{
        redirect_uri: window.location.origin,
        audience: auth0Config.audience,
      }}
      // Rotating refresh tokens keep the session across reloads in browsers
      // that block third-party cookies. See docs/decisions/0003-auth0.md.
      useRefreshTokens
      cacheLocation="localstorage"
      onRedirectCallback={(appState?: AppState) =>
        navigate(appState?.returnTo ?? '/', { replace: true })
      }
    >
      <Auth0Bridge>{children}</Auth0Bridge>
    </Auth0Provider>
  );
}

function Auth0Bridge({ children }: { children: ReactNode }) {
  const {
    isLoading,
    isAuthenticated,
    user,
    error,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
  } = useAuth0();

  const value = useMemo<AuthState>(
    () => ({
      status: isLoading ? 'loading' : isAuthenticated ? 'authenticated' : 'anonymous',
      user: user ? { name: user.name, email: user.email } : null,
      error: error?.message,
      login: ({ returnTo, signUp } = {}) =>
        void loginWithRedirect({
          appState: { returnTo },
          authorizationParams: signUp ? { screen_hint: 'signup' } : undefined,
        }),
      logout: () => void logout({ logoutParams: { returnTo: window.location.origin } }),
      getAccessToken: async () => {
        const token = await getAccessTokenSilently();
        if (!token) throw new Error('Auth0 returned no access token');
        return token;
      },
    }),
    [
      isLoading,
      isAuthenticated,
      user,
      error,
      loginWithRedirect,
      logout,
      getAccessTokenSilently,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
