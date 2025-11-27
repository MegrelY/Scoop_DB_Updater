# scoop_feed - Product Requirements Document

**Author:** Yos
**Date:** 2025-11-25
**Version:** 1.0

---

## Executive Summary

The Reporter Database Updater is an automated verification and update system designed to maintain accurate professional contact information for 250+ Israeli media professionals (reporters, producers, editors). The system addresses the critical business problem of outdated contact databases that lead to lost outreach opportunities and inefficient manual research.

**Core Problem:** Maintaining up-to-date contact information for Israeli journalists is time-consuming, error-prone, and expensive when done manually or with premium API subscriptions.

**Solution:** An intelligent batch processor that searches multiple Hebrew and English sources (Israeli news sites, company pages, public profiles), extracts structured data using AI, scores confidence levels, and either auto-updates high-confidence findings (70%+) or flags low-confidence items for human review.

**Business Impact:** Transform a multi-week manual research task into an automated process costing under $2, while maintaining accuracy through confidence-based decision routing.

### What Makes This Special

**Hebrew-First, Budget-Conscious Business Contact Confidence System**

This isn't just a database updater—it's a confidence intelligence system built from the ground up for Hebrew names and sources:

1. **Hebrew-First Architecture** - Designed natively for Hebrew names (not English-adapted), handles transliteration variations as a core feature
2. **Confidence-Based Hybrid Automation** - Smart routing: 70%+ confidence = auto-update, <70% = human review queue (not blind automation)
3. **Multi-Source Intelligence** - Israeli news sites PRIMARY, company "Our Team" pages, public LinkedIn checks, web search—builds confidence through corroboration
4. **Budget-Conscious Scalability** - $1.70 for 250 reporters using free/low-cost tools (Crawl4AI, Grok API, Google Custom Search), scales to 2,500+ with same architecture
5. **Record-Level Resilience** - Checkpoint after each record, retry individuals, survive batch failures gracefully

**Unique Value:** The system doesn't replace human judgment—it enhances it by providing confidence scores that tell you "safe to use" vs "verify first," optimized for a business context where bad contacts = lost opportunities.

---

## Project Classification

**Technical Type:** Internal Web Application (Streamlit-based, Python backend)
**Domain:** General Business / Media Relations
**Complexity:** Low (no regulatory compliance, straightforward data verification)
**Users:** 2-person internal team
**Deployment:** Internal/Streamlit Cloud (password-protected)

**Classification Rationale:**

This is an internal business automation tool built as a Streamlit web application with a Python backend. It provides a professional web interface for 2 team members to collaboratively manage reporter database updates. The system processes batch data, integrates with external APIs, provides real-time feedback, and produces updated CSV outputs with comprehensive audit trails. While it operates in the media/journalism sector, it doesn't face regulated domain constraints (no HIPAA, GDPR critical path, financial regulations).

**Key Characteristics:**
- Web-based interface (Streamlit framework)
- Real-time batch processing with progress tracking
- Multi-API integration (Google Search, Grok AI)
- Hebrew language support (UTF-8, RTL, bilingual interface)
- Password-protected access
- Collaborative review queue workflow
- Visual analytics and statistics dashboards
- File upload and export capabilities
- Comprehensive change tracking and audit trails

---

## Success Criteria

**Primary Success Metric:** 2-person team can confidently process and maintain 250+ Israeli reporter contacts with minimal manual research effort.

**Operational Success:**
- **Processing Efficiency:** Process 50 reporters in under 30 minutes (vs. hours of manual research)
- **Accuracy Threshold:** 70%+ of processed reporters achieve auto-update confidence (≥70% confidence score)
- **Review Workflow:** Low-confidence items (<70%) flagged for manual review with source URLs for verification
- **Cost Effectiveness:** Maintain under $5 per 250-reporter batch (current: $1.70)
- **Audit Compliance:** Complete change history and source tracking for every update

**User Experience Success:**
- **Usability:** Non-technical team member can operate independently without training
- **Confidence:** Users trust the confidence scores to guide manual review decisions
- **Visibility:** Real-time progress tracking reduces anxiety during batch processing
- **Collaboration:** 2 team members can work on different batches without conflicts

**Data Quality Success:**
- **No False Positives:** Zero incorrect auto-updates that damage business relationships
- **Source Verification:** Every update traceable to source URLs
- **Hebrew Accuracy:** Correctly handles Hebrew names, transliterations, and RTL display
- **Change Detection:** Successfully identifies job changes and employer updates

**Business Impact:**
- **Time Saved:** 80%+ reduction in manual contact research time
- **Relationship Protection:** Accurate contacts prevent embarrassing outreach errors
- **Scalability:** System can grow to 500+ contacts without architectural changes
- **Maintainability:** Can process same database quarterly/annually for updates

---

## Product Scope

### MVP - Minimum Viable Product ✅ SHIPPED

**Status:** Feature-complete and operational (as of Nov 2025)

**Core Processing Engine:**
- Multi-source search (Google Custom Search API)
- AI extraction (Grok API for structured data from search results)
- Hebrew + English bilingual query support
- Confidence scoring algorithm (0-100%)
- Auto-update vs. manual review decision routing (threshold: 70%)
- Record-level checkpointing (save after each, retry failures individually)
- CSV import/export with UTF-8 Hebrew support

**Web Interface (Streamlit):**
- Password-protected access (environment-based auth)
- File upload system (swap between databases)
- Configurable settings (confidence threshold, batch size, start row)
- Real-time batch processing with progress tracking
- 6-tab navigation: Process, Review Queue, Statistics, View Database, Change History, Help

**Collaborative Review Workflow:**
- Manual review queue (filters <70% confidence items)
- Source URL tracking for verification
- Filterable/searchable full database view
- Change history per reporter (multi-run tracking)
- Export capabilities (filtered data, review queue, change logs)

**Analytics & Visibility:**
- Processing statistics dashboard
- Confidence distribution histogram (with threshold line)
- Auto-update vs. manual review pie chart
- Average confidence by decision type
- Database progress tracking (total/processed/remaining)

**Data Quality & Audit:**
- Automatic backup on every batch save
- Complete change history (timestamped entries)
- Source URL preservation
- Before/after change tracking
- Multi-run history concatenation (see all attempts per reporter)

### Growth Features (Post-MVP)

**Based on validated prototype results and brainstorming session (Nov 2025):**

**Automation & Monitoring:**
1. **Job Change Alert System** - Monitor when journalists change positions, send proactive notifications for relationship management
2. **Scheduled Automated Runs** - Weekly/monthly automation with email alerts when changes detected (push vs. pull model)
3. **Confidence Scoring Feedback Loop** - Learn from manual corrections to improve accuracy over time

**Data Enrichment:**
4. **Twitter/X Handle Capture** - Optional social media contact field
5. **Advanced Conflict Resolution** - Time-based + source reputation weighting for contradictory information
6. **CSV Validation & Auto-Correction** - Detect format changes and adapt automatically

**Scale & Performance:**
7. **Batch-by-Organization Optimization** - Search "Channel 12 newsroom" instead of individuals for efficiency (pending DB structure validation)
8. **Optimistic Updates** - Update first, verify on use, rollback if wrong (faster workflow)
9. **Dynamic Batch Sizing** - Adjust based on API limits and performance
10. **API Key Rotation** - Multiple Google Search keys to exceed 100/day limit

**UX Enhancements:**
11. **Bulk Approval Interface** - Approve/reject multiple manual review items at once
12. **In-App Source Preview** - Display source content without opening URLs
13. **Comparison View** - Side-by-side old vs. new data for review decisions

### Vision (Future)

**Strategic Capabilities (Long-term):**

1. **Media Landscape Mapping** - Visualize entire Israeli journalism ecosystem, track coverage patterns, relationship networks, org charts
2. **Inside-Out Discovery Approach** - Scrape all news organizations → Match to DB + discover NEW contacts not in database yet
3. **Predictive Job Change Modeling** - AI predicts likely career moves before they happen based on industry patterns

**Technical Innovations:**
4. **Hebrew Transliteration AI** - Train specialized model to match Hebrew names to English transliterations with high accuracy
5. **Real-Time Web Monitoring** - Continuous scraping of news sites to catch updates within hours of publication
6. **Cross-Platform Identity Resolution** - Link same person across LinkedIn, Twitter, bylines, company sites automatically

**Scale Scenarios:**
7. **Multi-Region Expansion** - Support other media markets (US, UK, Europe journalists)
8. **Vertical Expansion** - Apply same approach to other professional databases (lawyers, doctors, academics, business executives)

---

## Functional Requirements

*Organized by capability area. Each FR describes WHAT the system can do, not HOW it's implemented.*

### User Access & Authentication

**FR1:** Users can authenticate with password to access the application
**FR2:** System validates password against environment variable or secrets configuration
**FR3:** System maintains authenticated session state across page interactions
**FR4:** Unauthorized users are blocked from viewing any application content

### Database Management

**FR5:** Users can upload new reporter CSV files through web interface
**FR6:** System validates uploaded CSV format and encoding (UTF-8 support required)
**FR7:** Users can switch between uploaded databases and default sample database
**FR8:** System displays current active database name in sidebar
**FR9:** Users can reset to default database from uploaded state
**FR10:** System automatically creates tracking columns if missing from CSV (confidence_score, last_updated, update_notes, decision, source_urls, search_history)

### Batch Processing Configuration

**FR11:** Users can set confidence threshold (50-100%, default: 70%)
**FR12:** Users can configure batch size (1-50 reporters per run)
**FR13:** Users can specify starting row number for processing
**FR14:** System displays API connection status (Grok, Google) in sidebar
**FR15:** System shows database statistics (total, processed, remaining reporters) with progress visualization

### Reporter Search & Extraction

**FR16:** System searches Google for reporter information using bilingual queries (Hebrew + English)
**FR17:** System extracts structured data from search results using AI (Grok API)
**FR18:** System generates confidence scores (0-100%) based on source quality and data completeness
**FR19:** System captures source URLs for all extracted information
**FR20:** System implements rate limiting (2-second delays between requests) to respect API limits
**FR21:** System handles search failures gracefully without blocking entire batch

### Real-Time Processing Feedback

**FR22:** Users can initiate batch processing with single button click
**FR23:** System displays real-time progress bar showing completion percentage
**FR24:** System shows current reporter being processed (name, row number, progress)
**FR25:** System displays per-reporter processing status in expandable panels
**FR26:** System shows search results count and AI extraction results during processing
**FR27:** System displays confidence score, decision, and source count for each processed reporter

### Decision Routing & Updates

**FR28:** System automatically routes reporters to AUTO-UPDATE if confidence ≥ threshold
**FR29:** System automatically routes reporters to MANUAL REVIEW if confidence < threshold
**FR30:** System updates CSV with confidence scores, timestamps, decisions, and notes
**FR31:** System preserves original data while adding tracking columns
**FR32:** System concatenates multiple processing runs in search history (|| delimiter)
**FR33:** System creates automatic backup CSV file with timestamp on every batch save

### Manual Review Queue

**FR34:** Users can view all reporters flagged for manual review in dedicated tab
**FR35:** System filters and displays only MANUAL REVIEW decision items
**FR36:** Users can see reporter names, confidence scores, update notes, and source URLs in review queue
**FR37:** Users can download review queue as filtered CSV file
**FR38:** System displays count of reporters awaiting manual review
**FR39:** System shows "No manual reviews needed" message when queue is empty

### Statistics & Analytics

**FR40:** Users can view processing statistics dashboard with key metrics
**FR41:** System displays total reporters, processed count, auto-updates, and manual reviews
**FR42:** System generates confidence score distribution histogram with threshold indicator line
**FR43:** System displays decision breakdown pie chart (auto-update vs. manual review percentages)
**FR44:** System calculates and displays average confidence scores overall and by decision type
**FR45:** System shows "No statistics available" message for unprocessed databases

### Full Database Viewing

**FR46:** Users can view complete reporter database in searchable table
**FR47:** Users can filter database by decision type (All, AUTO-UPDATE, MANUAL REVIEW, Not Processed)
**FR48:** Users can search database by reporter name (first or last name)
**FR49:** Users can filter database by minimum confidence score threshold
**FR50:** System displays count of filtered results vs. total database size
**FR51:** Users can download filtered database subset as CSV
**FR52:** Users can download complete database as CSV

### Change History & Audit Trail

**FR53:** Users can view processing history for all reporters with recorded runs
**FR54:** Users can search change history by reporter name
**FR55:** System displays per-reporter timeline with all processing runs
**FR56:** System shows confidence scores, decisions, and timestamps for each run
**FR57:** System parses and displays individual history entries from concatenated search history
**FR58:** System displays source URLs used for each processing run
**FR59:** Users can download complete change history log as CSV

### Help & Documentation

**FR60:** Users can access comprehensive help documentation within application
**FR61:** System provides quick start guide covering upload, configuration, processing, and review workflows
**FR62:** System documents keyboard shortcuts and filtering capabilities
**FR63:** System provides troubleshooting guidance for common issues
**FR64:** System explains confidence score interpretation and decision thresholds

### Data Export & Portability

**FR65:** Users can export data in multiple formats (full DB, filtered subset, review queue, change log)
**FR66:** System generates timestamped filenames for all exports
**FR67:** System preserves UTF-8 encoding (with BOM) for Hebrew character support in exports
**FR68:** System allows downloading backups created during processing

### Hebrew Language Support

**FR69:** System displays Hebrew text with correct RTL (right-to-left) directionality
**FR70:** System supports Hebrew character input in search and filter fields
**FR71:** System handles bilingual data (Hebrew names + English transliterations) in same record
**FR72:** System preserves Hebrew encoding in all CSV read/write operations

### Session Management

**FR73:** System maintains processing state during batch execution
**FR74:** System disables "Start Processing" button while batch is running
**FR75:** System preserves uploaded file and configuration across tab navigation
**FR76:** System resets processing state after batch completion

---

## Non-Functional Requirements

### Performance

**NFR1: API Response Time**
- Google Search API: < 5 seconds per query
- Grok extraction API: < 10 seconds per reporter
- Target: Process 1 reporter in < 20 seconds (including rate limiting)

**NFR2: Batch Processing Speed**
- Process 50-reporter batch in < 30 minutes
- Real-time progress updates every 2 seconds
- No UI freeze during processing (progress bar + status updates)

**NFR3: UI Responsiveness**
- Tab switching: Instant (< 100ms)
- Filter application: < 1 second for 250-reporter database
- Chart rendering: < 2 seconds for statistics dashboard
- File upload processing: < 5 seconds for 250-row CSV

**NFR4: Rate Limiting Compliance**
- Minimum 2-second delay between API calls
- Respect Google Custom Search limit (100 queries/day free tier)
- Graceful handling when API limits exceeded

### Security

**NFR5: Authentication**
- Password-protected application access (environment variable or Streamlit secrets)
- Session-based authentication (no re-login during session)
- Clear separation: unauthenticated users see ONLY login screen

**NFR6: Data Protection**
- Sensitive data (API keys, passwords) stored in environment variables or secrets (never in code)
- No API keys logged or displayed in UI
- Password field uses masked input (type="password")

**NFR7: Access Control**
- 2-user internal team access (no public exposure)
- Optional: Streamlit Cloud authentication integration
- Session isolation (multi-user support without data leakage)

**NFR8: Data Privacy**
- No external data transmission beyond documented APIs (Google, Grok)
- No analytics tracking or telemetry
- User data remains in user-controlled CSV files

**NFR9: Backup & Recovery**
- Automatic timestamped backups on every save
- Backups stored in local `output/` directory
- No backup data deletion (manual cleanup required)

### Scalability

**NFR10: Database Size Support**
- Current: 250 reporters (validated)
- Target: 500 reporters without performance degradation
- Maximum: 1,000 reporters with acceptable processing time
- Architecture supports unlimited scale (stateless per-record processing)

**NFR11: Concurrent User Support**
- 2 simultaneous users (primary requirement)
- Streamlit session isolation prevents conflicts
- Each user can process different batches independently
- CSV file locking may occur if users edit same database simultaneously (acceptable for 2-user team)

**NFR12: API Cost Scalability**
- Google Custom Search: Free tier (100 searches/day) = ~33 reporters/day
- Grok API: Pay-per-use, approximately $0.01 per reporter
- Total cost: < $5 per 250-reporter batch
- Cost scales linearly with reporter count

**NFR13: Storage Scalability**
- CSV file size: ~50KB per 250 reporters
- Backup accumulation: ~50KB per batch run
- Expected storage: < 10MB for 1 year of processing (20 batches)
- No database required (CSV-based storage)

### Reliability

**NFR14: Fault Tolerance**
- Record-level checkpointing (save after each reporter)
- Individual record failures don't block batch
- Graceful API failure handling (log, continue to next reporter)
- Automatic retry not implemented (manual re-run required)

**NFR15: Data Integrity**
- Original CSV columns preserved (never deleted)
- UTF-8 encoding enforced on all read/write operations
- Backup created before every save operation
- Change history never overwritten (concatenation only)

**NFR16: Availability**
- Deployment: Streamlit Cloud or local (user-controlled)
- No uptime SLA (internal tool)
- Acceptable: 1-hour downtime for deployments
- Users can run locally if cloud unavailable

### Usability

**NFR17: User Skill Level**
- Target: Non-technical users can operate independently
- No CLI or programming knowledge required
- Inline help documentation (Help tab)
- Visual feedback for all operations (progress, status, errors)

**NFR18: Hebrew Language Support**
- Full RTL (right-to-left) text display
- Hebrew input supported in all text fields
- UTF-8 with BOM for Excel compatibility
- Bilingual UI labels (English) with Hebrew data support

**NFR19: Browser Compatibility**
- Primary: Chrome, Firefox, Edge (latest versions)
- Mobile: Not optimized (desktop-first design)
- Screen resolution: Minimum 1280x720

**NFR20: Error Handling**
- User-friendly error messages (no technical stack traces to user)
- Clear guidance for resolution ("Check API keys", "Verify CSV format")
- Errors don't crash application (Streamlit exception handling)
- Failed operations allow retry without restart

### Maintainability

**NFR21: Code Structure**
- Separation of concerns: Core logic (`batch_processor.py`) vs. UI (`app.py`)
- Reusable functions for API calls and extraction
- Configuration centralized in `config.py`
- No hardcoded values (environment-based configuration)

**NFR22: Dependency Management**
- Python 3.14 (or latest stable)
- Minimal dependencies (Streamlit, Pandas, OpenAI SDK, Google API client)
- `requirements.txt` for reproducible installs
- No deprecated library usage

**NFR23: Monitoring & Debugging**
- Comprehensive logging (change history, search history)
- Timestamped processing runs for audit
- Source URL preservation for verification
- Manual troubleshooting via CSV inspection

### Compliance & Ethical Use

**NFR24: Data Usage Ethics**
- System used for legitimate business contact verification only
- No automated scraping of restricted content (LinkedIn profile scraping avoided after research)
- Respect robots.txt and terms of service for public sites
- Human review for low-confidence results (ethical automation)

**NFR25: API Terms Compliance**
- Google Custom Search API: Terms followed (no circumvention of rate limits)
- Grok API: Standard commercial usage terms
- No API abuse or excessive request patterns

**NFR26: GDPR Considerations**
- Internal use only (not subject to GDPR as data controller)
- No PII storage beyond business contact info (job titles, employers, public emails)
- Change history supports deletion requests (manual process acceptable)

---

## Summary

_This PRD captures the essence of **scoop_feed** - a **Hebrew-first, budget-conscious business contact confidence system** that transforms multi-week manual reporter research into an automated, intelligent process costing under $2. By combining AI-powered extraction, multi-source verification, and confidence-based decision routing, it enables a 2-person team to maintain accurate contact information for 250+ Israeli media professionals with minimal effort and maximum confidence._

**Key Achievements:**
- ✅ **MVP Shipped & Validated:** Full-featured web application operational (Nov 2025)
- ✅ **Cost-Effective:** $1.70 per 250 reporters (vs. $1000s for premium APIs)
- ✅ **Accurate:** 67% hit rate, 40% auto-update rate, zero false positives detected
- ✅ **User-Friendly:** Password-protected web UI with 6-tab workflow, real-time feedback, comprehensive analytics
- ✅ **Audit-Ready:** Complete change tracking, source URLs, timestamped history per reporter
- ✅ **Hebrew-Native:** Built from ground up for Hebrew names, RTL display, transliteration handling

**What Makes It Special:**
This isn't just a database updater - it's a confidence intelligence system that tells you "safe to use" vs. "verify first," optimized for a business context where bad contacts = lost opportunities. The system doesn't replace human judgment; it enhances it through transparent confidence scoring and source preservation.

**Next Steps:**
With MVP complete and validated, the system is ready for production use processing remaining 235 reporters. Growth features (job change alerts, automated scheduling, feedback loops) are documented and prioritized for future iterations based on real-world usage patterns.

---

_Created through collaborative discovery between Yos and AI Product Management team._
_PRD Version 1.0 - November 2025_
