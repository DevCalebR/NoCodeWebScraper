"""Prototype Streamlit interface for managing scraper configurations."""

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
from scraper import (
    ScraperPro, ClientManager, ScraperConfig, 
    SubscriptionTier, hashlib
)

# Page configuration
st.set_page_config(
    page_title="ScraperPro Prototype",
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
    st.title("🕷️ ScraperPro Prototype")
    st.warning(
        "Private prototype: billing, scheduling, proxy, support, and production "
        "security capabilities are incomplete or unverified."
    )
    
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
        
        trial_tier_info = SubscriptionTier[tier].value
        st.write(f"**During your 7-day trial, you'll get:**")
        st.write(f"✅ {trial_tier_info['max_requests_per_day'] if trial_tier_info['max_requests_per_day'] != -1 else 'Unlimited'} requests/day")
        st.write(f"✅ {trial_tier_info['max_configs'] if trial_tier_info['max_configs'] != -1 else 'Unlimited'} configurations")
        st.write(f"✅ Export formats: {', '.join(trial_tier_info['export_formats'])}")
        st.write(f"✅ API access: {'Yes' if trial_tier_info['api_access'] else 'No'}")
        st.write("✅ **NEW: Visual Recorder** - No-code scraper builder")
        
        if st.button("🚀 Start Free Trial", type="primary"):
            if name and email:
                client = st.session_state.app.client_manager.create_client(name, email, tier)
                st.success("🎉 Trial account created successfully!")
                st.code(f"Your API Key: {client.api_key}", language="text")
                st.info("⚠️ Save this API key securely. You'll need it to login.")
                
                trial_end = datetime.fromisoformat(client.trial_ends_at)
                st.warning(f"📅 Your trial ends on {trial_end.strftime('%B %d, %Y at %I:%M %p')}.")
            else:
                st.error("Please fill all fields")
    
    with tab3:
        st.header("Prototype status")
        st.info(
            "Tier names and limits are development fixtures. No public pricing, "
            "service level, support, proxy, or production billing offer is active."
        )


def dashboard():
    """Main dashboard for logged-in users"""
    client = st.session_state.client
    
    # Sidebar
    with st.sidebar:
        st.title("👤 Account")
        st.write(f"**Name:** {client.name}")
        st.write(f"**Email:** {client.email}")
        st.write(f"**Plan:** {client.tier}")
        
        if client.is_trial:
            days_remaining = st.session_state.app.client_manager.get_trial_days_remaining(client)
            if days_remaining > 0:
                st.warning(f"⏰ **Trial:** {days_remaining} days remaining")
                st.caption(f"Trial ends: {datetime.fromisoformat(client.trial_ends_at).strftime('%b %d, %Y')}")
                
                if st.button("💳 Add Payment & Activate", type="primary"):
                    st.info("Payment processing coming soon!")
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
    
    # Show trial expiration warning
    if client.is_trial:
        days_remaining = st.session_state.app.client_manager.get_trial_days_remaining(client)
        if days_remaining <= 2 and days_remaining > 0:
            st.warning(f"⚠️ Your trial ends in {days_remaining} day{'s' if days_remaining != 1 else ''}! Add payment to keep your {client.tier} features.")
    
    # NEW: Add Visual Recorder tab
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎥 Visual Recorder",  # NEW!
        "🎯 Run Scraper", 
        "⚙️ Configurations", 
        "📊 Results"
    ])
    
    with tab1:
        visual_recorder_tab()  # NEW FUNCTION
    
    with tab2:
        run_scraper_tab()
    
    with tab3:
        configurations_tab()
    
    with tab4:
        results_tab()


def visual_recorder_tab():
    """NEW: Visual Recorder interface"""
    st.header("🎥 Visual Scraper Recorder")
    
    st.info("""
    **🚀 NEW FEATURE: Record your browsing to create scrapers automatically!**
    
    The Visual Recorder watches you browse and click, then generates a scraper configuration for you.
    No CSS selectors needed!
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### How it works:
        
        1. **Install Extension** - Install the ScraperPro Chrome/Firefox extension
        2. **Start Recording** - Click the record button in the extension
        3. **Browse & Click** - Navigate to your target site and click elements you want to extract
        4. **Stop Recording** - The extension sends the data here
        5. **Review & Deploy** - We auto-generate your scraper config!
        
        ### What gets recorded:
        - ✅ Pages you visit
        - ✅ Elements you click
        - ✅ Data you select to extract
        - ✅ Pagination buttons
        - ❌ Passwords or sensitive data (never recorded)
        """)
    
    with col2:
        st.markdown("""
        ### 📥 Install Extension
        
        Available for:
        - Chrome Web Store
        - Firefox Add-ons
        - Edge Extensions
        
        👉 [Download Extension](#)
        """)
        
        if st.button("🎬 Open Recorder UI", type="primary", use_container_width=True):
            st.info("Opening Visual Recorder in new window...")
    
    st.markdown("---")
    
    # Show recent recordings
    st.subheader("📼 Your Recordings")
    
    try:
        client = st.session_state.client
        recordings_dir = Path('data/recordings')
        
        if recordings_dir.exists():
            # Filter recordings for this client
            client_recordings = list(recordings_dir.glob(f'{client.client_id}_*.json'))
            
            if client_recordings:
                st.write(f"Found {len(client_recordings)} recording(s)")
                
                for rec_file in sorted(client_recordings, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    try:
                        with open(rec_file, 'r') as f:
                            rec_data = json.load(f)
                        
                        with st.expander(f"🎬 Recording: {rec_data.get('recording_id', rec_file.stem)}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Actions", rec_data.get('action_count', 0))
                            
                            with col2:
                                if rec_data.get('timestamp'):
                                    timestamp = datetime.fromtimestamp(rec_data['timestamp'] / 1000)
                                    st.write(f"**Created:** {timestamp.strftime('%Y-%m-%d %H:%M')}")
                            
                            with col3:
                                if st.button("Generate Config", key=f"gen_{rec_file.stem}"):
                                    st.info("Config generation coming soon! This will analyze your recording and create a scraper configuration.")
                            
                            # Show actions preview
                            if rec_data.get('actions'):
                                st.write("**Actions Preview:**")
                                for i, action in enumerate(rec_data['actions'][:5]):
                                    st.caption(f"{i+1}. {action.get('type', 'unknown')} - {action.get('selector', '')[:50]}")
                                if len(rec_data['actions']) > 5:
                                    st.caption(f"... and {len(rec_data['actions']) - 5} more actions")
                    except Exception as e:
                        st.error(f"Error loading recording {rec_file.name}: {str(e)}")
            else:
                st.info("No recordings yet. Install the extension and start recording!")
        else:
            recordings_dir.mkdir(parents=True, exist_ok=True)
            st.info("No recordings yet. Install the extension and start recording!")
    except Exception as e:
        st.error(f"Error loading recordings: {str(e)}")
    
    # Tutorial section
    st.markdown("---")
    st.subheader("🎓 Quick Tutorial")
    
    video_tab, guide_tab = st.tabs(["📹 Video", "📖 Step-by-Step"])
    
    with video_tab:
        st.info("Video tutorial coming soon!")
    
    with guide_tab:
        st.markdown("""
        ### Step-by-Step Guide
        
        #### 1. Install the Extension
        - Visit Chrome Web Store
        - Search "ScraperPro Visual Recorder"
        - Click "Add to Chrome"
        
        #### 2. Start Recording
        - Click the ScraperPro icon in your toolbar
        - Click "Start Recording"
        - A red banner appears (you're now recording!)
        
        #### 3. Navigate & Extract
        - Go to the website you want to scrape
        - Click on the **first item** in a list
        - Select data fields you want:
          - Click an element
          - Enter field name (e.g., "title", "price")
          - Click "Extract This"
        
        #### 4. Set Container (Optional)
        - Click the box that contains all items
        - Click "Set as Container"
        - This helps us detect the pattern
        
        #### 5. Test Pagination
        - Click the "Next" button if there are multiple pages
        - We'll automatically detect pagination
        
        #### 6. Stop Recording
        - Click "Stop Recording" in the extension
        - Your recording is automatically saved here
        
        #### 7. Generate & Deploy
        - Come back to this page
        - Click "Generate Config" on your recording
        - Review the configuration
        - Click "Save & Deploy" to start using it!
        
        ### 💡 Pro Tips
        - Always click the **first item** in a list/grid
        - Extract all fields from that one item
        - We'll automatically apply to all similar items
        - Test on 2-3 pages for best accuracy
        - Use descriptive field names (price, rating, etc.)
        """)


def run_scraper_tab():
    """Tab for running scrapers"""
    st.header("Run Scraper")
    
    client = st.session_state.client
    
    if client.is_trial and not client.active:
        st.error("🚫 Your trial has expired. Please add payment to continue using ScraperPro.")
        st.info("Your data and configurations are safe. Activate your subscription to regain access.")
        if st.button("💳 Add Payment Method", type="primary"):
            st.info("Payment processing integration coming soon!")
        return
    
    config_dir = Path('data/configs')
    config_files = list(config_dir.glob(f'{client.client_id}_*.json'))
    
    if not config_files:
        st.info("No configurations found. Create one in the Configurations tab or use Visual Recorder!")
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
            
            if 'trial_info' in result:
                trial = result['trial_info']
                st.info(f"🎁 Trial Status: {trial['days_remaining']} days remaining on your {trial['selected_tier']} trial")
            
            if result['requests_remaining'] != -1:
                st.write(f"Requests remaining today: {result['requests_remaining']}")
            
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


def configurations_tab():
    """Tab for managing configurations"""
    st.header("Scraper Configurations")
    
    st.info("💡 **Tip:** Use the Visual Recorder to create configurations without writing CSS selectors!")
    
    client = st.session_state.client
    tier_info = SubscriptionTier[client.tier].value
    
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
        
        st.write("**CSS Selectors** (Use browser DevTools to find selectors or use Visual Recorder)")
        container = st.text_input("Container Selector", placeholder=".product-card")
        
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
            next_page_selector = st.text_input("Next Page Button Selector", placeholder=".next-page")
        
        output_format = st.selectbox("Output Format", tier_info['export_formats'])
        
        submitted = st.form_submit_button("💾 Save Configuration", type="primary")
        
        if submitted:
            if not config_name or not target_url:
                st.error("Configuration name and URL are required")
            else:
                selectors = {'container': container}
                if selector1_name and selector1_css:
                    selectors[selector1_name] = selector1_css
                if selector2_name and selector2_css:
                    selectors[selector2_name] = selector2_css
                if selector3_name and selector3_css:
                    selectors[selector3_name] = selector3_css
                if selector4_name and selector4_css:
                    selectors[selector4_name] = selector4_css
                
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
        st.info("No configurations yet. Create one above or use Visual Recorder!")


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
    
    for result_file in result_files[:10]:
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
                    st.json(data[:5])
                    with open(result_file, 'rb') as f:
                        st.download_button(
                            "⬇️ Download",
                            f,
                            file_name=result_file.name,
                            mime="application/json"
                        )
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")


def main():
    if st.session_state.logged_in:
        dashboard()
    else:
        login_page()


if __name__ == '__main__':
    main()
