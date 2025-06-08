"use client";
import { useBoolean } from "@/hooks";
import { useAuthContext } from "@/auth/hooks";
import { useLocalStorage } from "minimal-shared/hooks";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { schemaSignIn } from "@/auth/view/sign-in/schema";
import { Field, Form } from "@/components/hook-form";
import Box from "@mui/material/Box";
import { useTranslate } from "@/locales";
import { FormHead } from "@/auth/components/form-head";
import { RouterLink } from "@/routes/components";
import Link from "@mui/material/Link";
import { paths } from "@/routes/paths";
import { Iconify } from "@/components/iconify";
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import Tooltip from "@mui/material/Tooltip";
import Button from "@mui/material/Button";
import { FormDivider } from "@/auth/components/form-divider";
import { VerifyDialog } from "@/auth/view/sign-in/view/verify-dialog";
import { useEffect, useState } from "react";

export function SignInView() {
  const { t: translateErrorZod, currentLang } = useTranslate("zod_fields_error");
  const { t: translateCommon } = useTranslate("common");
  const { value: isShowPassword, onToggle: toggleShowPassword } = useBoolean(false);

  const { value: isOpenDialogVerify, onTrue: onOpenDialogVerify, onFalse: onCloseDialogVerify } = useBoolean(false);

  const {
    state: AuthUserData,
    setState: setAuthUserData,
    setField: setFieldAuthUserData,
  } = useLocalStorage("auth-user-data", { isAuthenticated: false, email: "" });

  const [methodOtp, setMethodOtp] = useState([]);

  const { signIn, verifySignInOtp, verifyEnabled, simulateSignin } = useAuthContext();

  let defaultValues = {
    email: AuthUserData.rememberMe ? AuthUserData?.email || "" : "",
    password: "",
    rememberMe: AuthUserData?.rememberMe || false,
  };

  const methods = useForm({
    resolver: zodResolver(schemaSignIn(translateErrorZod)),
    defaultValues,
    mode: "onChange",
    reValidateMode: "onChange",
    shouldUnregister: false,
  });
  const {
    handleSubmit,
    register,
    trigger,
    watch,
    formState: { isSubmitting, isSubmitSuccessful, errors },
  } = methods;
  const { email: emailValue, password: passwordValue, rememberMe } = watch();
  const onSubmit = handleSubmit(async (data) => {
    // try {
    //   const response = await signIn(data);
    //   if (response.enabled_2fa && response.enabled_2fa.length > 0) {
    //     onOpenDialogVerify();
    //     setMethodOtp(response.enabled_2fa);
    //   }
    // } catch (e) {
    //   console.log(e);
    // }
    simulateSignin();
  });

  useEffect(() => {
    if (emailValue.length > 0) {
      trigger("email");
    }
    if (passwordValue.length > 0) {
      trigger("password");
    }
  }, [currentLang]);
  const renderSignInForm = () => (
    <Box sx={{ gap: 3, display: "flex", flexDirection: "column" }}>
      <Field.Text
        name={"email"}
        label={translateCommon("label_email_input")}
        placeholder={translateCommon("placeholder_email_input")}
        slotProps={{
          inputLabel: { shrink: true },
          input: {
            sx: {
              "& input": {
                paddingLeft: 1,
              },
            },
            startAdornment: <Iconify icon="custom:mail-fill" />,
          },
        }}
      />
      <Box sx={{ gap: 1, display: "flex", flexDirection: "column" }}>
        <Field.Text
          name={"password"}
          label={translateCommon("label_password_input")}
          placeholder={translateCommon("placeholder_password_input")}
          type={isShowPassword ? "text" : "password"}
          slotProps={{
            inputLabel: { shrink: true },
            input: {
              sx: {
                "& input": {
                  paddingLeft: 1,
                },
              },
              startAdornment: <Iconify icon="custom:lock-fill" />,
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={toggleShowPassword} edge="end">
                    <Iconify icon={isShowPassword ? "eva:eye-off-fill" : "eva:eye-fill"} />
                  </IconButton>
                </InputAdornment>
              ),
            },
          }}
        />
        <Box
          sx={{
            display: "flex",
            flexWrap: "wrap",
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Tooltip title={translateCommon("remember_me_tooltip")} placement="left">
            <Field.Checkbox name={"rememberMe"} label={translateCommon("remember_me_label")} />
          </Tooltip>
          <Link component={RouterLink} href={paths.auth.forgotPassword} variant="subtitle2" color="text.secondary">
            {translateCommon("forgot_password")}
          </Link>
        </Box>
      </Box>
      <Button
        fullWidth
        color="inherit"
        size="large"
        type="submit"
        variant="contained"
        loading={isSubmitting}
        loadingIndicator={translateCommon("sign_in_button_loading_indicator")}
      >
        {translateCommon("sign_in_button_label")}
      </Button>
    </Box>
  );

  return (
    <>
      <FormHead
        title={translateCommon("sign_in_page_title_form_head")}
        description={
          <>
            {translateCommon("sign_in_page_description_form_head")}
            <Link component={RouterLink} href={paths.auth.signUp} variant="subtitle2" sx={{ pl: 1 }}>
              {translateCommon("sign_up")}
            </Link>
          </>
        }
      />
      <Form methods={methods} onSubmit={onSubmit}>
        {renderSignInForm()}
      </Form>
      <FormDivider label={translateCommon("or")} />
      <Box
        sx={{
          gap: 3,
          display: "flex",
          flexWrap: "wrap",
          flexDirection: "row",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <Iconify width={40} icon={"socials:google"} sx={{ cursor: "pointer" }} onClick={() => console.log("google")} />
        <Iconify width={40} icon={"socials:facebook"} sx={{ cursor: "pointer" }} onClick={() => console.log("facebook")} />
        {/*<Iconify*/}
        {/*  width={40}*/}
        {/*  icon={"socials:github"}*/}
        {/*  sx={{ cursor: "pointer" }}*/}
        {/*  onClick={() => console.log("google")}*/}
        {/*/>*/}
        {/*<Iconify*/}
        {/*  width={40}*/}
        {/*  icon={"socials:twitter"}*/}
        {/*  sx={{ cursor: "pointer" }}*/}
        {/*  onClick={() => console.log("google")}*/}
        {/*/>*/}
      </Box>
      <VerifyDialog open={isOpenDialogVerify} onClose={onCloseDialogVerify} methodOtp={methodOtp} />
    </>
  );
}
