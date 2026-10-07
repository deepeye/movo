import path from 'node:path';
import { defineConfig } from '@playwright/test';

const evidenceRoot = path.resolve(process.env.MOVO_E2E_EVIDENCE_DIR || 'evidence/release-smoke');

export default defineConfig({
  testDir: '.',
  testMatch: 'release-smoke.spec.ts',
  outputDir: path.join(evidenceRoot, 'results'),
  reporter: [['list'], ['html', { outputFolder: path.join(evidenceRoot, 'report'), open: 'never' }]],
  workers: 1,
  retries: 0,
  timeout: 180_000,
  use: {
    baseURL: process.env.MOVO_E2E_BASE_URL || 'http://127.0.0.1:3000',
    locale: 'zh-CN',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});
