/**
 * UNIFIED DESIGN SYSTEM - COMPONENT INDEX
 * 
 * Import all unified components from this single file for consistency.
 * 
 * Usage:
 * import { Button, Card, Input, Select } from '@/design-system'
 */

// Core components
export { UnifiedButton as Button } from './ui/unified-button';
export { UnifiedCard as Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './ui/unified-card';
export { UnifiedInput as Input } from './ui/unified-input';
export { UnifiedSelect as Select } from './ui/unified-select';

// Design tokens
export { DesignTokens } from '../design-system/tokens';

// Legacy components (for backwards compatibility - gradually migrate away from these)
export { Button as LegacyButton } from './ui/button';
export { Card as LegacyCard } from './ui/card';
export { Input as LegacyInput } from './ui/input';
