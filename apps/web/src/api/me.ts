import type { ApiFetch } from './client';

export interface UserProfile {
  id: number;
  subject: string;
  email: string | null;
  created_at: string;
}

export async function fetchMe(apiFetch: ApiFetch): Promise<UserProfile> {
  const response = await apiFetch('/api/me/');
  if (!response.ok) throw new Error(`GET /api/me/ failed with ${response.status}`);
  return response.json();
}
