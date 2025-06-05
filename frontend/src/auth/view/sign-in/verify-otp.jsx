"use client";
import { CONFIG } from "@/global-config";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { schemaVerifySignInOtp } from "@/auth/view/sign-in/schema";
import { useTranslate } from "@/locales";
import { useCallback } from "react";
import { FormHead } from "@/auth/components/form-head";
import Box from "@mui/material/Box";
import { Field, Form } from "@/components/hook-form";
import Button from "@mui/material/Button";
import { background } from "@/theme";
import { useAuthContext } from "@/auth/hooks";

export function VerifyOtp({ type, onClose }) {
  const { verifySignInOtp } = useAuthContext();
  const { t: translateErrorZod } = useTranslate("zod_fields_error");
  const { t: translateCommon } = useTranslate("common");
  const otpLength = type === "email" ? CONFIG.otpLength : CONFIG.totpLength;
  const headDescription =
    type === "email"
      ? translateCommon("description_enter_the_code_you_received_in_your_email")
      : translateCommon("description_enter_your_2fa_app_code");
  let defaultValues = {
    otp_type: type,
    otp_code: "",
  };
  const methods = useForm({
    resolver: zodResolver(schemaVerifySignInOtp(translateErrorZod)),
    defaultValues,
    mode: "onChange",
    reValidateMode: "onChange",
    shouldUnregister: false,
  });
  const {
    handleSubmit,
    register,
    watch,
    trigger,
    formState: { isSubmitting, isDirty, errors },
  } = methods;

  const onSubmit = useCallback(async (data) => {
    try {
      await verifySignInOtp(data);
    } catch (error) {
      console.error(error);
    }
  }, []);
  const renderFormVerify = () => (
    <Box
      sx={{
        display: "flex",
        gap: 5,
        flexDirection: "column",
        alignContent: "center",
        justifyContent: "center",
      }}
    >
      <Field.Code
        name={"otp_code"}
        placeholder={"*"}
        length={otpLength}
        sx={{
          justifyContent: "center",
        }}
        slotProps={{
          textField: {
            type: type === "email" ? "text" : "number",
            inputProps: {
              inputMode: "numeric",
              pattern: "[0-9]*",
            },
          },
        }}
      />
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          gap: 5,
          justifyContent: "space-between",
        }}
      >
        <Button
          fullWidth
          color={"primary"}
          type="submit"
          variant="contained"
          loading={isSubmitting}
          loadingIndicator={translateCommon("sign_in_button_loading_indicator")}
        >
          {translateCommon("verify")}
        </Button>
        <Button
          fullWidth
          variant={"outlined"}
          color={"inherit"}
          onClick={onClose}
        >
          {translateCommon("cancel")}
        </Button>
      </Box>
    </Box>
  );
  return (
    <>
      <FormHead
        description={
          <>
            {headDescription}{" "}
            {type === "email" && (
              <Button
                variant={"text"}
                color={"primary"}
                disableFocusRipple
                disableRipple
                sx={{ p: 0, "&:hover": { background: "none", border: "none" } }}
              >
                {translateCommon("resend-sign-in-otp")}
              </Button>
            )}
          </>
        }
      />
      <Form methods={methods} onSubmit={handleSubmit(onSubmit)}>
        {renderFormVerify()}
      </Form>
    </>
  );
}
