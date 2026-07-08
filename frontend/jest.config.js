/** @type {import('jest').Config} */
const nextJest = require("next/jest");

const createJestConfig = nextJest({
  // Points to the Next.js app directory
  dir: "./",
});

const config = {
  coverageProvider: "v8",
  testEnvironment: "jsdom",
  // Jest's correct option for setup files that run after the test framework
  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],
  // Handle module name aliases from tsconfig paths
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },
  testMatch: [
    "**/__tests__/**/*.[jt]s?(x)",
    "**/?(*.)+(spec|test).[jt]s?(x)",
  ],
  // Ignore Next.js internal files and node_modules
  testPathIgnorePatterns: ["/node_modules/", "/.next/"],
  // Collect coverage from source files only
  collectCoverageFrom: [
    "src/**/*.{ts,tsx}",
    "!src/**/*.d.ts",
    "!src/**/layout.tsx",
  ],
};

module.exports = createJestConfig(config);
