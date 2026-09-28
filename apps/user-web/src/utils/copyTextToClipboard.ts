interface ClipboardWriter {
  writeText(text: string): Promise<void>
}

interface ClipboardEnvironment {
  clipboard?: ClipboardWriter
  document?: Document
  secureContext?: boolean
}

function browserEnvironment(): ClipboardEnvironment {
  return {
    clipboard: typeof navigator === 'undefined' ? undefined : navigator.clipboard,
    document: typeof document === 'undefined' ? undefined : document,
    secureContext: typeof window === 'undefined' ? undefined : window.isSecureContext,
  }
}

function copyWithSelection(text: string, documentRef: Document): boolean {
  if (!documentRef.body || typeof documentRef.execCommand !== 'function') return false

  const activeElement = documentRef.activeElement as HTMLElement | null
  const textarea = documentRef.createElement('textarea')
  textarea.value = text
  textarea.readOnly = true
  textarea.setAttribute('aria-hidden', 'true')
  Object.assign(textarea.style, {
    position: 'fixed',
    inset: '0 auto auto -9999px',
    opacity: '0',
    pointerEvents: 'none',
  })
  documentRef.body.appendChild(textarea)

  try {
    textarea.focus()
    textarea.select()
    textarea.setSelectionRange(0, textarea.value.length)
    return documentRef.execCommand('copy')
  } finally {
    textarea.remove()
    activeElement?.focus?.()
  }
}

/** Copies text in secure browsers and desktop WebViews with a selection fallback. */
export async function copyTextToClipboard(
  text: string,
  environment: ClipboardEnvironment = browserEnvironment(),
): Promise<void> {
  if (environment.clipboard?.writeText) {
    try {
      await environment.clipboard.writeText(text)
      return
    } catch {
      // Desktop WebViews can expose the Clipboard API while denying write access.
    }
  }

  // An HTTP IP address is not a secure context. Chrome may report success from
  // the legacy copy command without updating the system clipboard.
  if (environment.secureContext === false) throw new Error('Clipboard write is unavailable in an insecure context')

  if (environment.document && copyWithSelection(text, environment.document)) return
  throw new Error('Clipboard write is unavailable')
}

export type { ClipboardEnvironment }
