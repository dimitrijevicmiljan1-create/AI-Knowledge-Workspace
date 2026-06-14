"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  type LoginPayload,
  type RegisterPayload,
} from "@/lib/api/auth";
import { hasStoredSession } from "@/lib/auth-storage";

export const authQueryKey = ["auth", "me"] as const;

export function useAuth() {
  const queryClient = useQueryClient();

  const {
    data: user,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: authQueryKey,
    queryFn: getCurrentUser,
    enabled: hasStoredSession(),
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: (payload: LoginPayload) => loginUser(payload),
    onSuccess: (nextUser) => {
      queryClient.setQueryData(authQueryKey, nextUser);
    },
  });

  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => registerUser(payload),
  });

  const logout = () => {
    logoutUser();
    queryClient.removeQueries({ queryKey: authQueryKey });
    queryClient.clear();
  };

  const isAuthenticated = Boolean(user);

  return {
    user,
    isLoading: hasStoredSession() && isLoading,
    isAuthenticated,
    isUnauthorized: hasStoredSession() && isError,
    authError: error,
    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout,
    refetch,
  };
}
