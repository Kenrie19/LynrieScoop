# Email Notifications

LynrieScoop implements automated email notifications for important user events. This document describes the email notification system architecture and configuration.

## Overview

The application sends automated emails for key events:

- **Booking Confirmations**: When a user books a ticket, they receive a confirmation email with all booking details
- **Future Extensions**: The architecture supports adding additional notification types as needed (password resets, promotional emails, etc.)

## Technical Implementation

### Email Generation

The email notification system uses Python's standard `smtplib` and `email.mime` packages to compose and send emails:

```python
# Create a proper MIME email
msg = MIMEMultipart("alternative")
msg["Subject"] = f"Booking Confirmation - {booking.booking_number}"
msg["From"] = sender
msg["To"] = receiver

# Attach HTML part
html_part = MIMEText(message_html, "html")
msg.attach(html_part)
```

### Email Content

Emails are formatted as HTML to provide a rich user experience:

- **HTML Template**: Custom HTML template styled with inline CSS for maximum email client compatibility
- **Responsive Design**: Layout adapts to different screen sizes
- **Booking Information**: Includes all essential booking details such as:
  - Booking number (for customer support reference)
  - Movie title
  - Showing date and time
  - Room information
  - Total price
  - Status

## Configuration

Email sending is configured through environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| SMTP_HOST | SMTP server hostname | smtp.example.com |
| SMTP_PORT | SMTP server port | 587 |
| SMTP_USER | SMTP username | <user@example.com> |
| SMTP_PASSWORD | SMTP password | password123 |
| EMAILS_FROM_EMAIL | Sender email address | <noreply@lynriescoop.com> |
| EMAILS_FROM_NAME | Sender name | LynrieScoop Cinema |

These settings can be configured in the `.env` file or as environment variables.

## Error Handling

The system includes robust error handling to ensure booking completion even if email sending fails:

1. Email sending errors are logged but don't prevent booking completion
2. The system doesn't retry failed emails automatically, but they could be implemented in future versions

## Testing Email Configuration

To test if your email configuration is working:

```bash
# From the backend directory
python -c "
import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

sender = f'{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>'
receiver = 'test@example.com'
msg = MIMEText('Test email from LynrieScoop Cinema')
msg['Subject'] = 'Test Email'
msg['From'] = sender
msg['To'] = receiver

with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
    server.starttls()
    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    server.sendmail(sender, receiver, msg.as_string())
    print('Email sent successfully')
"
```

## Development Setup

For development, you can use services like [Mailtrap](https://mailtrap.io/) that provide a testing inbox for development environments. Configure your environment variables to use their SMTP servers.

## Future Enhancements

Planned improvements for the email notification system:

1. Email templates stored as separate files
2. Queue-based sending for improved reliability
3. HTML and plain text alternatives
4. Localization support for multi-language emails
