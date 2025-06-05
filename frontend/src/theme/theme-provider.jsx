"use client";

import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider as ThemeVarsProvider } from "@mui/material/styles";

import { useTranslate } from "@/locales";

import { useSettingsContext } from "@/components/settings";

import { createTheme } from "./create-theme";
import { Rtl } from "./with-settings/right-to-left";
import GlobalStyles from "@mui/material/GlobalStyles";

// ----------------------------------------------------------------------

export function ThemeProvider({ themeOverrides, children, ...other }) {
  const settings = useSettingsContext();
  const { currentLang } = useTranslate();

  const theme = createTheme({
    settingsState: settings.state,
    localeComponents: currentLang?.systemValue,
    themeOverrides,
  });

  const globalAutoFillStyles = () => ({
    "input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus, input:-webkit-autofill:active":
      {
        WebkitBoxShadow:
          "0 0 0px 1000px var(--mui-palette-background-paper) inset !important",
        WebkitTextFillColor: "var(--mui-palette-text-primary) !important",
        backgroundColor: "transparent !important", //
        transition: "background-color 9999s ease-in-out 0s !important",
      },
  });

  return (
    <ThemeVarsProvider disableTransitionOnChange theme={theme} {...other}>
      <CssBaseline />
      <GlobalStyles styles={globalAutoFillStyles()} />
      <Rtl direction={settings.state.direction}>{children}</Rtl>
    </ThemeVarsProvider>
  );
}
