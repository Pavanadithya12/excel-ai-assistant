---
name: design-system-resources
description: >-
  Expert guidance for integrating Coolors color palettes, Iconify icon framework,
  and Pattern Monster SVG patterns into web applications, UI components, and design systems.
  Use when designing frontend UI, generating color schemes, adding icons, or styling SVG backgrounds.
---

# Design System Resources: Coolors, Iconify & Pattern Monster

This skill equips the agent with best practices and reference implementations for three core design tools:
1. **Coolors** (Color Palettes & Semantic Tokens)
2. **Iconify** (Universal Icon Framework & SVG Icons)
3. **Pattern Monster** (Repeatable SVG Background Patterns)

---

## 1. Coolors (`coolors.co`) – Color Palettes & Tokens

When designing UI or styling components, structure color systems according to harmonic color theory and accessible contrast.

### Palette Architecture (60-30-10 Rule)
- **60% Dominant / Surface**: Neutral backgrounds (`#F8FAFC` in light mode, `#0F172A` in dark mode).
- **30% Secondary / Structure**: Cards, borders, muted text, headers, and navigation bars.
- **10% Accent / Brand**: Buttons, badges, active states, and call-to-actions.

### CSS Custom Properties Template
```css
:root {
  /* Primary & Accent (Coolors Inspired) */
  --color-primary: #3B82F6;
  --color-primary-hover: #2563EB;
  --color-accent: #F59E0B;
  
  /* Neutrals & Surfaces */
  --color-bg: #F8FAFC;
  --color-surface: #FFFFFF;
  --color-border: #E2E8F0;
  --color-text-main: #0F172A;
  --color-text-muted: #64748B;
  
  /* Functional / Status */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;
  --color-info: #06B6D4;
}

[data-theme="dark"] {
  --color-bg: #0B0F19;
  --color-surface: #1E293B;
  --color-border: #334155;
  --color-text-main: #F1F5F9;
  --color-text-muted: #94A3B8;
}
```

### Contrast & Accessibility (WCAG 2.1)
- Verify that text-to-background contrast is at least **4.5:1** for normal text and **3.0:1** for large headings/UI boundaries.
- Never use color alone to convey state—pair colors with icons or labels.

---

## 2. Iconify (`iconify.design`) – Universal Icons

Iconify provides over 200,000 open-source icons across popular sets (Lucide, Material Design, Tabler, Phosphor, FontAwesome).

### A. HTML / Web Component (Universal & Fast)
Include the lightweight web component script in `<head>`:
```html
<script src="https://code.iconify.design/iconify-icon/2.1.0/iconify-icon.min.js"></script>
```
Render any icon on demand:
```html
<!-- Lucide icon -->
<iconify-icon icon="lucide:check-circle" width="24" height="24"></iconify-icon>

<!-- Material Symbols / Design Icons -->
<iconify-icon icon="mdi:bell-outline" width="24" height="24"></iconify-icon>

<!-- Tabler Icons -->
<iconify-icon icon="tabler:settings" width="20" height="20" class="text-gray-600 hover:text-blue-500"></iconify-icon>
```

### B. React / Next.js
Install: `npm install @iconify/react`
```tsx
import { Icon } from '@iconify/react';

export function ActionButton() {
  return (
    <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
      <Icon icon="lucide:download" className="w-5 h-5" />
      <span>Download</span>
    </button>
  );
}
```

### C. Direct Inline SVG
When frameworks or external scripts cannot be loaded, output inline SVGs styled with `currentColor`:
```html
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <!-- path content -->
</svg>
```

---

## 3. Pattern Monster (`pattern.monster`) – SVG Patterns & Backgrounds

Pattern Monster generates geometric, abstract, and repeatable SVG patterns. Use them for hero backgrounds, cards, and subtle website textures.

### Pattern Implementation Guidelines
1. **Subtlety**: Background patterns must have low opacity (between `0.03` and `0.15`) or use subtle tone-on-tone colors so they never impede text readability.
2. **Responsive Scaling**: Use `svg` with `<defs><pattern>` or base64 / UTF-8 CSS data URIs.

### Example A: Repeating SVG Pattern Definition
```html
<svg class="absolute inset-0 -z-10 h-full w-full stroke-gray-200 [mask-image:radial-gradient(100%_100%_at_top_right,white,transparent)]" aria-hidden="true">
  <defs>
    <pattern id="pattern-grid" width="40" height="40" patternUnits="userSpaceOnUse" patternTransform="rotate(0)">
      <path d="M0 40L40 0H20L0 20M40 40V20L20 40" stroke="currentColor" stroke-width="1" fill="none" opacity="0.12" />
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#pattern-grid)" />
</svg>
```

### Example B: Pure CSS Dot/Grid Background
```css
/* Subtle Dot Grid */
.bg-pattern-dots {
  background-color: #ffffff;
  background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
  background-size: 24px 24px;
}

/* Subtle Geometric Grid */
.bg-pattern-grid {
  background-color: #f8fafc;
  background-image: 
    linear-gradient(to right, #e2e8f0 1px, transparent 1px),
    linear-gradient(to bottom, #e2e8f0 1px, transparent 1px);
  background-size: 32px 32px;
}
```

---

## Summary Checklist for Generating UI
- [ ] **Palette**: Is there a coherent Coolors-style color hierarchy with WCAG-compliant contrast?
- [ ] **Icons**: Are icons using Iconify icon IDs or uniform SVGs with `currentColor`?
- [ ] **Background**: If a background pattern is requested, is it a lightweight, unobtrusive Pattern Monster style SVG?
