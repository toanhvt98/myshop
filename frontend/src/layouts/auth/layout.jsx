"use client";
import { merge } from "es-toolkit";
import { Logo } from "@/components/logo";
import { HeaderSection, LayoutSection, MainSection } from "@/layouts/core";
import { AuthCenteredContent } from "./content";
import { CONFIG } from "@/global-config";
import { SettingsButton } from "@/layouts/components/settings-button";
import { LanguagePopover } from "@/components/language-popover";
import { allLangs } from "@/locales";

export function AuthLayout({
  sx,
  cssVars,
  children,
  slotProps,
  layoutQuery = "md",
}) {
  const renderHeader = () => {
    const headerSlotProps = {
      // container: { maxWidth: false }
    };

    const headerSlots = {
      topArea: <></>,
      leftArea: (
        <>
          {/** @slot Logo */}
          <Logo />
        </>
      ),
      rightArea: (
        <>
          <SettingsButton />
          <LanguagePopover data={allLangs} />
        </>
      ),
    };

    return (
      <HeaderSection
        // disableElevation
        layoutQuery={layoutQuery}
        {...slotProps?.header}
        slots={{ ...headerSlots, ...slotProps?.header?.slots }}
        slotProps={merge(headerSlotProps, slotProps?.header?.slotProps ?? {})}
        sx={[
          { position: { [layoutQuery]: "fixed" } },
          ...(Array.isArray(slotProps?.header?.sx)
            ? (slotProps?.header?.sx ?? [])
            : [slotProps?.header?.sx]),
        ]}
      />
    );
  };
  const renderMain = () => (
    <MainSection
      {...slotProps?.main}
      sx={[
        (theme) => ({
          alignItems: "center",
          position: "relative",
          width: "100%",
          height: "100%",
          overflow: "hidden",
          zIndex: 1,
          p: theme.spacing(3, 2, 10, 2),
          [theme.breakpoints.up(layoutQuery)]: {
            justifyContent: "center",
            p: theme.spacing(10, 0, 10, 0),
          },
        }),

        ...(Array.isArray(slotProps?.main?.sx)
          ? (slotProps?.main?.sx ?? [])
          : [slotProps?.main?.sx]),
      ]}
    >
      <AuthCenteredContent {...slotProps?.content}>
        {children}
      </AuthCenteredContent>
    </MainSection>
  );
  return (
    <LayoutSection
      /** **************************************
       * @Header
       *************************************** */
      headerSection={renderHeader()}
      /** **************************************
       * @Footer
       *************************************** */
      // footerSection={renderFooter()}
      /** **************************************
       * @Styles
       *************************************** */
      cssVars={{ "--layout-auth-content-width": "420px", ...cssVars }}
      sx={[
        (theme) => ({
          position: "relative",
          "&::before": backgroundStyles(theme),
        }),
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
    >
      {renderMain()}
    </LayoutSection>
  );
}

const backgroundStyles = (theme, visible = true) => ({
  ...theme.mixins.bgGradient({
    images: [
      `url(${CONFIG.assetsDir}/assets/background/background-3-blur.webp)`,
    ],
  }),
  zIndex: 1,
  display: visible ? "block" : "none",
  opacity: 0.24,
  width: "100%",
  height: "100%",
  content: "''",
  position: "absolute",
  ...theme.applyStyles("dark", {
    opacity: 0.08,
  }),
});
