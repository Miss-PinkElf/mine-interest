/** 通用 fetch 封装，统一 JSON 与错误处理。 */

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(path, init)
  if (!response.ok) {
    const detail = await response.text()
    throw new ApiError(response.status, detail || response.statusText)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}
