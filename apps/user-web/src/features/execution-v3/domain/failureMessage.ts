/** Keep host internals out of historical and live failure rows. */
export function failureMessageKey(message: string): string | null {
  if (/session "dsh-[^"]+" not found/i.test(message)) {
    return 'execution.v3.failed_session_missing'
  }
  if (/fetch failed|failed to fetch/i.test(message)) {
    return 'execution.v3.failed_network'
  }
  return null
}
