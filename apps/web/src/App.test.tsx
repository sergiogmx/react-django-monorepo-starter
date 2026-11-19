import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';
import { renderWithAuth } from './test/renderWithAuth';

function mockFetch(response: Partial<Response>) {
  const fetchMock = vi.fn().mockResolvedValue(response);
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

const healthy = {
  ok: true,
  status: 200,
  json: async () => ({ status: 'ok', database: 'up' }),
};

afterEach(() => vi.unstubAllGlobals());

describe('Home page health check', () => {
  it('shows the API and database status', async () => {
    mockFetch(healthy);
    renderWithAuth(<App />);
    expect(await screen.findByText('API: ok · Database: up')).toBeInTheDocument();
  });

  it('shows a degraded status when the database is down', async () => {
    mockFetch({
      ok: false,
      status: 503,
      json: async () => ({ status: 'error', database: 'down' }),
    });
    renderWithAuth(<App />);
    expect(await screen.findByText('API: error · Database: down')).toBeInTheDocument();
  });

  it('tells the user when the API is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('network')));
    renderWithAuth(<App />);
    expect(await screen.findByText(/API unreachable/)).toBeInTheDocument();
  });
});

describe('Header', () => {
  beforeEach(() => mockFetch(healthy));

  it('offers log in and sign up to anonymous users', async () => {
    const auth = renderWithAuth(<App />);

    await userEvent.click(screen.getByRole('button', { name: 'Log in' }));
    await userEvent.click(screen.getByRole('button', { name: 'Sign up' }));

    expect(auth.login).toHaveBeenNthCalledWith(1);
    expect(auth.login).toHaveBeenNthCalledWith(2, { signUp: true });
  });

  it('shows the user and a log out button when authenticated', async () => {
    const auth = renderWithAuth(<App />, {
      auth: { status: 'authenticated', user: { email: 'ana@example.com' } },
    });

    expect(screen.getByText('ana@example.com')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Log in' })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Log out' }));
    expect(auth.logout).toHaveBeenCalledOnce();
  });

  it('shows a notice instead of log in when Auth0 is not configured', () => {
    renderWithAuth(<App />, { auth: { status: 'unconfigured' } });

    expect(screen.getByText('Auth0 is not configured')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Log in' })).not.toBeInTheDocument();
  });

  it('shows login errors from the identity provider', () => {
    renderWithAuth(<App />, { auth: { error: 'Service not found' } });

    expect(screen.getByRole('alert')).toHaveTextContent('Service not found');
  });
});

describe('Profile page', () => {
  it('sends anonymous users to login and back to /profile', () => {
    mockFetch(healthy);
    const auth = renderWithAuth(<App />, { route: '/profile' });

    expect(auth.login).toHaveBeenCalledWith({ returnTo: '/profile' });
    expect(screen.getByText('Redirecting to login…')).toBeInTheDocument();
  });

  it('loads the profile with the access token', async () => {
    const fetchMock = mockFetch({
      ok: true,
      status: 200,
      json: async () => ({
        id: 7,
        subject: 'auth0|ana',
        email: 'ana@example.com',
        created_at: '2026-11-18T10:00:00Z',
      }),
    });

    renderWithAuth(<App />, {
      route: '/profile',
      auth: { status: 'authenticated', user: { email: 'ana@example.com' } },
    });

    expect(await screen.findByText('auth0|ana')).toBeInTheDocument();
    const [path, init] = fetchMock.mock.calls[0];
    expect(path).toBe('/api/me/');
    expect(new Headers(init.headers).get('Authorization')).toBe('Bearer test-token');
  });

  it('shows an error when the API rejects the token', async () => {
    mockFetch({ ok: false, status: 401 });

    renderWithAuth(<App />, { route: '/profile', auth: { status: 'authenticated' } });

    expect(await screen.findByRole('alert')).toHaveTextContent('401');
  });
});
