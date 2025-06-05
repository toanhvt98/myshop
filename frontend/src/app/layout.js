import "@/global.css";

import InitColorSchemeScript from "@mui/material/InitColorSchemeScript";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";

import { CONFIG } from "@/global-config";
import { primary } from "@/theme/core/palette";
import { LocalizationProvider } from "@/locales";
import { detectLanguage } from "@/locales/server";
import { themeConfig, ThemeProvider } from "@/theme";
import { I18nProvider } from "@/locales/i18n-provider";

import { Snackbar } from "@/components/snackbar";
import { ProgressBar } from "@/components/progress-bar";
// import { MotionLazy } from '@/components/animate/motion-lazy';
import { detectSettings } from "@/components/settings/server";
import {
  SettingsDrawer,
  defaultSettings,
  SettingsProvider,
} from "@/components/settings";
import { MotionLazy } from "@/components/animate/motion-lazy";
import { AuthProvider } from "@/auth/context";

// import { CheckoutProvider } from '@/sections/checkout/context';

// ----------------------------------------------------------------------

// ----------------------------------------------------------------------

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: primary.main,
};

// ----------------------------------------------------------------------

export const metadata = {
  icons: [
    {
      rel: "icon",
      url: `${CONFIG.assetsDir}/favicon.ico`,
    },
  ],
};

async function getAppConfig() {
  if (CONFIG.isStaticExport) {
    return {
      lang: "en",
      i18nLang: undefined,
      cookieSettings: undefined,
      dir: defaultSettings.direction,
    };
  } else {
    const [lang, settings] = await Promise.all([
      detectLanguage(),
      detectSettings(),
    ]);

    return {
      lang,
      i18nLang: lang,
      cookieSettings: settings,
      dir: settings.direction,
    };
  }
}

// ----------------------------------------------------------------------

export default async function RootLayout({ children }) {
  const appConfig = await getAppConfig();

  return (
    <html lang={appConfig.lang} dir={appConfig.dir} suppressHydrationWarning>
      <body>
        <InitColorSchemeScript
          modeStorageKey={themeConfig.modeStorageKey}
          attribute={themeConfig.cssVariables.colorSchemeSelector}
          defaultMode={themeConfig.defaultMode}
        />

        <I18nProvider lang={appConfig.i18nLang}>
          <SettingsProvider
            cookieSettings={appConfig.cookieSettings}
            defaultSettings={defaultSettings}
          >
            <LocalizationProvider>
              <AppRouterCacheProvider options={{ key: "css" }}>
                <ThemeProvider
                  modeStorageKey={themeConfig.modeStorageKey}
                  defaultMode={themeConfig.defaultMode}
                >
                  <MotionLazy>
                    <AuthProvider>
                      <Snackbar />
                      <ProgressBar />
                      <SettingsDrawer defaultSettings={defaultSettings} />
                      {children}
                    </AuthProvider>
                  </MotionLazy>
                </ThemeProvider>
              </AppRouterCacheProvider>
            </LocalizationProvider>
          </SettingsProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
