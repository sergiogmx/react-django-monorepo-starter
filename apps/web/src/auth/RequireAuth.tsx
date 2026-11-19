import { useEffect, type ReactNode } from 'react';
import { useLocation } from 'react-router';
import { Auth0Notice } from '../components/Auth0Notice';
import { useAuth } from './AuthContext';

/** Renders children only for logged-in users; sends everyone else to login
 * and brings them back to the same page afterwards. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const auth = useAuth();
  const { pathname, search } = useLocation();

  useEffect(() => {
    if (auth.status === 'anonymous') auth.login({ returnTo: pathname + search });
  }, [auth, pathname, search]);

  if (auth.status === 'authenticated') return children;
  if (auth.status === 'unconfigured') return <Auth0Notice />;
  return (
    <p className="text-neutral-700">
      {auth.status === 'loading' ? 'Loading…' : 'Redirecting to login…'}
    </p>
  );
}
