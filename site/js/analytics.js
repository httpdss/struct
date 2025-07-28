/* Phase 3: Advanced Analytics & Performance Monitoring */

class StructAnalytics {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.startTime = Date.now();
    this.interactions = [];
    this.performanceMetrics = {};

    this.init();
  }

  init() {
    this.setupPerformanceMonitoring();
    this.setupUserInteractionTracking();
    this.setupVisibilityTracking();
    this.setupErrorTracking();
    this.startHeartbeat();
  }

  /* ===== PERFORMANCE MONITORING ===== */

  setupPerformanceMonitoring() {
    // Monitor Core Web Vitals
    this.monitorWebVitals();

    // Monitor resource loading
    this.monitorResourceLoading();

    // Monitor JavaScript execution time
    this.monitorJSPerformance();

    // Monitor scroll performance
    this.monitorScrollPerformance();
  }

  monitorWebVitals() {
    // First Contentful Paint (FCP)
    if (window.performance && window.performance.getEntriesByType) {
      const paintEntries = window.performance.getEntriesByType('paint');
      paintEntries.forEach((entry) => {
        if (entry.name === 'first-contentful-paint') {
          this.performanceMetrics.fcp = entry.startTime;
          this.reportMetric('core_web_vitals', 'fcp', entry.startTime);
        }
      });
    }

    // Largest Contentful Paint (LCP)
    if (window.PerformanceObserver) {
      try {
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          this.performanceMetrics.lcp = lastEntry.startTime;
          this.reportMetric('core_web_vitals', 'lcp', lastEntry.startTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {
        console.warn('LCP monitoring not supported:', e);
      }
    }

    // Cumulative Layout Shift (CLS)
    if (window.PerformanceObserver) {
      try {
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          this.performanceMetrics.cls = clsValue;
          this.reportMetric('core_web_vitals', 'cls', clsValue);
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
      } catch (e) {
        console.warn('CLS monitoring not supported:', e);
      }
    }

    // First Input Delay (FID)
    if (window.PerformanceObserver) {
      try {
        const fidObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            this.performanceMetrics.fid =
              entry.processingStart - entry.startTime;
            this.reportMetric(
              'core_web_vitals',
              'fid',
              this.performanceMetrics.fid
            );
          }
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
      } catch (e) {
        console.warn('FID monitoring not supported:', e);
      }
    }
  }

  monitorResourceLoading() {
    window.addEventListener('load', () => {
      const navigation = window.performance.getEntriesByType('navigation')[0];
      if (navigation) {
        this.performanceMetrics.pageLoadTime =
          navigation.loadEventEnd - navigation.fetchStart;
        this.performanceMetrics.domContentLoaded =
          navigation.domContentLoadedEventEnd - navigation.fetchStart;
        this.performanceMetrics.timeToInteractive =
          navigation.loadEventEnd - navigation.fetchStart;

        this.reportMetric(
          'performance',
          'page_load_time',
          this.performanceMetrics.pageLoadTime
        );
        this.reportMetric(
          'performance',
          'dom_content_loaded',
          this.performanceMetrics.domContentLoaded
        );
      }

      // Monitor resource timings
      const resources = window.performance.getEntriesByType('resource');
      const resourceMetrics = {
        css: [],
        js: [],
        images: [],
        fonts: [],
      };

      resources.forEach((resource) => {
        const loadTime = resource.responseEnd - resource.fetchStart;
        const resourceType = this.getResourceType(resource.name);

        if (resourceMetrics[resourceType]) {
          resourceMetrics[resourceType].push({
            url: resource.name,
            loadTime: loadTime,
            size: resource.transferSize || 0,
          });
        }
      });

      this.performanceMetrics.resources = resourceMetrics;
      this.reportResourceMetrics(resourceMetrics);
    });
  }

  monitorJSPerformance() {
    // Monitor long tasks
    if (window.PerformanceObserver) {
      try {
        const longTaskObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            this.reportMetric('performance', 'long_task', {
              duration: entry.duration,
              startTime: entry.startTime,
            });
          }
        });
        longTaskObserver.observe({ entryTypes: ['longtask'] });
      } catch (e) {
        console.warn('Long task monitoring not supported:', e);
      }
    }

    // Monitor function execution times
    this.originalFetch = window.fetch;
    window.fetch = (...args) => {
      const startTime = performance.now();
      return this.originalFetch.apply(window, args).then((response) => {
        const endTime = performance.now();
        this.reportMetric('performance', 'fetch_duration', {
          url: args[0],
          duration: endTime - startTime,
          status: response.status,
        });
        return response;
      });
    };
  }

  monitorScrollPerformance() {
    let scrollStartTime = null;
    let scrollCount = 0;

    const scrollHandler = this.throttle(() => {
      if (!scrollStartTime) {
        scrollStartTime = performance.now();
      }
      scrollCount++;
    }, 16); // 60fps

    const scrollEndHandler = this.debounce(() => {
      if (scrollStartTime) {
        const scrollDuration = performance.now() - scrollStartTime;
        this.reportMetric('interaction', 'scroll_performance', {
          duration: scrollDuration,
          events: scrollCount,
        });
        scrollStartTime = null;
        scrollCount = 0;
      }
    }, 150);

    window.addEventListener(
      'scroll',
      () => {
        scrollHandler();
        scrollEndHandler();
      },
      { passive: true }
    );
  }

  /* ===== USER INTERACTION TRACKING ===== */

  setupUserInteractionTracking() {
    this.trackClicks();
    this.trackFormInteractions();
    this.trackKeyboardShortcuts();
    this.trackTimeOnPage();
    this.trackScrollDepth();
  }

  trackClicks() {
    document.addEventListener('click', (e) => {
      const target = e.target.closest('a, button, [role="button"]');
      if (target) {
        this.recordInteraction('click', {
          element: this.getElementInfo(target),
          timestamp: Date.now(),
          coordinates: { x: e.clientX, y: e.clientY },
        });
      }
    });
  }

  trackFormInteractions() {
    document.addEventListener('submit', (e) => {
      const form = e.target;
      if (form.tagName === 'FORM') {
        this.recordInteraction('form_submit', {
          formId: form.id,
          formClass: form.className,
          timestamp: Date.now(),
        });
      }
    });

    // Track input focus
    document.addEventListener(
      'focus',
      (e) => {
        if (e.target.matches('input, textarea, select')) {
          this.recordInteraction('input_focus', {
            inputType: e.target.type,
            inputId: e.target.id,
            timestamp: Date.now(),
          });
        }
      },
      true
    );
  }

  trackKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey) {
        this.recordInteraction('keyboard_shortcut', {
          key: e.key,
          ctrlKey: e.ctrlKey,
          metaKey: e.metaKey,
          altKey: e.altKey,
          shiftKey: e.shiftKey,
          timestamp: Date.now(),
        });
      }
    });
  }

  trackTimeOnPage() {
    this.pageStartTime = Date.now();

    window.addEventListener('beforeunload', () => {
      const timeOnPage = Date.now() - this.pageStartTime;
      this.reportMetric('engagement', 'time_on_page', timeOnPage);
    });
  }

  trackScrollDepth() {
    let maxScrollDepth = 0;
    const trackPoints = [25, 50, 75, 90, 100];
    const trackedPoints = new Set();

    const scrollHandler = this.throttle(() => {
      const scrollTop = window.pageYOffset;
      const documentHeight =
        document.documentElement.scrollHeight - window.innerHeight;
      const scrollPercentage = Math.round((scrollTop / documentHeight) * 100);

      maxScrollDepth = Math.max(maxScrollDepth, scrollPercentage);

      trackPoints.forEach((point) => {
        if (scrollPercentage >= point && !trackedPoints.has(point)) {
          trackedPoints.add(point);
          this.recordInteraction('scroll_depth', {
            percentage: point,
            timestamp: Date.now(),
          });
        }
      });
    }, 100);

    window.addEventListener('scroll', scrollHandler, { passive: true });
  }

  /* ===== VISIBILITY TRACKING ===== */

  setupVisibilityTracking() {
    // Page visibility
    document.addEventListener('visibilitychange', () => {
      this.recordInteraction('visibility_change', {
        hidden: document.hidden,
        timestamp: Date.now(),
      });
    });

    // Element visibility using Intersection Observer
    this.setupElementVisibilityTracking();
  }

  setupElementVisibilityTracking() {
    const importantSections = document.querySelectorAll(`
      #features,
      #installation,
      #demos,
      #quick-reference,
      #api-preview,
      #wizard,
      #community,
      #testimonials,
      #project-showcase
    `);

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.recordInteraction('section_view', {
              sectionId: entry.target.id,
              intersectionRatio: entry.intersectionRatio,
              timestamp: Date.now(),
            });
          }
        });
      },
      {
        threshold: 0.5,
        rootMargin: '0px 0px -10% 0px',
      }
    );

    importantSections.forEach((section) => observer.observe(section));
  }

  /* ===== ERROR TRACKING ===== */

  setupErrorTracking() {
    // JavaScript errors
    window.addEventListener('error', (e) => {
      this.reportError('javascript_error', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        stack: e.error ? e.error.stack : null,
        timestamp: Date.now(),
      });
    });

    // Unhandled promise rejections
    window.addEventListener('unhandledrejection', (e) => {
      this.reportError('unhandled_promise_rejection', {
        reason: e.reason,
        timestamp: Date.now(),
      });
    });

    // Network errors (fetch failures)
    const originalFetch = window.fetch;
    window.fetch = (...args) => {
      return originalFetch.apply(window, args).catch((error) => {
        this.reportError('network_error', {
          url: args[0],
          error: error.message,
          timestamp: Date.now(),
        });
        throw error;
      });
    };
  }

  /* ===== FEATURE USAGE TRACKING ===== */

  trackFeatureUsage(featureName, details = {}) {
    this.recordInteraction('feature_usage', {
      feature: featureName,
      details: details,
      timestamp: Date.now(),
    });
  }

  /* ===== UTILITY METHODS ===== */

  getResourceType(url) {
    if (url.includes('.css')) return 'css';
    if (url.includes('.js')) return 'js';
    if (url.match(/\.(jpg|jpeg|png|gif|svg|webp)$/i)) return 'images';
    if (url.match(/\.(woff|woff2|ttf|otf)$/i)) return 'fonts';
    return 'other';
  }

  getElementInfo(element) {
    return {
      tagName: element.tagName,
      id: element.id,
      className: element.className,
      textContent: element.textContent?.slice(0, 100),
      href: element.href,
      type: element.type,
    };
  }

  recordInteraction(type, data) {
    this.interactions.push({
      type,
      data,
      sessionId: this.sessionId,
      timestamp: Date.now(),
    });

    // Batch send interactions
    if (this.interactions.length >= 10) {
      this.sendInteractions();
    }
  }

  reportMetric(category, metric, value) {
    // In a real implementation, this would send to your analytics service
    if (window.gtag) {
      window.gtag('event', metric, {
        event_category: category,
        value: typeof value === 'number' ? Math.round(value) : value,
        custom_map: { metric_1: 'performance_metric' },
      });
    }

    console.log(`📊 ${category}.${metric}:`, value);
  }

  reportResourceMetrics(metrics) {
    Object.entries(metrics).forEach(([type, resources]) => {
      if (resources.length > 0) {
        const avgLoadTime =
          resources.reduce((sum, r) => sum + r.loadTime, 0) / resources.length;
        const totalSize = resources.reduce((sum, r) => sum + r.size, 0);

        this.reportMetric('resources', `${type}_avg_load_time`, avgLoadTime);
        this.reportMetric('resources', `${type}_total_size`, totalSize);
      }
    });
  }

  reportError(type, error) {
    // In a real implementation, this would send to your error tracking service
    console.error(`🚨 ${type}:`, error);

    if (window.gtag) {
      window.gtag('event', 'exception', {
        description: `${type}: ${error.message || error.reason}`,
        fatal: false,
      });
    }
  }

  sendInteractions() {
    const interactions = [...this.interactions];
    this.interactions = [];

    // In a real implementation, send to your analytics endpoint
    console.log('📈 Sending interactions:', interactions);
  }

  startHeartbeat() {
    // Send interactions every 30 seconds
    setInterval(() => {
      if (this.interactions.length > 0) {
        this.sendInteractions();
      }
    }, 30000);

    // Send final batch on page unload
    window.addEventListener('beforeunload', () => {
      if (this.interactions.length > 0) {
        this.sendInteractions();
      }
    });
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  throttle(func, limit) {
    let inThrottle;
    return function () {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /* ===== PUBLIC API ===== */

  // Track custom events
  track(eventName, properties = {}) {
    this.recordInteraction('custom_event', {
      eventName,
      properties,
      timestamp: Date.now(),
    });
  }

  // Get current performance metrics
  getPerformanceMetrics() {
    return { ...this.performanceMetrics };
  }

  // Get session summary
  getSessionSummary() {
    return {
      sessionId: this.sessionId,
      duration: Date.now() - this.startTime,
      interactions: this.interactions.length,
      performanceMetrics: this.performanceMetrics,
    };
  }
}

// Initialize analytics
document.addEventListener('DOMContentLoaded', () => {
  window.structAnalytics = new StructAnalytics();

  // Track feature usage in existing components
  if (window.structPhase3) {
    const originalCopyToClipboard = window.structPhase3.copyToClipboard;
    window.structPhase3.copyToClipboard = function (text) {
      window.structAnalytics.trackFeatureUsage('copy_to_clipboard', {
        textLength: text.length,
      });
      return originalCopyToClipboard.call(this, text);
    };
  }

  // Track search usage
  if (window.advancedSearch) {
    const originalHandleSearch = window.advancedSearch.handleSearch;
    window.advancedSearch.handleSearch = function (e) {
      window.structAnalytics.trackFeatureUsage('search', {
        query: e.target.value,
      });
      return originalHandleSearch.call(this, e);
    };
  }
});
