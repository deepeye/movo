/** Theme tokens shared by the app provider and messages shown outside its setup. */
export const naiveThemeOverrides = {
  common: {
    primaryColor: '#2563eb',
    primaryColorHover: '#1d4ed8',
    primaryColorPressed: '#1e40af',
    primaryColorSuppl: '#2563eb',
    infoColor: '#2563eb',
    infoColorHover: '#1d4ed8',
    infoColorPressed: '#1e40af',
    borderRadius: '12px',
  },
  Input: {
    caretColor: '#2563eb',
    borderHover: '#93c5fd',
    borderFocus: '#2563eb',
    boxShadowFocus: '0 0 0 2px rgba(37, 99, 235, 0.15)',
  },
  Select: {
    peers: {
      InternalSelection: {
        borderHover: '#93c5fd',
        borderFocus: '#2563eb',
        boxShadowFocus: '0 0 0 2px rgba(37, 99, 235, 0.15)',
      },
    },
  },
  Switch: {
    railColorActive: '#2563eb',
    railColorActiveHover: '#1d4ed8',
    buttonColor: '#ffffff',
    boxShadowFocus: '0 0 0 2px rgba(37, 99, 235, 0.18)',
  },
}

/** Naive's dark theme uses dark ink on filled primary buttons. The product
 * blue needs white ink; text, ghost and secondary buttons keep their own tokens. */
export function themeOverridesForPlatform(windowsDark: boolean) {
  if (!windowsDark) return naiveThemeOverrides
  const whiteInk = {
    textColorPrimary: '#ffffff',
    textColorHoverPrimary: '#ffffff',
    textColorPressedPrimary: '#ffffff',
    textColorFocusPrimary: '#ffffff',
    textColorDisabledPrimary: '#ffffff',
    textColorInfo: '#ffffff',
    textColorHoverInfo: '#ffffff',
    textColorPressedInfo: '#ffffff',
    textColorFocusInfo: '#ffffff',
    textColorDisabledInfo: '#ffffff',
    textColorTextPrimary: '#b9d3ff',
    textColorTextHoverPrimary: '#d5e5ff',
    textColorTextPressedPrimary: '#a9c8ff',
    textColorGhostPrimary: '#b9d3ff',
    textColorGhostHoverPrimary: '#d5e5ff',
    textColorGhostPressedPrimary: '#a9c8ff',
    textColorTextInfo: '#b9d3ff',
    textColorGhostInfo: '#b9d3ff',
  }
  return { ...naiveThemeOverrides, Button: whiteInk }
}
