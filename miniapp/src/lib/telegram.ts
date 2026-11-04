import crypto from "crypto";

const MAX_AGE_SEC = 24 * 60 * 60;

export function validateTelegramInitData(initData: string, botToken: string) {
  const params = new URLSearchParams(initData);
  const hash = params.get("hash");
  params.delete("hash");

  const dataCheckString = Array.from(params.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k}=${v}`)
    .join("\n");

  const secret = crypto.createHmac("sha256", "WebAppData").update(botToken).digest();
  const computedHash = crypto.createHmac("sha256", secret).update(dataCheckString).digest("hex");

  if (!hash || computedHash.length !== hash.length) return false;
  if (!crypto.timingSafeEqual(Buffer.from(computedHash), Buffer.from(hash))) return false;
  // initData старше суток не принимаем: иначе перехваченная строка работает вечно
  const authDate = Number(params.get("auth_date"));
  return Number.isFinite(authDate) && Date.now() / 1000 - authDate < MAX_AGE_SEC;
}
