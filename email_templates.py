"""
Email Templates and Automation for ScraperPro
Integrates with SendGrid, Mailgun, or any SMTP service
"""

import os
from datetime import datetime
from typing import Dict
from scraper import ClientConfig
import logging

logger = logging.getLogger(__name__)

# Email service configuration
EMAIL_SERVICE = os.environ.get('EMAIL_SERVICE', 'sendgrid')  # 'sendgrid', 'mailgun', 'smtp'
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@scraperpro.com')
FROM_NAME = os.environ.get('FROM_NAME', 'ScraperPro Team')
COMPANY_URL = os.environ.get('COMPANY_URL', 'https://scraperpro.com')


class EmailTemplates:
    """Email templates for different trial stages"""
    
    @staticmethod
    def welcome_email(client: ClientConfig, trial_end_date: str) -> Dict:
        """Welcome email on signup"""
        return {
            'subject': f"Welcome to ScraperPro! Your 7-day {client.tier} trial starts now 🎉",
            'html': f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                    .content {{ padding: 30px; background: #f9f9f9; border-radius: 10px; margin: 20px 0; }}
                    .feature {{ padding: 10px 0; }}
                    .button {{ background: #667eea; color: white; padding: 15px 30px; 
                             text-decoration: none; border-radius: 5px; display: inline-block; 
                             margin: 20px 0; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to ScraperPro!</h1>
                        <p>Your {client.tier} trial is now active</p>
                    </div>
                    
                    <div class="content">
                        <p>Hi {client.name},</p>
                        
                        <p>You now have <strong>7 days</strong> of full {client.tier} access to scrape any website!</p>
                        
                        <p><strong>Your trial includes:</strong></p>
                        <div class="feature">✅ Unlimited scraper configurations</div>
                        <div class="feature">✅ Export to CSV, Excel, and JSON</div>
                        <div class="feature">✅ Full API access</div>
                        <div class="feature">✅ Automated scheduling</div>
                        <div class="feature">✅ Priority support</div>
                        
                        <p><strong>Trial ends:</strong> {trial_end_date}</p>
                        
                        <a href="{COMPANY_URL}/dashboard" class="button">Get Started Now →</a>
                        
                        <p>Your API Key: <code>{client.api_key}</code></p>
                        <p style="font-size: 12px; color: #666;">Keep this safe - you'll need it to access the API</p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                        
                        <p><strong>Quick Start Guide:</strong></p>
                        <ol>
                            <li>Click "Get Started" button above</li>
                            <li>Create your first scraper configuration</li>
                            <li>Run it and export your data</li>
                            <li>Try the API if you're technical</li>
                        </ol>
                        
                        <p>Need help? Just reply to this email - I personally respond to every message!</p>
                        
                        <p>Excited to see what you build,<br>
                        The ScraperPro Team</p>
                    </div>
                    
                    <div class="footer">
                        <p>ScraperPro | {COMPANY_URL}</p>
                        <p>You're receiving this because you started a free trial</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            'text': f"""
Welcome to ScraperPro!

Hi {client.name},

Your {client.tier} trial is now active! You have 7 days of full access.

Your trial includes:
- Unlimited scraper configurations
- Export to CSV, Excel, and JSON
- Full API access
- Automated scheduling
- Priority support

Trial ends: {trial_end_date}

Get started: {COMPANY_URL}/dashboard
Your API Key: {client.api_key}

Need help? Just reply to this email!

- The ScraperPro Team
            """
        }
    
    @staticmethod
    def mid_trial_checkin(client: ClientConfig, stats: Dict) -> Dict:
        """Check-in email on day 3"""
        return {
            'subject': "How's your ScraperPro trial going? 📊",
            'html': f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Hi {client.name},</h2>
                    
                    <p>You're halfway through your trial! Here's what you've accomplished:</p>
                    
                    <div style="background: #f0f9ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <h3>Your Stats:</h3>
                        <p>📊 Scrapers created: <strong>{stats.get('configs', 0)}</strong></p>
                        <p>📥 Data exported: <strong>{stats.get('records', 0)} records</strong></p>
                        <p>🔄 API requests: <strong>{stats.get('requests', 0)}</strong></p>
                    </div>
                    
                    <p>Still have <strong>4 days</strong> to explore everything.</p>
                    
                    <p><strong>Need help maximizing your trial?</strong></p>
                    <ul>
                        <li>📖 <a href="{COMPANY_URL}/docs">Browse documentation</a></li>
                        <li>💬 <a href="{COMPANY_URL}/support">Chat with support</a></li>
                        <li>📅 <a href="{COMPANY_URL}/demo">Schedule a demo call</a></li>
                    </ul>
                    
                    <p>Any questions? Just hit reply!</p>
                    
                    <p>Cheers,<br>The ScraperPro Team</p>
                </div>
            </body>
            </html>
            """,
            'text': f"""
Hi {client.name},

You're halfway through your trial!

Your stats:
- Scrapers created: {stats.get('configs', 0)}
- Data exported: {stats.get('records', 0)} records
- API requests: {stats.get('requests', 0)}

4 days left to explore!

Need help? Reply to this email.

- The ScraperPro Team
            """
        }
    
    @staticmethod
    def trial_ending_2_days(client: ClientConfig, payment_link: str) -> Dict:
        """Warning email 2 days before expiration"""
        tier_price = "49" if client.tier == "PRO" else "199"
        return {
            'subject': f"⏰ Your ScraperPro trial ends in 2 days",
            'html': f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #fef3c7; padding: 20px; border-left: 4px solid #f59e0b; margin-bottom: 20px;">
                        <h2 style="margin: 0; color: #92400e;">⏰ Your trial ends in 2 days</h2>
                    </div>
                    
                    <p>Hi {client.name},</p>
                    
                    <p>Just a friendly heads up - your {client.tier} trial ends in <strong>2 days</strong>.</p>
                    
                    <p><strong>To keep your:</strong></p>
                    <ul>
                        <li>✅ Scraper configurations</li>
                        <li>✅ Exported data files</li>
                        <li>✅ Full {client.tier} features</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{payment_link}" 
                           style="background: #667eea; color: white; padding: 15px 40px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;
                                  font-size: 18px;">
                            Add Payment - Just ${tier_price}/month →
                        </a>
                    </div>
                    
                    <p><strong>Still have questions?</strong></p>
                    <ul>
                        <li>💬 Reply to this email</li>
                        <li>📞 <a href="{COMPANY_URL}/call">Book a quick call</a></li>
                        <li>❓ <a href="{COMPANY_URL}/faq">Check our FAQ</a></li>
                    </ul>
                    
                    <p>We're here to help!</p>
                    
                    <p>Best,<br>The ScraperPro Team</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #666;">
                        No credit card was required for your trial. You'll only be charged if you add payment.
                    </p>
                </div>
            </body>
            </html>
            """,
            'text': f"""
⏰ Your ScraperPro trial ends in 2 days

Hi {client.name},

Your {client.tier} trial ends in 2 days.

To keep everything you've built, add payment now: {payment_link}

Just ${tier_price}/month to continue.

Questions? Reply to this email!

- The ScraperPro Team
            """
        }
    
    @staticmethod
    def trial_ending_1_day(client: ClientConfig, payment_link: str) -> Dict:
        """Final warning email"""
        tier_price = "49" if client.tier == "PRO" else "199"
        return {
            'subject': f"🚨 Last day of your ScraperPro trial",
            'html': f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: #fee2e2; padding: 20px; border-left: 4px solid #dc2626; margin-bottom: 20px;">
                        <h2 style="margin: 0; color: #991b1b;">🚨 Your trial ends tomorrow</h2>
                    </div>
                    
                    <p>Hi {client.name},</p>
                    
                    <p>This is your <strong>last day</strong> with full {client.tier} access.</p>
                    
                    <p><strong>Tomorrow at this time:</strong></p>
                    <ul>
                        <li>❌ No more scraping</li>
                        <li>❌ Can't access configurations</li>
                        <li>❌ API access disabled</li>
                    </ul>
                    
                    <p><strong>But your data is safe:</strong></p>
                    <ul>
                        <li>✅ All configurations saved</li>
                        <li>✅ Exported files preserved</li>
                        <li>✅ Reactivate anytime</li>
                    </ul>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{payment_link}" 
                           style="background: #dc2626; color: white; padding: 20px 50px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;
                                  font-size: 20px; font-weight: bold;">
                            Activate Now - ${tier_price}/month
                        </a>
                    </div>
                    
                    <p style="text-align: center; color: #666;">
                        Takes 30 seconds. Cancel anytime.
                    </p>
                    
                    <hr style="margin: 30px 0;">
                    
                    <p><strong>Still not sure? Let's talk!</strong></p>
                    <p>Book a 15-minute call and I'll personally help you decide: 
                       <a href="{COMPANY_URL}/call">Schedule now</a></p>
                    
                    <p>Thanks for trying ScraperPro,<br>The ScraperPro Team</p>
                </div>
            </body>
            </html>
            """,
            'text': f"""
🚨 Last day of your ScraperPro trial

Hi {client.name},

Your trial ends tomorrow.

Activate now to keep everything: {payment_link}
Just ${tier_price}/month.

Not sure? Let's talk: {COMPANY_URL}/call

- The ScraperPro Team
            """
        }
    
    @staticmethod
    def trial_expired(client: ClientConfig, reactivation_link: str) -> Dict:
        """Email sent when trial expires"""
        tier_price = "49" if client.tier == "PRO" else "199"
        return {
            'subject': "Your ScraperPro trial has ended",
            'html': f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Hi {client.name},</h2>
                    
                    <p>Your 7-day trial has ended.</p>
                    
                    <p><strong>Your work is safe:</strong></p>
                    <div style="background: #dcfce7; padding: 20px; border-radius: 10px; margin: 20px 0;">
                        <p>✅ All scraper configurations saved</p>
                        <p>✅ Exported data files preserved</p>
                        <p>✅ Easy to reactivate anytime</p>
                    </div>
                    
                    <p>Reactivate in one click and pick up right where you left off:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reactivation_link}" 
                           style="background: #667eea; color: white; padding: 15px 40px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            Reactivate Now - ${tier_price}/month →
                        </a>
                    </div>
                    
                    <p><strong>Questions or concerns?</strong><br>
                    Just reply to this email - I personally respond to every message.</p>
                    
                    <p>Hope to see you back soon!<br>
                    The ScraperPro Team</p>
                </div>
            </body>
            </html>
            """,
            'text': f"""
Your ScraperPro trial has ended

Hi {client.name},

Your work is safe and ready when you are.

Reactivate now: {reactivation_link}
Just ${tier_price}/month.

Questions? Reply to this email.

- The ScraperPro Team
            """
        }
    
    @staticmethod
    def winback_discount(client: ClientConfig, discount_link: str) -> Dict:
        """Win-back email with discount (send 3 days after expiration)"""
        tier_price = "49" if client.tier == "PRO" else "199"
        discount_price = "39" if client.tier == "PRO" else "159"
        return {
            'subject': f"Come back to ScraperPro - 20% off first month",
            'html': f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                               color: white; padding: 30px; text-align: center; border-radius: 10px;">
                        <h1>We miss you! 💙</h1>
                        <p style="font-size: 24px; margin: 20px 0;">Get 20% off your first month</p>
                    </div>
                    
                    <div style="padding: 30px 0;">
                        <p>Hi {client.name},</p>
                        
                        <p>We noticed you haven't activated your ScraperPro account yet.</p>
                        
                        <p>To welcome you back, here's an <strong>exclusive offer</strong>:</p>
                        
                        <div style="background: #fef3c7; padding: 30px; border-radius: 10px; 
                                   text-align: center; margin: 30px 0; border: 3px solid #f59e0b;">
                            <p style="font-size: 18px; margin: 0;">
                                <strike>${tier_price}/month</strike>
                            </p>
                            <p style="font-size: 36px; color: #f59e0b; margin: 10px 0; font-weight: bold;">
                                ${discount_price}/month
                            </p>
                            <p style="margin: 0;">for your first month!</p>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{discount_link}" 
                               style="background: #f59e0b; color: white; padding: 20px 50px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;
                                      font-size: 20px; font-weight: bold;">
                                Claim Your Discount →
                            </a>
                        </div>
                        
                        <p style="text-align: center; color: #dc2626; font-weight: bold; margin-top: 20px;">
                            ⏰ Offer expires in 48 hours
                        </p>
                        
                        <hr style="margin: 30px 0;">
                        
                        <p><strong>Why customers love ScraperPro:</strong></p>
                        <blockquote style="border-left: 4px solid #667eea; padding-left: 20px; color: #666;">
                            "Saved me 10 hours a week on data collection. Worth every penny!"
                            <br>- Sarah, Marketing Agency Owner
                        </blockquote>
                        
                        <p>Questions? Reply to this email anytime.</p>
                        
                        <p>Best,<br>The ScraperPro Team</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            'text': f"""
We miss you! Come back to ScraperPro

Hi {client.name},

Special offer just for you:
${discount_price}/month (20% off) for your first month!

Regular price: ${tier_price}/month

Claim discount: {discount_link}

Expires in 48 hours!

- The ScraperPro Team
            """
        }


class EmailSender:
    """Send emails via your preferred service"""
    
    def __init__(self):
        self.service = EMAIL_SERVICE
    
    def send(self, to_email: str, to_name: str, template_data: Dict) -> bool:
        """Send email using configured service"""
        try:
            if self.service == 'sendgrid':
                return self._send_sendgrid(to_email, to_name, template_data)
            elif self.service == 'mailgun':
                return self._send_mailgun(to_email, to_name, template_data)
            elif self.service == 'smtp':
                return self._send_smtp(to_email, to_name, template_data)
            else:
                logger.error(f"Unknown email service: {self.service}")
                return False
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def _send_sendgrid(self, to_email: str, to_name: str, template_data: Dict) -> bool:
        """Send via SendGrid"""
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        
        message = Mail(
            from_email=Email(FROM_EMAIL, FROM_NAME),
            to_emails=To(to_email, to_name),
            subject=template_data['subject'],
            plain_text_content=Content("text/plain", template_data['text']),
            html_content=Content("text/html", template_data['html'])
        )
        
        response = sg.send(message)
        logger.info(f"Sent email to {to_email}: {template_data['subject']}")
        return response.status_code == 202
    
    def _send_mailgun(self, to_email: str, to_name: str, template_data: Dict) -> bool:
        """Send via Mailgun"""
        import requests
        
        return requests.post(
            f"https://api.mailgun.net/v3/{os.environ.get('MAILGUN_DOMAIN')}/messages",
            auth=("api", os.environ.get('MAILGUN_API_KEY')),
            data={
                "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                "to": f"{to_name} <{to_email}>",
                "subject": template_data['subject'],
                "text": template_data['text'],
                "html": template_data['html']
            }
        ).status_code == 200
    
    def _send_smtp(self, to_email: str, to_name: str, template_data: Dict) -> bool:
        """Send via SMTP"""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        
        message = MIMEMultipart('alternative')
        message['Subject'] = template_data['subject']
        message['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message['To'] = f"{to_name} <{to_email}>"
        
        message.attach(MIMEText(template_data['text'], 'plain'))
        message.attach(MIMEText(template_data['html'], 'html'))
        
        with smtplib.SMTP(os.environ.get('SMTP_HOST'), int(os.environ.get('SMTP_PORT', 587))) as server:
            server.starttls()
            server.login(os.environ.get('SMTP_USER'), os.environ.get('SMTP_PASS'))
            server.send_message(message)
        
        return True


# Example usage
if __name__ == '__main__':
    from scraper import ClientConfig
    
    # Create test client
    client = ClientConfig(
        client_id="test123",
        name="John Doe",
        email="john@example.com",
        tier="PRO",
        api_key="test_key",
        created_at=datetime.now().isoformat(),
        trial_ends_at=(datetime.now()).isoformat(),
        is_trial=True
    )
    
    # Generate welcome email
    template = EmailTemplates.welcome_email(client, "November 19, 2024")
    
    # Send email
    sender = EmailSender()
    sender.send(client.email, client.name, template)
