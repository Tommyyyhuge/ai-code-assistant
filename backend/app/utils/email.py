"""邮件发送工具 — 使用 SMTP"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def send_reset_code_email(to_email: str, code: str) -> None:
    """发送密码重置验证码邮件"""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        # 未配置 SMTP 时打印到日志（开发环境）
        import logging
        logging.getLogger("auth").warning(f"[DEV] Reset code for {to_email}: {code}")
        return

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "AI Code Assistant - 密码重置验证码"

    body = f"""您好，

您正在为 AI Code Assistant 账户重置密码。

验证码：{code}
有效期：10 分钟

如非本人操作，请忽略此邮件。
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # SSL/TLS 自动选择
    if settings.SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
    else:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10)
        server.starttls()

    try:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
    finally:
        server.quit()
