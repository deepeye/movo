import assert from 'node:assert/strict'
import { failureMessageKey } from '../src/features/execution-v3/domain/failureMessage'

assert.equal(
  failureMessageKey('DSH Runtime Host rejected the request: session "dsh-8bcdcfd7-f940-4f26-9bdf-2327c222184b" not found'),
  'execution.v3.failed_session_missing',
)
assert.equal(failureMessageKey('fetch failed'), 'execution.v3.failed_network')
assert.equal(failureMessageKey('model returned 429'), null)
