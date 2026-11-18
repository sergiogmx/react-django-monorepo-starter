import { render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';

function mockFetch(response: Partial<Response>) {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response));
}

describe('App', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('shows the API and database status', async () => {
    mockFetch({
      ok: true,
      status: 200,
      json: async () => ({ status: 'ok', database: 'up' }),
    });
    render(<App />);
    expect(await screen.findByText('API: ok · Database: up')).toBeInTheDocument();
  });

  it('shows a degraded status when the database is down', async () => {
    mockFetch({
      ok: false,
      status: 503,
      json: async () => ({ status: 'error', database: 'down' }),
    });
    render(<App />);
    expect(await screen.findByText('API: error · Database: down')).toBeInTheDocument();
  });

  it('tells the user when the API is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('network')));
    render(<App />);
    expect(await screen.findByText(/API unreachable/)).toBeInTheDocument();
  });
});
