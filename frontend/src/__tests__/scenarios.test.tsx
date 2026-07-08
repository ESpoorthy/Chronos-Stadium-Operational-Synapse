/**
 * Unit tests for the Generative Scenario Engine page (/scenarios).
 * Tests input rendering, API integration, loading state, and error handling.
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Scenarios from "@/app/scenarios/page";
import * as api from "@/lib/api";

// Mock the API client
jest.mock("@/lib/api", () => ({
  ...jest.requireActual("@/lib/api"),
  runSimulation: jest.fn(),
}));

// Mock framer-motion
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

const mockRunSimulation = api.runSimulation as jest.MockedFunction<typeof api.runSimulation>;

const mockFutures = [
  {
    probability: 85,
    risk_score: 7.5,
    description: "High congestion at Gate C due to weather and crowd arrival.",
    operational_impact: "Severe",
    recommended_decision: "Open Gate D immediately.",
  },
  {
    probability: 40,
    risk_score: 4.0,
    description: "Crowd disperses evenly across Gates A and B.",
    operational_impact: "Low",
    recommended_decision: "Monitor situation.",
  },
];

describe("Scenarios page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the page heading", () => {
    render(<Scenarios />);
    expect(
      screen.getByRole("heading", { name: /generative scenario engine/i, level: 1 })
    ).toBeInTheDocument();
  });

  it("renders the query input with a label", () => {
    render(<Scenarios />);
    const input = screen.getByRole("textbox", { name: /scenario query/i });
    expect(input).toBeInTheDocument();
  });

  it("renders the Simulate button", () => {
    render(<Scenarios />);
    // Button accessible name comes from aria-label="Run simulation"
    expect(screen.getByRole("button", { name: /run simulation/i })).toBeInTheDocument();
  });

  it("Simulate button is disabled when input is empty", () => {
    render(<Scenarios />);
    const button = screen.getByRole("button", { name: /run simulation/i });
    expect(button).toBeDisabled();
  });

  it("Simulate button becomes enabled when text is entered", async () => {
    render(<Scenarios />);
    const input = screen.getByRole("textbox", { name: /scenario query/i });
    await userEvent.type(input, "What if it rains?");
    const button = screen.getByRole("button", { name: /run simulation/i });
    expect(button).not.toBeDisabled();
  });

  it("shows simulation results after successful API call", async () => {
    mockRunSimulation.mockResolvedValueOnce({
      futures: mockFutures,
      messages: ["Planner analyzed.", "Simulation complete."],
    });

    render(<Scenarios />);
    const input = screen.getByRole("textbox", { name: /scenario query/i });
    await userEvent.type(input, "What if heavy rain starts?");

    fireEvent.click(screen.getByRole("button", { name: /run simulation/i }));

    await waitFor(() => {
      expect(screen.getByText(/top ranked futures/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/High congestion at Gate C/i)).toBeInTheDocument();
    expect(screen.getByText(/Open Gate D immediately/i)).toBeInTheDocument();
  });

  it("displays an error alert when the API call fails", async () => {
    mockRunSimulation.mockRejectedValueOnce(
      new api.ApiError(500, "Simulation service unavailable.")
    );

    render(<Scenarios />);
    const input = screen.getByRole("textbox", { name: /scenario query/i });
    await userEvent.type(input, "What if the game goes to penalties?");

    fireEvent.click(screen.getByRole("button", { name: /run simulation/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });
    expect(screen.getByText(/simulation service unavailable/i)).toBeInTheDocument();
  });

  it("calls the API with the typed scenario", async () => {
    mockRunSimulation.mockResolvedValueOnce({ futures: mockFutures, messages: [] });

    render(<Scenarios />);
    const input = screen.getByRole("textbox", { name: /scenario query/i });
    await userEvent.type(input, "What if metro is delayed?");

    fireEvent.click(screen.getByRole("button", { name: /run simulation/i }));

    await waitFor(() => {
      expect(mockRunSimulation).toHaveBeenCalledWith(
        expect.objectContaining({
          scenario: "What if metro is delayed?",
        })
      );
    });
  });

  it("renders each future as an article", async () => {
    mockRunSimulation.mockResolvedValueOnce({ futures: mockFutures, messages: [] });

    render(<Scenarios />);
    const input = screen.getByRole("textbox", { name: /scenario query/i });
    await userEvent.type(input, "Test scenario");

    fireEvent.click(screen.getByRole("button", { name: /run simulation/i }));

    await waitFor(() => {
      const articles = screen.getAllByRole("article");
      expect(articles).toHaveLength(2);
    });
  });
});
