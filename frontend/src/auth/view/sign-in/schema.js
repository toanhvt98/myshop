import { z as zod } from "zod";

import { CONFIG } from "@/global-config";

const totp_length = CONFIG.totpLength;
let otp_length = CONFIG.otpLength;

export const schemaSignIn = (t) =>
  zod.object({
    email: zod
      .string({
        required_error: t("zod_fields_error:email_is_required"),
      })
      .email({
        message: t("zod_fields_error:please_enter_a_valid_email_address"),
      }),
    password: zod
      .string({
        required_error: t("zod_fields_error:password_is_required"),
      })
      .min(CONFIG.minLengthPassword, {
        message: t("zod_fields_error:password_must_be_at_least_characters", {
          length: CONFIG.minLengthPassword,
        }),
      }),
    rememberMe: zod.boolean(),
  });
export const schemaVerifySignInOtp = (t) =>
  zod
    .object({
      otp_code: zod.string(),
      otp_type: zod.enum(["totp", "email"], {
        invalid_type_error: t("zod_fields_error:invalid_otp_type"),
      }),
    })
    .superRefine((data, ctx) => {
      const { otp_code, otp_type } = data;
      if (otp_type === "totp") {
        const totpRegex = new RegExp(`^\\d{${totp_length}}$`);
        if (!totpRegex.test(otp_code)) {
          ctx.addIssue({
            code: zod.ZodIssueCode.custom,
            message: t("zod_fields_error:invalid_totp_code", {
              length: totp_length,
            }),
            path: ["otp_code"],
          });
        }
      } else if (otp_type === "email") {
        const otpRegex = new RegExp(`^[a-zA-Z0-9]{${otp_length}}$`);
        if (!otpRegex.test(otp_code)) {
          ctx.addIssue({
            code: zod.ZodIssueCode.custom,
            message: t("zod_fields_error:invalid_otp_code", {
              length: otp_length,
            }),
            path: ["otp_code"],
          });
        }
      }
    });
