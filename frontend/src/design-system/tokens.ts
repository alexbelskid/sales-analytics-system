/**
 * UNIFIED DESIGN SYSTEM TOKENS
 * 
 * This file contains all design tokens for the application.
 * All components should reference these tokens for consistency.
 */

export const DesignTokens = {
  // ============================================
  // COLORS
  // ============================================
  colors: {
    // Background colors
    background: {
      primary: 'hsl(0, 0%, 4%)',        // #0A0A0A - Main app background
      secondary: 'hsl(0, 0%, 8%)',      // #141414 - Card/panel background
      tertiary: 'hsl(0, 0%, 12%)',      // #1F1F1F - Muted elements
      hover: 'rgba(255, 255, 255, 0.05)', // Hover state
    },

    // Text colors
    text: {
      primary: 'hsl(0, 0%, 100%)',      // #FFFFFF - Primary text
      secondary: 'hsl(0, 0%, 70%)',     // #B3B3B3 - Secondary text
      muted: 'hsl(0, 0%, 50%)',         // #808080 - Muted text
      disabled: 'hsl(0, 0%, 30%)',      // #4D4D4D - Disabled text
    },

    // Brand colors
    brand: {
      primary: 'hsl(348, 70%, 36%)',    // #9B1B30 - Burgundy accent
      primaryHover: 'hsl(348, 70%, 42%)', // Lighter burgundy
      secondary: 'hsl(0, 0%, 100%)',    // White
    },

    // Semantic colors
    semantic: {
      success: 'hsl(142, 71%, 45%)',    // #22C55E - Green
      successMuted: 'hsla(142, 71%, 45%, 0.1)',
      warning: 'hsl(38, 92%, 50%)',     // #F59E0B - Amber
      warningMuted: 'hsla(38, 92%, 50%, 0.1)',
      error: 'hsl(0, 80%, 55%)',        // #E33D3D - Red
      errorMuted: 'hsla(0, 80%, 55%, 0.1)',
      info: 'hsl(188, 78%, 41%)',       // #14B8A6 - Cyan
      infoMuted: 'hsla(188, 78%, 41%, 0.1)',
    },

    // Border colors
    border: {
      default: 'rgba(255, 255, 255, 0.08)',  // Subtle border
      muted: 'rgba(255, 255, 255, 0.05)',    // Very subtle
      emphasis: 'rgba(255, 255, 255, 0.12)', // More visible
      focus: 'hsl(348, 70%, 36%)',           // Focus state
    },

    // Glass effect colors
    glass: {
      surface: 'rgba(255, 255, 255, 0.02)',   // Glass background
      highlight: 'rgba(255, 255, 255, 0.05)', // Glass highlight
      border: 'rgba(255, 255, 255, 0.08)',    // Glass border
    },
  },

  // ============================================
  // TYPOGRAPHY
  // ============================================
  typography: {
    fontFamily: {
      sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif',
      mono: '"SF Mono", "Monaco", "Inconsolata", monospace',
    },

    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
    },

    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },

    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
    },

    letterSpacing: {
      tight: '-0.02em',
      normal: '0',
      wide: '0.02em',
    },
  },

  // ============================================
  // SPACING
  // ============================================
  spacing: {
    xs: '0.25rem',    // 4px
    sm: '0.5rem',     // 8px
    md: '1rem',       // 16px
    lg: '1.5rem',     // 24px
    xl: '2rem',       // 32px
    '2xl': '3rem',    // 48px
    '3xl': '4rem',    // 64px
  },

  // ============================================
  // BORDER RADIUS
  // ============================================
  borderRadius: {
    none: '0',
    sm: '0.5rem',      // 8px
    md: '0.75rem',     // 12px
    lg: '1rem',        // 16px
    xl: '1.5rem',      // 24px
    '2xl': '2rem',     // 32px
    '3xl': '2.5rem',   // 40px
    full: '9999px',    // Fully rounded
  },

  // ============================================
  // OPACITY
  // ============================================
  opacity: {
    disabled: 0.5,
    muted: 0.7,
    hover: 0.9,
    pressed: 0.8,
    glass: 0.02,
    glassBorder: 0.08,
    glassHighlight: 0.05,
  },

  // ============================================
  // SHADOWS
  // ============================================
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.5)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.6)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.7)',
    '2xl': '0 40px 80px -20px rgba(0, 0, 0, 0.8)',
    glass: '0 40px 80px -20px rgba(0, 0, 0, 0.8), inset 0 0 40px 0 rgba(255, 255, 255, 0.02)',
    glassHover: '0 50px 100px -20px rgba(0, 0, 0, 0.9), inset 0 0 60px 0 rgba(255, 255, 255, 0.04)',
    focus: '0 0 0 3px hsla(348, 70%, 36%, 0.3)',
  },

  // ============================================
  // TRANSITIONS
  // ============================================
  transitions: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '600ms',
    },

    timing: {
      default: 'cubic-bezier(0.4, 0, 0.2, 1)',
      smooth: 'cubic-bezier(0.2, 0.8, 0.2, 1)',  // Liquid smooth
      spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
    },
  },

  // ============================================
  // Z-INDEX
  // ============================================
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1100,
    overlay: 1200,
    modal: 1300,
    popover: 1400,
    toast: 1500,
  },

  // ============================================
  // COMPONENT SIZES
  // ============================================
  sizes: {
    button: {
      sm: { height: '36px', padding: '0 16px', fontSize: '0.875rem' },
      md: { height: '44px', padding: '0 24px', fontSize: '0.875rem' },
      lg: { height: '52px', padding: '0 32px', fontSize: '1rem' },
    },

    input: {
      sm: { height: '36px', padding: '0 12px', fontSize: '0.875rem' },
      md: { height: '44px', padding: '0 16px', fontSize: '0.875rem' },
      lg: { height: '52px', padding: '0 20px', fontSize: '1rem' },
    },
  },

  // ============================================
  // BACKDROP FILTERS
  // ============================================
  backdropFilters: {
    glass: 'blur(30px) saturate(100%)',
    heavy: 'blur(40px) saturate(120%)',
    light: 'blur(20px) saturate(100%)',
  },
} as const;

// Type exports for TypeScript
export type ColorToken = typeof DesignTokens.colors;
export type TypographyToken = typeof DesignTokens.typography;
export type SpacingToken = typeof DesignTokens.spacing;
