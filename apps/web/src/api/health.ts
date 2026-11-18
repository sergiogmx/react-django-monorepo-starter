export interface Health {
  status: 'ok' | 'error';
  database: 'up' | 'down';
}

export async function fetchHealth(): Promise<Health> {
  const response = await fetch('/api/health/');
  // A 503 still carries a valid health body; anything else is unexpected.
  if (!response.ok && response.status !== 503) {
    throw new Error(`Unexpected response: ${response.status}`);
  }
  return response.json();
}
