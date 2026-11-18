import type { GlobalProvider } from '@ladle/react';
import '../src/styles.css';

export const Provider: GlobalProvider = ({ children }) => (
  <div className="p-6 font-sans text-neutral-900">{children}</div>
);
