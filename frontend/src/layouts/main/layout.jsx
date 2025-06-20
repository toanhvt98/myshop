"use client";

import { useBoolean } from "minimal-shared/hooks";

import Box from "@mui/material/Box";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";

import { paths } from "@/routes/paths";
import { usePathname } from "@/routes/hooks";

import { CustomLogoText, Logo } from "@/components/logo";

import { NavMobile } from "./nav/mobile";
import { NavDesktop } from "./nav/desktop";
import { Footer, HomeFooter } from "./footer";
import { MenuButton } from "../components/menu-button";
import { navData as mainNavData } from "../nav-config-main";
import { SignInButton } from "../components/sign-in-button";
import { SettingsButton } from "../components/settings-button";
import { MainSection, LayoutSection, HeaderSection } from "../core";
import { LanguagePopover } from "@/components/language-popover";
import { allLangs } from "@/locales";

// ----------------------------------------------------------------------

export function MainLayout({ sx, cssVars, children, slotProps, layoutQuery = "md" }) {
  const pathname = usePathname();

  const { value: open, onFalse: onClose, onTrue: onOpen } = useBoolean();

  const isHomePage = pathname === "/";

  // const navData = slotProps?.nav?.data ?? mainNavData;

  const renderHeader = () => {
    const headerSlots = {
      topArea: (
        <Alert severity="info" sx={{ display: "none", borderRadius: 0 }}>
          This is an info Alert.
        </Alert>
      ),
      leftArea: (
        <>
          {/** @slot Nav mobile */}
          <MenuButton
            onClick={onOpen}
            sx={(theme) => ({
              mr: 1,
              ml: -1,
              [theme.breakpoints.up(layoutQuery)]: { display: "none" },
            })}
          />
          {/* <NavMobile data={navData} open={open} onClose={onClose} /> */}

          {/** @slot Logo */}
          {/* <Logo /> */}
          <CustomLogoText />
        </>
      ),
      rightArea: (
        <>
          {/** @slot Nav desktop */}
          {/* <NavDesktop
            data={navData}
            sx={(theme) => ({
              display: 'none',
              [theme.breakpoints.up(layoutQuery)]: { mr: 2.5, display: 'flex' },
            })}
          /> */}

          <Box sx={{ display: "flex", alignItems: "center", gap: { xs: 1, sm: 1.5 } }}>
            {/** @slot Sign in button */}
            <SignInButton />

            <SettingsButton />
            <LanguagePopover data={allLangs} />
          </Box>
        </>
      ),
    };

    return (
      <HeaderSection
        layoutQuery={layoutQuery}
        {...slotProps?.header}
        slots={{ ...headerSlots, ...slotProps?.header?.slots }}
        slotProps={slotProps?.header?.slotProps}
        sx={slotProps?.header?.sx}
      />
    );
  };

  const renderFooter = () =>
    isHomePage ? <HomeFooter sx={slotProps?.footer?.sx} /> : <Footer sx={slotProps?.footer?.sx} layoutQuery={layoutQuery} />;

  const renderMain = () => <MainSection {...slotProps?.main}>{children}</MainSection>;

  return (
    <LayoutSection
      /** **************************************
       * @Header
       *************************************** */
      headerSection={renderHeader()}
      /** **************************************
       * @Footer
       *************************************** */
      footerSection={renderFooter()}
      /** **************************************
       * @Styles
       *************************************** */
      cssVars={cssVars}
      sx={sx}
    >
      {renderMain()}
    </LayoutSection>
  );
}
