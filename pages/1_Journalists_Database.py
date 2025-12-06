"""
Israeli Journalists Database - Streamlit Page
Browse and search journalists scraped from Israeli media organizations
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth import check_password

# Page config
st.set_page_config(
    page_title="Journalists Database",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check password first
if not check_password():
    st.stop()

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
JOURNALISTS_FILE = DATA_DIR / "journalists.json"
ORGANIZATIONS_FILE = DATA_DIR / "media_organizations.json"

# Custom CSS matching main app style
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --info-color: #17a2b8;
    }

    /* Custom cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Info boxes */
    .info-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
    }

    /* Button improvements */
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Hebrew text support */
    .hebrew-text {
        direction: rtl;
        text-align: right;
        font-family: 'Arial', 'Helvetica', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading
@st.cache_data
def load_journalists_data():
    """Load journalists from JSON file with caching"""
    try:
        with open(JOURNALISTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading journalists: {e}")
        return {"journalists": [], "metadata": {}}

@st.cache_data
def load_organizations_data():
    """Load organizations from JSON file with caching"""
    try:
        with open(ORGANIZATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"organizations": []}

# Title
st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   font-size: 2.5em;
                   font-weight: bold;'>
            👥 Israeli Journalists Database
        </h1>
        <p style='color: #666; font-size: 1.1em;'>Browse and search journalists from Israeli media organizations</p>
    </div>
""", unsafe_allow_html=True)

# Load data
journalists_data = load_journalists_data()
orgs_data = load_organizations_data()

journalists = journalists_data.get('journalists', [])
metadata = journalists_data.get('metadata', {})

if not journalists:
    st.warning("No journalist data found. Run the scraping script first:")
    st.code("py -3.12 src/scrape_organizations.py scrape-all", language="bash")
    st.stop()

# Summary metrics
st.markdown("""
<div class='info-box'>
    <strong>Database Overview:</strong> Journalists scraped from Israeli media organization websites using Crawl4AI + Grok AI extraction.
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Journalists", len(journalists))
with col2:
    unique_orgs = len(set(j.get('organization_name', 'Unknown') for j in journalists))
    st.metric("Organizations", unique_orgs)
with col3:
    verified = sum(1 for j in journalists if j.get('verified', False))
    st.metric("Verified", verified)
with col4:
    with_email = sum(1 for j in journalists if j.get('email'))
    st.metric("With Email", with_email)

st.markdown("---")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filters")

    # Organization filter
    org_names = sorted(set(j.get('organization_name', 'Unknown') for j in journalists))
    selected_org = st.selectbox(
        "Organization",
        options=['All Organizations'] + org_names,
        index=0
    )

    # Search by name
    search_name = st.text_input("Search by Name", "", placeholder="Enter name...")

    # Beat/topic filter
    all_beats = []
    for j in journalists:
        beat = j.get('beat', '')
        if beat:
            all_beats.extend([b.strip() for b in beat.split(',') if b.strip()])
    unique_beats = sorted(set(all_beats))

    selected_beat = st.selectbox(
        "Beat/Topic",
        options=['All Beats'] + unique_beats[:50],
        index=0
    )

    # Job title filter
    all_titles = sorted(set(j.get('job_title_english', '') or j.get('job_title_hebrew', '') or 'Unknown'
                           for j in journalists if j.get('job_title_english') or j.get('job_title_hebrew')))
    selected_title = st.selectbox(
        "Job Title",
        options=['All Titles'] + all_titles[:50],
        index=0
    )

    st.markdown("---")

    # Database info
    st.subheader("📊 Database Stats")
    if metadata:
        st.caption(f"**Last Updated:** {metadata.get('last_updated', 'Unknown')[:10]}")
        st.caption(f"**Total Records:** {metadata.get('total_journalists', len(journalists))}")

    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# Apply filters
filtered = journalists.copy()

if selected_org != 'All Organizations':
    filtered = [j for j in filtered if j.get('organization_name') == selected_org]

if search_name:
    search_lower = search_name.lower()
    filtered = [j for j in filtered if
               search_lower in (j.get('name_english', '') or '').lower() or
               search_lower in (j.get('name_hebrew', '') or '').lower()]

if selected_beat != 'All Beats':
    filtered = [j for j in filtered if selected_beat.lower() in (j.get('beat', '') or '').lower()]

if selected_title != 'All Titles':
    filtered = [j for j in filtered if
               selected_title == (j.get('job_title_english', '') or j.get('job_title_hebrew', ''))]

# Display results count
st.info(f"Showing **{len(filtered)}** of **{len(journalists)}** journalists")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📋 Table View", "📈 Analytics", "🔍 Details"])

# TAB 1: TABLE VIEW
with tab1:
    if filtered:
        df_journalists = pd.DataFrame(filtered)

        # Select and rename columns for display
        display_cols = ['name_english', 'name_hebrew', 'organization_name', 'job_title_english',
                      'beat', 'email', 'profile_url', 'verified', 'confidence_score']
        available_cols = [col for col in display_cols if col in df_journalists.columns]

        # Rename columns for better display
        col_rename = {
            'name_english': 'Name (EN)',
            'name_hebrew': 'Name (HE)',
            'organization_name': 'Organization',
            'job_title_english': 'Title',
            'beat': 'Beat/Topics',
            'email': 'Email',
            'profile_url': 'Profile URL',
            'verified': 'Verified',
            'confidence_score': 'Confidence'
        }

        df_display = df_journalists[available_cols].rename(columns=col_rename)

        # Display table
        st.dataframe(
            df_display,
            use_container_width=True,
            height=600,
            column_config={
                "Profile URL": st.column_config.LinkColumn("Profile URL"),
                "Email": st.column_config.TextColumn("Email"),
                "Confidence": st.column_config.ProgressColumn(
                    "Confidence",
                    min_value=0,
                    max_value=100,
                    format="%d%%"
                ),
                "Verified": st.column_config.CheckboxColumn("Verified")
            }
        )

        # Download buttons
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Download filtered as CSV
            csv_filtered = df_journalists.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download Filtered (CSV)",
                data=csv_filtered,
                file_name=f"journalists_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Download full database as CSV
            df_all = pd.DataFrame(journalists)
            csv_full = df_all.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download All (CSV)",
                data=csv_full,
                file_name=f"journalists_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col3:
            # Download as JSON
            st.download_button(
                label="📥 Download All (JSON)",
                data=json.dumps(journalists, ensure_ascii=False, indent=2),
                file_name=f"journalists_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.warning("No journalists match the selected filters.")

# TAB 2: ANALYTICS
with tab2:
    import plotly.express as px

    st.subheader("📊 Journalists by Organization")

    # Organization distribution
    org_counts = {}
    for j in journalists:
        org = j.get('organization_name', 'Unknown')
        org_counts[org] = org_counts.get(org, 0) + 1

    org_counts_sorted = dict(sorted(org_counts.items(), key=lambda x: -x[1]))

    df_orgs = pd.DataFrame({
        'Organization': list(org_counts_sorted.keys())[:20],
        'Journalists': list(org_counts_sorted.values())[:20]
    })

    fig = px.bar(
        df_orgs,
        x='Journalists',
        y='Organization',
        orientation='h',
        title="Top 20 Organizations by Journalist Count",
        color='Journalists',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    # Beat distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Top Beats/Topics")
        beat_counts = {}
        for j in journalists:
            beat = j.get('beat', '')
            if beat:
                for b in beat.split(','):
                    b = b.strip()
                    if b:
                        beat_counts[b] = beat_counts.get(b, 0) + 1

        beat_counts_sorted = dict(sorted(beat_counts.items(), key=lambda x: -x[1])[:15])

        df_beats = pd.DataFrame({
            'Beat': list(beat_counts_sorted.keys()),
            'Count': list(beat_counts_sorted.values())
        })

        fig2 = px.pie(
            df_beats,
            values='Count',
            names='Beat',
            title="Distribution by Beat/Topic"
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("📧 Contact Information")
        with_email = sum(1 for j in journalists if j.get('email'))
        with_profile = sum(1 for j in journalists if j.get('profile_url'))
        total = len(journalists)

        contact_data = pd.DataFrame({
            'Type': ['With Email', 'Without Email', 'With Profile URL', 'Without Profile URL'],
            'Count': [with_email, total - with_email, with_profile, total - with_profile]
        })

        fig3 = px.bar(
            contact_data,
            x='Type',
            y='Count',
            color='Type',
            title="Contact Information Availability"
        )
        fig3.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    # Scrape dates
    st.subheader("📅 Data Freshness")
    scrape_dates = {}
    for j in journalists:
        date = j.get('scraped_date', '')[:10] if j.get('scraped_date') else 'Unknown'
        scrape_dates[date] = scrape_dates.get(date, 0) + 1

    st.write(f"**Scrape Dates:** {', '.join(sorted(scrape_dates.keys()))}")
    st.write(f"**Records per date:** {scrape_dates}")

# TAB 3: DETAILS VIEW
with tab3:
    st.subheader("🔍 Journalist Details")

    if filtered:
        # Select a journalist
        journalist_names = [f"{j.get('name_english', '')} - {j.get('organization_name', '')}" for j in filtered]
        selected_idx = st.selectbox(
            "Select a journalist",
            options=range(len(journalist_names)),
            format_func=lambda i: journalist_names[i]
        )

        if selected_idx is not None:
            j = filtered[selected_idx]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Basic Information")
                st.write(f"**Name (English):** {j.get('name_english', 'N/A')}")
                st.write(f"**Name (Hebrew):** {j.get('name_hebrew', 'N/A')}")
                st.write(f"**Organization:** {j.get('organization_name', 'N/A')}")
                st.write(f"**Title (English):** {j.get('job_title_english', 'N/A')}")
                st.write(f"**Title (Hebrew):** {j.get('job_title_hebrew', 'N/A')}")
                st.write(f"**Beat/Topics:** {j.get('beat', 'N/A')}")

            with col2:
                st.markdown("### Contact & Links")
                st.write(f"**Email:** {j.get('email', 'N/A')}")

                profile_url = j.get('profile_url')
                if profile_url:
                    st.write(f"**Profile:** [{profile_url}]({profile_url})")
                else:
                    st.write("**Profile:** N/A")

                source_url = j.get('source_url')
                if source_url:
                    st.write(f"**Source:** [{source_url}]({source_url})")

            st.markdown("---")
            st.markdown("### Metadata")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence Score", f"{j.get('confidence_score', 0)}%")
            with col2:
                st.metric("Verified", "Yes" if j.get('verified') else "No")
            with col3:
                st.metric("Status", j.get('status', 'Unknown'))

            st.write(f"**Scraped Date:** {j.get('scraped_date', 'N/A')}")
            st.write(f"**ID:** {j.get('id', 'N/A')}")

            # Raw JSON
            with st.expander("View Raw JSON"):
                st.json(j)
    else:
        st.info("Select filters in the sidebar to view journalist details.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Israeli Journalists Database</strong></p>
    <p>Scraped from media organization websites using Crawl4AI + Grok AI</p>
    <small>Part of the Reporter Database Updater system</small>
</div>
""", unsafe_allow_html=True)
