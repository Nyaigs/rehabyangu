import { useAuth } from '../../context/AuthContext';

export function AppFooter() {
  const { tenantBranding, tenantName } = useAuth();
  const year = new Date().getFullYear();
  const footerText = tenantBranding?.footer_text?.trim();

  return <footer className="flex flex-col gap-1 border-t border-border px-4 py-4 text-caption font-medium normal-case tracking-normal text-ink-secondary sm:flex-row sm:items-center sm:justify-between md:px-8"><span>{footerText || `© ${year} ${tenantName || 'RehabYangu'}`}</span><span>Powered by Weiraro Technologies</span></footer>;
}
