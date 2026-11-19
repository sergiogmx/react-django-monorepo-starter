import { useEffect, useState } from 'react';
import { useApiFetch } from '../api/client';
import { fetchMe, type UserProfile } from '../api/me';

type State =
  | { kind: 'loading' }
  | { kind: 'loaded'; profile: UserProfile }
  | { kind: 'error'; message: string };

export function ProfilePage() {
  const apiFetch = useApiFetch();
  const [state, setState] = useState<State>({ kind: 'loading' });

  useEffect(() => {
    let cancelled = false;
    fetchMe(apiFetch)
      .then((profile) => !cancelled && setState({ kind: 'loaded', profile }))
      .catch(
        (error: Error) =>
          !cancelled && setState({ kind: 'error', message: error.message }),
      );
    return () => {
      cancelled = true;
    };
  }, [apiFetch]);

  return (
    <>
      <h1 className="text-3xl font-semibold">Your profile</h1>
      <p className="text-neutral-700">
        Returned by <code>GET /api/me/</code>, using your Auth0 access token.
      </p>

      {state.kind === 'loading' && <p>Loading your profile…</p>}
      {state.kind === 'error' && (
        <p role="alert" className="text-danger-600">
          Could not load your profile: {state.message}
        </p>
      )}
      {state.kind === 'loaded' && (
        <dl className="grid grid-cols-[max-content_1fr] gap-x-6 gap-y-2 rounded-lg border border-neutral-200 bg-white p-4">
          <dt className="text-neutral-500">ID</dt>
          <dd>{state.profile.id}</dd>
          <dt className="text-neutral-500">Auth0 subject</dt>
          <dd className="font-mono text-sm">{state.profile.subject}</dd>
          <dt className="text-neutral-500">Email</dt>
          <dd>{state.profile.email ?? '—'}</dd>
          <dt className="text-neutral-500">Member since</dt>
          <dd>{new Date(state.profile.created_at).toLocaleDateString()}</dd>
        </dl>
      )}
    </>
  );
}
