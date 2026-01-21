# DESIGN_VISION: Organic Liquid Interface

## Core Philosophy
The interface is not a static set of pixels. It is a **living, fluid simulation**. It behaves like physical materials—glass, water, mercury—reacting to light and interaction.

### 1. Art-First
*   **Every Screen is a Canvas**: We are not just displaying data; we are rendering a composition. The background is never flat; it is a generative, moving mesh of light.
*   **Emotion over Utility**: While usability is paramount, the *feeling* of the interface comes first. It should evoke a sense of calm sophistication and high-tech fluidity.

### 2. Radical Symmetry
*   **The Axis**: Layouts are balanced around a central vertical axis.
*   **Harmony**: Even asymmetrical content is balanced by visual weight.
*   **Centering**: Key interactions often occur at the center of the viewport.

### 3. Physical Materiality
*   **Liquid Glass**: The primary material. It is thick, heavy, and refractive.
    *   **Refraction**: Background elements are blurred and distorted behind glass panels.
    *   **Caustics**: Light focuses on edges and curves, creating bright, sharp highlights.
    *   **Fresnel**: Edges glow when viewed at glancing angles.
*   **Mercury**: Interactive elements (buttons, toggles) behave like liquid metal—surface tension keeps them round, but force (clicks) deforms them.
*   **Light**: Light sources are dynamic. Shadows are "diffuse"—they carry the color of the object casting them, simulating subsurface scattering.

### 4. Minimalism
*   **Content is King**: The chrome (UI markings, borders, scrollbars) is invisible until needed.
*   **Breathing Room**: Extensive use of negative space.
*   **Typography**: Clean, sans-serif, high contrast. Text floats above the glass.

## Physics Engine Specs

### Lighting Model
*   **Global Light**: Top-down, slightly angled (simulating a studio softbox).
*   **Local Light**: Cursor position acts as a point light source, revealing texture on hover.

### Motion ('The Flow')
*   **Easing**: No linear animations. All motion uses `cubic-bezier(0.2, 0.8, 0.2, 1)` for a snappy yet smooth "heavy object" feel.
*   **Response**: Interactions feel immediate but have "weight". Dragging a card feels like dragging a distinct physical object through water (viscosity).

### Distortion
*   **Turbulence**: Backgrounds and glass edges have subtle, slow-moving Perlin noise distortion (`<feTurbulence>`) to simulate liquid movement.
