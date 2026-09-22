/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'], content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {
    colors: {
      primary: { DEFAULT: '#1D5A70', hover: '#184A5C', subtle: '#E8F0F2', 50: '#EAF3F6', 100: '#DCE8EC', 600: '#1D5A70', 700: '#0F2E3D' },
      dark: { DEFAULT: '#0F2E3D', panel: '#0B2531' }, background: '#F4F6F7', surface: '#FFFFFF',
      accent: { DEFAULT: '#237A57', subtle: '#E7F3ED', 600: '#237A57', 700: '#1A5E42' }, warning: { DEFAULT: '#8A611F', subtle: '#FBF4E9' }, danger: { DEFAULT: '#8C3A2F', subtle: '#FAECEA' }, border: { DEFAULT: '#DCE2E4', strong: '#B9C3C6' }, ink: { primary: '#1A2B31', secondary: '#5B6B76', muted: '#738188' }, secondary: { 50: '#F5F6F7', 100: '#ECEEF0', 200: '#D3D7DB', 400: '#8F979F', 500: '#5B6B76', 600: '#3D454C', 700: '#2F363B', 800: '#1F2428' },
      card: { DEFAULT: 'hsl(var(--card))', foreground: 'hsl(var(--card-foreground))' }, popover: { DEFAULT: 'hsl(var(--popover))', foreground: 'hsl(var(--popover-foreground))' }, muted: { DEFAULT: 'hsl(var(--muted))', foreground: 'hsl(var(--muted-foreground))' }, input: 'hsl(var(--input))', ring: 'hsl(var(--ring))', foreground: 'hsl(var(--foreground))',
    },
    fontFamily: { sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'], numeric: ['IBM Plex Sans', 'sans-serif'] },
    fontSize: { display: ['34px', { lineHeight: '1.2', fontWeight: '700' }], 'page-title': ['28px', { lineHeight: '1.25', fontWeight: '700' }], 'section-title': ['21px', { lineHeight: '1.3', fontWeight: '700' }], 'component-title': ['17px', { lineHeight: '1.4', fontWeight: '600' }], body: ['15px', { lineHeight: '1.6' }], secondary: ['14px', { lineHeight: '1.55' }], caption: ['12px', { lineHeight: '1.4', fontWeight: '600', letterSpacing: '0.04em' }] },
    borderRadius: { card: '16px', btn: '10px', input: '10px' }, boxShadow: { card: '0 1px 2px rgba(15, 46, 61, .06), 0 1px 1px rgba(15, 46, 61, .04)', raised: '0 4px 12px rgba(15, 46, 61, .10)', dropdown: '0 4px 16px rgba(15, 46, 61, .08)', modal: '0 16px 48px rgba(0, 0, 0, .12)' },
  } }, plugins: [],
};
