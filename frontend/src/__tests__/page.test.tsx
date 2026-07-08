/**
 * Unit tests for the Chronos Stadium AI landing page (/).
 * Tests key content, navigation, and accessibility attributes.
 */
import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

// Mock framer-motion to avoid animation issues in tests
jest.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
    section: ({ children, ...props }: React.HTMLAttributes<HTMLElement>) => (
      <section {...props}>{children}</section>
    ),
  },
}));

describe("Home page", () => {
  it("renders the main heading", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { name: /chronos stadium ai/i, level: 1 })
    ).toBeInTheDocument();
  });

  it("renders the hero tagline", () => {
    render(<Home />);
    expect(screen.getByText(/generative future engine/i)).toBeInTheDocument();
  });

  it("renders an Enter Dashboard nav link", () => {
    render(<Home />);
    // This link has aria-label="Enter the Chronos operations dashboard"
    const navLink = screen.getByRole("link", { name: /enter the chronos operations dashboard/i });
    expect(navLink).toBeInTheDocument();
    expect(navLink).toHaveAttribute("href", "/dashboard");
  });

  it("renders the Initialize Operations CTA link", () => {
    render(<Home />);
    // This link has aria-label "Initialize stadium operations — go to the dashboard"
    const cta = screen.getByRole("link", { name: /initialize stadium operations/i });
    expect(cta).toBeInTheDocument();
    expect(cta).toHaveAttribute("href", "/dashboard");
  });

  it("renders all three feature cards as articles", () => {
    render(<Home />);
    expect(screen.getByRole("article", { name: /feature: future simulation/i })).toBeInTheDocument();
    expect(screen.getByRole("article", { name: /feature: live intelligence/i })).toBeInTheDocument();
    expect(screen.getByRole("article", { name: /feature: proactive defense/i })).toBeInTheDocument();
  });

  it("has a navigation landmark", () => {
    render(<Home />);
    expect(screen.getByRole("navigation", { name: /main navigation/i })).toBeInTheDocument();
  });

  it("feature cards contain descriptive text", () => {
    render(<Home />);
    expect(
      screen.getByText(/continuously generates hundreds of possible operational scenarios/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/real-time tracking of crowd density/i)
    ).toBeInTheDocument();
    expect(
      screen.getByText(/identifies risks before they occur/i)
    ).toBeInTheDocument();
  });

  it("feature card headings are present", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: /future simulation/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /live intelligence/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /proactive defense/i })).toBeInTheDocument();
  });
});
