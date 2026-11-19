export interface Auth0Config {
  domain: string;
  clientId: string;
  audience: string;
}

type Env = Partial<
  Record<'VITE_AUTH0_DOMAIN' | 'VITE_AUTH0_CLIENT_ID' | 'VITE_AUTH0_AUDIENCE', string>
>;

/** Returns null when any variable is missing, so the app can run without Auth0. */
export function readAuth0Config(env: Env): Auth0Config | null {
  const domain = env.VITE_AUTH0_DOMAIN?.trim()
    .replace(/^https?:\/\//, '')
    .replace(/\/+$/, '');
  const clientId = env.VITE_AUTH0_CLIENT_ID?.trim();
  const audience = env.VITE_AUTH0_AUDIENCE?.trim();
  if (!domain || !clientId || !audience) return null;
  return { domain, clientId, audience };
}

export const auth0Config = readAuth0Config(import.meta.env);
