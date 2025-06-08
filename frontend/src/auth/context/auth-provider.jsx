"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import AuthContext from "@/auth/context/auth-context";
import { useLocalStorage } from "minimal-shared/hooks";
import { axiosClient, ENDPOINTS } from "@/libs";

export function AuthProvider({ children }) {
  const [state, setState] = useState({
    user: null,
    isLoading: true,
  });
  const {
    state: AuthUserData,
    setState: setAuthUserData,
    setField: setFieldAuthUserData,
  } = useLocalStorage("auth-user-data", {
    isAuthenticated: false,
    email: "",
    rememberMe: false,
  });

  const simulateSignin = useCallback(() => {
    setState({ user: { firstName: "a", lastName: "b" }, isLoading: false });
  }, []);

  const signIn = useCallback(async (data) => {
    try {
      const response = await axiosClient.post(ENDPOINTS.auth.signIn, data);
      if (response.data.enabled_2fa && response.data.enabled_2fa.length > 0) {
        setState({ ...state, user: null, isLoading: false });
      } else {
        setState({
          ...state,
          user: response.data,
          isLoading: false,
        });
      }
      return response.data;
    } catch (e) {
      setState({ ...state, user: null, isLoading: false });
      throw e;
    }
  }, []);

  const verifySignInOtp = useCallback(async (data) => {
    try {
      const response = await axiosClient.post(ENDPOINTS.auth.verifySignInOtp, data);
      setState({
        ...state,
        user: response.data,
        isLoading: false,
      });
    } catch (e) {
      setState({ ...state, user: null, isLoading: false });
      throw e.response.data.errors[0].detail;
    }
  }, []);

  const signUp = useCallback(async (data) => {
    try {
      const response = await axiosClient.post(ENDPOINTS.auth.signUp, data);
      setState({ ...state, user: response.data, isLoading: false });
      return response.data;
    } catch (e) {
      setState({ ...state, user: null, isLoading: false });
      throw e;
    }
  }, []);

  const checkUserSession = useCallback(async () => {
    if (AuthUserData.isAuthenticated) {
      //
    } else {
      setState({ user: null, isLoading: false });
    }
  }, []);

  useEffect(() => {
    checkUserSession();
    // eslint-disable-next-line
  }, []);

  const checkAuthenticated = state.user ? "authenticated" : "unauthenticated";
  const status = state.isLoading ? "loading" : checkAuthenticated;

  const memoizedValue = useMemo(
    () => ({
      user: state.user,
      checkUserSession,
      signIn,
      verifySignInOtp,
      setState,
      loading: status === "loading",
      authenticated: status === "authenticated",
      unauthenticated: status === "unauthenticated",

      simulateSignin,
    }),
    [state, state.user, setState, status, checkUserSession, signIn, verifySignInOtp, signUp]
  );
  return <AuthContext value={memoizedValue}>{children}</AuthContext>;
}
