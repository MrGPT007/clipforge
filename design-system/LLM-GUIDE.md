# ClipForge UI Contract for LLMs

This file is the source of truth for code-generating models working on ClipForge UI.

## Non-negotiable rules

1. **Use existing primitives first.** Check `design-system/manifest.json` and `components/ui/` before creating a new component.
2. **Use semantic tokens only.** Never introduce product UI colors as hex/rgb literals. Use `bg-background`, `bg-card`, `bg-primary`, `bg-secondary`, `text-foreground`, `text-muted-foreground`, `border-border`, or the CSS variables in `design-system/tokens.css`.
3. **Use the fluid scale.** Prefer `var(--space-*)`, `var(--text-*)`, `var(--control-h-*)`, and existing utilities. Do not add breakpoint-specific sizes when a `clamp()` token can solve the layout.
4. **Support light and dark automatically.** Never write a light-only background or text color. Semantic tokens invert in `.dark`.
5. **Use ClipForge elevation.** Raised interactive surfaces use hard offset shadows (`--shadow-xs` to `--shadow-lg`). Do not introduce blurry generic SaaS card shadows unless `--shadow-soft` is explicitly appropriate.
6. **Motion communicates state.** Use `--duration-fast/base/slow` with `--ease-standard` or `--ease-emphasized`. Pressable controls move toward their shadow on active. Respect `prefers-reduced-motion`.
7. **Accessibility is part of the component.** Keep visible focus, keyboard access, labels, `aria-*` state, 44px-ish comfortable hit targets for primary controls, and sufficient contrast.
8. **Grandma-proof copy.** Use everyday words. Tell the user what a button does, not what the system calls the operation. Explain irreversible, paid, publishing, account, or external-service effects before the action.
9. **No mystery icons.** Icon-only buttons require `aria-label` and `title` when the meaning is not universally obvious.
10. **Do not fork the visual language.** New screens should look like ClipForge, not like a fresh template.

## Preferred composition order

For a new screen, choose in this order:

- Page shell: `.cf-page`, `.cf-stack`, `.cf-cluster`, `.cf-grid`
- Navigation: Sidebar, Breadcrumb, Tabs, NavigationMenu
- Content: Card, Item, Alert, Empty, Badge, Avatar
- Input: Field/Form + Input/Textarea/Select/Checkbox/Switch/RadioGroup/Slider
- Actions: Button; use `default` for primary task, `secondary` for lime support actions, `outline` for neutral actions, `destructive` only for destructive actions, `ghost` for low-emphasis chrome
- Overlays: Dialog for focused decisions/forms, Sheet/Drawer for side/mobile workflows, Popover for lightweight local controls, Tooltip for terse clarification
- Feedback: Sonner/toast for transient result, Alert for persistent context, Progress/Spinner for active work, Skeleton for initial loading

## Visual grammar

- Background is warm paper, not pure gray.
- Primary accent is lavender; secondary accent is lime.
- Borders are dark/light ink depending on theme and are often 1.5–2px.
- Raised objects use a crisp offset shadow, giving a printed/editorial feel.
- Corners are modestly rounded, never pill-heavy except avatars/status chips.
- Typography is compact, friendly, highly legible, and uses strong labels.
- Dense screens should still have obvious grouping and plain-language help text.

## Fluid examples

```css
/* Good */
padding: var(--space-4);
font-size: var(--text-lg);
min-height: var(--control-h-md);
gap: var(--space-3);
box-shadow: var(--shadow-sm);

/* Avoid */
padding: 17px;
font-size: 15px;
@media (max-width: 900px) { padding: 13px; }
```

## New component checklist

Before adding a new component, confirm all of these are true:

- No existing component or composition covers the job.
- It has a `data-slot` name for stable styling and agent discovery.
- It consumes semantic tokens.
- It works in light, dark, keyboard, touch, and reduced-motion modes.
- States are defined: default, hover, focus-visible, active, disabled, loading when applicable, error/invalid when applicable.
- The component is added to `design-system/manifest.json`.
- Any user-facing copy follows `docs/GRANDMA-PROOF-UI-COPY-RULEBOOK.md`.

