/**
 * DESIGN SYSTEM SHOWCASE
 * 
 * This page demonstrates all unified components and their variants.
 * Use this as a living style guide and reference.
 */

'use client';

import { Button, Card, CardHeader, CardTitle, CardContent, Input, Select } from '@/components/unified';
import { Plus, Download, Trash2, Settings, Search } from 'lucide-react';

export default function DesignSystemShowcase() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-foreground">Unified Design System</h1>
          <p className="text-foreground-secondary">All components in one place</p>
        </div>

        {/* Buttons */}
        <Card>
          <CardHeader>
            <CardTitle>Buttons</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Variants */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Variants</h3>
              <div className="flex flex-wrap gap-4">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="accent">Accent</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="destructive">Destructive</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="link">Link</Button>
              </div>
            </div>

            {/* Sizes */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Sizes</h3>
              <div className="flex flex-wrap items-center gap-4">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
                <Button size="icon"><Plus /></Button>
                <Button size="icon-sm"><Settings /></Button>
              </div>
            </div>

            {/* With Icons */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">With Icons</h3>
              <div className="flex flex-wrap gap-4">
                <Button icon={Plus} iconPosition="left">Add Item</Button>
                <Button icon={Download} iconPosition="right" variant="secondary">Download</Button>
                <Button icon={Trash2} variant="destructive">Delete</Button>
              </div>
            </div>

            {/* States */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">States</h3>
              <div className="flex flex-wrap gap-4">
                <Button>Normal</Button>
                <Button disabled>Disabled</Button>
                <Button fullWidth>Full Width Button</Button>
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Cards */}
        <Card>
          <CardHeader>
            <CardTitle>Cards</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card variant="default" padding="md">
                <div className="space-y-2">
                  <h4 className="font-medium">Default Glass</h4>
                  <p className="text-sm text-foreground-secondary">
                    Full glass morphism effect with backdrop blur
                  </p>
                </div>
              </Card>

              <Card variant="compact" padding="md">
                <div className="space-y-2">
                  <h4 className="font-medium">Compact</h4>
                  <p className="text-sm text-foreground-secondary">
                    Lighter glass effect for subtle elevation
                  </p>
                </div>
              </Card>

              <Card variant="flat" padding="md">
                <div className="space-y-2">
                  <h4 className="font-medium">Flat</h4>
                  <p className="text-sm text-foreground-secondary">
                    Solid background without glass effect
                  </p>
                </div>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card padding="none">
                <div className="p-4 space-y-1">
                  <h4 className="font-medium">No Padding</h4>
                  <p className="text-xs text-foreground-secondary">padding="none"</p>
                </div>
              </Card>

              <Card padding="sm">
                <div className="space-y-1">
                  <h4 className="font-medium">Small</h4>
                  <p className="text-xs text-foreground-secondary">padding="sm"</p>
                </div>
              </Card>

              <Card padding="md">
                <div className="space-y-1">
                  <h4 className="font-medium">Medium</h4>
                  <p className="text-xs text-foreground-secondary">padding="md"</p>
                </div>
              </Card>

              <Card padding="lg">
                <div className="space-y-1">
                  <h4 className="font-medium">Large</h4>
                  <p className="text-xs text-foreground-secondary">padding="lg"</p>
                </div>
              </Card>
            </div>

          </CardContent>
        </Card>

        {/* Inputs */}
        <Card>
          <CardHeader>
            <CardTitle>Inputs</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Variants */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Variants</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input variant="default" placeholder="Default variant" />
                <Input variant="glass" placeholder="Glass variant (Default)" />
                <Input variant="flat" placeholder="Flat variant" />
              </div>
            </div>

            {/* Sizes */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Sizes</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input inputSize="sm" placeholder="Small (36px)" />
                <Input inputSize="md" placeholder="Medium (44px)" />
                <Input inputSize="lg" placeholder="Large (52px)" />
              </div>
            </div>

            {/* Types */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Types</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input type="text" placeholder="Text input" />
                <Input type="email" placeholder="Email input" />
                <Input type="password" placeholder="Password input" />
                <Input type="number" placeholder="Number input" />
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Selects */}
        <Card>
          <CardHeader>
            <CardTitle>Selects</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Variants */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Variants</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Select 
                  variant="default"
                  options={[
                    { value: '1', label: 'Default Variant' },
                    { value: '2', label: 'Option 2' },
                  ]}
                />
                <Select 
                  variant="glass"
                  options={[
                    { value: '1', label: 'Glass Variant (Default)' },
                    { value: '2', label: 'Option 2' },
                  ]}
                />
                <Select 
                  variant="flat"
                  options={[
                    { value: '1', label: 'Flat Variant' },
                    { value: '2', label: 'Option 2' },
                  ]}
                />
              </div>
            </div>

            {/* Sizes */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Sizes</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Select 
                  selectSize="sm"
                  options={[
                    { value: '1', label: 'Small (36px)' },
                    { value: '2', label: 'Option 2' },
                  ]}
                />
                <Select 
                  selectSize="md"
                  options={[
                    { value: '1', label: 'Medium (44px)' },
                    { value: '2', label: 'Option 2' },
                  ]}
                />
                <Select 
                  selectSize="lg"
                  options={[
                    { value: '1', label: 'Large (52px)' },
                    { value: '2', label: 'Option 2' },
                  ]}
                />
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Color Palette */}
        <Card>
          <CardHeader>
            <CardTitle>Color Palette</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            
            {/* Backgrounds */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Backgrounds</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-background border border-border rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Background</div>
                  <div className="text-xs text-foreground-secondary">#0A0A0A</div>
                </div>
                <div className="bg-background-secondary border border-border rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Secondary</div>
                  <div className="text-xs text-foreground-secondary">#141414</div>
                </div>
                <div className="bg-background-tertiary border border-border rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Tertiary</div>
                  <div className="text-xs text-foreground-secondary">#1F1F1F</div>
                </div>
                <div className="bg-background-hover border border-border rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Hover</div>
                  <div className="text-xs text-foreground-secondary">5% White</div>
                </div>
              </div>
            </div>

            {/* Semantic Colors */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-foreground-secondary">Semantic Colors</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-success text-white rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Success</div>
                  <div className="text-xs opacity-80">#22C55E</div>
                </div>
                <div className="bg-warning text-white rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Warning</div>
                  <div className="text-xs opacity-80">#F59E0B</div>
                </div>
                <div className="bg-destructive text-white rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Error</div>
                  <div className="text-xs opacity-80">#E33D3D</div>
                </div>
                <div className="bg-info text-white rounded-xl p-4 text-center">
                  <div className="text-sm font-medium">Info</div>
                  <div className="text-xs opacity-80">#14B8A6</div>
                </div>
              </div>
            </div>

          </CardContent>
        </Card>

        {/* Example Form */}
        <Card>
          <CardHeader>
            <CardTitle>Example Form</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground-secondary">Name</label>
                <Input placeholder="Enter your name" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground-secondary">Email</label>
                <Input type="email" placeholder="your@email.com" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground-secondary">Category</label>
              <Select 
                options={[
                  { value: '1', label: 'Category 1' },
                  { value: '2', label: 'Category 2' },
                  { value: '3', label: 'Category 3' },
                ]}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button variant="primary" fullWidth>Submit</Button>
              <Button variant="secondary" fullWidth>Cancel</Button>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
