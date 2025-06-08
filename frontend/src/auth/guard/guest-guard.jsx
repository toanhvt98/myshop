"use client";
import { usePathname, useRouter, useSearchParams } from "@/routes/hooks";
import { useAuthContext } from "../hooks";
import { useEffect, useState, useRef } from "react";
import { CONFIG } from "@/global-config";
import { paths } from "@/routes/paths";
import { LoadingScreen } from "@/components/loading";
export function GuestGuard({ children }) {
  const { loading, authenticated } = useAuthContext();
  const [isComponentLoading, setIsComponentLoading] = useState(true);
  const searchParams = useSearchParams();
  const returnTo = searchParams.get("returnTo") || CONFIG.auth.redirectPath;
  const router = useRouter();
  //   const pathname = usePathname();
  //   const savedReturnTo = useRef(returnTo);

  const checkAuthentication = () => {
    if (loading) return;
    if (authenticated) {
      router.replace(returnTo, { shallow: true });
      return;
    }
    setIsComponentLoading(false);
  };

  useEffect(() => {
    checkAuthentication();
  }, [loading, authenticated]);

  if (isComponentLoading) {
    return <LoadingScreen />;
  }
  return <>{children}</>;
}
