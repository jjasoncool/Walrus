import logging
import smtplib
import argparse
from email.message import EmailMessage
from typing import Iterable

from src.config import Config

logger = logging.getLogger(__name__)


def _recipients() -> list[str]:
    return [email.strip() for email in Config.EMAIL_TO.split(",") if email.strip()]


def send_email(subject: str, body: str) -> bool:
    """依 .env SMTP 設定寄信；未啟用時只寫 log。"""
    if not Config.EMAIL_ENABLED:
        logger.info("EMAIL_ENABLED=false，略過寄信。Subject: %s\n%s", subject, body)
        return False

    recipients = _recipients()
    if not Config.SMTP_HOST or not Config.EMAIL_FROM or not recipients:
        logger.warning("Email 設定不完整，無法寄信。Subject: %s", subject)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = Config.EMAIL_FROM
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    try:
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=30) as smtp:
            if Config.SMTP_USE_TLS:
                smtp.starttls()
            if Config.SMTP_USERNAME:
                smtp.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            smtp.send_message(message)
        logger.info("Email 通知已寄出：%s", subject)
        return True
    except Exception as exc:
        logger.error("Email 通知寄送失敗：%s", exc)
        return False


def send_nsea_failure_summary(snapshot_date: str, failures: Iterable[dict]) -> bool:
    failures = list(failures)
    if not failures:
        return False

    lines = [
        "近海漁業預報截圖任務發生失敗。",
        "",
        f"日期：{snapshot_date}",
        f"來源：{Config.NSEA_SCREENSHOT_SOURCE_URL}",
        "",
        "失敗海域：",
    ]
    for item in failures:
        lines.append(f"- {item.get('area_id')} {item.get('area_name')}: {item.get('error')}")

    return send_email(
        subject=f"[Walrus] 近海漁業預報截圖失敗 - {snapshot_date}",
        body="\n".join(lines),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="測試 Walrus SMTP Email 通知設定")
    parser.add_argument("--subject", default="[Walrus] Email 測試", help="測試信主旨")
    parser.add_argument("--body", default="這是一封 Walrus SMTP 測試信。", help="測試信內容")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()
    sent = send_email(args.subject, args.body)
    if sent:
        print("Email 測試信已送出")
    else:
        print("Email 測試信未送出，請檢查 EMAIL_ENABLED 與 SMTP 設定/log")


if __name__ == "__main__":
    main()