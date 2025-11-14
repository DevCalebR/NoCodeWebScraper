🎁 Trial Management Guide
Complete guide to managing the 7-day free trial system in ScraperPro.
🎯 Trial System Overview
How It Works

User Signs Up

Chooses Pro or Enterprise plan
No credit card required
Gets instant access to full features
Trial starts immediately


During Trial (Days 1-7)

Full access to chosen tier features
Usage tracked but not billed
Daily reminder when 2 days or less remain
Can add payment anytime


Trial Expiration (Day 7)

Account automatically deactivates
Data and configurations preserved
User prompted to add payment
Can reactivate instantly with payment


Post-Payment

Trial converts to paid subscription
Account reactivates immediately
Billing starts from conversion date
User keeps all their work



💳 Payment Integration
Stripe Setup (Required for Production)
1. Create Stripe Account
bash# Go to: https://stripe.com
# Sign up for free account
# Get your API keys from Dashboard
2. Create Products in Stripe
Pro Plan:

Name: "ScraperPro Pro"
Price: $49/month
Billing: Recurring monthly
Copy the Price ID (e.g., price_1234abcd)

Enterprise Plan:

Name: "ScraperPro Enterprise"
Price: $199/month
Billing: Recurring monthly
Copy the Price ID (e.g., price_5678efgh)

3. Set Environment Variables
bash# Add to .env file
STRIPE_SECRET_KEY=REMOVED_PLACEHOLDER_VALUE
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_PRO=price_1234abcd
STRIPE_PRICE_ENTERPRISE=price_5678efgh
4. Install Stripe
bashpip install stripe
5. Add Payment Button to Streamlit
Update app.py in the sidebar trial warning section:
pythonif client.is_trial:
    days_remaining = st.session_state.app.client_manager.get_trial_days_remaining(client)
    
    if days_remaining > 0:
        st.warning(f"⏰ **Trial:** {days_remaining} days remaining")
        
        if st.button("💳 Add Payment & Activate", type="primary"):
            # Import payment processor
            from stripe_payments import PaymentProcessor
            
            payment_processor = PaymentProcessor(st.session_state.app.client_manager)
            
            # Create checkout session
            result = payment_processor.create_checkout_session(
                client,
                success_url="http://localhost:8501/?payment=success",
                cancel_url="http://localhost:8501/?payment=cancelled"
            )
            
            if result['success']:
                st.markdown(f"[Click here to add payment]({result['checkout_url']})")
            else:
                st.error(f"Error: {result['error']}")
6. Handle Payment Success
Add to top of app.py:
python# Check for payment success in URL
query_params = st.query_params
if query_params.get('payment') == 'success':
    st.success("🎉 Payment successful! Your account is now active.")
    st.balloons()
📧 Trial Communication Strategy
Day 0: Welcome Email
Subject: Welcome to ScraperPro! Your 7-day trial starts now 🎉

Hi [Name],

Your ScraperPro [Pro/Enterprise] trial is now active!

You have 7 days to:
✅ Create unlimited configurations
✅ Scrape data from any website
✅ Export in multiple formats
✅ Test our API

Trial expires: [Date]

Get started: [Dashboard Link]

Need help? Reply to this email!

- The ScraperPro Team
Day 3: Mid-Trial Check-in
Subject: How's your ScraperPro trial going?

Hi [Name],

You're halfway through your trial! 

Trial status: 4 days remaining
Scrapers created: [X]
Data exported: [Y] records

Need help getting more value? Schedule a quick call: [Calendly Link]

- The ScraperPro Team
Day 5: Reminder (2 Days Left)
Subject: ⏰ Your ScraperPro trial ends in 2 days

Hi [Name],

Just a heads up - your trial ends in 2 days.

To keep your:
- [X] configurations
- [Y] exported files
- Full [Pro/Enterprise] features

👉 Add payment now: [Payment Link]

Questions? We're here to help!

- The ScraperPro Team
Day 6: Last Day Warning
Subject: 🚨 Last day of your ScraperPro trial

Hi [Name],

Your trial ends tomorrow.

After that:
❌ No more scraping
❌ Can't access configurations
✅ Your data is saved

Activate now for just $[49/199]/month: [Payment Link]

Still have questions? Book a call: [Calendly]

- The ScraperPro Team
Day 7: Trial Expired
Subject: Your ScraperPro trial has ended

Hi [Name],

Your 7-day trial has ended.

Your work is safe:
✅ All configurations saved
✅ Exported data preserved
✅ Easy to reactivate

Reactivate in 1 click: [Payment Link]

Or reply with questions!

- The ScraperPro Team
Day 10: Win-back Offer
Subject: Come back to ScraperPro - 20% off

Hi [Name],

We miss you! Come back and get 20% off your first month.

[Pro Plan: $39/month instead of $49]
[Enterprise: $159/month instead of $199]

Claim discount: [Special Link]

Offer expires in 48 hours.

- The ScraperPro Team
🤖 Automated Trial Management
Run Daily Cron Job
Create check_trials.py:
python"""
Daily cron job to check trial expirations and send reminders
Run daily at 9 AM: 0 9 * * * python check_trials.py
"""

from scraper import ScraperPro, ClientConfig
from datetime import datetime
from pathlib import Path
import json

def send_email(client: ClientConfig, template: str):
    """Send email notification (integrate with SendGrid, Mailgun, etc.)"""
    print(f"Sending {template} email to {client.email}")
    # TODO: Implement actual email sending

def check_and_notify_trials():
    """Check all trials and send appropriate notifications"""
    app = ScraperPro()
    client_dir = Path('data/clients')
    
    for client_file in client_dir.glob('*.json'):
        with open(client_file, 'r') as f:
            data = json.load(f)
            client = ClientConfig(**data)
        
        if not client.is_trial:
            continue
        
        days_remaining = app.client_manager.get_trial_days_remaining(client)
        
        # Send notifications based on days remaining
        if days_remaining == 5:
            send_email(client, 'trial_2_days_warning')
        elif days_remaining == 6:
            send_email(client, 'trial_1_day_warning')
        elif days_remaining == 0:
            send_email(client, 'trial_expired')
        elif days_remaining == -3:
            send_email(client, 'win_back_offer')

if __name__ == '__main__':
    check_and_notify_trials()
Add to Crontab
bash# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/scraper-pro && python check_trials.py
📊 Trial Analytics to Track
Key Metrics

Trial Signup Rate

Visitors → Trial signups
Target: 5-10% of landing page visitors


Trial Activation Rate

Signups → Actually use the product
Target: 60-80%


Trial-to-Paid Conversion

Completed trials → Paid subscriptions
Target: 25-40%


Time to First Value

Signup → First successful scrape
Target: <10 minutes


Trial Engagement

Scrapers created during trial
Data exported during trial
API requests made



Dashboard Example
python# Add to admin dashboard
def trial_analytics():
    """Calculate trial conversion metrics"""
    client_dir = Path('data/clients')
    
    total_trials = 0
    active_trials = 0
    expired_trials = 0
    converted = 0
    
    for client_file in client_dir.glob('*.json'):
        with open(client_file, 'r') as f:
            client = ClientConfig(**json.load(f))
        
        if client.is_trial or client.trial_ends_at:
            total_trials += 1
            
            if client.is_trial and client.active:
                active_trials += 1
            elif not client.is_trial and client.active:
                converted += 1
            else:
                expired_trials += 1
    
    conversion_rate = (converted / total_trials * 100) if total_trials > 0 else 0
    
    return {
        'total_trials': total_trials,
        'active_trials': active_trials,
        'expired_trials': expired_trials,
        'converted': converted,
        'conversion_rate': f"{conversion_rate:.1f}%"
    }
🎯 Improving Trial Conversion
Tactics That Work

Personalized Onboarding

Ask what they want to scrape
Provide pre-configured templates
Send targeted tutorial videos


Quick Wins

One-click demo scrapers
Sample configurations
Instant results


Human Touch

Personal welcome email from founder
Offer setup call for Enterprise trials
Respond to questions within 1 hour


Show Value

Daily email: "You've scraped X records worth $Y"
Comparison to manual alternatives
Time saved calculator


Reduce Friction

One-click payment
Multiple payment methods
Cancel anytime promise


Social Proof

Show recent scrapers created
Customer testimonials
Trust badges



⚠️ Common Trial Pitfalls to Avoid
❌ Too Long Trials (30+ days)

Users forget about it
Lose urgency
✅ Solution: 7 days is optimal

❌ Credit Card Required

Massive signup barrier
Looks predatory
✅ Solution: No CC to start

❌ Limited Features

Users don't see full value
Nothing to lose at trial end
✅ Solution: Full access during trial

❌ No Communication

Users forget they signed up
No reminder to convert
✅ Solution: Strategic emails

❌ Automatic Charging

Bad user experience
Chargebacks and complaints
✅ Solution: Require explicit payment

🚀 Launch Checklist
Before enabling trials in production:

 Stripe account set up
 Products created in Stripe
 Webhook endpoint configured
 Payment buttons working
 Trial expiration tested
 Email templates ready
 Cron job for notifications
 Analytics tracking
 Terms of service updated
 Privacy policy updated
 Refund policy created
 Customer support ready

💡 Pro Tips

A/B Test Trial Length

Try 7, 10, 14 days
Measure conversion for each
7 days usually best


Offer Extension

"Need more time? Get 3 more days"
Shows you care
Often converts hesitant users


Exit Survey

Ask why they didn't convert
Learn what features are missing
Win back with specific solutions


Reactivation Campaign

Day 10: Discount offer
Day 20: Feature update
Day 30: Personal outreach


Champion Users

Identify power users during trial
Offer discount to convert early
Get testimonial in exchange



📞 Support Strategy
During Trial

Respond within 1 hour
Offer free setup help
Send helpful resources proactively

At Expiration

Personal follow-up email
Offer extension if needed help
Ask for feedback

Post-Expiration

Reactivation discounts
Feature announcements
Win-back campaigns
