import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import test from 'node:test'
import { compileStyle, parse } from '@vue/compiler-sfc'

const componentsDirectory = resolve(import.meta.dirname, '../src/components')

function vueFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const path = join(directory, entry.name)
    return entry.isDirectory() ? vueFiles(path) : entry.name.endsWith('.vue') ? [path] : []
  })
}

test('dark selectors in scoped components retain their target after Vue compilation', () => {
  for (const file of vueFiles(componentsDirectory)) {
    const source = readFileSync(file, 'utf8')
    assert.doesNotMatch(source, /:global\(html\.(?:theme-dark|platform-windows)\)\s+[^,{]+/, file)
    assert.doesNotMatch(source, /:global\(html\.theme-dark\s+(?:header|footer|main|nav|textarea)(?:[\s:)]|$)/, `${file}: dark rules must be scoped to a component`)
  }

  const file = join(componentsDirectory, 'code/GitBranchSelector.vue')
  const { descriptor } = parse(readFileSync(file, 'utf8'), { filename: file })
  const style = descriptor.styles.find(block => block.scoped)
  assert.ok(style)
  const result = compileStyle({ source: style.content, filename: file, id: 'branch-selector-test', scoped: true })
  assert.deepEqual(result.errors, [])
  assert.match(result.code, /html\.theme-dark \.branch-selector/)
  assert.match(result.code, /html\.theme-dark \.branch-search/)

  const picker = join(componentsDirectory, 'code/BranchContextPicker.vue')
  const pickerStyle = parse(readFileSync(picker, 'utf8'), { filename: picker }).descriptor.styles.find(block => block.scoped)
  assert.ok(pickerStyle)
  const pickerResult = compileStyle({ source: pickerStyle.content, filename: picker, id: 'branch-picker-test', scoped: true })
  assert.deepEqual(pickerResult.errors, [])
  assert.match(pickerResult.code, /html\.theme-dark \.branch-popover/)
})
