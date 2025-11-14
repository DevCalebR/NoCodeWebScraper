"""
ScraperPro - Web Interface
Streamlit-based UI for managing scraper configurations
"""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from scraper import (
    ScraperPro, ClientManager, ScraperConfig, 
    SubscriptionTier, hashlib, datetime
)

# Page configuration
st.set_page_config(
    page_title="ScraperPro - Enterprise Web Scraping",
    page_icon="🕷️",
    layout="wide"
)

# Initialize session state
if 'app' not in st.session_state:
    st.session_state.app = ScraperPro()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'client' not in st.session_state:
    st.session_state.client = None


def login_page():
    """Login/Register page"""
    st.title("🕷️ ScraperPro - Enterprise Web Scraping Platform")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Pricing"])
    
    with tab1:
        st.header("Login to Your Account")
        api_key = st.text_input("API Key", type="password")
        if st.button("Login"):
            client = st.session_state.app.client_manager.verify_api_key(api_key)
            if client:
                st.session_state.logged_in = True
                st.session_state.client = client
                st.success(f"Welcome back, {client.name}!")
                st.rerun()
            else:
                st.error("Invalid API key")
    
    with tab2:
        st.header("Start Your 7-Day Free Trial")
        st.info("🎉 Try any plan free for 7 days! No credit card required to start.")
        
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        tier = st.selectbox(
            "Select Your Trial Plan", 
            ["PRO", "ENTERPRISE"],
            help="Choose the plan you'd like to try. You'll get full access for 7 days!"
        )
        
        # Show what they'll get during trial
        trial_tier_info = SubscriptionTier[tier].value
        st.write(f"**During your 7-day trial, you'll get:**")
        st.write(f"✅ {trial_tier_info['max_requests_per_day'] if trial_tier_info['max_requests_per_day'] != -1 else 'Unlimited'} requests/day")
        st.write(f"✅ {trial_tier_info['max_configs'] if trial_tier_info['max_configs'] != -1 else 'Unlimited'} configurations")
        st.write(f"✅ Export formats: {', '.join(trial_tier_info['export_formats'])}")
        st.write(f"✅ API access: {'Yes' if trial_tier_info['api_access'] else 'No'}")
        
        if st.button("🚀 Start Free Trial", type="primary"):
            if name and email:
                client = st.session_state.app.client_manager.create_client(name, email, tier)
                st.success("🎉 Trial account created successfully!")
                st.code(f"Your API Key: {client.api_key}", language="text")
                st.info("⚠️ Save this API key securely. You'll need it to login.")
                
                # Calculate trial end date for display
                from datetime import datetime
                trial_end = datetime.fromisoformat(client.trial_ends_at)
                st.warning(f"📅 Your trial ends on {trial_end.strftime('%B %d, %Y at %I:%M %p')}. After that, you'll need to add payment to continue using {tier}.")
            else:
                st.error("Please fill all fields")
    
    with tab3:
        st.header("💰 Pricing Plans")
        
        st.info("🎁 **All plans include a 7-day free trial!** Try before you buy.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⭐ Pro")
            st.metric("Price", "$49/month")
            st.caption("After 7-day free trial")
            st.write("**Features:**")
            st.write("✅ 1,000 requests/day")
            st.write("✅ 10 configurations")
            st.write("✅ CSV, Excel, JSON export")
            st.write("✅ Scheduled scraping")
            st.write("✅ API access")
            st.write("✅ Custom headers")
            st.write("✅ 7-day free trial")
        
        with col2:
            st.subheader("🚀 Enterprise")
            st.metric("Price", "$199/month")
            st.caption("After 7-day free trial")
            st.write("**Features:**")
            st.write("✅ Unlimited requests")
            st.write("✅ Unlimited configurations")
            st.write("✅ All export formats + SQL")
            st.write("✅ Advanced scheduling")
            st.write("✅ Priority support")
            st.write("✅ Dedicated proxies")
            st.write("✅ Custom integrations")
            st.write("✅ 7-day free trial")
        
        st.write("---")
        st.write("### ❓ Frequently Asked Questions")
        
        with st.expander("How does the free trial work?"):
            st.write("""
            - Sign up and choose either Pro or Enterprise
            - Get full access to all features for 7 days
            - No credit card required to start
            - On day 7, your trial expires
            - Add payment to continue with your chosen plan
            - Cancel anytime during the trial with no charges
            """)
        
        with st.expander("What happens after the trial?"):
            st.write("""
            When your 7-day trial ends:
            - Your account will be temporarily deactivated
            - Your data and configurations are saved
            - Add payment to reactivate and continue
            - You'll be charged the monthly rate for your selected plan
            """)
        
        with st.expander("Can I switch plans?"):
            st.write("""
            Yes! Contact support to:
            - Upgrade from Pro to Enterprise anytime
            - Downgrade (at next billing cycle)
            - Cancel your subscription
            """)


def dashboard():
    """Main dashboard for logged-in users"""
    client = st.session_state.client
    
    # Sidebar
    with st.sidebar:
        st.title("👤 Account")
        st.write(f"**Name:** {client.name}")
        st.write(f"**Email:** {client.email}")
        st.write(f"**Plan:** {client.tier}")
        
        # Trial warning banner
        if client.is_trial:
            days_remaining = st.session_state.app.client_manager.get_trial_days_remaining(client)
            if days_remaining > 0:
                st.warning(f"⏰ **Trial:** {days_remaining} days remaining")
                st.caption(f"Trial ends: {datetime.fromisoformat(client.trial_ends_at).strftime('%b %d, %Y')}")
                
                if st.button("💳 Add Payment & Activate", type="primary"):
                    st.info("Payment processing coming soon! This will convert your trial to a paid subscription.")
                    # TODO: Integrate Stripe here
                    # if st.session_state.app.client_manager.convert_trial_to_paid(client):
                    #     st.success("Account activated!")
                    #     st.rerun()
            else:
                st.error("⚠️ Trial Expired")
                st.write("Your trial has ended. Add payment to continue.")
                if st.button("💳 Activate Subscription", type="primary"):
                    st.info("Payment processing coming soon!")
        else:
            st.success("✅ Active Subscription")
        
        st.write("---")
        
        tier_info = SubscriptionTier[client.tier].value
        if tier_info['max_requests_per_day'] == -1:
            st.metric("Requests Today", client.requests_today, "Unlimited")
        else:
            remaining = tier_info['max_requests_per_day'] - client.requests_today
            st.metric("Requests Remaining", remaining, f"of {tier_info['max_requests_per_day']}")
        
        st.write("---")
        if st.button("🔑 Show API Key"):
            st.code(client.api_key, language="text")
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.client = None
            st.rerun()
    
    # Main content
    st.title(f"🕷️ ScraperPro Dashboard")
    
    # Show trial expiration warning at top if trial is ending soon
    if client.is_trial:
        days_remaining = st.session_state.app.client_manager.get_trial_days_remaining(client)
        if days_remaining <= 2 and days_remaining > 0:
            st.warning(f"⚠️ Your trial ends in {days_remaining} day{'s' if days_remaining != 1 else ''}! Add payment to keep your {client.tier} features.")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Run Scraper", "⚙️ Configurations", "📊 Results"])
    
    with tab1:
        run_scraper_tab()
    
    with tab2:
        configurations_tab()
    
    with tab3:
        results_tab()


def run_scraper_tab():
    """Tab for running scrapers"""
    st.header("Run Scraper")
    
    client = st.session_state.client
    
    # Check if trial expired
    if client.is_trial and not client.active:
        st.error("🚫 Your trial has expired. Please add payment to continue using ScraperPro.")
        st.info("Your data and configurations are safe. Activate your subscription to regain access.")
        if st.button("💳 Add Payment Method", type="primary"):
            st.info("Payment processing integration coming soon! This will activate your subscription.")
        return
    
    # List existing configurations
    config_dir = Path('data/configs')
    config_files = list(config_dir.glob(f'{client.client_id}_*.json'))
    
    if not config_files:
        st.info("No configurations found. Create one in the Configurations tab first.")
        return
    
    config_options = {}
    for config_file in config_files:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            config_options[config_data['name']] = config_data['config_id']
    
    selected_config_name = st.selectbox("Select Configuration", list(config_options.keys()))
    
    if st.button("🚀 Run Scraper", type="primary"):
        config_id = config_options[selected_config_name]
        
        with st.spinner("Scraping in progress..."):
            result = st.session_state.app.execute_scrape(client.api_key, config_id)
        
        if result['success']:
            st.success(f"✅ Scraping completed! {result['records']} records extracted.")
            st.info(f"Output file: {result['output_file']}")
            
            # Show trial info if applicable
            if 'trial_info' in result:
                trial = result['trial_info']
                st.info(f"🎁 Trial Status: {trial['days_remaining']} days remaining on your {trial['selected_tier']} trial")
            
            if result['requests_remaining'] != -1:
                st.write(f"Requests remaining today: {result['requests_remaining']}")
            
            # Show preview
            if result['output_file'].endswith('.csv'):
                df = pd.read_csv(result['output_file'])
                st.dataframe(df.head(10))
        else:
            if result.get('trial_expired'):
                st.error(f"❌ {result['error']}")
                if st.button("💳 Activate Now", type="primary"):
                    st.info("Payment processing coming soon!")
            else:
                st.error(f"❌ Scraping failed: {result['error']}")
                if 'upgrade_url' in result:
                    st.warning("Consider upgrading your plan for higher limits!")


def configurations_tab():
    """Tab for managing configurations"""
    st.header("Scraper Configurations")
    
    client = st.session_state.client
    tier_info = SubscriptionTier[client.tier].value
    
    # Check config limit
    config_dir = Path('data/configs')
    existing_configs = len(list(config_dir.glob(f'{client.client_id}_*.json')))
    max_configs = tier_info['max_configs']
    
    if max_configs != -1:
        st.write(f"Configurations: {existing_configs} / {max_configs}")
        if existing_configs >= max_configs:
            st.warning("⚠️ Configuration limit reached. Upgrade to add more configurations.")
            return
    
    st.subheader("Create New Configuration")
    
    with st.form("new_config"):
        config_name = st.text_input("Configuration Name", placeholder="My E-commerce Scraper")
        target_url = st.text_input("Target URL", placeholder="https://example.com/products")
        
        st.write("**CSS Selectors** (Use browser DevTools to find selectors)")
        container = st.text_input("Container Selector", placeholder=".product-card", 
                                  help="Selector for each item container")
        
        col1, col2 = st.columns(2)
        with col1:
            selector1_name = st.text_input("Field 1 Name", placeholder="title")
            selector1_css = st.text_input("Field 1 Selector", placeholder=".product-title")
        with col2:
            selector2_name = st.text_input("Field 2 Name", placeholder="price")
            selector2_css = st.text_input("Field 2 Selector", placeholder=".product-price")
        
        col3, col4 = st.columns(2)
        with col3:
            selector3_name = st.text_input("Field 3 Name", placeholder="rating")
            selector3_css = st.text_input("Field 3 Selector", placeholder=".rating")
        with col4:
            selector4_name = st.text_input("Field 4 Name", placeholder="url")
            selector4_css = st.text_input("Field 4 Selector", placeholder="a.product-link")
        
        enable_pagination = st.checkbox("Enable Pagination")
        next_page_selector = None
        if enable_pagination:
            next_page_selector = st.text_input("Next Page Button Selector", 
                                              placeholder=".next-page")
        
        output_format = st.selectbox("Output Format", tier_info['export_formats'])
        
        submitted = st.form_submit_button("💾 Save Configuration", type="primary")
        
        if submitted:
            if not config_name or not target_url:
                st.error("Configuration name and URL are required")
            else:
                # Build selectors dictionary
                selectors = {'container': container}
                if selector1_name and selector1_css:
                    selectors[selector1_name] = selector1_css
                if selector2_name and selector2_css:
                    selectors[selector2_name] = selector2_css
                if selector3_name and selector3_css:
                    selectors[selector3_name] = selector3_css
                if selector4_name and selector4_css:
                    selectors[selector4_name] = selector4_css
                
                # Create configuration
                config_id = hashlib.md5(f"{config_name}{datetime.now()}".encode()).hexdigest()[:8]
                
                pagination = None
                if enable_pagination and next_page_selector:
                    pagination = {'next_selector': next_page_selector}
                
                config = ScraperConfig(
                    config_id=config_id,
                    client_id=client.client_id,
                    name=config_name,
                    target_url=target_url,
                    selectors=selectors,
                    pagination=pagination,
                    output_format=output_format
                )
                
                st.session_state.app.save_scraper_config(config)
                st.success(f"✅ Configuration '{config_name}' saved successfully!")
                st.rerun()
    
    # List existing configurations
    st.write("---")
    st.subheader("Existing Configurations")
    
    config_files = list(config_dir.glob(f'{client.client_id}_*.json'))
    
    if config_files:
        for config_file in config_files:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                with st.expander(f"📋 {config_data['name']}"):
                    st.write(f"**URL:** {config_data['target_url']}")
                    st.write(f"**Format:** {config_data['output_format']}")
                    st.json(config_data['selectors'])
    else:
        st.info("No configurations yet. Create one above!")


def results_tab():
    """Tab for viewing results"""
    st.header("Scraping Results")
    
    client = st.session_state.client
    output_dir = Path('output')
    
    result_files = sorted(
        [f for f in output_dir.glob(f'{client.client_id}_*') 
         if f.suffix in ['.csv', '.xlsx', '.json']],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if not result_files:
        st.info("No results yet. Run a scraper to see results here!")
        return
    
    st.write(f"Found {len(result_files)} result files")
    
    for result_file in result_files[:10]:  # Show last 10 results
        with st.expander(f"📄 {result_file.name}"):
            st.write(f"**Size:** {result_file.stat().st_size / 1024:.2f} KB")
            st.write(f"**Created:** {datetime.fromtimestamp(result_file.stat().st_mtime)}")
            
            try:
                if result_file.suffix == '.csv':
                    df = pd.read_csv(result_file)
                    st.dataframe(df)
                    st.download_button(
                        "⬇️ Download",
                        df.to_csv(index=False),
                        file_name=result_file.name,
                        mime="text/csv"
                    )
                elif result_file.suffix == '.json':
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                    st.json(data[:5])  # Show first 5 records
                    with open(result_file, 'rb') as f:
                        st.download_button(
                            "⬇️ Download",
                            f,
                            file_name=result_file.name,
                            mime="application/json"
                        )
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")


# Main app logic
def main():
    if st.session_state.logged_in:
        dashboard()
    else:
        login_page()


if __name__ == '__main__':
    main()
