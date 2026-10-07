import assert from 'node:assert/strict'
import test from 'node:test'

import { resolvePresetModules } from '../src/official-host/preset-module-resolution.mjs'

const installation = {
  resolveDependency(name) {
    return `/installed/${name.replaceAll('/', '_')}`
  },
}

test('resolve package modules inside declarative preset groups without rewriting custom modules', () => {
  const source = [{ insert: [{
    id: 'preset-test', name: '@deepseek-ai/dsh-agent-preset',
    config: { id: 'test', plugins: [{
      id: 'group', group: true, config: [
        { id: 'native', name: '@deepseek-ai/dsh-tool-skill' },
        { id: 'custom', name: '/movo/custom-plugin.mjs' },
      ],
    }] },
  }] }]

  const result = resolvePresetModules(source, installation)
  assert.equal(result[0].insert[0].config.plugins[0].config[0].name, '/installed/@deepseek-ai_dsh-tool-skill')
  assert.equal(result[0].insert[0].config.plugins[0].config[1].name, '/movo/custom-plugin.mjs')
  assert.equal(source[0].insert[0].config.plugins[0].config[0].name, '@deepseek-ai/dsh-tool-skill')
})

test('drop unmounted schedule tools from shipped subagent deny list only', () => {
  const patches = [{ insert: [{
    id: 'preset-test', name: '@deepseek-ai/dsh-agent-preset',
    config: { id: 'test', plugins: [{
      id: 'tool-subagent', name: '@deepseek-ai/dsh-tool-subagent',
      config: { toolFilter: { deny: ['schedule_create', 'read', 'schedule_list'] } },
    }] },
  }] }]

  const result = resolvePresetModules(patches, installation)
  assert.deepEqual(result[0].insert[0].config.plugins[0].config.toolFilter.deny, ['read'])
})
