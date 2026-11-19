import { useCallback } from 'react';
import { useAuth } from '../auth/AuthContext';

export type ApiFetch = (path: string, init?: RequestInit) => Promise<Response>;

/** `fetch` for protected endpoints: adds `Authorization: Bearer <token>`. */
export function useApiFetch(): ApiFetch {
  const { getAccessToken } = useAuth();

  return useCallback(
    async (path, init = {}) => {
      const token = await getAccessToken();
      const headers = new Headers(init.headers);
      headers.set('Authorization', `Bearer ${token}`);
      return fetch(path, { ...init, headers });
    },
    [getAccessToken],
  );
}
