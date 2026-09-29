type PlatformNavigator = Pick<Navigator, 'platform' | 'userAgent'> & {
  userAgentData?: { platform?: string }
}

/** Keep Windows-only presentation fixes out of macOS and other web clients. */
export function isWindowsPlatform(navigatorInfo: PlatformNavigator): boolean {
  const reportedPlatform = navigatorInfo.userAgentData?.platform || navigatorInfo.platform
  if (reportedPlatform) return /^win(dows|32|64)?$/i.test(reportedPlatform)
  return /\bWindows\b/i.test(navigatorInfo.userAgent)
}
