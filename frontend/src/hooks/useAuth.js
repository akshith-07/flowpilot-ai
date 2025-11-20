import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useCallback } from 'react';
import {
  loginUser,
  registerUser,
  logoutUser,
  requestPasswordReset,
  resetPassword,
  setupMFA,
  verifyMFA,
  disableMFA,
  fetchCurrentUser,
} from '@/store/slices/authSlice';
import { ROUTES } from '@/constants/routes';

/**
 * Custom hook for authentication
 * Provides auth state and actions
 */
export const useAuth = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const {
    user,
    isAuthenticated,
    loading,
    error,
    mfaRequired,
    mfaSetupData,
  } = useSelector((state) => state.auth);

  const login = useCallback(
    async (credentials) => {
      const result = await dispatch(loginUser(credentials));
      if (loginUser.fulfilled.match(result)) {
        navigate(ROUTES.DASHBOARD);
        return { success: true };
      }
      return { success: false, error: result.error.message };
    },
    [dispatch, navigate]
  );

  const register = useCallback(
    async (userData) => {
      const result = await dispatch(registerUser(userData));
      if (registerUser.fulfilled.match(result)) {
        navigate(ROUTES.DASHBOARD);
        return { success: true };
      }
      return { success: false, error: result.error.message };
    },
    [dispatch, navigate]
  );

  const logout = useCallback(async () => {
    await dispatch(logoutUser());
    navigate(ROUTES.LOGIN);
  }, [dispatch, navigate]);

  const forgotPassword = useCallback(
    async (email) => {
      const result = await dispatch(requestPasswordReset(email));
      return requestPasswordReset.fulfilled.match(result)
        ? { success: true }
        : { success: false, error: result.error.message };
    },
    [dispatch]
  );

  const resetUserPassword = useCallback(
    async (token, password) => {
      const result = await dispatch(resetPassword({ token, password }));
      if (resetPassword.fulfilled.match(result)) {
        navigate(ROUTES.LOGIN);
        return { success: true };
      }
      return { success: false, error: result.error.message };
    },
    [dispatch, navigate]
  );

  const enableMFA = useCallback(async () => {
    const result = await dispatch(setupMFA());
    return setupMFA.fulfilled.match(result)
      ? { success: true, data: result.payload }
      : { success: false, error: result.error.message };
  }, [dispatch]);

  const verifyMFACode = useCallback(
    async (code) => {
      const result = await dispatch(verifyMFA(code));
      return verifyMFA.fulfilled.match(result)
        ? { success: true }
        : { success: false, error: result.error.message };
    },
    [dispatch]
  );

  const disableMFACode = useCallback(
    async (password) => {
      const result = await dispatch(disableMFA(password));
      return disableMFA.fulfilled.match(result)
        ? { success: true }
        : { success: false, error: result.error.message };
    },
    [dispatch]
  );

  const refreshUser = useCallback(async () => {
    await dispatch(fetchCurrentUser());
  }, [dispatch]);

  return {
    user,
    isAuthenticated,
    loading,
    error,
    mfaRequired,
    mfaSetupData,
    login,
    register,
    logout,
    forgotPassword,
    resetUserPassword,
    enableMFA,
    verifyMFACode,
    disableMFACode,
    refreshUser,
  };
};
