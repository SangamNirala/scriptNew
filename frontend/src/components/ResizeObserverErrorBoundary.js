import React from 'react';

class ResizeObserverErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Check if it's a ResizeObserver error
    if (error.message === 'ResizeObserver loop completed with undelivered notifications.') {
      // Don't update state, just return null to prevent the error from being thrown
      return null;
    }
    // For other errors, update state to show fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log only non-ResizeObserver errors
    if (error.message !== 'ResizeObserver loop completed with undelivered notifications.') {
      console.error('Component error caught:', error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
          <h2 className="text-lg font-semibold text-red-800">Something went wrong</h2>
          <p className="text-red-600">Please refresh the page and try again.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ResizeObserverErrorBoundary;