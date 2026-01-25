# Design System - Quick Reference Card

## 📦 Import Components

```tsx
import { Button, Card, Input, Select } from '@/components/unified';
```

---

## 🔘 Button

```tsx
// Variants
<Button variant="primary">Primary Action</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="accent">Important</Button>
<Button variant="ghost">Minimal</Button>
<Button variant="destructive">Delete</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium (Default)</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Plus /></Button>

// With Icon
<Button icon={Plus} iconPosition="left">Add Item</Button>
<Button icon={Download} iconPosition="right">Download</Button>

// Full Width
<Button fullWidth>Full Width Button</Button>
```

---

## 🎴 Card

```tsx
// Variants
<Card variant="default">Glass Effect (Default)</Card>
<Card variant="compact">Compact Glass</Card>
<Card variant="flat">Solid Background</Card>

// Padding
<Card padding="none">No Padding</Card>
<Card padding="sm">Small (16px)</Card>
<Card padding="md">Medium (24px, Default)</Card>
<Card padding="lg">Large (32px)</Card>

// Interactive
<Card interactive onClick={handleClick}>
  Clickable Card
</Card>

// Full Example
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content here</CardContent>
  <CardFooter>Footer actions</CardFooter>
</Card>
```

---

## 📝 Input

```tsx
// Variants
<Input variant="default" placeholder="Text..." />
<Input variant="glass" placeholder="Glass effect (Default)" />
<Input variant="flat" placeholder="Solid background" />

// Sizes
<Input inputSize="sm" />  // 36px
<Input inputSize="md" />  // 44px (Default)
<Input inputSize="lg" />  // 52px

// Types
<Input type="email" placeholder="Email..." />
<Input type="password" placeholder="Password..." />
<Input type="number" placeholder="Amount..." />
```

---

## 📋 Select

```tsx
// With Options Array
<Select 
  variant="glass"
  options={[
    { value: 'opt1', label: 'Option 1' },
    { value: 'opt2', label: 'Option 2' },
  ]}
/>

// Manual Children
<Select variant="glass">
  <option value="1">Option 1</option>
  <option value="2">Option 2</option>
</Select>

// Sizes
<Select selectSize="sm" />  // 36px
<Select selectSize="md" />  // 44px (Default)
<Select selectSize="lg" />  // 52px
```

---

## 🎨 Color Classes

### Background
```tsx
className="bg-background"           // Main (#0A0A0A)
className="bg-background-secondary" // Cards (#141414)
className="bg-background-tertiary"  // Muted (#1F1F1F)
className="bg-background-hover"     // Hover state
```

### Text
```tsx
className="text-foreground"           // Primary (white)
className="text-foreground-secondary" // 70% opacity
className="text-foreground-muted"     // 50% opacity
className="text-foreground-disabled"  // 30% opacity
```

### Brand
```tsx
className="bg-brand-primary"       // Burgundy
className="text-brand-primary"     // Burgundy text
className="border-brand-primary"   // Burgundy border
```

### Semantic
```tsx
className="text-success"     // Green
className="text-warning"     // Amber
className="text-destructive" // Red
className="text-info"        // Cyan
```

---

## 📏 Spacing

```tsx
className="p-xs"   // 4px
className="p-sm"   // 8px
className="p-md"   // 16px
className="p-lg"   // 24px
className="p-xl"   // 32px
className="p-2xl"  // 48px
className="p-3xl"  // 64px
```

---

## 🔲 Border Radius

```tsx
className="rounded-sm"   // 8px
className="rounded-md"   // 12px
className="rounded-lg"   // 16px
className="rounded-xl"   // 24px
className="rounded-2xl"  // 40px (glass panels)
className="rounded-full" // Fully rounded
```

---

## ⚡ Transitions

```tsx
className="transition-all duration-fast"   // 150ms
className="transition-all duration-normal" // 300ms
className="transition-all duration-slow"   // 600ms

className="ease-smooth"  // Liquid smooth easing
className="ease-spring"  // Spring easing
```

---

## 🔍 Common Patterns

### Glass Panel
```tsx
<div className="glass-panel p-6">
  Content with glass effect
</div>
```

### Hover Effect
```tsx
<div className="transition-all duration-300 hover:scale-105">
  Scales on hover
</div>
```

### Focus State
```tsx
<input className="focus:ring-2 focus:ring-brand-primary" />
```

### Grid Layout
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-lg">
  <Card>Card 1</Card>
  <Card>Card 2</Card>
  <Card>Card 3</Card>
</div>
```

---

## 📱 Responsive Design

```tsx
// Mobile first approach
<div className="
  p-4              /* Mobile: 16px */
  md:p-6           /* Tablet: 24px */
  lg:p-8           /* Desktop: 32px */
">
  Responsive padding
</div>

// Grid columns
<div className="
  grid 
  grid-cols-1      /* Mobile: 1 column */
  md:grid-cols-2   /* Tablet: 2 columns */
  lg:grid-cols-3   /* Desktop: 3 columns */
  gap-4
">
  Content
</div>
```

---

## ✅ Best Practices

1. **Always use unified components for consistency**
   ```tsx
   import { Button } from '@/components/unified'; ✅
   import LiquidButton from '@/components/LiquidButton'; ❌ (legacy)
   ```

2. **Use design tokens for colors**
   ```tsx
   className="bg-background-secondary" ✅
   className="bg-[#141414]" ❌ (hardcoded)
   ```

3. **Maintain touch-friendly sizes (44px minimum)**
   ```tsx
   <Button size="md">Click me</Button> ✅ (44px)
   <button className="h-8">Too small</button> ❌ (32px)
   ```

4. **Use glass effect for main UI elements**
   ```tsx
   <Card variant="default">Glass effect</Card> ✅
   ```

5. **Consistent spacing**
   ```tsx
   className="gap-4 p-6" ✅
   className="gap-[13px] p-[23px]" ❌
   ```

---

**Pro Tip**: Keep this file handy while developing! 📌
