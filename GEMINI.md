# Design & UI Guidelines

Whenever designing UI, frontend components, or visual assets:

1. **Color Schemes (Coolors)**:
   - Use harmonious color palettes inspired by [Coolors](https://coolors.co).
   - Follow the 60-30-10 rule (dominant neutral background, secondary structure/surface, accent call-to-actions).
   - Ensure WCAG AA contrast compliance (4.5:1 minimum for body text).

2. **Icons (Iconify)**:
   - Standardize icon usage with [Iconify](https://iconify.design).
   - Use `<iconify-icon icon="prefix:name">` for web components or `@iconify/react` for React/Next.js.
   - For pure SVGs, ensure uniform 24px viewBox and `currentColor` fill/stroke.

3. **Backgrounds & Patterns (Pattern Monster)**:
   - When subtle background textures or geometric patterns are needed, use [Pattern Monster](https://pattern.monster) style clean SVG repeatable patterns.
   - Keep pattern stroke opacity subtle (0.05 - 0.15) to maintain high contrast and readability.
