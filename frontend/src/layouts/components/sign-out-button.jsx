import { useCallback } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

import Button from '@mui/material/Button';

import { useRouter } from '@/routes/hooks';

import { CONFIG } from '@/global-config';

import { toast } from '@/components/snackbar';

import { useAuthContext } from '@/auth/hooks';
import { signOut as jwtSignOut } from '@/auth/context/context/action';
import { signOut as amplifySignOut } from '@/auth/context/amplify/action';
import { signOut as supabaseSignOut } from '@/auth/context/supabase/action';
import { signOut as firebaseSignOut } from '@/auth/context/firebase/action';

// ----------------------------------------------------------------------

const signOut =
  (CONFIG.auth.method === 'supabase' && supabaseSignOut) ||
  (CONFIG.auth.method === 'firebase' && firebaseSignOut) ||
  (CONFIG.auth.method === 'amplify' && amplifySignOut) ||
  jwtSignOut;

// ----------------------------------------------------------------------

export function SignOutButton({ onClose, sx, ...other }) {
  const router = useRouter();

  const { checkUserSession } = useAuthContext();

  const { logout: signOutAuth0 } = useAuth0();

  const handleLogout = useCallback(async () => {
    try {
      await signOut();
      await checkUserSession?.();

      onClose?.();
      router.refresh();
    } catch (error) {
      console.error(error);
      toast.error('Unable to logout!');
    }
  }, [checkUserSession, onClose, router]);

  const handleLogoutAuth0 = useCallback(async () => {
    try {
      await signOutAuth0();

      onClose?.();
      router.refresh();
    } catch (error) {
      console.error(error);
      toast.error('Unable to logout!');
    }
  }, [onClose, router, signOutAuth0]);

  return (
    <Button
      fullWidth
      variant="soft"
      size="large"
      color="error"
      onClick={CONFIG.auth.method === 'auth0' ? handleLogoutAuth0 : handleLogout}
      sx={sx}
      {...other}
    >
      Logout
    </Button>
  );
}
