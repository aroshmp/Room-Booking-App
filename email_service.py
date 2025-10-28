# email_service.py
# US-03: Automatic Confirmation - SendGrid Email Service

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from datetime import datetime


class EmailService:
    """Handle email sending via SendGrid API"""

    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('SENDGRID_FROM_EMAIL', 'doxdoxdox9@gmail.com')

        if not self.api_key:
            print("WARNING: SENDGRID_API_KEY not set. Emails will not be sent.")

    def send_booking_confirmation(self, booking_data, ics_content=None):
        """
        Send booking confirmation email with optional calendar attachment

        Args:
            booking_data (dict): Booking information including:
                - booking_id
                - user_email
                - room_name
                - room_location
                - date
                - start_time
                - end_time
            ics_content (str): iCalendar file content (optional)

        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.api_key:
            return False, "SendGrid API key not configured"

        try:
            # Format date and time for display
            booking_date = datetime.fromisoformat(booking_data['start_time']).strftime('%A, %B %d, %Y')
            start_time = datetime.fromisoformat(booking_data['start_time']).strftime('%I:%M %p')
            end_time = datetime.fromisoformat(booking_data['end_time']).strftime('%I:%M %p')

            # Create email subject
            subject = f"Booking Confirmation - {booking_data['room_name']}"

            # Create HTML email body
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                    }}
                    .content {{
                        background-color: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 8px 8px;
                    }}
                    .booking-details {{
                        background-color: white;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        border-left: 4px solid #667eea;
                    }}
                    .detail-row {{
                        padding: 10px 0;
                        border-bottom: 1px solid #e0e0e0;
                    }}
                    .detail-row:last-child {{
                        border-bottom: none;
                    }}
                    .label {{
                        font-weight: bold;
                        color: #555;
                    }}
                    .value {{
                        color: #333;
                    }}
                    .booking-id {{
                        background-color: #e3f2fd;
                        padding: 15px;
                        border-radius: 6px;
                        text-align: center;
                        font-size: 18px;
                        font-weight: bold;
                        color: #1976d2;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        padding: 20px;
                        color: #666;
                        font-size: 14px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #28a745;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏢 Booking Confirmed!</h1>
                    </div>
                    <div class="content">
                        <p>Dear User,</p>
                        <p>Your conference room booking has been successfully confirmed.</p>

                        <div class="booking-id">
                            Booking ID: {booking_data['booking_id']}
                        </div>

                        <div class="booking-details">
                            <h3>Booking Details</h3>
                            <div class="detail-row">
                                <span class="label">Room:</span>
                                <span class="value">{booking_data['room_name']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Location:</span>
                                <span class="value">{booking_data.get('room_location', 'N/A')}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Date:</span>
                                <span class="value">{booking_date}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Time:</span>
                                <span class="value">{start_time} - {end_time}</span>
                            </div>
                        </div>

                        <p><strong>What's Next?</strong></p>
                        <ul>
                            <li>A calendar invite has been attached to this email</li>
                            <li>Add it to your calendar to receive reminders</li>
                            <li>Arrive 5 minutes early to set up</li>
                        </ul>

                        <p>If you need to modify or cancel this booking, please visit our booking system.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from the Conference Room Booking System.</p>
                        <p>&copy; 2025 Room Booking System. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create plain text version
            text_content = f"""
            BOOKING CONFIRMED

            Booking ID: {booking_data['booking_id']}

            Room: {booking_data['room_name']}
            Location: {booking_data.get('room_location', 'N/A')}
            Date: {booking_date}
            Time: {start_time} - {end_time}

            A calendar invite has been attached to this email.

            ---
            Conference Room Booking System
            """

            # Create the email message
            message = Mail(
                from_email=self.from_email,
                to_emails=booking_data['user_email'],
                subject=subject,
                plain_text_content=text_content,
                html_content=html_content
            )

            # Attach calendar invite if provided
            if ics_content:
                # Encode the ICS content to base64
                encoded_ics = base64.b64encode(ics_content.encode('utf-8')).decode()

                # Create attachment
                attachment = Attachment(
                    FileContent(encoded_ics),
                    FileName('booking.ics'),
                    FileType('text/calendar'),
                    Disposition('attachment')
                )
                message.attachment = attachment

            # Send the email
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent successfully to {booking_data['user_email']}")
                return True, "Email sent successfully"
            else:
                print(f"⚠️ Email send returned status {response.status_code}")
                return False, f"Email send returned status {response.status_code}"

        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False, f"Error sending email: {str(e)}"

    def send_cancellation_email(self, booking_data):
        """Send booking cancellation confirmation email"""
        if not self.api_key:
            return False, "SendGrid API key not configured"

        try:
            booking_date = datetime.fromisoformat(booking_data['start_time']).strftime('%A, %B %d, %Y')
            start_time = datetime.fromisoformat(booking_data['start_time']).strftime('%I:%M %p')

            subject = f"Booking Cancelled - {booking_data['room_name']}"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #dc3545;">Booking Cancelled</h2>
                    <p>Your conference room booking has been cancelled.</p>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Booking ID:</strong> {booking_data['booking_id']}</p>
                        <p><strong>Room:</strong> {booking_data['room_name']}</p>
                        <p><strong>Date:</strong> {booking_date}</p>
                        <p><strong>Time:</strong> {start_time}</p>
                    </div>
                    <p>If you did not request this cancellation, please contact support immediately.</p>
                </div>
            </body>
            </html>
            """

            message = Mail(
                from_email=self.from_email,
                to_emails=booking_data['user_email'],
                subject=subject,
                html_content=html_content
            )

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return response.status_code in [200, 201, 202], "Cancellation email sent"

        except Exception as e:
            print(f"Error sending cancellation email: {str(e)}")
            return False, f"Error: {str(e)}"


# Create a global instance
email_service = EmailService()