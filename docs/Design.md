# Design Guidelines — Atlas (2035 Aesthetic)

This document details the visual style, typography, spacing, component aesthetics, and animations that make Atlas look like premium software from 2035.

---

## 1. Visual Aesthetics & Theme

Atlas adopts a **Glassmorphic / Neo-Futuristic** dark theme. It draws inspiration from Nothing OS (minimal dot-matrix accents, high-contrast monochrome), Arc Browser (sidebar utilities, clean panels), and Apple Vision Pro (layering, depth, ambient back-glows).

### 1.1 Color Tokens
- **Background Deep**: `#050505` (True black base)
- **Glass Card Base**: `rgba(15, 15, 15, 0.6)`
- **Border Subtle**: `rgba(255, 255, 255, 0.07)`
- **Border Highlight**: `rgba(255, 255, 255, 0.15)`
- **Accent Glow (Primary)**: `#7c3aed` (Electric violet)
- **Accent Glow (Secondary)**: `#06b6d4` (Neon cyan)
- **Text Primary**: `#f5f5f5` (Off-white)
- **Text Secondary**: `#a3a3a3` (Muted gray)

---

## 2. Glassmorphism CSS Specification

Apply this standard structure for all floating panels, dialogs, and main windows:

```css
.glass-panel {
  background: rgba(15, 15, 15, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37),
              0 0 40px 0 rgba(124, 58, 237, 0.05); /* subtle primary color glow */
}
```

---

## 3. Typography

- **Headings & Accents**: `Outfit` or `Geist Sans`
- **Body Text**: `Inter` or `Geist Sans` (font weights: 400 for regular, 500 for medium, 600 for semi-bold)
- **Code & Command Prompts**: `Geist Mono` or `Fira Code`

---

## 4. Key UI Components

### 4.1 The Command HUD (Alt + Space)
- A floating input field centered on the screen.
- Sleek, borders transition from subtle gray to a vibrant gradient (violet to cyan) when active.
- Features real-time voice levels displayed as an animated wave when mic is listening.

### 4.2 Assistant Dialogue Thread
- Messages slide in upwards with subtle scale-ins.
- User messages: Simple right-aligned containers with clean borders.
- Atlas messages: Styled left-aligned containers with ambient background glows.

---

## 5. Motion & Transitions (Framer Motion)

Animations must be smooth and fast. Avoid long, sluggish transitions.
- **Entry Transitions**:
  - `y: [15, 0]`, `opacity: [0, 1]`, transition duration: `0.3s` using ease `cubic-bezier(0.16, 1, 0.3, 1)`.
- **Exit Transitions**:
  - `opacity: [1, 0]`, transition duration: `0.15s` ease-in.
- **Hover Micro-interactions**:
  - Scale up by `1.02` with an ambient glow expansion.
