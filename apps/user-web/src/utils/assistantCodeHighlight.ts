import hljs from 'highlight.js/lib/core'
import bash from 'highlight.js/lib/languages/bash'
import css from 'highlight.js/lib/languages/css'
import javascript from 'highlight.js/lib/languages/javascript'
import json from 'highlight.js/lib/languages/json'
import python from 'highlight.js/lib/languages/python'
import sql from 'highlight.js/lib/languages/sql'
import typescript from 'highlight.js/lib/languages/typescript'
import xml from 'highlight.js/lib/languages/xml'
import yaml from 'highlight.js/lib/languages/yaml'

const languages = { bash, css, javascript, json, python, sql, typescript, xml, yaml }
for (const [name, grammar] of Object.entries(languages)) hljs.registerLanguage(name, grammar)

const aliases: Record<string, keyof typeof languages> = {
  bash: 'bash', sh: 'bash', shell: 'bash', zsh: 'bash',
  css: 'css', scss: 'css',
  js: 'javascript', jsx: 'javascript', javascript: 'javascript',
  json: 'json', jsonc: 'json',
  py: 'python', python: 'python',
  sql: 'sql',
  ts: 'typescript', tsx: 'typescript', typescript: 'typescript',
  html: 'xml', xml: 'xml', vue: 'xml', svg: 'xml',
  yml: 'yaml', yaml: 'yaml',
}

export function highlightAssistantCode(code: string, language: string): string | null {
  const grammar = aliases[language.toLowerCase()]
  if (!grammar) return null
  try { return hljs.highlight(code, { language: grammar, ignoreIllegals: true }).value }
  catch { return null }
}
