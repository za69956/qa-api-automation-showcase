import { defineConfig, devices } from '@playwright/test';

const PORT = 4173;

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1, // tests share one in-memory backend and reset it before each test
  retries: process.env.CI ? 1 : 0,
  forbidOnly: !!process.env.CI,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    // Video needs Playwright's ffmpeg; skipped when running against a local Chrome via PW_CHROME.
    video: process.env.PW_CHROME ? 'off' : 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Optional local override, e.g. PW_CHROME=/usr/bin/google-chrome; CI uses Playwright's own Chromium.
        launchOptions: process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {},
      },
    },
    {
      name: 'mobile-chrome',
      use: {
        ...devices['Pixel 7'],
        launchOptions: process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {},
      },
      testMatch: /ui\.spec\.ts/,
    },
  ],
  webServer: {
    command: 'node app/server.js',
    url: `http://localhost:${PORT}/api/summary`,
    reuseExistingServer: !process.env.CI,
    env: { PORT: String(PORT) },
  },
});
