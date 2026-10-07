import { expect, test, type Page } from '@playwright/test';

const username = process.env.MOVO_E2E_USERNAME;
const password = process.env.MOVO_E2E_PASSWORD;
const expectedText = process.env.MOVO_E2E_EXPECTED_TEXT;
const composerSelector = 'textarea[placeholder="有问题，尽管问"]';

test.beforeAll(() => {
  if (!username || !password) {
    throw new Error('Set MOVO_E2E_USERNAME and MOVO_E2E_PASSWORD for a dedicated release-test user.');
  }
});

async function login(page: Page): Promise<void> {
  await page.goto('/');
  await expect(page.locator('#movo-login-username')).toBeVisible();
  await page.locator('#movo-login-username').fill(username!);
  await page.locator('#movo-login-password').fill(password!);
  await page.locator('button[type="submit"]').click();
  await expect(page.locator('#movo-login-username')).toBeHidden({ timeout: 30_000 });
  await expect(page.getByRole('button', { name: '新建对话' }).first()).toBeVisible();
}

test('基础回归：新建会话、多轮任务、刷新后保留会话', async ({ page }) => {
  test.setTimeout(180_000);
  await login(page);
  await page.getByRole('button', { name: '新建对话' }).first().click();

  const marker = String(Date.now());
  const task = `发布前浏览器验收 ${marker}：请只回复 MOVO_E2E_OK`;
  const composer = page.locator(composerSelector).first();
  await expect(composer).toBeVisible();
  const completion = page.waitForResponse(
    (response) => response.url().includes('/askai-api/api/chat/completions') && response.request().method() === 'POST',
    { timeout: 120_000 },
  );
  await composer.fill(task);
  await composer.press('Enter');
  const response = await completion;
  expect(response.ok(), `chat request returned HTTP ${response.status()}`).toBeTruthy();
  const sessionId = response.headers()['x-session-id'];
  expect(sessionId, 'chat response must contain X-Session-Id').toBeTruthy();

  await expect(page.locator('[class*="group/user-message"]').filter({ hasText: task })).toBeVisible();
  const answer = page.locator('.assistant-content').last();
  await expect(answer).not.toBeEmpty({ timeout: 120_000 });
  await expect(composer).toBeEnabled({ timeout: 120_000 });
  if (expectedText) await expect(answer).toContainText(expectedText);
  else await expect(answer).toContainText('MOVO_E2E_OK');

  const followUp = '请回忆上一轮任务中的数字标记，只回复该数字。';
  const secondCompletion = page.waitForResponse(
    (res) => res.url().includes('/askai-api/api/chat/completions') && res.request().method() === 'POST',
    { timeout: 120_000 },
  );
  await composer.fill(followUp);
  await composer.press('Enter');
  expect((await secondCompletion).ok()).toBeTruthy();
  await expect(page.locator('[class*="group/user-message"]').filter({ hasText: followUp })).toBeVisible();
  await expect(page.locator('.assistant-content')).toHaveCount(2, { timeout: 120_000 });
  await expect(composer).toBeEnabled({ timeout: 120_000 });
  if (!expectedText) await expect(page.locator('.assistant-content').last()).toContainText(marker);
  else await expect(page.locator('.assistant-content').last()).toContainText(expectedText);

  await page.reload();
  await expect(page.getByRole('button', { name: '新建对话' }).first()).toBeVisible();
  await page.getByRole('button', { name: '新建对话' }).first().click();
  const sessionResponse = page.waitForResponse(
    (res) => res.url().includes(`/askai-api/api/sessions/${sessionId}`) && res.request().method() === 'GET',
    { timeout: 30_000 },
  );
  await page.locator('[role="button"]').filter({ has: page.locator('[title^="发布前浏览器验收"]') }).first().click();
  expect((await sessionResponse).ok()).toBeTruthy();
  await expect(page.locator('[class*="group/user-message"]').filter({ hasText: task })).toBeVisible();
  await expect(page.locator('[class*="group/user-message"]').filter({ hasText: followUp })).toBeVisible();
  await expect(page.locator('.assistant-content')).toHaveCount(2);
  await expect(page.locator('.assistant-content').first()).toContainText(expectedText || 'MOVO_E2E_OK');
});
