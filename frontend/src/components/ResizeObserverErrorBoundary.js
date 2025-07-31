import React from 'react';

class ResizeObserverErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Check for ResizeObserver errors (common with Radix UI components)
    const resizeObserverErrors = [
      'ResizeObserver loop completed with undelivered notifications.',
      'ResizeObserver loop limit exceeded',
      'ResizeObserver loop completed with undelivered notifications'
    ];
    
    const isResizeObserverError = resizeObserverErrors.some(errorMsg => 
      error.message && error.message.includes('ResizeObserver')
    );
    
    if (isResizeObserverError) {
      // Don't update state for ResizeObserver errors - just suppress them
      return null;
    }
    
    // For other errors, show fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Only log non-ResizeObserver errors
    const isResizeObserverError = error.message && error.message.includes('ResizeObserver');
    
    if (!isResizeObserverError) {
      console.error('Component error caught:', error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
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