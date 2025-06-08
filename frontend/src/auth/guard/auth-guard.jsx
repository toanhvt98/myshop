"use client";
import { usePathname, useRouter } from "@/routes/hooks";
import { useAuthContext } from "../hooks";
import { paths } from "@/routes/paths";
import { useEffect, useRef, useState } from "react";
import { LoadingScreen } from "@/components/loading";
export function AuthGuard({ children }) {
  const { loading, unauthenticated } = useAuthContext();
  const [isComponentLoading, setIsComponentLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();
  const createRedirectPath = (signinPath) => {
    const queryString = new URLSearchParams({ returnTo: pathname }).toString();
    return `${signinPath}?${queryString}`;
  };
  const checkAuthentication = () => {
    if (loading) return;
    if (unauthenticated) {
      const signinPath = paths.auth.signIn;
      router.replace(createRedirectPath(signinPath));
      return;
    }
    setIsComponentLoading(false);
  };
  useEffect(() => {
    checkAuthentication();
  }, [loading, unauthenticated]);
  if (isComponentLoading || loading) {
    return <LoadingScreen />;
  }
  return <>{children}</>;
}
