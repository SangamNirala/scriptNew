// ResizeObserver polyfill to prevent "loop completed with undelivered notifications" errors
// This wraps the native ResizeObserver to ensure callbacks execute asynchronously

(function() {
  if (typeof window === 'undefined' || !window.ResizeObserver) {
    return;
  }

  const OriginalResizeObserver = window.ResizeObserver;

  window.ResizeObserver = class ResizeObserver {
    constructor(callback) {
      // Wrap the callback to execute asynchronously using requestAnimationFrame
      const wrappedCallback = (entries, observer) => {
        requestAnimationFrame(() => {
          try {
            callback(entries, observer);
          } catch (error) {
            // Suppress ResizeObserver-related errors
            if (!error.message || !error.message.includes('ResizeObserver')) {
              throw error;
            }
          }
        });
      };

      this.originalObserver = new OriginalResizeObserver(wrappedCallback);
    }

    observe(target, options) {
      return this.originalObserver.observe(target, options);
    }

    unobserve(target) {
      return this.originalObserver.unobserve(target);
    }

    disconnect() {
      return this.originalObserver.disconnect();
    }
  };
})();