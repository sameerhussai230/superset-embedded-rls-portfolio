// src/components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error: error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("ERROR BOUNDARY CAUGHT ERROR:", error);
    console.error("ERROR BOUNDARY INFO:", errorInfo);
    this.setState({ errorInfo: errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div style={{ padding: '20px', border: '2px solid red', margin: '10px', backgroundColor: '#ffebeb' }}>
          <h2>Something went wrong embedding the dashboard.</h2>
          <details style={{ whiteSpace: 'pre-wrap', marginTop: '10px' }}>
            <summary>Error Details</summary>
            {this.state.error && <p><strong>Error:</strong> {this.state.error.toString()}</p>}
            {this.state.errorInfo && <p><strong>Stack Trace:</strong> {this.state.errorInfo.componentStack}</p>}
          </details>
          <p style={{marginTop: '10px'}}>Please check the browser console (F12) for more details and report the error.</p>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      );
    }

    // If no error, render children normally
    return this.props.children;
  }
}

export default ErrorBoundary;