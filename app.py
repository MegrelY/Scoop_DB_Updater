"""
Reporter Database Updater - Streamlit Web UI
Enhanced with file upload, full database view, and change tracking
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import time
from datetime import datetime
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.batch_processor import search_google, extract_with_grok
from src.auth import check_password

# Page config
st.set_page_config(
    page_title="Reporter Database Updater",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check password first - stop here if not authenticated
if not check_password():
    st.stop()

# Session state initialization
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'results' not in st.session_state:
    st.session_state.results = []
if 'current_db_path' not in st.session_state:
    st.session_state.current_db_path = Config.DB_SAMPLE_PATH
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# Enhanced Custom CSS
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

    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: var(--primary-color);
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

    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
    }

    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
    }

    /* Info boxes */
    .info-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
    }

    /* Table styling */
    .dataframe {
        font-size: 14px;
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

    /* Sidebar improvements */
    .css-1d391kg {
        padding-top: 1rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px 8px 0 0;
        padding-left: 20px;
        padding-right: 20px;
    }

    /* Hebrew text support */
    .hebrew-text {
        direction: rtl;
        text-align: right;
        font-family: 'Arial', 'Helvetica', sans-serif;
    }

    /* Expander improvements */
    .streamlit-expanderHeader {
        border-radius: 8px;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Title with gradient
st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   font-size: 3em;
                   font-weight: bold;'>
            📰 Reporter Database Updater
        </h1>
        <p style='color: #666; font-size: 1.2em;'>Hebrew-first, AI-powered contact verification system</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # === FILE UPLOAD SECTION ===
    st.subheader("📁 Database Management")

    uploaded_file = st.file_uploader(
        "Upload New CSV File",
        type=['csv'],
        help="Upload a new reporter database CSV file"
    )

    if uploaded_file is not None:
        try:
            # Save uploaded file
            upload_path = Config.OUTPUT_PATH / "uploaded" / uploaded_file.name
            upload_path.parent.mkdir(parents=True, exist_ok=True)

            # Read and validate CSV
            df_upload = pd.read_csv(uploaded_file, encoding='utf-8')

            # Save to disk
            df_upload.to_csv(upload_path, index=False, encoding='utf-8-sig')

            st.session_state.current_db_path = upload_path
            st.session_state.uploaded_file_name = uploaded_file.name

            st.success(f"✅ Uploaded: {uploaded_file.name}")
            st.info(f"📊 {len(df_upload)} reporters loaded")

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

    # Show current database
    current_db_name = st.session_state.uploaded_file_name or "Sample list.csv"
    st.caption(f"**Current DB:** {current_db_name}")

    # Reset to default button
    if st.session_state.uploaded_file_name:
        if st.button("🔄 Reset to Default DB"):
            st.session_state.current_db_path = Config.DB_SAMPLE_PATH
            st.session_state.uploaded_file_name = None
            st.rerun()

    st.divider()

    # API Status
    st.subheader("🔌 API Status")
    col1, col2 = st.columns(2)
    with col1:
        if Config.GROK_API_KEY:
            st.success("✅ Grok")
        else:
            st.error("❌ Grok")
    with col2:
        if Config.GOOGLE_API_KEY:
            st.success("✅ Google")
        else:
            st.error("❌ Google")

    st.divider()

    # Settings
    st.subheader("⚡ Processing Settings")
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=50,
        max_value=100,
        value=Config.CONFIDENCE_THRESHOLD,
        step=5,
        help="Minimum confidence % for auto-update"
    )

    batch_size = st.number_input(
        "Batch Size",
        min_value=1,
        max_value=50,
        value=10,
        help="Number of reporters to process"
    )

    start_row = st.number_input(
        "Start Row",
        min_value=2,
        max_value=1000,
        value=2,
        help="CSV row to start from (2 = first reporter)"
    )

    st.divider()

    # Database info
    st.subheader("📊 Database Stats")
    try:
        df = pd.read_csv(st.session_state.current_db_path, encoding='utf-8')

        total = len(df)
        processed = df['confidence_score'].notna().sum() if 'confidence_score' in df.columns else 0
        remaining = total - processed

        # Metrics with colored backgrounds
        st.metric("Total Reporters", total, delta=None)
        st.metric("✅ Processed", processed, delta=None)
        st.metric("⏳ Remaining", remaining, delta=None)

        # Progress bar
        if total > 0:
            progress = processed / total
            st.progress(progress)
            st.caption(f"{progress*100:.1f}% complete")

    except Exception as e:
        st.error(f"Error: {e}")

# Main content - Enhanced tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Process",
    "📋 Review Queue",
    "📊 Statistics",
    "🗄️ View Database",
    "📝 Change History"
])

# ==================== TAB 1: PROCESS ====================
with tab1:
    st.header("🚀 Process Reporters")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"""
        <div class='info-box'>
            <strong>⚙️ Current Settings:</strong><br>
            • Confidence Threshold: <strong>{confidence_threshold}%</strong><br>
            • Batch Size: <strong>{batch_size}</strong> reporters<br>
            • Starting from Row: <strong>{start_row}</strong><br>
            • Database: <strong>{current_db_name}</strong>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("▶️ Start Processing", type="primary", disabled=st.session_state.processing, use_container_width=True):
            st.session_state.processing = True
            st.rerun()

    # Processing logic
    if st.session_state.processing:
        st.markdown("---")
        st.subheader("⚡ Processing in Progress...")

        # Load CSV
        df = pd.read_csv(st.session_state.current_db_path, encoding='utf-8')

        # Add tracking columns if needed
        for col in ['confidence_score', 'last_updated', 'update_notes', 'decision', 'source_urls', 'search_history']:
            if col not in df.columns:
                df[col] = None

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()

        results = []
        end_row = min(start_row + batch_size, len(df) + 1)
        total = end_row - start_row

        for idx, i in enumerate(range(start_row - 1, end_row - 1)):
            row = df.iloc[i]
            first_name = row['שם פרטי']
            last_name = row['שם משפחה']
            full_name = f"{first_name} {last_name}"

            status_text.markdown(f"**Processing {idx + 1}/{total}:** {full_name}")
            progress_bar.progress((idx + 1) / total)

            with results_container:
                with st.expander(f"Row {i + 2}: {full_name}", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("🔍 **Searching Google...**")

                    # Search
                    query = f'"{full_name}" Israel journalist reporter media'
                    search_results = search_google(query, num_results=5)

                    with col2:
                        if search_results:
                            st.success(f"✅ Found {len(search_results)} results")
                        else:
                            st.warning("⚠️ No results found")
                            continue

                    # Extract
                    st.write("🤖 **Extracting with AI...**")
                    extracted = extract_with_grok(full_name, search_results)

                    if extracted:
                        confidence = extracted.get('confidence_score', 0)
                        decision = "AUTO-UPDATE" if confidence >= confidence_threshold else "MANUAL REVIEW"

                        # Display results
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Confidence", f"{confidence}%")
                        with col2:
                            if decision == "AUTO-UPDATE":
                                st.success(f"✅ {decision}")
                            else:
                                st.warning(f"⚠️ {decision}")
                        with col3:
                            st.metric("Sources", len(extracted.get('source_urls', [])))

                        # Show extracted data
                        st.json(extracted, expanded=False)

                        results.append({
                            'row': i + 2,
                            'name': full_name,
                            'confidence': confidence,
                            'decision': decision,
                            'extracted': extracted
                        })

                    time.sleep(2)  # Rate limiting

        # Save results
        status_text.text("💾 Saving results...")

        # Update DataFrame
        for result in results:
            i = result['row'] - 2
            extracted = result['extracted']
            confidence = extracted.get('confidence_score', 0)
            decision = result['decision']

            timestamp = datetime.now().isoformat()
            df.at[i, 'confidence_score'] = confidence
            df.at[i, 'last_updated'] = timestamp
            df.at[i, 'decision'] = decision

            source_urls = extracted.get('source_urls', [])
            df.at[i, 'source_urls'] = "; ".join(source_urls) if source_urls else None

            # Update search history
            update_notes = extracted.get('notes', '')
            history_entry = f"[{timestamp}] Confidence: {confidence}% | Decision: {decision} | {update_notes}"
            existing_history = df.at[i, 'search_history']
            if pd.isna(existing_history) or existing_history == '':
                df.at[i, 'search_history'] = history_entry
            else:
                df.at[i, 'search_history'] = existing_history + " || " + history_entry

        # Save
        backup_path = Config.OUTPUT_PATH / f"backup_reporters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        Config.OUTPUT_PATH.mkdir(exist_ok=True)
        df.to_csv(st.session_state.current_db_path, index=False, encoding='utf-8-sig')
        df.to_csv(backup_path, index=False, encoding='utf-8-sig')

        progress_bar.progress(1.0)
        status_text.markdown("### ✅ Processing Complete!")

        # Summary
        st.markdown("---")
        st.subheader("📊 Summary")

        auto_updates = sum(1 for r in results if r['decision'] == 'AUTO-UPDATE')
        manual_reviews = sum(1 for r in results if r['decision'] == 'MANUAL REVIEW')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Processed", len(results))
        with col2:
            st.metric("✅ Auto-Updates", auto_updates)
        with col3:
            st.metric("⚠️ Manual Reviews", manual_reviews)

        st.session_state.results = results
        st.session_state.processing = False

        st.success(f"💾 Backup saved: {backup_path.name}")

# ==================== TAB 2: REVIEW QUEUE ====================
with tab2:
    st.header("📋 Review Queue")

    try:
        df = pd.read_csv(st.session_state.current_db_path, encoding='utf-8')

        if 'decision' in df.columns:
            # Filter for manual review
            manual_review_df = df[df['decision'] == 'MANUAL REVIEW'].copy()

            if len(manual_review_df) > 0:
                st.warning(f"⚠️ **{len(manual_review_df)} reporters need manual review**")

                # Display as table
                display_cols = ['שם פרטי', 'שם משפחה', 'confidence_score', 'update_notes', 'source_urls', 'last_updated']
                available_cols = [col for col in display_cols if col in manual_review_df.columns]

                st.dataframe(
                    manual_review_df[available_cols],
                    use_container_width=True,
                    height=500
                )

                # Download button
                col1, col2 = st.columns(2)
                with col1:
                    csv = manual_review_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Download Review Queue CSV",
                        data=csv,
                        file_name=f"manual_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.success("✅ **No reporters need manual review!**")
        else:
            st.info("ℹ️ No processing data available yet. Run a batch first.")

    except Exception as e:
        st.error(f"❌ Error loading review queue: {e}")

# ==================== TAB 3: STATISTICS ====================
with tab3:
    st.header("📊 Statistics Dashboard")

    try:
        df = pd.read_csv(st.session_state.current_db_path, encoding='utf-8')

        if 'confidence_score' in df.columns:
            processed_df = df[df['confidence_score'].notna()].copy()

            if len(processed_df) > 0:
                # Key metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("📊 Total Reporters", len(df))
                with col2:
                    st.metric("✅ Processed", len(processed_df))
                with col3:
                    auto_count = len(processed_df[processed_df['decision'] == 'AUTO-UPDATE'])
                    st.metric("🟢 Auto-Updates", auto_count)
                with col4:
                    manual_count = len(processed_df[processed_df['decision'] == 'MANUAL REVIEW'])
                    st.metric("🟡 Manual Reviews", manual_count)

                st.markdown("---")

                # Confidence distribution
                st.subheader("📈 Confidence Distribution")

                import plotly.express as px
                import plotly.graph_objects as go

                fig = px.histogram(
                    processed_df,
                    x='confidence_score',
                    nbins=10,
                    title="Confidence Score Distribution",
                    labels={'confidence_score': 'Confidence Score (%)', 'count': 'Number of Reporters'},
                    color_discrete_sequence=['#667eea']
                )
                fig.add_vline(x=confidence_threshold, line_dash="dash", line_color="red",
                             annotation_text=f"Threshold: {confidence_threshold}%")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

                # Decision breakdown
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("🎯 Decision Breakdown")
                    decision_counts = processed_df['decision'].value_counts()
                    fig = px.pie(
                        values=decision_counts.values,
                        names=decision_counts.index,
                        title="Auto-Update vs Manual Review",
                        color_discrete_sequence=['#11998e', '#f5576c']
                    )
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("📊 Average Confidence")
                    avg_confidence = processed_df['confidence_score'].mean()
                    st.metric("Overall Average", f"{avg_confidence:.1f}%")

                    st.write("**By Decision Type:**")
                    for decision in processed_df['decision'].unique():
                        if pd.notna(decision):
                            avg = processed_df[processed_df['decision'] == decision]['confidence_score'].mean()
                            st.write(f"• {decision}: **{avg:.1f}%**")

            else:
                st.info("📊 No processing statistics available yet. Run a batch to see analytics.")
        else:
            st.warning("⚠️ No processing data available yet. Run a batch first.")

    except Exception as e:
        st.error(f"❌ Error loading statistics: {e}")

# ==================== TAB 4: VIEW DATABASE ====================
with tab4:
    st.header("🗄️ View Full Database")

    try:
        df = pd.read_csv(st.session_state.current_db_path, encoding='utf-8')

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            # Filter by decision
            if 'decision' in df.columns:
                decision_filter = st.selectbox(
                    "Filter by Decision",
                    options=['All', 'AUTO-UPDATE', 'MANUAL REVIEW', 'Not Processed'],
                    index=0
                )
            else:
                decision_filter = 'All'

        with col2:
            # Search by name
            search_name = st.text_input("🔍 Search by Name", "")

        with col3:
            # Filter by confidence
            if 'confidence_score' in df.columns:
                min_confidence = st.slider(
                    "Min Confidence %",
                    0, 100, 0
                )
            else:
                min_confidence = 0

        # Apply filters
        filtered_df = df.copy()

        if decision_filter != 'All':
            if decision_filter == 'Not Processed':
                filtered_df = filtered_df[filtered_df['decision'].isna()]
            else:
                filtered_df = filtered_df[filtered_df['decision'] == decision_filter]

        if search_name:
            filtered_df = filtered_df[
                filtered_df['שם פרטי'].str.contains(search_name, case=False, na=False) |
                filtered_df['שם משפחה'].str.contains(search_name, case=False, na=False)
            ]

        if 'confidence_score' in filtered_df.columns and min_confidence > 0:
            filtered_df = filtered_df[filtered_df['confidence_score'] >= min_confidence]

        # Display info
        st.info(f"📊 Showing **{len(filtered_df)}** of **{len(df)}** reporters")

        # Display dataframe with formatting
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600
        )

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            # Download filtered data
            csv_filtered = filtered_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download Filtered Data",
                data=csv_filtered,
                file_name=f"filtered_reporters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Download full database
            csv_full = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download Full Database",
                data=csv_full,
                file_name=f"full_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"❌ Error loading database: {e}")

# ==================== TAB 5: CHANGE HISTORY ====================
with tab5:
    st.header("📝 Change History")

    try:
        df = pd.read_csv(st.session_state.current_db_path, encoding='utf-8')

        if 'search_history' in df.columns:
            # Filter reporters with history
            history_df = df[df['search_history'].notna()].copy()

            if len(history_df) > 0:
                st.success(f"📋 **{len(history_df)} reporters** have processing history")

                # Search for specific reporter
                search_reporter = st.text_input("🔍 Search for reporter", "")

                if search_reporter:
                    history_df = history_df[
                        history_df['שם פרטי'].str.contains(search_reporter, case=False, na=False) |
                        history_df['שם משפחה'].str.contains(search_reporter, case=False, na=False)
                    ]

                # Display each reporter's history
                for idx, row in history_df.iterrows():
                    first_name = row['שם פרטי']
                    last_name = row['שם משפחה']
                    full_name = f"{first_name} {last_name}"

                    with st.expander(f"📄 {full_name} - Row {idx + 2}"):
                        # Current status
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if 'confidence_score' in row and pd.notna(row['confidence_score']):
                                st.metric("Current Confidence", f"{row['confidence_score']}%")
                        with col2:
                            if 'decision' in row and pd.notna(row['decision']):
                                st.metric("Decision", row['decision'])
                        with col3:
                            if 'last_updated' in row and pd.notna(row['last_updated']):
                                st.metric("Last Updated", row['last_updated'][:10])

                        st.markdown("---")

                        # Parse and display history
                        st.subheader("🕒 Processing History")
                        history_entries = row['search_history'].split(' || ')

                        for i, entry in enumerate(reversed(history_entries)):
                            st.markdown(f"**Run #{len(history_entries) - i}:**")
                            st.code(entry, language=None)

                        # Show source URLs if available
                        if 'source_urls' in row and pd.notna(row['source_urls']):
                            st.markdown("---")
                            st.subheader("🔗 Source URLs")
                            urls = row['source_urls'].split('; ')
                            for url in urls:
                                st.markdown(f"- [{url}]({url})")

                # Export change log
                st.markdown("---")
                changelog_csv = history_df[['שם פרטי', 'שם משפחה', 'confidence_score', 'decision', 'last_updated', 'search_history']].to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Download Change History Log",
                    data=changelog_csv,
                    file_name=f"change_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("ℹ️ No processing history available yet.")
        else:
            st.warning("⚠️ No change history tracked yet. Process some reporters first.")

    except Exception as e:
        st.error(f"❌ Error loading change history: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Reporter Database Updater v2.0</strong></p>
    <p>Hebrew-first AI-powered contact verification | Enhanced UI with full database management</p>
    <small>🔒 Secure • 🌐 Hebrew-first • ⚡ AI-powered • 📊 Data-driven</small>
</div>
""", unsafe_allow_html=True)
