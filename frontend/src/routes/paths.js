import { kebabCase } from "es-toolkit";

// ----------------------------------------------------------------------

const ROOTS = {
  AUTH: "/auth",
  DASHBOARD: "/dashboard",
};

// ----------------------------------------------------------------------

export const paths = {
  auth: {
    signIn: `${ROOTS.AUTH}/sign-in`,
    signUp: `${ROOTS.AUTH}/sign-up`,
    verifySignInOtp: `${ROOTS.AUTH}/verify-sign-in-otp`,
    requestSignInOtp: `${ROOTS.AUTH}/request-sign-in-otp`,
    forgotPassword: `${ROOTS.AUTH}/forgot-password`,
  },
};
