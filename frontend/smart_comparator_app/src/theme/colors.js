export const lightColors = {
  background: '#F6F7FB',
  card: '#FFFFFF',
  elevated: '#FFFFFF',
  primary: '#3B82F6',
  primaryDark: '#2563EB',
  success: '#16A34A',
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  border: '#E5E7EB',
  borderSubtle: 'rgba(17,24,39,0.08)',
  danger: '#DC2626',
  infoSurface: '#EEF4FF',
  shadow: '#0B1324',
  chipBg: '#EEF4FF',
  inputBg: '#F8FAFC',
  headerGradientStart: '#1F2937',
  headerGradientEnd: '#111827',
};

export const darkColors = {
  background: '#0F172A',
  card: '#111827',
  elevated: '#1F2937',
  primary: '#60A5FA',
  primaryDark: '#3B82F6',
  success: '#22C55E',
  textPrimary: '#F9FAFB',
  textSecondary: '#94A3B8',
  border: '#1F2937',
  borderSubtle: 'rgba(255,255,255,0.10)',
  danger: '#EF4444',
  infoSurface: '#172554',
  shadow: '#000000',
  chipBg: '#1E293B',
  inputBg: '#0B1220',
  headerGradientStart: '#111827',
  headerGradientEnd: '#0B1220',
};

export const colors = lightColors;

export const spacing = {
  xxs: 4,
  xs: 8,
  sm: 12,
  md: 16,
  lg: 24,
  xl: 24,
};

export const radius = {
  sm: 12,
  md: 16,
  lg: 24,
  xl: 24,
  pill: 999,
};

export const createTypography = (palette) => ({
  heading: { fontSize: 24, fontWeight: '700', color: palette.textPrimary },
  headingSmall: { fontSize: 22, fontWeight: '700', color: palette.textPrimary },
  title: { fontSize: 18, fontWeight: '600', color: palette.textPrimary },
  subtitle: { fontSize: 16, fontWeight: '500', color: palette.textSecondary },
  body: { fontSize: 14, color: palette.textPrimary },
  caption: { fontSize: 12, color: palette.textSecondary },
  price: { fontSize: 22, fontWeight: '700', color: palette.success },
});

export const typography = createTypography(lightColors);

export const createShadows = (palette) => ({
  card: {
    shadowColor: palette.shadow,
    shadowOpacity: 0.16,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 16,
    elevation: 4,
  },
  soft: {
    shadowColor: palette.shadow,
    shadowOpacity: 0.12,
    shadowOffset: { width: 0, height: 6 },
    shadowRadius: 12,
    elevation: 3,
  },
  glow: {
    shadowColor: palette.primary,
    shadowOpacity: 0.25,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 14,
    elevation: 5,
  },
});

export const shadows = createShadows(lightColors);

export function buildTheme(mode = 'light') {
  const palette = mode === 'dark' ? darkColors : lightColors;
  return {
    mode,
    colors: palette,
    spacing,
    radius,
    typography: createTypography(palette),
    shadows: createShadows(palette),
  };
}
