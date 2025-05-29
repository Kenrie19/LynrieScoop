export function setCookie(name: string, value: string, days: number) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/`;
}

export function getCookie(name: string): string | null {
  const cookies = document.cookie.split('; ');
  const found = cookies.find((row) => row.startsWith(name + '='));
  return found ? found.split('=')[1] : null;
}

export function decodeJwtPayload(token: string): any {
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}
