import { CONFIG } from "@/global-config";
import { getServerTranslations } from "@/locales/server";
import { SignInView } from "@/auth/view/sign-in";

export async function generateMetadata() {
  const { t } = await getServerTranslations("metadata");
  return {
    title: t("sign_in_page_title", { appName: CONFIG.appName }),
    description: t("sign_in_page_description", { appName: CONFIG.appName }),
  };
}
export default function Page() {
  return <SignInView />;
}
