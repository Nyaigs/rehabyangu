import { Component, type ErrorInfo, type ReactNode } from 'react';
import { ErrorBanner } from './ErrorBanner';

type Props = { children: ReactNode };
type State = { error: Error | null };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State { return { error }; }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled application error', error, info);
  }

  render() {
    if (this.state.error) {
      return <main className="grid min-h-screen place-items-center bg-[#f7f9f8] p-6"><div className="w-full max-w-lg"><ErrorBanner onRetry={() => this.setState({ error: null })}>Something went wrong while loading this screen. Please try again.</ErrorBanner></div></main>;
    }
    return this.props.children;
  }
}
