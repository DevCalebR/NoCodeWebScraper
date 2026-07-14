"""
ScraperPro Admin Panel
Complete dashboard for monitoring clients, trials, revenue, and system health
"""

import hmac
import os

import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from scraper import ScraperPro, ClientConfig, SubscriptionTier
import plotly.express as px
import plotly.graph_objects as go

ADMIN_PASSWORD = os.environ.get("SCRAPERPRO_ADMIN_PASSWORD")

st.set_page_config(
    page_title="ScraperPro Admin Panel",
    page_icon="🔐",
    layout="wide"
)

# Initialize
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'app' not in st.session_state:
    st.session_state.app = ScraperPro()


def admin_login():
    """Admin login page"""
    st.title("🔐 ScraperPro Admin Panel")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")

        if not ADMIN_PASSWORD:
            st.error(
                "Admin access is disabled. Set SCRAPERPRO_ADMIN_PASSWORD in the "
                "server environment before starting the admin panel."
            )
            return

        password = st.text_input("Admin Password", type="password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if hmac.compare_digest(password, ADMIN_PASSWORD):
                st.session_state.admin_logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid password")
        
        st.markdown("---")
        st.caption("Admin credentials are configured through the server environment.")


def get_all_clients():
    """Load all client data"""
    client_dir = Path('data/clients')
    clients = []
    
    for client_file in client_dir.glob('*.json'):
        with open(client_file, 'r') as f:
            data = json.load(f)
            clients.append(ClientConfig(**data))
    
    return clients


def get_client_stats():
    """Calculate aggregate statistics"""
    clients = get_all_clients()
    
    total_clients = len(clients)
    active_trials = sum(1 for c in clients if c.is_trial and c.active)
    expired_trials = sum(1 for c in clients if c.is_trial and not c.active)
    paid_clients = sum(1 for c in clients if not c.is_trial and c.active)
    
    # Revenue calculation
    mrr = 0
    for client in clients:
        if not client.is_trial and client.active:
            tier_price = SubscriptionTier[client.tier].value['price']
            mrr += tier_price
    
    arr = mrr * 12
    
    # Trial conversion rate
    total_trials = active_trials + expired_trials + paid_clients
    conversion_rate = (paid_clients / total_trials * 100) if total_trials > 0 else 0
    
    return {
        'total_clients': total_clients,
        'active_trials': active_trials,
        'expired_trials': expired_trials,
        'paid_clients': paid_clients,
        'mrr': mrr,
        'arr': arr,
        'conversion_rate': conversion_rate
    }


def get_usage_stats():
    """Get usage statistics"""
    clients = get_all_clients()
    
    total_requests_today = sum(c.requests_today for c in clients)
    
    # Count configurations
    config_dir = Path('data/configs')
    total_configs = len(list(config_dir.glob('*.json')))
    
    # Count output files
    output_dir = Path('output')
    total_outputs = len(list(output_dir.glob('*.*')))
    
    return {
        'total_requests_today': total_requests_today,
        'total_configs': total_configs,
        'total_outputs': total_outputs
    }


def dashboard():
    """Main admin dashboard"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 ScraperPro Admin Dashboard")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
    
    st.markdown("---")
    
    # Get stats
    stats = get_client_stats()
    usage = get_usage_stats()
    
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("💰 MRR", f"${stats['mrr']:,.0f}", f"${stats['arr']:,.0f} ARR")
    
    with col2:
        st.metric("👥 Total Clients", stats['total_clients'])
    
    with col3:
        st.metric("💳 Paid Clients", stats['paid_clients'])
    
    with col4:
        st.metric("🎁 Active Trials", stats['active_trials'])
    
    with col5:
        st.metric("📈 Conversion", f"{stats['conversion_rate']:.1f}%")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "👥 Clients", 
        "🎁 Trials", 
        "💰 Revenue",
        "⚙️ System"
    ])
    
    with tab1:
        overview_tab(stats, usage)
    
    with tab2:
        clients_tab()
    
    with tab3:
        trials_tab()
    
    with tab4:
        revenue_tab()
    
    with tab5:
        system_tab()


def overview_tab(stats, usage):
    """Overview dashboard"""
    st.header("Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Business Metrics")
        
        metrics_data = {
            'Metric': ['MRR', 'ARR', 'Paid Clients', 'Active Trials', 'Conversion Rate'],
            'Value': [
                f"${stats['mrr']:,.0f}",
                f"${stats['arr']:,.0f}",
                stats['paid_clients'],
                stats['active_trials'],
                f"{stats['conversion_rate']:.1f}%"
            ]
        }
        st.dataframe(pd.DataFrame(metrics_data), use_container_width=True, hide_index=True)
        
        # Quick actions
        st.markdown("### 🚀 Quick Actions")
        if st.button("📧 Send Trial Reminders", use_container_width=True):
            st.info("Trial reminder emails would be sent here")
        
        if st.button("📊 Export Client Data", use_container_width=True):
            clients = get_all_clients()
            df = pd.DataFrame([{
                'Name': c.name,
                'Email': c.email,
                'Tier': c.tier,
                'Status': 'Trial' if c.is_trial else 'Paid',
                'Active': c.active,
                'Created': c.created_at
            } for c in clients])
            csv = df.to_csv(index=False)
            st.download_button(
                "⬇️ Download CSV",
                csv,
                "clients.csv",
                "text/csv"
            )
    
    with col2:
        st.subheader("📈 Usage Statistics")
        
        usage_data = {
            'Metric': ['Requests Today', 'Total Configs', 'Output Files'],
            'Value': [
                usage['total_requests_today'],
                usage['total_configs'],
                usage['total_outputs']
            ]
        }
        st.dataframe(pd.DataFrame(usage_data), use_container_width=True, hide_index=True)
        
        # Recent activity
        st.markdown("### 🕐 Recent Activity")
        output_dir = Path('output')
        recent_files = sorted(
            output_dir.glob('*.*'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:5]
        
        if recent_files:
            for f in recent_files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                st.caption(f"📄 {f.name} - {mtime.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.info("No recent activity")


def clients_tab():
    """Client management tab"""
    st.header("👥 Client Management")
    
    clients = get_all_clients()
    
    if not clients:
        st.info("No clients yet")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("Status", ["All", "Active", "Inactive"])
    
    with col2:
        filter_type = st.selectbox("Type", ["All", "Trial", "Paid"])
    
    with col3:
        filter_tier = st.selectbox("Tier", ["All", "PRO", "ENTERPRISE"])
    
    # Filter clients
    filtered = clients
    
    if filter_status != "All":
        filtered = [c for c in filtered if c.active == (filter_status == "Active")]
    
    if filter_type != "All":
        if filter_type == "Trial":
            filtered = [c for c in filtered if c.is_trial]
        else:
            filtered = [c for c in filtered if not c.is_trial]
    
    if filter_tier != "All":
        filtered = [c for c in filtered if c.tier == filter_tier]
    
    st.write(f"**Showing {len(filtered)} of {len(clients)} clients**")
    
    # Client table
    for client in filtered:
        with st.expander(f"👤 {client.name} - {client.email}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Account Info:**")
                st.write(f"- **ID:** {client.client_id}")
                st.write(f"- **Tier:** {client.tier}")
                st.write(f"- **Status:** {'🟢 Active' if client.active else '🔴 Inactive'}")
                st.write(f"- **Type:** {'🎁 Trial' if client.is_trial else '💳 Paid'}")
                st.write(f"- **Created:** {datetime.fromisoformat(client.created_at).strftime('%Y-%m-%d')}")
                
                if client.is_trial and client.trial_ends_at:
                    trial_end = datetime.fromisoformat(client.trial_ends_at)
                    days_left = (trial_end - datetime.now()).days
                    st.write(f"- **Trial Ends:** {trial_end.strftime('%Y-%m-%d')} ({days_left} days)")
            
            with col2:
                st.write("**Usage:**")
                st.write(f"- **Requests Today:** {client.requests_today}")
                st.write(f"- **Last Request:** {client.last_request_date or 'Never'}")
                
                # Count configs
                config_dir = Path('data/configs')
                user_configs = len(list(config_dir.glob(f'{client.client_id}_*.json')))
                st.write(f"- **Configurations:** {user_configs}")
                
                # Count outputs
                output_dir = Path('output')
                user_outputs = len(list(output_dir.glob(f'{client.client_id}_*')))
                st.write(f"- **Output Files:** {user_outputs}")
            
            # Actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Email Client", key=f"email_{client.client_id}"):
                    st.info(f"Would send email to {client.email}")
            
            with col2:
                if client.is_trial and st.button("💳 Convert to Paid", key=f"convert_{client.client_id}"):
                    st.session_state.app.client_manager.convert_trial_to_paid(client)
                    st.success("Converted to paid!")
                    st.rerun()
            
            with col3:
                if client.active:
                    if st.button("❌ Deactivate", key=f"deact_{client.client_id}"):
                        client.active = False
                        st.session_state.app.client_manager._save_client(client)
                        st.success("Deactivated!")
                        st.rerun()
                else:
                    if st.button("✅ Activate", key=f"act_{client.client_id}"):
                        client.active = True
                        st.session_state.app.client_manager._save_client(client)
                        st.success("Activated!")
                        st.rerun()


def trials_tab():
    """Trial management tab"""
    st.header("🎁 Trial Management")
    
    clients = get_all_clients()
    trials = [c for c in clients if c.is_trial or c.trial_ends_at]
    
    if not trials:
        st.info("No trials yet")
        return
    
    # Trial stats
    active = [c for c in trials if c.is_trial and c.active]
    expired = [c for c in trials if c.is_trial and not c.active]
    converted = [c for c in trials if not c.is_trial and c.trial_ends_at]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🟢 Active Trials", len(active))
    
    with col2:
        st.metric("⏰ Expired Trials", len(expired))
    
    with col3:
        st.metric("💰 Converted", len(converted))
    
    st.markdown("---")
    
    # Expiring soon
    st.subheader("⚠️ Trials Expiring Soon")
    
    expiring_soon = []
    for client in active:
        trial_end = datetime.fromisoformat(client.trial_ends_at)
        days_left = (trial_end - datetime.now()).days
        if days_left <= 2:
            expiring_soon.append((client, days_left))
    
    if expiring_soon:
        for client, days_left in sorted(expiring_soon, key=lambda x: x[1]):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{client.name}** ({client.email})")
                st.caption(f"{client.tier} tier")
            
            with col2:
                if days_left > 0:
                    st.warning(f"⏰ {days_left} day{'s' if days_left != 1 else ''}")
                else:
                    st.error("🚨 Expired")
            
            with col3:
                if st.button("📧 Remind", key=f"remind_{client.client_id}"):
                    st.success(f"Reminder sent to {client.email}")
    else:
        st.info("No trials expiring in the next 2 days")
    
    st.markdown("---")
    
    # All trials
    st.subheader("📋 All Trials")
    
    for client in trials:
        status = "🟢 Active" if (client.is_trial and client.active) else "⏰ Expired" if client.is_trial else "💰 Converted"
        
        with st.expander(f"{status} - {client.name} ({client.tier})"):
            if client.trial_ends_at:
                trial_end = datetime.fromisoformat(client.trial_ends_at)
                days_left = (trial_end - datetime.now()).days
                
                st.write(f"**Email:** {client.email}")
                st.write(f"**Started:** {datetime.fromisoformat(client.created_at).strftime('%Y-%m-%d')}")
                st.write(f"**Ends:** {trial_end.strftime('%Y-%m-%d')}")
                
                if client.is_trial:
                    st.write(f"**Days Left:** {max(0, days_left)}")


def revenue_tab():
    """Revenue tracking tab"""
    st.header("💰 Revenue Analytics")
    
    clients = get_all_clients()
    paid = [c for c in clients if not c.is_trial and c.active]
    
    if not paid:
        st.info("No paid customers yet")
        return
    
    # Current MRR breakdown
    pro_count = sum(1 for c in paid if c.tier == 'PRO')
    ent_count = sum(1 for c in paid if c.tier == 'ENTERPRISE')
    
    pro_mrr = pro_count * 49
    ent_mrr = ent_count * 199
    total_mrr = pro_mrr + ent_mrr
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Total MRR", f"${total_mrr:,.0f}")
        st.caption(f"${total_mrr * 12:,.0f} ARR")
    
    with col2:
        st.metric("⭐ Pro Clients", pro_count)
        st.caption(f"${pro_mrr:,.0f}/mo")
    
    with col3:
        st.metric("🚀 Enterprise Clients", ent_count)
        st.caption(f"${ent_mrr:,.0f}/mo")
    
    # Revenue chart
    st.subheader("📊 Revenue Breakdown")
    
    fig = go.Figure(data=[
        go.Bar(name='Pro', x=['Current MRR'], y=[pro_mrr]),
        go.Bar(name='Enterprise', x=['Current MRR'], y=[ent_mrr])
    ])
    
    fig.update_layout(
        title="MRR by Tier",
        yaxis_title="Revenue ($)",
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Customer list
    st.subheader("💳 Paid Customers")
    
    customer_data = []
    for client in paid:
        tier_price = SubscriptionTier[client.tier].value['price']
        customer_data.append({
            'Name': client.name,
            'Email': client.email,
            'Tier': client.tier,
            'MRR': f"${tier_price}",
            'Joined': datetime.fromisoformat(client.created_at).strftime('%Y-%m-%d')
        })
    
    df = pd.DataFrame(customer_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def system_tab():
    """System health and settings"""
    st.header("⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 Storage")
        
        # Calculate directory sizes
        def get_dir_size(path):
            total = 0
            for p in Path(path).rglob('*'):
                if p.is_file():
                    total += p.stat().st_size
            return total / (1024 * 1024)  # MB
        
        st.write(f"**Clients:** {get_dir_size('data/clients'):.2f} MB")
        st.write(f"**Configs:** {get_dir_size('data/configs'):.2f} MB")
        st.write(f"**Output:** {get_dir_size('output'):.2f} MB")
        st.write(f"**Logs:** {get_dir_size('logs'):.2f} MB")
        
        if st.button("🗑️ Clear Old Outputs (30+ days)"):
            count = 0
            cutoff = datetime.now() - timedelta(days=30)
            for f in Path('output').glob('*'):
                if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                    f.unlink()
                    count += 1
            st.success(f"Deleted {count} old files")
    
    with col2:
        st.subheader("🔐 Security")
        
        st.write("**Admin Password:**")
        new_password = st.text_input("Change Admin Password", type="password")
        if st.button("Update Password"):
            if new_password:
                st.warning("⚠️ Update ADMIN_PASSWORD in admin_panel.py file manually")
            else:
                st.error("Enter a new password")
        
        st.markdown("---")
        
        st.write("**API Keys:**")
        clients = get_all_clients()
        st.write(f"Total API keys: {len(clients)}")
        
        if st.button("🔄 Regenerate All Keys"):
            st.warning("⚠️ This would invalidate all client API keys!")


# Main app logic
def main():
    if st.session_state.admin_logged_in:
        dashboard()
    else:
        admin_login()


if __name__ == '__main__':
    main()
