"use client";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { useTranslate } from "@/locales";
import IconButton from "@mui/material/IconButton";
import { Iconify } from "@/components/iconify";
import { useState } from "react";
import Box from "@mui/material/Box";
import Backdrop from "@mui/material/Backdrop";
import { VerifyOtp } from "@/auth/view/sign-in/verify-otp";

export function VerifyDialog({ open, onClose, sx, methodOtp = [] }) {
  const { t } = useTranslate("common");
  const listMethodsSortedByPriority = methodOtp.sort((a, b) => {
    if (a.is_priority === true && b.is_priority === false) {
      return -1;
    }
    if (a.is_priority === false && b.is_priority === true) {
      return 1;
    }
    return 0;
  });
  const [value, setValue] = useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      fullWidth
      maxWidth="sm"
      scroll="body"
      sx={{
        "& .MuiDialog-paper": { position: "relative", overflow: "visible" },
      }}
      slots={{ backdrop: Backdrop }}
      slotProps={{
        backdrop: {
          sx: {
            backdropFilter: "blur(2px)",
            WebkitBackdropFilter: "blur(2px)",
          },
        },
      }}
    >
      <IconButton
        sx={{
          position: "absolute",
          right: -15,
          top: -15,
          p: 0.5,
          color: "inherit",
          backgroundColor: (theme) => theme.vars.palette.background.paper,
          "&:hover": {
            backgroundColor: (theme) => theme.vars.palette.background.paper,
          },
        }}
        onClick={onClose}
      >
        <Iconify width={25} icon="mingcute:close-line" />
      </IconButton>
      <DialogTitle sx={{ textAlign: "center" }}>
        {t("dialog_verify_sign_in_code_title")}
      </DialogTitle>

      <DialogContent>
        <Tabs value={value} onChange={handleChange} variant="fullWidth">
          {listMethodsSortedByPriority.map((item, index) => (
            <Tab label={item.display} key={index} />
          ))}
        </Tabs>
        {listMethodsSortedByPriority.map((item, index) => (
          <Box
            sx={{
              alignItems: "center",
              display: value === index ? "block" : "none",
              p: { xs: 2, md: 5 },
            }}
            key={index}
          >
            <VerifyOtp type={item.type} onClose={onClose} />
          </Box>
        ))}
      </DialogContent>
    </Dialog>
  );
}
