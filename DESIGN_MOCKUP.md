# ISL Interpreter Web App — Visual Mockup & UI Spec

## Labeled Layout Mockup (Desktop ~1200px wide)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ NAVIGATION (68px h)                                                         │
│ [🤟 Logo 42x42]           ISL Interpreter Web App             [☰ Menu 40x40]│
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────┬───────────────────────────────────┐
│ MAIN SECTION (Webcam + Prediction)       │ HISTORY PANEL (Right)             │
│ card: ~850w, radius 18, soft shadow      │ card: 330w, scrollable            │
│                                          │                                   │
│ Webcam label                              │ History label + toggle (mobile)  │
│ ┌──────────────────────────────────────┐  │ ┌───────────────────────────────┐ │
│ │ Webcam Feed 16:9 (max h ~500)       │  │ │ 🤟 Hello        11:35:12 AM  │ │
│ │ Animated border when active          │  │ │ 🤟 Thank You    11:35:09 AM  │ │
│ │ Overlay status at bottom             │  │ │ ... up to 5–10 items         │ │
│ └──────────────────────────────────────┘  │ └───────────────────────────────┘ │
│                                          │                                   │
│ Prediction label                          │                                   │
│ Detected Gesture: {RESULT} (large, bold) │                                   │
│ Confidence: XX.XX%                        │                                   │
│                                          │                                   │
│ [Start Camera] [Stop Camera] [Speak ☑]   │                                   │
│                                          │                                   │
│ UPLOAD SECTION                            │                                   │
│ Upload a saved video to detect gestures   │                                   │
│ [Choose video file card] [Submit Video]   │                                   │
└──────────────────────────────────────────┴───────────────────────────────────┘

Bottom Center Toast: "Gesture recognized: {RESULT}"
```

## Responsive Behavior
- **Desktop/Tablet (`>=960px`)**: 2-column layout, webcam main focus.
- **Smaller screens (`<960px`)**: history collapses into an expandable drawer (`Show/Hide`), webcam remains centered.

## Approximate Dimensions & Spacing
- Navbar height: **68px**.
- Content max width: **1200px**, horizontal padding: **16px**.
- Grid columns: **main flexible + 330px history**.
- Card radius: **18px**, internal padding: **14–16px**.
- Webcam frame max width: **760px**, border **4px**.
- Section vertical gaps: **10–16px**.
- History list item height: ~**44–52px** each.

## Color Palette
- Background gradient: `#f7f2ff` → `#edf4ff` → `#f9fff8`
- Primary button gradient: `#7c3aed` → `#2563eb`
- Accent border: `#c4b5fd`
- Active border: `#22c55e`
- Detected flash border: `#f59e0b`
- Text primary: `#1e1b2f`, muted: `#64748b`

## Font Suggestions
- Primary font: **Inter**
- Alternatives: **Roboto**, **Poppins**
- Prediction text: **800 weight**, 1.35rem–2rem (responsive clamp)

## Interactions
- Animated webcam border pulse while camera is active.
- Prediction text bounce animation when updated.
- Gesture-detected outline effect on webcam frame.
- Toast notification appears at bottom for each recognized gesture.
- History items include icon + gesture + timestamp, with subtle hover shift.
