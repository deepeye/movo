import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'
import test from 'node:test'
import postcss from 'postcss'
import { isWindowsPlatform } from '../src/platform/windowsPlatform.ts'
import { naiveThemeOverrides, themeOverridesForPlatform } from '../src/composables/naiveThemeOverrides.ts'

test('Windows detection works in browsers and Electron without marking Mac', () => {
  assert.equal(isWindowsPlatform({ platform: 'Win32', userAgent: '' }), true)
  assert.equal(isWindowsPlatform({ platform: 'MacIntel', userAgent: '' }), false)
  assert.equal(isWindowsPlatform({ platform: '', userAgent: '', userAgentData: { platform: 'Windows' } }), true)
  assert.equal(isWindowsPlatform({ platform: '', userAgent: 'Mozilla/5.0 (Windows NT 10.0)' }), true)
  assert.equal(isWindowsPlatform({ platform: 'Linux x86_64', userAgent: '' }), false)
})

test('every shared Windows selector is platform- and theme-gated', () => {
  const directory = resolve(import.meta.dirname, '../src/styles/windows-dark')
  const files = readdirSync(directory).filter(name => name !== 'index.css' && name.endsWith('.css'))
  const indexCss = readFileSync(resolve(directory, 'index.css'), 'utf8')
  const imports = [...indexCss.matchAll(/@import '\.\/([^']+\.css)';/g)].map(match => match[1])
  assert.deepEqual(files.sort(), imports.sort())
  for (const file of files) {
    const root = postcss.parse(readFileSync(resolve(directory, file), 'utf8'), { from: file })
    root.walkRules(rule => {
      if (rule.parent?.type === 'atrule' && /keyframes$/i.test(rule.parent.name)) return
      for (const selector of rule.selectors) {
        assert.match(selector, /^html\.platform-windows(?:\.theme-dark|:not\(\.theme-dark\))(?:\b|[\s.#:[>+~])/, `${file}: ${selector}`)
      }
    })
  }
})

test('filled blue actions use white ink only on Windows dark', () => {
  assert.equal(themeOverridesForPlatform(false), naiveThemeOverrides)
  const overrides = themeOverridesForPlatform(true)
  assert.equal(overrides.Button.textColorPrimary, '#ffffff')
  assert.equal(overrides.Button.textColorHoverPrimary, '#ffffff')
  assert.equal(overrides.Button.textColorInfo, '#ffffff')
  assert.equal(overrides.Button.textColorTextPrimary, '#b9d3ff')
  assert.equal(overrides.Button.textColorGhostPrimary, '#b9d3ff')
})

test('dark callout surfaces and their strong text colors are paired', () => {
  const css = readFileSync(resolve(import.meta.dirname, '../src/styles/windows-dark/windows-dark-utilities-theme.css'), 'utf8')
  for (const className of ['bg-indigo-100', 'bg-violet-100', 'bg-amber-100', 'bg-emerald-50']) {
    assert.ok(css.includes(`.${className}`), `${className} needs a dark surface`)
  }
  for (const className of ['text-indigo-700', 'text-violet-600', 'text-amber-950', 'text-emerald-900']) {
    assert.ok(css.includes(`.${className}`), `${className} needs light ink`)
  }
})
