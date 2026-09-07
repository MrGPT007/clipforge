/** ClipForge Design System token names for tooling, agents, and typed consumers. */
export const clipForgeTokens = {
  color: {
    background: "var(--background)", foreground: "var(--foreground)", card: "var(--card)",
    primary: "var(--primary)", secondary: "var(--secondary)", muted: "var(--muted)",
    accent: "var(--accent)", destructive: "var(--destructive)", border: "var(--border)",
    ring: "var(--ring)", success: "var(--success)", warning: "var(--warning)", info: "var(--info)",
  },
  typography: {
    xs: "var(--text-xs)", sm: "var(--text-sm)", base: "var(--text-base)", md: "var(--text-md)",
    lg: "var(--text-lg)", xl: "var(--text-xl)", "2xl": "var(--text-2xl)", "3xl": "var(--text-3xl)",
  },
  space: {
    1: "var(--space-1)", 2: "var(--space-2)", 3: "var(--space-3)", 4: "var(--space-4)",
    5: "var(--space-5)", 6: "var(--space-6)", 8: "var(--space-8)", 10: "var(--space-10)", 12: "var(--space-12)",
  },
  radius: { xs: "var(--radius-xs)", sm: "var(--radius-sm)", md: "var(--radius-md)", lg: "var(--radius-lg)", xl: "var(--radius-xl)" },
  shadow: { xs: "var(--shadow-xs)", sm: "var(--shadow-sm)", md: "var(--shadow-md)", lg: "var(--shadow-lg)", soft: "var(--shadow-soft)" },
  motion: { fast: "var(--duration-fast)", base: "var(--duration-base)", slow: "var(--duration-slow)", standard: "var(--ease-standard)", emphasized: "var(--ease-emphasized)" },
} as const;
export type ClipForgeTokenGroup = keyof typeof clipForgeTokens;
