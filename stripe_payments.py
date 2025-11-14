"""
Stripe Payment Integration for ScraperPro
Handles trial conversion, subscriptions, and billing
"""

import os
import stripe
from typing import Dict, Optional
from scraper import ClientManager, ClientConfig, SubscriptionTier
import logging

logger = logging.getLogger(__name__)

# Set your Stripe secret key
# Get from: https://dashboard.stripe.com/apikeys
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_YOUR_KEY_HERE')

# Stripe Price IDs (create these in Stripe Dashboard)
STRIPE_PRICES = {
    'PRO': os.environ.get('STRIPE_PRICE_PRO', 'price_pro_monthly'),
    'ENTERPRISE': os.environ.get('STRIPE_PRICE_ENTERPRISE', 'price_ent_monthly')
}


class PaymentProcessor:
    """Handles all payment-related operations"""
    
    def __init__(self, client_manager: ClientManager):
        self.client_manager = client_manager
    
    def create_checkout_session(self, client: ClientConfig, success_url: str, cancel_url: str) -> Dict:
        """
        Create Stripe Checkout session for trial conversion
        Returns checkout URL for customer
        """
        try:
            # Create or retrieve Stripe customer
            stripe_customer = self._get_or_create_stripe_customer(client)
            
            # Get price ID for client's tier
            price_id = STRIPE_PRICES.get(client.tier)
            if not price_id:
                raise ValueError(f"No price configured for tier: {client.tier}")
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=stripe_customer.id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'client_id': client.client_id,
                    'tier': client.tier
                },
                subscription_data={
                    'metadata': {
                        'client_id': client.client_id,
                    }
                },
                # Apply trial if user hasn't used it yet
                subscription_data={
                    'trial_period_days': 0  # No additional trial, they already had 7 days
                } if not client.is_trial else {}
            )
            
            logger.info(f"Created checkout session for client {client.client_id}")
            
            return {
                'success': True,
                'checkout_url': session.url,
                'session_id': session.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_or_create_stripe_customer(self, client: ClientConfig) -> stripe.Customer:
        """Get existing Stripe customer or create new one"""
        # Check if customer already exists in Stripe
        customers = stripe.Customer.list(email=client.email, limit=1)
        
        if customers.data:
            return customers.data[0]
        
        # Create new customer
        customer = stripe.Customer.create(
            email=client.email,
            name=client.name,
            metadata={
                'client_id': client.client_id,
                'tier': client.tier
            }
        )
        
        logger.info(f"Created Stripe customer for {client.email}")
        return customer
    
    def handle_successful_payment(self, session_id: str) -> Dict:
        """
        Handle successful payment callback from Stripe
        Called after customer completes checkout
        """
        try:
            # Retrieve the session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                client_id = session.metadata.get('client_id')
                
                if not client_id:
                    return {'success': False, 'error': 'Missing client_id'}
                
                # Load client
                client = self.client_manager.load_client(client_id)
                if not client:
                    return {'success': False, 'error': 'Client not found'}
                
                # Convert trial to paid
                success = self.client_manager.convert_trial_to_paid(client)
                
                if success:
                    logger.info(f"Successfully converted trial to paid for client {client_id}")
                    return {
                        'success': True,
                        'message': 'Subscription activated',
                        'client_id': client_id
                    }
            
            return {'success': False, 'error': 'Payment not completed'}
            
        except stripe.error.StripeError as e:
            logger.error(f"Error handling payment: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict:
        """
        Handle Stripe webhooks for subscription events
        IMPORTANT: Set webhook endpoint in Stripe Dashboard to:
        https://yourdomain.com/webhook/stripe
        """
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        
        if not webhook_secret:
            return {'success': False, 'error': 'Webhook secret not configured'}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return {'success': False, 'error': 'Invalid signature'}
        
        # Handle different event types
        if event.type == 'checkout.session.completed':
            session = event.data.object
            self.handle_successful_payment(session.id)
        
        elif event.type == 'customer.subscription.deleted':
            # Subscription cancelled - deactivate account
            subscription = event.data.object
            client_id = subscription.metadata.get('client_id')
            
            if client_id:
                client = self.client_manager.load_client(client_id)
                if client:
                    client.active = False
                    self.client_manager._save_client(client)
                    logger.info(f"Deactivated client {client_id} due to subscription cancellation")
        
        elif event.type == 'customer.subscription.updated':
            # Subscription updated - could be plan change
            subscription = event.data.object
            client_id = subscription.metadata.get('client_id')
            
            if client_id:
                logger.info(f"Subscription updated for client {client_id}")
        
        elif event.type == 'invoice.payment_failed':
            # Payment failed - notify user
            invoice = event.data.object
            customer_email = invoice.customer_email
            logger.warning(f"Payment failed for {customer_email}")
            # TODO: Send email notification
        
        return {'success': True}
    
    def cancel_subscription(self, client: ClientConfig) -> Dict:
        """Cancel a client's subscription"""
        try:
            # Find customer in Stripe
            customers = stripe.Customer.list(email=client.email, limit=1)
            
            if not customers.data:
                return {'success': False, 'error': 'Customer not found'}
            
            customer = customers.data[0]
            
            # Get active subscriptions
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status='active',
                limit=1
            )
            
            if not subscriptions.data:
                return {'success': False, 'error': 'No active subscription'}
            
            # Cancel subscription at period end
            subscription = subscriptions.data[0]
            updated_subscription = stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=True
            )
            
            logger.info(f"Scheduled cancellation for client {client.client_id}")
            
            return {
                'success': True,
                'message': 'Subscription will cancel at period end',
                'period_end': updated_subscription.current_period_end
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def change_plan(self, client: ClientConfig, new_tier: str) -> Dict:
        """Change client's subscription plan"""
        try:
            # Validate new tier
            if new_tier not in ['PRO', 'ENTERPRISE']:
                return {'success': False, 'error': 'Invalid tier'}
            
            # Find customer
            customers = stripe.Customer.list(email=client.email, limit=1)
            if not customers.data:
                return {'success': False, 'error': 'Customer not found'}
            
            customer = customers.data[0]
            
            # Get subscription
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status='active',
                limit=1
            )
            
            if not subscriptions.data:
                return {'success': False, 'error': 'No active subscription'}
            
            subscription = subscriptions.data[0]
            
            # Update subscription
            new_price_id = STRIPE_PRICES[new_tier]
            stripe.Subscription.modify(
                subscription.id,
                items=[{
                    'id': subscription['items'].data[0].id,
                    'price': new_price_id,
                }],
                proration_behavior='always_invoice'  # Charge/credit difference immediately
            )
            
            # Update client tier
            client.tier = new_tier
            self.client_manager._save_client(client)
            
            logger.info(f"Changed plan for client {client.client_id} to {new_tier}")
            
            return {
                'success': True,
                'message': f'Plan changed to {new_tier}',
                'new_tier': new_tier
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error changing plan: {str(e)}")
            return {'success': False, 'error': str(e)}


# Flask webhook endpoint example
"""
Add to api_server.py:

from stripe_payments import PaymentProcessor

payment_processor = PaymentProcessor(scraper_app.client_manager)

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    result = payment_processor.handle_webhook(payload, sig_header)
    
    if result['success']:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'error': result['error']}), 400

@app.route('/api/v1/checkout', methods=['POST'])
@require_api_key
def create_checkout():
    client = request.client
    
    success_url = request.json.get('success_url', 'https://yourdomain.com/success')
    cancel_url = request.json.get('cancel_url', 'https://yourdomain.com/pricing')
    
    result = payment_processor.create_checkout_session(client, success_url, cancel_url)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400
"""
