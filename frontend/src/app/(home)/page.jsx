import { MainSection } from "@/layouts/core";
import { getServerTranslations } from "@/locales/server";
import { CONFIG } from "@/global-config";

export async function generateMetadata() {
  const { t } = await getServerTranslations("metadata");
  return {
    title: t("home_page_title", { appName: CONFIG.appName }),
  };
}

export default function Home() {
  return <MainSection>abc </MainSection>;
}
