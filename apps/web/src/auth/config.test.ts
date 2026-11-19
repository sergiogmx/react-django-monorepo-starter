import { describe, expect, it } from 'vitest';
import { readAuth0Config } from './config';

const complete = {
  VITE_AUTH0_DOMAIN: 'tenant.us.auth0.com',
  VITE_AUTH0_CLIENT_ID: 'client-123',
  VITE_AUTH0_AUDIENCE: 'https://api.starter.local',
};

describe('readAuth0Config', () => {
  it('returns the config when every variable is set', () => {
    expect(readAuth0Config(complete)).toEqual({
      domain: 'tenant.us.auth0.com',
      clientId: 'client-123',
      audience: 'https://api.starter.local',
    });
  });

  it.each(['VITE_AUTH0_DOMAIN', 'VITE_AUTH0_CLIENT_ID', 'VITE_AUTH0_AUDIENCE'])(
    'returns null when %s is empty',
    (name) => {
      expect(readAuth0Config({ ...complete, [name]: ' ' })).toBeNull();
    },
  );

  it('accepts a domain pasted with https:// and a trailing slash', () => {
    const config = readAuth0Config({
      ...complete,
      VITE_AUTH0_DOMAIN: 'https://tenant.us.auth0.com/',
    });
    expect(config?.domain).toBe('tenant.us.auth0.com');
  });
});
