import { getApiBaseUrl } from "@/lib/api/config";
import type { ApiErrorBody } from "@/lib/api/types";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "@/lib/auth-storage";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  auth?: boolean;
};

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as ApiErrorBody;
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (
      data.detail &&
      typeof data.detail === "object" &&
      !Array.isArray(data.detail) &&
      "message" in data.detail &&
      typeof data.detail.message === "string"
    ) {
      const errors = data.detail.errors ?? [];
      if (errors.length > 0) {
        return `${data.detail.message}: ${errors.map((item) => item.message).join(", ")}`;
      }
      return data.detail.message;
    }
    if (Array.isArray(data.detail) && data.detail.length > 0) {
      return data.detail.map((item) => item.msg).join(", ");
    }
  } catch {
    // Response body is not JSON.
  }
  return response.statusText || "Request failed";
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  const response = await fetch(`${getApiBaseUrl()}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    clearTokens();
    return null;
  }

  const tokens = (await response.json()) as {
    access_token: string;
    refresh_token: string;
  };
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens.access_token;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { body, auth = true, headers, ...init } = options;

  const requestHeaders = new Headers(headers);
  if (body !== undefined) {
    requestHeaders.set("Content-Type", "application/json");
  }

  if (auth) {
    const accessToken = getAccessToken();
    if (accessToken) {
      requestHeaders.set("Authorization", `Bearer ${accessToken}`);
    }
  }

  const url = `${getApiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;

  let response = await fetch(url, {
    ...init,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401 && auth) {
    const newAccessToken = await refreshAccessToken();
    if (newAccessToken) {
      requestHeaders.set("Authorization", `Bearer ${newAccessToken}`);
      response = await fetch(url, {
        ...init,
        headers: requestHeaders,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
    }
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function apiUpload<T>(
  path: string,
  formData: FormData,
  options: { auth?: boolean } = {},
): Promise<T> {
  const { auth = true } = options;
  const requestHeaders = new Headers();

  if (auth) {
    const accessToken = getAccessToken();
    if (accessToken) {
      requestHeaders.set("Authorization", `Bearer ${accessToken}`);
    }
  }

  const url = `${getApiBaseUrl()}${path.startsWith("/") ? path : `/${path}`}`;

  let response = await fetch(url, {
    method: "POST",
    headers: requestHeaders,
    body: formData,
  });

  if (response.status === 401 && auth) {
    const newAccessToken = await refreshAccessToken();
    if (newAccessToken) {
      requestHeaders.set("Authorization", `Bearer ${newAccessToken}`);
      response = await fetch(url, {
        method: "POST",
        headers: requestHeaders,
        body: formData,
      });
    }
  }

  if (!response.ok) {
    throw new ApiError(await parseErrorMessage(response), response.status);
  }

  return (await response.json()) as T;
}
