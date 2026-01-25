# Unified Design System

## Overview

This design system provides a complete, consistent set of components and design tokens for the application. All styles are centralized for maximum consistency and maintainability.

## 🎨 Design Philosophy

**Liquid Glass Interface** - Our design is inspired by physical materials (glass, water, mercury) that react to light and interaction. Every element should feel fluid, smooth, and premium.

### Core Principles:
1. **Consistency** - All components share the same visual language
2. **Fluidity** - Smooth animations and transitions throughout
3. **Glass Morphism** - Subtle transparency and blur effects
4. **Minimalism** - Clean, focused, breathing room
5. **Accessibility** - Proper contrast, touch targets (44px minimum)

---

## 📦 Components

### Button

Unified button component with multiple variants and sizes.

**Variants:**
- `primary` - Mercury/metallic style for main CTAs (default)
- `secondary` - Glass style for secondary actions
- `accent` - Brand burgundy color for important actions
- `ghost` - Minimal style for tertiary actions
- `destructive` - Red for delete/remove actions
- `outline` - Bordered transparent style
- `link` - Text-only style

**Sizes:**
- `sm` - 36px height
- `md` - 44px height (default, touch-friendly)
- `lg` - 52px height
- `icon` - 44x44px square for icon-only
- `icon-sm` - 36x36px square

**Usage:**
```tsx
import { Button } from '@/components/unified';

<Button variant="primary" size="md">Click me</Button>
<Button variant="secondary" icon={Plus}>Add Item</Button>
<Button variant="accent" fullWidth>Submit</Button>
```

---

### Card

Glass panel card component with consistent styling.

**Variants:**
- `default` - Full glass panel effect (default)
- `compact` - Lighter backdrop blur
- `flat` - Solid background, no glass effect

**Padding:**
- `none` - No padding
- `sm` - 16px padding
- `md` - 24px padding (default)
- `lg` - 32px padding

**Props:**
- `interactive` - Adds hover scale effect for clickable cards

**Usage:**
```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/unified';

<Card variant="default" padding="md">
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    Card content goes here
  </CardContent>
</Card>
```

---

### Input

Unified input component with glass effect.

**Variants:**
- `default` - Semi-transparent with backdrop blur
- `glass` - Full glass effect (default)
- `flat` - Solid background

**Sizes:**
- `sm` - 36px height
- `md` - 44px height (default)
- `lg` - 52px height

**Usage:**
```tsx
import { Input } from '@/components/unified';

<Input 
  variant="glass" 
  inputSize="md" 
  placeholder="Enter text..." 
/>
```

---

### Select

Unified select/dropdown component.

**Variants:**
- `default` - Semi-transparent with backdrop blur
- `glass` - Full glass effect (default)
- `flat` - Solid background

**Sizes:**
- `sm` - 36px height
- `md` - 44px height (default)
- `lg` - 52px height

**Usage:**
```tsx
import { Select } from '@/components/unified';

<Select 
  variant="glass"
  selectSize="md"
  options={[
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
  ]}
/>
```

---

## 🎨 Design Tokens

All design tokens are centralized in `/src/design-system/tokens.ts` and exposed as CSS variables in `globals.css`.

### Colors

**Background:**
- `--background` - Main app background (#0A0A0A)
- `--background-secondary` - Cards/panels (#141414)
- `--background-tertiary` - Muted elements (#1F1F1F)
- `--background-hover` - Hover state

**Text:**
- `--foreground` - Primary text (white)
- `--foreground-secondary` - Secondary text (70% white)
- `--foreground-muted` - Muted text (50% white)
- `--foreground-disabled` - Disabled text (30% white)

**Brand:**
- `--brand-primary` - Burgundy accent (#9B1B30)
- `--brand-primary-hover` - Lighter burgundy
- `--brand-secondary` - White

**Semantic:**
- `--success` - Green (#22C55E)
- `--warning` - Amber (#F59E0B)
- `--destructive` - Red (#E33D3D)
- `--info` - Cyan (#14B8A6)

**Usage in CSS:**
```css
.my-element {
  background: hsl(var(--background-secondary));
  color: hsl(var(--foreground));
  border: 1px solid hsl(var(--border));
}
```

**Usage in Tailwind:**
```tsx
<div className="bg-background-secondary text-foreground border border-border">
  Content
</div>
```

---

### Spacing

```
xs:  4px
sm:  8px
md:  16px
lg:  24px
xl:  32px
2xl: 48px
3xl: 64px
```

---

### Border Radius

```
sm:   8px
md:   12px
lg:   16px
xl:   24px
2xl:  40px (glass panels)
full: 9999px (fully rounded)
```

---

### Typography

**Font Family:**
- Sans: `-apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", sans-serif`
- Mono: `"SF Mono", "Monaco", "Inconsolata", monospace`

**Font Sizes:**
- xs: 12px
- sm: 14px
- base: 16px
- lg: 18px
- xl: 20px
- 2xl: 24px
- 3xl: 30px
- 4xl: 36px

**Font Weights:**
- normal: 400
- medium: 500
- semibold: 600
- bold: 700

---

### Transitions

**Durations:**
- `fast`: 150ms
- `normal`: 300ms
- `slow`: 600ms

**Easing:**
- `default`: cubic-bezier(0.4, 0, 0.2, 1)
- `smooth`: cubic-bezier(0.2, 0.8, 0.2, 1) - Liquid smooth
- `spring`: cubic-bezier(0.34, 1.56, 0.64, 1)

**Usage:**
```tsx
<div className="transition-all duration-normal ease-smooth">
  Smooth animation
</div>
```

---

## 🔧 Migration Guide

### From Old Components to Unified Components

**Button Migration:**
```tsx
// Old (multiple variants)
import LiquidButton from '@/components/LiquidButton';
import { Button } from '@/components/ui/button';

// New (unified)
import { Button } from '@/components/unified';

// Before
<LiquidButton variant="primary">Click</LiquidButton>

// After
<Button variant="primary">Click</Button>
```

**Card Migration:**
```tsx
// Old
<div className="glass-panel p-6">Content</div>
<div className="ui-card">Content</div>

// New
import { Card } from '@/components/unified';
<Card>Content</Card>
```

**Input Migration:**
```tsx
// Old
import GlassInput from '@/components/GlassInput';
import { Input } from '@/components/ui/input';

// New
import { Input } from '@/components/unified';
<Input variant="glass" placeholder="Text" />
```

---

## 📏 Best Practices

### Touch Targets
All interactive elements should be **minimum 44x44px** for accessibility and mobile usability.

### Glass Effect Usage
Use glass panels (`glass-panel` class or `Card` component) for:
- Main content cards
- Modal dialogs
- Popovers
- Sidebars

### Color Usage
- **Primary actions**: Use `brand-primary` (burgundy)
- **Secondary actions**: Use glass/transparent styles
- **Success states**: Use `success` (green)
- **Warnings**: Use `warning` (amber)
- **Errors/Delete**: Use `destructive` (red)

### Animation
- **Fast (150ms)**: Micro-interactions (hovers, focus states)
- **Normal (300ms)**: UI transitions (modals, dropdowns)
- **Slow (600ms)**: Page transitions, glass panel hovers

---

## 🚀 Quick Start

1. **Import unified components:**
```tsx
import { Button, Card, Input, Select } from '@/components/unified';
```

2. **Use CSS variables in custom styles:**
```tsx
<div className="bg-background-secondary text-foreground border border-border rounded-2xl p-6">
  Custom styled element
</div>
```

3. **Access design tokens programmatically:**
```tsx
import { DesignTokens } from '@/components/unified';

const primaryColor = DesignTokens.colors.brand.primary;
```

---

## 📚 Resources

- **Design Vision**: `/frontend/DESIGN_VISION.md`
- **Design Tokens**: `/frontend/src/design-system/tokens.ts`
- **Global Styles**: `/frontend/src/app/globals.css`
- **Tailwind Config**: `/frontend/tailwind.config.js`

---

**Last Updated**: January 2026
