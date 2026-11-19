import { Button } from '@starter/ui';
import { NavLink } from 'react-router';
import { useAuth } from '../auth/AuthContext';

const linkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'font-medium text-primary-700' : 'text-neutral-700 hover:text-neutral-900';

export function Header() {
  const auth = useAuth();

  return (
    <header className="border-b border-neutral-200 bg-white">
      <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 p-4">
        <nav className="flex gap-4">
          <NavLink to="/" end className={linkClass}>
            Home
          </NavLink>
          <NavLink to="/profile" className={linkClass}>
            Profile
          </NavLink>
        </nav>

        <div className="flex items-center gap-3">
          {auth.status === 'authenticated' && (
            <>
              <span className="text-sm text-neutral-700">
                {auth.user?.name ?? auth.user?.email}
              </span>
              <Button variant="secondary" size="sm" onClick={() => auth.logout()}>
                Log out
              </Button>
            </>
          )}
          {auth.status === 'anonymous' && (
            <>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => auth.login({ signUp: true })}
              >
                Sign up
              </Button>
              <Button size="sm" onClick={() => auth.login()}>
                Log in
              </Button>
            </>
          )}
        </div>
      </div>
      {auth.error && (
        <p role="alert" className="mx-auto max-w-3xl px-4 pb-3 text-sm text-danger-600">
          Login error: {auth.error}
        </p>
      )}
    </header>
  );
}
