// Centralized API configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getApiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

export async function apiRequest(
  url: string,
  token: string,
  method="GET",
  body?: any
){
  // If url is a path (starts with /api), prepend base URL
  const fullUrl = url.startsWith('http') ? url : getApiUrl(url);

  const response = await fetch(fullUrl,{
    method,
    headers:{
      "Content-Type":"application/json",
      "Authorization":`Bearer ${token}`
    },
    body: body ? JSON.stringify(body) : undefined
  })

  return response.json()
}
