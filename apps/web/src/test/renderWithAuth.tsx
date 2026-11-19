import { render } from '@testing-library/react';
import type { ReactElement } from 'react';
import { MemoryRouter } from 'react-router';
import { vi } from 'vitest';
import { AuthContext, type AuthState } from '../auth/AuthContext';

/** Render inside a router with a fake auth state. Returns that state so tests
 * can assert on login/logout calls. */
export function renderWithAuth(
  ui: ReactElement,
  { auth = {}, route = '/' }: { auth?: Partial<AuthState>; route?: string } = {},
) {
  const state: AuthState = {
    status: 'anonymous',
    user: null,
    login: vi.fn(),
    logout: vi.fn(),
    getAccessToken: vi.fn().mockResolvedValue('test-token'),
    ...auth,
  };
  render(
    <MemoryRouter initialEntries={[route]}>
      <AuthContext.Provider value={state}>{ui}</AuthContext.Provider>
    </MemoryRouter>,
  );
  return state;
}
