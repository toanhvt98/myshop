import resourcesToBackend from "i18next-resources-to-backend";

// MUI Core Locales
import {
  frFR as frFRCore,
  viVN as viVNCore,
  zhCN as zhCNCore,
  arSA as arSACore,
} from "@mui/material/locale";
// MUI Date Pickers Locales
import {
  enUS as enUSDate,
  frFR as frFRDate,
  viVN as viVNDate,
  zhCN as zhCNDate,
} from "@mui/x-date-pickers/locales";
// MUI Data Grid Locales
import {
  enUS as enUSDataGrid,
  frFR as frFRDataGrid,
  viVN as viVNDataGrid,
  zhCN as zhCNDataGrid,
  arSD as arSDDataGrid,
} from "@mui/x-data-grid/locales";
import { CONFIG } from "@/global-config";

// ----------------------------------------------------------------------

// Supported languages
export const supportedLngs = ["en", "vi"];

// Fallback and default namespace
export const fallbackLng = "vi";
export const defaultNS = "common";

// Storage config
export const storageConfig = {
  cookie: { key: CONFIG.i18nextCookieName, autoDetection: false },
  localStorage: { key: "i18nextLng", autoDetection: false },
};

export const allLangs = [
  {
    value: "en",
    label: "English",
    countryCode: "GB",
    adapterLocale: "en",
    numberFormat: { code: "en-US", currency: "USD" },
    systemValue: {
      components: { ...enUSDate.components, ...enUSDataGrid.components },
    },
  },
  {
    value: "vi",
    label: "Vietnamese",
    countryCode: "VN",
    adapterLocale: "vi",
    numberFormat: { code: "vi-VN", currency: "VND" },
    systemValue: {
      components: {
        ...viVNCore.components,
        ...viVNDate.components,
        ...viVNDataGrid.components,
      },
    },
  },
];

// ----------------------------------------------------------------------

export const i18nResourceLoader = resourcesToBackend(
  (lang, namespace) => import(`./langs/${lang}/${namespace}.json`),
);

export function i18nOptions(lang = fallbackLng, namespace = defaultNS) {
  return {
    // debug: true,
    supportedLngs,
    fallbackLng,
    lng: lang,
    /********/
    fallbackNS: defaultNS,
    defaultNS,
    ns: namespace,
  };
}

export function getCurrentLang(lang) {
  const fallbackLang =
    allLangs.find((l) => l.value === fallbackLng) ?? allLangs[0];

  if (!lang) {
    return fallbackLang;
  }

  return allLangs.find((l) => l.value === lang) ?? fallbackLang;
}
