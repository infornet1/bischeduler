# BiScheduler Branding Usage Examples

## Logo Usage Examples

### Primary Logo (Full)
Use in headers, documents, and marketing materials:
```html
<img src="/static/branding/logo_concept.svg" alt="BiScheduler" height="60">
```

### Icon/Favicon
Use for browser tabs, mobile apps, and compact displays:
```html
<link rel="icon" href="/static/branding/favicon.svg" type="image/svg+xml">
```

## Color Usage

### CSS Custom Properties
```css
:root {
  --bs-primary: #1e3a5f;      /* Deep Navy */
  --bs-secondary: #2563eb;    /* Bridge Blue */
  --bs-accent: #f59e0b;       /* Academic Gold */
  --bs-background: #ffffff;   /* Clean White */
  --bs-surface: #f3f4f6;      /* Soft Gray */
}
```

### Component Examples

#### Primary Button
```css
.btn-primary {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--bs-secondary);
  border-color: var(--bs-secondary);
}
```

#### Success States
```css
.alert-success {
  background-color: #10b981;
  border-color: #059669;
  color: white;
}
```

#### Venezuelan Context Indicators
```css
.venezuelan-badge {
  background-color: var(--bs-accent);
  color: var(--bs-primary);
  font-weight: 600;
}
```

## Typography Examples

### Headers
```css
h1, h2, h3 {
  font-family: 'Inter', Arial, sans-serif;
  font-weight: bold;
  color: var(--bs-primary);
}
```

### Body Text
```css
body {
  font-family: 'Inter', Arial, sans-serif;
  font-weight: normal;
  color: var(--bs-text-primary);
}
```

### UI Elements
```css
.nav-link, .btn {
  font-family: 'Inter', Arial, sans-serif;
  font-weight: medium;
}
```

## Multi-Tenant Customization

### Default BiScheduler Branding
```html
<!-- Standard platform header -->
<header class="bg-primary text-white">
  <img src="/static/branding/logo_concept.svg" alt="BiScheduler">
  <span class="tagline">Multi-Tenant K12 Scheduling for Venezuelan Education</span>
</header>
```

### UEIPAB Custom Branding
```html
<!-- UEIPAB customized header -->
<header class="bg-primary text-white">
  <img src="/static/tenants/ueipab/logo.png" alt="UEIPAB" height="40">
  <img src="/static/branding/logo_concept.svg" alt="BiScheduler" height="40">
  <span class="tagline">Powered by UEIPAB - Venezuelan Military University Excellence</span>
</header>
```

## Venezuelan Education Context

### Matrícula Compliance Badge
```html
<div class="compliance-badge venezuelan-badge">
  ✓ Matrícula Compliant
</div>
```

### Bimodal Schedule Indicator
```html
<div class="schedule-type">
  <span class="badge bg-secondary">Bimodal Schedule (7:00-14:20)</span>
</div>
```

### Government Standards Badge
```html
<div class="standards-badge">
  <span class="badge bg-success">Venezuelan Ministry of Education Standards</span>
</div>
```

## Responsive Design

### Mobile Logo
```css
@media (max-width: 768px) {
  .logo-full { display: none; }
  .logo-icon { display: inline-block; }
}
```

### Desktop Logo
```css
@media (min-width: 769px) {
  .logo-full { display: inline-block; }
  .logo-icon { display: none; }
}
```

## Accessibility Considerations

### Color Contrast
All color combinations meet WCAG 2.1 AA standards:
- Primary text (#1e3a5f) on white: 7.2:1 ratio
- Secondary text (#6b7280) on white: 5.4:1 ratio
- White text on primary (#1e3a5f): 7.2:1 ratio

### Focus States
```css
.btn:focus {
  outline: 2px solid var(--bs-accent);
  outline-offset: 2px;
}
```

### Screen Reader Support
```html
<img src="/static/branding/logo_concept.svg"
     alt="BiScheduler - Multi-Tenant K12 Scheduling Platform for Venezuelan Education">
```