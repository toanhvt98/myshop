import packageJson from "../package.json";

// ----------------------------------------------------------------------

export const CONFIG = {
  appName: process.env.NEXT_PUBLIC_SITE_NAME ?? "MyShop",
  appVersion: packageJson.version,
  serverApiUrl: process.env.NEXT_PUBLIC_SERVER_URL ?? "",
  assetsDir: process.env.NEXT_PUBLIC_ASSETS_DIR ?? "",
  isStaticExport: JSON.parse(process.env.BUILD_STATIC_EXPORT ?? "false"),
  /**
   * Auth
   * @method jwt | amplify | firebase | supabase | auth0
   */
  auth: {
    method: "jwt",
    redirectPath: "auth/sign-in",
    skip: false,
  },
  minLengthPassword: process.env.NEXT_PUBLIC_MIN_LENGTH_PASSWORD,
  otpLength: parseInt(process.env.NEXT_PUBLIC_OTP_LENGTH, 10),
  totpLength: parseInt(process.env.NEXT_PUBLIC_TOTP_DIGITS, 10),
  i18nextCookieName: process.env.NEXT_PUBLIC_I18NEXT_COOKIE_NAME,
};
