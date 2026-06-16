import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "../App";

function renderApp() {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

describe("App", () => {
  it("renders landing page on root route", () => {
    window.history.pushState({}, "", "/");
    renderApp();
    expect(screen.getByText(/NexTrade AI/i)).toBeInTheDocument();
  });
});
