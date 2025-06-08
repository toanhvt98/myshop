"use client";
import { BlinkBlur } from "react-loading-indicators";
import { styled } from "@mui/material/styles";
import { Portal } from "@mui/material";
import { Fragment } from "react";
export function LoadingScreen({ portal, sx, ...other }) {
  const PortalWrapper = portal ? Portal : Fragment;
  return (
    <PortalWrapper>
      <LoadingContent sx={{ ...sx }}>
        <BlinkBlur color={["#32cd32", "#327fcd", "#cd32cd", "#cd8032"]} variant="track-disc" speedPlus="2" easing="linear" />
      </LoadingContent>
    </PortalWrapper>
  );
}

const LoadingContent = styled("div")(({ theme }) => ({
  width: "100%",
  height: "100%",
  zIndex: 9998,
  flexGrow: 1,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  flexDirection: "column",
  backgroundColor: theme.vars.palette.background.default,

  position: "fixed",
  inset: 0,
}));
