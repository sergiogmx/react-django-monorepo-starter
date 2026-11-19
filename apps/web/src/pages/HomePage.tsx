import { Button } from '@starter/ui';
import { useCallback, useEffect, useState } from 'react';
import { fetchHealth, type Health } from '../api/health';
import { useAuth } from '../auth/AuthContext';
import { Auth0Notice } from '../components/Auth0Notice';

type State =
  { kind: 'loading' } | { kind: 'loaded'; health: Health } | { kind: 'unreachable' };

export function HomePage() {
  const auth = useAuth();
  const [state, setState] = useState<State>({ kind: 'loading' });

  const check = useCallback(() => {
    setState({ kind: 'loading' });
    fetchHealth()
      .then((health) => setState({ kind: 'loaded', health }))
      .catch(() => setState({ kind: 'unreachable' }));
  }, []);

  useEffect(check, [check]);

  return (
    <>
      <h1 className="text-3xl font-semibold">Full-stack starter</h1>
      <p className="text-neutral-700">
        React + TypeScript on the front, Django REST Framework with Clean Architecture on
        the back. This page checks that both sides are talking.
      </p>

      {auth.status === 'unconfigured' && <Auth0Notice />}

      <section
        className="rounded-lg border border-neutral-200 bg-white p-4"
        aria-live="polite"
      >
        <StatusLine state={state} />
      </section>

      <div>
        <Button onClick={check} disabled={state.kind === 'loading'}>
          Check again
        </Button>
      </div>
    </>
  );
}

function StatusLine({ state }: { state: State }) {
  if (state.kind === 'loading') return <p>Checking the API…</p>;
  if (state.kind === 'unreachable') {
    return <p className="text-danger-600">API unreachable. Is `make up` running?</p>;
  }
  const { status, database } = state.health;
  return (
    <p className={status === 'ok' ? 'text-success-600' : 'text-danger-600'}>
      API: {status} · Database: {database}
    </p>
  );
}
