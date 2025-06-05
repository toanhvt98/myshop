import { getServerTranslations } from "@/locales/server";
import { CONFIG } from "@/global-config";

export async function generateMetadata() {
  const { t } = await getServerTranslations("metadata");
  return {
    title: t("forgot_password_page_title", { appName: CONFIG.appName }),
    description: t("forgot_password_page_description", {
      appName: CONFIG.appName,
    }),
  };
}

export default function ForgotPasswordPage() {
  return (
    <div>
      <h1>Forgot Password</h1>
    </div>
  );
}
