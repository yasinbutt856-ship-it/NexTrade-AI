import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center justify-center min-h-[300px] text-gray-400 bg-dark-800/20 rounded-2xl p-8">
          <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="font-heading font-bold text-sm mb-1">Something went wrong</h3>
          <p className="text-xs text-gray-500 mb-4">{this.state.error?.message || "An unexpected error occurred"}</p>
          <button onClick={() => this.setState({ hasError: false })}
            className="text-xs bg-accent/10 text-accent px-4 py-2 rounded-lg border border-accent/20 hover:bg-accent/20 transition-colors"
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
