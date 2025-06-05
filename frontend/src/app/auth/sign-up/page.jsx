import { getServerTranslations } from "@/locales/server";
import { CONFIG } from "@/global-config";

export async function generateMetadata() {
  const { t } = await getServerTranslations("metadata");
  return {
    title: t("sign_up_page_title", { appName: CONFIG.appName }),
    description: t("sign_up_page_description", { appName: CONFIG.appName }),
  };
}
export default function RegisterPage() {
  return <>abc</>;
}
