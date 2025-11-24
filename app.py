"""
Reporter Database Updater - Streamlit Web UI
Production-ready interface for batch processing and review
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.batch_processor import search_google, extract_with_grok
from src.auth import check_password

# Page config
st.set_page_config(
    page_title="Reporter Database Updater",
    page_icon="📰",
    layout="wide"
)

# Check password first - stop here if not authenticated
if not check_password():
    st.stop()

# Session state initialization
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'results' not in st.session_state:
    st.session_state.results = []

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .success-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 10px 0;
    }
    .warning-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        margin: 10px 0;
    }
    .info-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("📰 Reporter Database Updater")
st.markdown("**Hebrew-first, AI-powered contact verification system**")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Status
    st.subheader("API Status")
    if Config.GROK_API_KEY:
        st.success("✅ Grok API: Connected")
    else:
        st.error("❌ Grok API: Not configured")

    if Config.GOOGLE_API_KEY:
        st.success("✅ Google Search: Connected")
    else:
        st.error("❌ Google Search: Not configured")

    st.divider()

    # Settings
    st.subheader("Settings")
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
        max_value=253,
        value=30,
        help="CSV row to start from (2 = first reporter)"
    )

    st.divider()

    # Database info
    st.subheader("📊 Database Info")
    try:
        df = pd.read_csv(Config.DB_SAMPLE_PATH, encoding='utf-8')
        st.metric("Total Reporters", len(df))

        # Count processed
        if 'confidence_score' in df.columns:
            processed = df['confidence_score'].notna().sum()
            st.metric("Processed", processed)
            st.metric("Remaining", len(df) - processed)
    except Exception as e:
        st.error(f"Error loading database: {e}")

# Main content
tab1, tab2, tab3 = st.tabs(["🚀 Process", "📋 Review", "📊 Statistics"])

with tab1:
    st.header("Process Reporters")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"""
        **Current Settings:**
        - Confidence Threshold: {confidence_threshold}%
        - Batch Size: {batch_size} reporters
        - Starting from Row: {start_row}
        """)

    with col2:
        if st.button("▶️ Start Processing", type="primary", disabled=st.session_state.processing):
            st.session_state.processing = True
            st.rerun()

    # Processing logic
    if st.session_state.processing:
        st.markdown("---")
        st.subheader("Processing...")

        # Load CSV
        df = pd.read_csv(Config.DB_SAMPLE_PATH, encoding='utf-8')

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

            status_text.text(f"Processing {idx + 1}/{total}: {full_name}")
            progress_bar.progress((idx + 1) / total)

            with results_container:
                with st.expander(f"Row {i + 2}: {full_name}", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Searching Google...**")

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
                    st.write("**Extracting with AI...**")
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
        status_text.text("Saving results...")

        # Update DataFrame (same logic as batch_processor.py)
        for result in results:
            i = result['row'] - 2
            extracted = result['extracted']
            confidence = extracted.get('confidence_score', 0)
            decision = result['decision']

            # Update logic here (simplified for UI)
            timestamp = datetime.now().isoformat()
            df.at[i, 'confidence_score'] = confidence
            df.at[i, 'last_updated'] = timestamp
            df.at[i, 'decision'] = decision

            source_urls = extracted.get('source_urls', [])
            df.at[i, 'source_urls'] = "; ".join(source_urls) if source_urls else None

        # Save
        backup_path = Config.OUTPUT_PATH / f"backup_reporters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        Config.OUTPUT_PATH.mkdir(exist_ok=True)
        df.to_csv(Config.DB_SAMPLE_PATH, index=False, encoding='utf-8-sig')
        df.to_csv(backup_path, index=False, encoding='utf-8-sig')

        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")

        # Summary
        st.markdown("---")
        st.subheader("📊 Summary")

        auto_updates = sum(1 for r in results if r['decision'] == 'AUTO-UPDATE')
        manual_reviews = sum(1 for r in results if r['decision'] == 'MANUAL REVIEW')

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Processed", len(results))
        with col2:
            st.metric("Auto-Updates", auto_updates)
        with col3:
            st.metric("Manual Reviews", manual_reviews)

        st.session_state.results = results
        st.session_state.processing = False

        st.success(f"✅ Backup saved to: {backup_path.name}")

with tab2:
    st.header("Review Queue")

    try:
        df = pd.read_csv(Config.DB_SAMPLE_PATH, encoding='utf-8')

        if 'decision' in df.columns:
            # Filter for manual review
            manual_review_df = df[df['decision'] == 'MANUAL REVIEW'].copy()

            if len(manual_review_df) > 0:
                st.info(f"📋 {len(manual_review_df)} reporters need manual review")

                # Display as table
                display_cols = ['שם פרטי', 'שם משפחה', 'confidence_score', 'update_notes', 'source_urls']
                available_cols = [col for col in display_cols if col in manual_review_df.columns]

                st.dataframe(
                    manual_review_df[available_cols],
                    use_container_width=True,
                    height=400
                )

                # Download button
                csv = manual_review_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Download Review Queue CSV",
                    data=csv,
                    file_name=f"manual_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.success("✅ No reporters need manual review!")
        else:
            st.warning("⚠️ No processing data available yet. Run a batch first.")

    except Exception as e:
        st.error(f"Error loading review queue: {e}")

with tab3:
    st.header("Statistics")

    try:
        df = pd.read_csv(Config.DB_SAMPLE_PATH, encoding='utf-8')

        if 'confidence_score' in df.columns:
            processed_df = df[df['confidence_score'].notna()].copy()

            if len(processed_df) > 0:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Reporters", len(df))
                with col2:
                    st.metric("Processed", len(processed_df))
                with col3:
                    auto_count = len(processed_df[processed_df['decision'] == 'AUTO-UPDATE'])
                    st.metric("Auto-Updates", auto_count)
                with col4:
                    manual_count = len(processed_df[processed_df['decision'] == 'MANUAL REVIEW'])
                    st.metric("Manual Reviews", manual_count)

                st.markdown("---")

                # Confidence distribution
                st.subheader("Confidence Distribution")

                import plotly.express as px

                fig = px.histogram(
                    processed_df,
                    x='confidence_score',
                    nbins=10,
                    title="Confidence Score Distribution",
                    labels={'confidence_score': 'Confidence Score (%)', 'count': 'Number of Reporters'}
                )
                fig.add_vline(x=confidence_threshold, line_dash="dash", line_color="red",
                             annotation_text=f"Threshold: {confidence_threshold}%")
                st.plotly_chart(fig, use_container_width=True)

                # Decision breakdown
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Decision Breakdown")
                    decision_counts = processed_df['decision'].value_counts()
                    fig = px.pie(
                        values=decision_counts.values,
                        names=decision_counts.index,
                        title="Auto-Update vs Manual Review"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.subheader("Average Confidence")
                    avg_confidence = processed_df['confidence_score'].mean()
                    st.metric("Average Score", f"{avg_confidence:.1f}%")

                    st.write("**By Decision:**")
                    for decision in processed_df['decision'].unique():
                        if pd.notna(decision):
                            avg = processed_df[processed_df['decision'] == decision]['confidence_score'].mean()
                            st.write(f"- {decision}: {avg:.1f}%")

            else:
                st.info("📊 No processing statistics available yet. Run a batch to see analytics.")
        else:
            st.warning("⚠️ No processing data available yet. Run a batch first.")

    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Reporter Database Updater v1.0 | Hebrew-first AI-powered contact verification</small>
</div>
""", unsafe_allow_html=True)
