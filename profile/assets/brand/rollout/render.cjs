// Run with installed Playwright on NODE_PATH; no browser accounts or live org writes.
const { chromium } = require('playwright');
const { readFileSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');
const { pathToFileURL } = require('node:url');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');

(async () => {
  const checks = JSON.parse(readFileSync(join(__dirname, 'checks.json')));
  const profile = readFileSync(join(__dirname, '../../../README.md'));
  assert.equal(createHash('sha256').update(profile).digest('hex'), checks.profile_sha256, 'Stale checks');
  assert(readFileSync(join(__dirname, 'preview.html'), 'utf8').includes(`content="${checks.profile_sha256}"`), 'Stale preview');
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_BIN || '/run/current-system/sw/bin/google-chrome-stable',
    headless: true,
  });
  try {
    const results = await Promise.all(['light', 'dark'].flatMap(theme => [1280, 360].map(async width => {
      const context = await browser.newContext({ colorScheme: theme, viewport: { width, height: 960 }, deviceScaleFactor: 1 });
      const page = await context.newPage();
      // A local-only render: no browser account, network font, tracking or third-party image.
      await page.route('https://**/*', route => route.abort());
      await page.goto(pathToFileURL(join(__dirname, 'preview.html')).href);
      await page.evaluate(() => document.fonts.ready);
      await page.locator('main img').evaluateAll(images => Promise.all(images.map(img => img.decode())));
      const evidence = await page.evaluate(() => ({
        viewport: innerWidth,
        contentWidth: document.documentElement.scrollWidth,
        images: [...document.querySelectorAll('main img')].map(img => ({
          alt: img.alt, source: img.currentSrc.split('/').pop(),
          loaded: img.complete && img.naturalWidth > 0, naturalWidth: img.naturalWidth,
          displayedWidth: img.getBoundingClientRect().width,
        })),
        links: [...document.querySelectorAll('main li strong a')].map(a => a.href),
      }));
      assert(evidence.contentWidth <= width, `Horizontal overflow: ${theme}/${width}`);
      assert(evidence.images.every(img => img.loaded && img.alt), 'Missing image/alt');
      assert(evidence.images[0].source === `logo-wordmark-${theme}.svg`, 'Wrong wordmark theme');
      assert.equal(evidence.links.length, 6, 'Six flagship links must survive Markdown sanitization');
      if (checks.mode === 'final-art') {
        const proof = JSON.parse(readFileSync(join(__dirname, 'art-provenance.json')));
        assert(evidence.images.some(img => img.source === proof.file), 'Final GPT image not rendered');
      }
      const screenshot = `${checks.mode}-${width}-${theme}.png`;
      await page.screenshot({ path: join(__dirname, screenshot), fullPage: true });
      // A failed image must not erase the project choices.
      await page.locator('main img').evaluateAll(images => images.forEach(img => img.remove()));
      assert.equal(await page.locator('main li strong a').count(), 6);
      assert(await page.locator('main h1').isVisible());
      await context.close();
      return { theme, mode: checks.mode, profile_sha256: checks.profile_sha256, ...evidence, screenshot, imageFailureNavigation: 'pass' };
    })));
    writeFileSync(join(__dirname, 'renders.json'), JSON.stringify(results, null, 2) + '\n');
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
