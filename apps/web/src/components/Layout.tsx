import { Outlet } from 'react-router';
import { Header } from './Header';

export function Layout() {
  return (
    <>
      <Header />
      <main className="mx-auto flex max-w-3xl flex-col gap-6 p-6">
        <Outlet />
      </main>
    </>
  );
}
