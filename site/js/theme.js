/* Phase 3: Advanced Theme System */

class ThemeManager {
  constructor() {
    this.currentTheme = 'dark';
    this.themes = {
      dark: {
        name: 'Dark',
        properties: {
          '--color-primary': '#00ff88',
          '--color-primary-dark': '#00cc6a',
          '--color-primary-light': '#33ff9f',
          '--color-secondary': '#0066ff',
          '--color-secondary-dark': '#0052cc',
          '--color-secondary-light': '#3385ff',
          '--color-accent': '#ff6600',
          '--color-accent-dark': '#cc5200',
          '--color-accent-light': '#ff8533',
          '--color-bg-primary': '#0a0a0a',
          '--color-bg-secondary': '#1a1a1a',
          '--color-bg-tertiary': '#2a2a2a',
          '--color-text-primary': '#ffffff',
          '--color-text-secondary': '#b0b0b0',
          '--color-text-tertiary': '#808080',
          '--color-border': '#333333',
          '--color-border-light': '#444444',
          '--color-success': '#00ff88',
          '--color-warning': '#ffaa00',
          '--color-error': '#ff4444',
          '--color-info': '#0066ff',
        },
      },
      light: {
        name: 'Light',
        properties: {
          '--color-primary': '#00aa5e',
          '--color-primary-dark': '#008a4d',
          '--color-primary-light': '#00cc6f',
          '--color-secondary': '#0052cc',
          '--color-secondary-dark': '#0042a3',
          '--color-secondary-light': '#1a66d9',
          '--color-accent': '#cc4400',
          '--color-accent-dark': '#a33600',
          '--color-accent-light': '#e55500',
          '--color-bg-primary': '#ffffff',
          '--color-bg-secondary': '#f8f9fa',
          '--color-bg-tertiary': '#e9ecef',
          '--color-text-primary': '#212529',
          '--color-text-secondary': '#6c757d',
          '--color-text-tertiary': '#adb5bd',
          '--color-border': '#dee2e6',
          '--color-border-light': '#e9ecef',
          '--color-success': '#28a745',
          '--color-warning': '#ffc107',
          '--color-error': '#dc3545',
          '--color-info': '#17a2b8',
        },
      },
      auto: {
        name: 'Auto',
        properties: {}, // Will be set based on system preference
      },
    };

    this.init();
  }

  init() {
    this.loadThemePreference();
    this.setupThemeToggle();
    this.setupSystemThemeDetection();
    this.applyTheme(this.currentTheme);
  }

  loadThemePreference() {
    const saved = localStorage.getItem('struct-theme');
    if (saved && this.themes[saved]) {
      this.currentTheme = saved;
    } else {
      // Default to auto theme
      this.currentTheme = 'auto';
    }
  }

  setupThemeToggle() {
    // Create theme toggle button
    const themeToggle = document.createElement('button');
    themeToggle.className = 'theme-toggle';
    themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
    themeToggle.setAttribute('aria-label', 'Toggle theme');
    themeToggle.setAttribute('title', 'Toggle theme (T)');

    // Add to navigation
    const navbar = document.querySelector('.navbar-content');
    if (navbar) {
      navbar.appendChild(themeToggle);
    }

    // Toggle functionality
    themeToggle.addEventListener('click', () => {
      this.cycleTheme();
    });

    // Keyboard shortcut (T)
    document.addEventListener('keydown', (e) => {
      if (e.key === 't' || e.key === 'T') {
        if (!e.target.matches('input, textarea')) {
          e.preventDefault();
          this.cycleTheme();
        }
      }
    });
  }

  setupSystemThemeDetection() {
    // Listen for system theme changes
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addListener(() => {
        if (this.currentTheme === 'auto') {
          this.applyAutoTheme();
        }
      });
    }
  }

  cycleTheme() {
    const themeOrder = ['dark', 'light', 'auto'];
    const currentIndex = themeOrder.indexOf(this.currentTheme);
    const nextIndex = (currentIndex + 1) % themeOrder.length;
    const nextTheme = themeOrder[nextIndex];

    this.setTheme(nextTheme);
  }

  setTheme(themeName) {
    if (!this.themes[themeName]) return;

    this.currentTheme = themeName;
    this.applyTheme(themeName);
    this.saveThemePreference();
    this.updateThemeToggle();
    this.announceThemeChange(themeName);

    // Track theme change
    if (window.structAnalytics) {
      window.structAnalytics.trackFeatureUsage('theme_change', {
        theme: themeName,
      });
    }
  }

  applyTheme(themeName) {
    const root = document.documentElement;

    if (themeName === 'auto') {
      this.applyAutoTheme();
    } else {
      const theme = this.themes[themeName];
      Object.entries(theme.properties).forEach(([property, value]) => {
        root.style.setProperty(property, value);
      });
    }

    // Update body class for theme-specific styles
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${themeName}`);

    // Update meta theme-color
    this.updateMetaThemeColor();
  }

  applyAutoTheme() {
    const prefersDark =
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches;
    const autoTheme = prefersDark ? 'dark' : 'light';

    const theme = this.themes[autoTheme];
    const root = document.documentElement;

    Object.entries(theme.properties).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });

    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-auto-${autoTheme}`);
  }

  updateThemeToggle() {
    const toggle = document.querySelector('.theme-toggle');
    if (!toggle) return;

    const icons = {
      dark: '<i class="fas fa-sun"></i>',
      light: '<i class="fas fa-moon"></i>',
      auto: '<i class="fas fa-adjust"></i>',
    };

    const titles = {
      dark: 'Switch to light theme',
      light: 'Switch to auto theme',
      auto: 'Switch to dark theme',
    };

    toggle.innerHTML = icons[this.currentTheme] || icons.dark;
    toggle.setAttribute('title', titles[this.currentTheme] || titles.dark);
  }

  updateMetaThemeColor() {
    const themeColorMeta = document.querySelector('meta[name="theme-color"]');
    if (themeColorMeta) {
      const bgColor = getComputedStyle(document.documentElement)
        .getPropertyValue('--color-bg-primary')
        .trim();
      themeColorMeta.setAttribute('content', bgColor);
    }
  }

  saveThemePreference() {
    localStorage.setItem('struct-theme', this.currentTheme);
  }

  announceThemeChange(themeName) {
    // Create accessible announcement
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = `Theme changed to ${this.themes[themeName].name}`;

    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  // Public API
  getCurrentTheme() {
    return this.currentTheme;
  }

  getAvailableThemes() {
    return Object.keys(this.themes);
  }

  // Custom theme creation
  createCustomTheme(name, properties) {
    this.themes[name] = {
      name: name.charAt(0).toUpperCase() + name.slice(1),
      properties: { ...properties },
    };
  }
}

// Theme toggle styles
const themeStyles = `
<style>
.theme-toggle {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-primary);
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: 1rem;
  font-size: 1rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-2px);
}

.theme-toggle:active {
  transform: translateY(0);
}

.theme-toggle i {
  transition: all 0.3s ease;
}

.theme-toggle:hover i {
  transform: rotate(15deg);
}

/* Screen reader only class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

/* Theme-specific adjustments */
.theme-light {
  --shadow-color: rgba(0, 0, 0, 0.1);
  --backdrop-blur: blur(10px);
}

.theme-dark {
  --shadow-color: rgba(0, 0, 0, 0.3);
  --backdrop-blur: blur(20px);
}

.theme-auto-light {
  --shadow-color: rgba(0, 0, 0, 0.1);
  --backdrop-blur: blur(10px);
}

.theme-auto-dark {
  --shadow-color: rgba(0, 0, 0, 0.3);
  --backdrop-blur: blur(20px);
}

/* Enhanced component styles for light theme */
.theme-light .hero {
  background: linear-gradient(135deg,
    var(--color-bg-primary) 0%,
    var(--color-bg-secondary) 100%);
}

.theme-light .card,
.theme-light .feature-card,
.theme-light .reference-card {
  box-shadow: 0 4px 20px var(--shadow-color);
}

.theme-light .navbar {
  backdrop-filter: var(--backdrop-blur);
  background: rgba(248, 249, 250, 0.9);
}

/* Dark theme enhancements */
.theme-dark .hero,
.theme-auto-dark .hero {
  background: radial-gradient(circle at 30% 20%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 70% 80%, rgba(0, 102, 255, 0.1) 0%, transparent 50%),
              var(--color-bg-primary);
}

.theme-dark .card,
.theme-dark .feature-card,
.theme-dark .reference-card,
.theme-auto-dark .card,
.theme-auto-dark .feature-card,
.theme-auto-dark .reference-card {
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(145deg,
    rgba(255, 255, 255, 0.02) 0%,
    rgba(255, 255, 255, 0.05) 100%);
}

/* Smooth theme transitions */
* {
  transition: background-color 0.3s ease,
              border-color 0.3s ease,
              color 0.3s ease,
              box-shadow 0.3s ease;
}

/* Respect user's motion preferences */
@media (prefers-reduced-motion: reduce) {
  .theme-toggle,
  .theme-toggle i {
    transition: none;
  }

  .theme-toggle:hover i {
    transform: none;
  }
}

@media (max-width: 768px) {
  .theme-toggle {
    margin-left: 0.5rem;
    width: 36px;
    height: 36px;
    font-size: 0.875rem;
  }
}
</style>
`;

// Initialize theme manager
document.addEventListener('DOMContentLoaded', () => {
  // Add theme styles
  document.head.insertAdjacentHTML('beforeend', themeStyles);

  // Initialize theme manager
  window.themeManager = new ThemeManager();
});
