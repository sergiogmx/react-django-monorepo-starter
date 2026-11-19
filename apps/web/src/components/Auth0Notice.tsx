export function Auth0Notice() {
  return (
    <div
      role="note"
      className="rounded-lg border border-neutral-200 bg-white p-4 text-neutral-700"
    >
      <p className="font-medium text-neutral-900">Auth0 is not configured</p>
      <p className="mt-1 text-sm">
        Fill the <code>VITE_AUTH0_*</code> and <code>AUTH0_*</code> variables in{' '}
        <code>.env</code> and restart with <code>make restart</code>. See{' '}
        <code>docs/auth0-setup.md</code>.
      </p>
    </div>
  );
}
