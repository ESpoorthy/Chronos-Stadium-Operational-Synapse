/**
 * Typed API client for the Chronos Stadium AI backend.
 * All requests go through this module for consistent error handling.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Request / Response Types ──────────────────────────────────────────────

export interface StadiumData {
  crowd_density: number; // 0–100
  weather_condition: "clear" | "cloudy" | "light_rain" | "heavy_rain" | "storm" | "fog";
  transit_status: "normal" | "delayed" | "disrupted" | "closed";
  temperature_celsius: number;
  humidity_percent: number;
  active_gates: number;
}

export interface SimulateRequest {
  scenario: string;
  stadium_data: StadiumData;
}

export interface SimulatedFuture {
  probability: number;
  risk_score: number;
  description: string;
  operational_impact: string;
  recommended_decision: string;
}

export interface SimulateResponse {
  futures: SimulatedFuture[];
  messages: string[];
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ─── API Functions ─────────────────────────────────────────────────────────

/**
 * Run the multi-agent future simulation engine.
 * @throws {ApiError} on non-2xx HTTP responses
 */
export async function runSimulation(payload: SimulateRequest): Promise<SimulateResponse> {
  const response = await fetch(`${API_BASE_URL}/ai/simulate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(30_000), // 30s timeout
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new ApiError(response.status, errorBody.detail ?? "Simulation request failed.");
  }

  return response.json() as Promise<SimulateResponse>;
}

/**
 * Default stadium telemetry used when querying from the Scenarios page.
 * In production this would come from live sensor data.
 */
export const DEFAULT_STADIUM_DATA: StadiumData = {
  crowd_density: 72,
  weather_condition: "cloudy",
  transit_status: "normal",
  temperature_celsius: 21.0,
  humidity_percent: 60.0,
  active_gates: 4,
};
