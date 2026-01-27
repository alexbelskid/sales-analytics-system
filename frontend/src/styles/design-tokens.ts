/**
 * KORTIX DESIGN SYSTEM - DESIGN TOKENS
 * Централизованная система дизайн-токенов для единообразия UI
 * 
 * Этот файл содержит все основные константы дизайна:
 * - Цвета и прозрачность
 * - Типографика (шрифты, размеры, веса)
 * - Spacing (отступы, gap)
 * - Border radius
 * - Тени и эффекты
 * - Анимации
 */

// ============================================
// ЦВЕТА И ПРОЗРАЧНОСТЬ
// ============================================

export const colors = {
  // Основные цвета приложения
  background: {
    primary: 'hsl(0, 0%, 4%)',      // #0A0A0A - основной фон
    secondary: 'hsl(0, 0%, 8%)',    // #141414 - карточки
    tertiary: 'hsl(0, 0%, 12%)',    // #1F1F1F - вторичные элементы
  },

  // Accent цвета (Rose/Burgundy)
  accent: {
    primary: 'hsl(348, 70%, 36%)',   // #9B1B30 - основной акцент
    hover: 'hsl(348, 70%, 40%)',     // Светлее для hover
    muted: 'hsl(348, 70%, 30%)',     // Темнее для активного состояния
  },

  // Текст
  text: {
    primary: 'hsl(0, 0%, 100%)',     // #FFFFFF - основной текст
    secondary: 'hsl(0, 0%, 70%)',    // #B3B3B3 - вторичный текст
    muted: 'hsl(0, 0%, 50%)',        // #808080 - приглушённый текст
    disabled: 'hsl(0, 0%, 30%)',     // #4D4D4D - disabled текст
  },

  // Статус-цвета
  status: {
    success: '#10b981',              // green-500
    error: '#ef4444',                // red-500
    warning: '#f59e0b',              // amber-500
    info: '#3b82f6',                 // blue-500
  },

  // Прозрачность (для glass-эффектов)
  glass: {
    surface: 'rgba(255, 255, 255, 0.02)',     // Поверхность
    surfaceHover: 'rgba(255, 255, 255, 0.05)', // Hover состояние
    border: 'rgba(255, 255, 255, 0.08)',      // Границы
    borderHover: 'rgba(255, 255, 255, 0.12)', // Границы при hover
    highlight: 'rgba(255, 255, 255, 0.05)',   // Подсветка
  },
} as const;

// ============================================
// ТИПОГРАФИКА
// ============================================

export const typography = {
  // Семейства шрифтов
  fontFamily: {
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif',
    mono: '"SF Mono", "Monaco", "Cascadia Code", "Roboto Mono", monospace',
  },

  // Размеры шрифтов (унифицированные)
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px - заголовки страниц
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
  },

  // Веса шрифтов (унифицированные)
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  // Line height
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },

  // Letter spacing
  letterSpacing: {
    tight: '-0.02em',
    normal: '0',
    wide: '0.05em',
  },
} as const;

// ============================================
// SPACING (ОТСТУПЫ)
// ============================================

export const spacing = {
  // Базовые отступы
  px: '1px',
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px

  // Семантические spacing
  card: {
    padding: '1.5rem',        // 24px - стандартный padding для карточек
    paddingCompact: '1rem',   // 16px - компактный padding
    gap: '1rem',              // 16px - gap между элементами в карточке
  },

  page: {
    padding: '1.5rem',        // 24px - padding страницы
    gap: '1.5rem',            // 24px - gap между секциями
  },

  component: {
    gap: '0.75rem',           // 12px - стандартный gap между элементами
    gapSmall: '0.5rem',       // 8px - маленький gap
    gapLarge: '1rem',         // 16px - большой gap
  },
} as const;

// ============================================
// BORDER RADIUS
// ============================================

export const borderRadius = {
  none: '0',
  sm: '0.5rem',      // 8px
  md: '1rem',        // 16px
  lg: '1.5rem',      // 24px - стандартный для карточек
  xl: '2rem',        // 32px
  '2xl': '2.5rem',   // 40px - для glass-панелей
  full: '9999px',    // Полностью круглый (для кнопок, инпутов)
} as const;

// ============================================
// ТЕНИ И ЭФФЕКТЫ
// ============================================

export const shadows = {
  // Стандартные тени
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',

  // Glass-эффект тени
  glass: '0 40px 80px -20px rgba(0, 0, 0, 0.8), inset 0 0 40px 0 rgba(255, 255, 255, 0.02)',
  glassHover: '0 50px 100px -20px rgba(0, 0, 0, 0.9), inset 0 0 60px 0 rgba(255, 255, 255, 0.04)',
} as const;

// ============================================
// АНИМАЦИИ И TRANSITIONS
// ============================================

export const animations = {
  // Durations
  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '600ms',
  },

  // Easing functions
  easing: {
    linear: 'linear',
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    satin: 'cubic-bezier(0.2, 0.8, 0.2, 1)',  // Kortix liquid easing
  },

  // Готовые transition строки
  transition: {
    all: 'all 300ms cubic-bezier(0.2, 0.8, 0.2, 1)',
    colors: 'color 150ms ease-in-out, background-color 150ms ease-in-out, border-color 150ms ease-in-out',
    transform: 'transform 300ms cubic-bezier(0.2, 0.8, 0.2, 1)',
    opacity: 'opacity 150ms ease-in-out',
  },
} as const;

// ============================================
// РАЗМЕРЫ КОМПОНЕНТОВ
// ============================================

export const components = {
  // Кнопки
  button: {
    height: {
      sm: '2.25rem',      // 36px
      md: '2.75rem',      // 44px - стандартная высота (touch-friendly)
      lg: '3rem',         // 48px
    },
    padding: {
      sm: '0.75rem 1rem',
      md: '0.75rem 1.5rem',
      lg: '1rem 2rem',
    },
    minWidth: {
      sm: '5rem',         // 80px
      md: '7.5rem',       // 120px
      lg: '10rem',        // 160px
    },
    iconSize: '2.75rem',  // 44px - квадратная кнопка с иконкой
  },

  // Инпуты
  input: {
    height: '2.75rem',    // 44px - стандартная высота
    padding: '0.75rem 1rem',
  },

  // Карточки
  card: {
    padding: '1.5rem',    // 24px
    borderRadius: '1.5rem', // 24px
  },

  // Модальные окна
  modal: {
    maxWidth: '40rem',    // 640px
    padding: '2rem',      // 32px
    borderRadius: '1.5rem', // 24px
  },
} as const;

// ============================================
// Z-INDEX LAYERS
// ============================================

export const zIndex = {
  background: -1,
  base: 0,
  dropdown: 10,
  sticky: 20,
  fixed: 30,
  modalBackdrop: 40,
  modal: 50,
  popover: 60,
  tooltip: 70,
  notification: 80,
} as const;

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Создаёт CSS класс для прозрачности
 */
export function opacity(value: number): string {
  return `rgba(255, 255, 255, ${value})`;
}

/**
 * Создаёт transition строку
 */
export function transition(
  property: string = 'all',
  duration: keyof typeof animations.duration = 'normal',
  easing: keyof typeof animations.easing = 'satin'
): string {
  return `${property} ${animations.duration[duration]} ${animations.easing[easing]}`;
}

/**
 * Экспорт всех токенов
 */
export const designTokens = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animations,
  components,
  zIndex,
} as const;

export default designTokens;
