import { defineConfig, devices } from '@playwright/test';
import path from 'path';

// Server must start from the repo root so both /web/ and /data/ are reachable.
const repoRoot = __dirname;

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : 4, // Cap at 4 — Python http.server is single-threaded
  reporter: 'html',
  timeout: 30_000,

  use: {
    baseURL: 'http://localhost:8089/web/',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1280, height: 720 },
      },
    },
  ],

  webServer: {
    command: `python3 -m http.server 8089 --directory "${repoRoot}"`,
    url: 'http://localhost:8089/web/',
    reuseExistingServer: !process.env.CI,
    timeout: 10_000,
  },
});
