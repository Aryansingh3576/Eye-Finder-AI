import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import re

# Set page config to match EyeFinder AI aesthetic
st.set_page_config(
    page_title="EyeFinder AI - Follow-Up Demo HUD",
    page_icon="👁️",
    layout="wide"
)

# Dark Mode Cyber Aesthetic Styling
st.markdown("""
<style>
    :root {
        --primary-accent: #06b6d4;     /* Cyan */
        --secondary-accent: #3b82f6;   /* Blue */
        --warning-accent: #f97316;     /* Orange */
        --success-accent: #10b981;     /* Green */
        --bg-color: #080e1b;
        --card-bg: rgba(13, 22, 42, 0.65);
        --panel-border: rgba(6, 182, 212, 0.15);
        --text-primary: #ffffff;
        --text-muted: #94a3b8;
    }
    
    .demo-header {
        font-family: 'Orbitron', sans-serif;
        color: var(--primary-accent);
        text-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        margin-bottom: 5px;
    }
    
    .timeline-container {
        border-left: 2px dashed var(--primary-accent);
        padding-left: 20px;
        margin-left: 10px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    
    .timeline-node {
        position: relative;
        margin-bottom: 20px;
    }
    
    .timeline-node::before {
        content: '●';
        position: absolute;
        left: -27px;
        top: -2px;
        font-size: 1.2rem;
    }
    
    .timeline-node.completed::before {
        color: var(--primary-accent);
        text-shadow: 0 0 8px var(--primary-accent);
    }
    
    .timeline-node.pending::before {
        color: var(--warning-accent);
        text-shadow: 0 0 8px var(--warning-accent);
    }
    
    .timeline-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
    }
    
    .timeline-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .due-card {
        background: rgba(249, 115, 22, 0.08);
        border: 1px solid rgba(249, 115, 22, 0.3);
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .due-title {
        color: var(--warning-accent);
        font-weight: 700;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.9rem;
    }
    
    .due-subtitle {
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    .outreach-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .badge-due {
        background: rgba(249, 115, 22, 0.15);
        border: 1px solid rgba(249, 115, 22, 0.4);
        color: var(--warning-accent);
    }
    
    .badge-ok {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: var(--success-accent);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='demo-header'>👁️ EYE FINDER AI — FOLLOW-UP DEMO</h2>", unsafe_allow_html=True)
st.write("This interactive demo showcases how the **Follow-Up Automation** feature can trace lead history and flag leads that are due for touchpoints.")

# ---------------------------------------------------------
# MOCK SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "demo_history" not in st.session_state:
    # 4 distinct scenarios
    st.session_state.demo_history = [
        # Scenario A: Contacted 5 days ago, needs follow up
        {
            "business_name": "Vision Care Retina Center",
            "category": "Eye Clinics",
            "phone": "9876543210",
            "address": "123 Ring Road, Patna",
            "history": [
                {
                    "channel": "WhatsApp",
                    "campaign_type": "B2B Partnership Proposal",
                    "timestamp": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
                    "stage": 1,
                    "status": "SENT"
                }
            ]
        },
        # Scenario B: Contacted 1 day ago, wait state (no follow up due yet)
        {
            "business_name": "Dr. Prasad Ophthalmic Hospital",
            "category": "Eye Hospitals",
            "phone": "9998887776",
            "address": "45 Fraser Road, Patna",
            "history": [
                {
                    "channel": "Email",
                    "campaign_type": "📧 Email Introduction",
                    "timestamp": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                    "stage": 1,
                    "status": "SENT"
                }
            ]
        },
        # Scenario C: Multi-stage outreach already completed
        {
            "business_name": "Apex Lasik Center",
            "category": "Lasik & Refractive Surgery Centers",
            "phone": "8887776665",
            "address": "78 Bailey Road, Patna",
            "history": [
                {
                    "channel": "Email",
                    "campaign_type": "Follow-up 1: B2B Review",
                    "timestamp": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
                    "stage": 2,
                    "status": "SENT"
                },
                {
                    "channel": "WhatsApp",
                    "campaign_type": "B2B Partnership Proposal",
                    "timestamp": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S"),
                    "stage": 1,
                    "status": "SENT"
                }
            ]
        },
        # Scenario D: Fresh lead, never contacted
        {
            "business_name": "Aurobindo Optical Store",
            "category": "Optical Stores",
            "phone": "7776665554",
            "address": "10 Exhibition Road, Patna",
            "history": []
        }
    ]

# ---------------------------------------------------------
# SIDEBAR: GENERAL HUD METRICS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ CONFIGURATION")
    threshold_days = st.slider("Follow-Up Delay (Days):", min_value=1, max_value=10, value=3, 
                               help="Flag a lead if they were contacted more than this many days ago and haven't had a follow-up.")
    
    st.markdown("<hr style='border-color: var(--panel-border);'>", unsafe_allow_html=True)
    st.markdown("### 📋 LOGGED HISTORY DATABASE")
    st.write("This mirrors your existing Google Drive database model but tracks sequential stages (`stage: 1`, `stage: 2`, etc.).")
    st.json(st.session_state.demo_history)

# ---------------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------------
col_hud, col_action = st.columns([1, 1.2])

# Left Column: Lead Radar HUD & Follow-Ups Due
with col_hud:
    st.markdown("### 🚨 LEAD RADAR HUD")
    st.write("This panel identifies which scanned targets require urgent communication.")

    # Calculate status for each lead
    due_leads = []
    active_leads = []
    fresh_leads = []

    for idx, lead in enumerate(st.session_state.demo_history):
        history = lead["history"]
        if not history:
            fresh_leads.append(lead)
        else:
            # Sorted with newest first
            newest_contact = sorted(history, key=lambda x: x["timestamp"], reverse=True)[0]
            contact_date = datetime.strptime(newest_contact["timestamp"], "%Y-%m-%d %H:%M:%S")
            days_since = (datetime.now() - contact_date).days
            
            lead_info = {
                "idx": idx,
                "lead": lead,
                "days_since": days_since,
                "last_channel": newest_contact["channel"],
                "last_stage": newest_contact["stage"]
            }
            
            if days_since >= threshold_days:
                due_leads.append(lead_info)
            else:
                active_leads.append(lead_info)

    # Render alerts
    if due_leads:
        st.markdown(f"#### ⏰ FOLLOW-UPS DUE ({len(due_leads)})")
        for item in due_leads:
            lead = item["lead"]
            with st.container():
                st.markdown(f"""
                <div class="due-card">
                    <div>
                        <div class="due-title">⚠️ {lead['business_name']}</div>
                        <div class="due-subtitle">{lead['category']} • Last contact {item['days_since']} days ago ({item['last_channel']})</div>
                    </div>
                    <span style="font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; background: #ea580c; color: white; padding: 2px 8px; border-radius: 4px;">STAGE {item['last_stage']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("🎉 Outstanding! All follow-ups are fully up to date.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🏢 TARGET LEADS STATUS SUMMARY")
    summary_data = []
    for l in st.session_state.demo_history:
        history = l["history"]
        if not history:
            status = "⚪ Never Contacted"
            last_date = "N/A"
        else:
            newest = sorted(history, key=lambda x: x["timestamp"], reverse=True)[0]
            contact_date = datetime.strptime(newest["timestamp"], "%Y-%m-%d %H:%M:%S")
            days_since = (datetime.now() - contact_date).days
            status = f"⚠️ Follow-up Due ({days_since}d)" if days_since >= threshold_days else f"✅ Waiting ({days_since}d)"
            last_date = contact_date.strftime("%Y-%m-%d")
        
        summary_data.append({
            "Clinic Name": l["business_name"],
            "Status": status,
            "Last Action Date": last_date,
            "History Count": len(history)
        })
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

# Right Column: Smart Follow-Up Generator
with col_action:
    st.markdown("### 💬 SMART FOLLOW-UP GENERATOR")
    
    lead_names = [l["business_name"] for l in st.session_state.demo_history]
    selected_name = st.selectbox("Select Target Lead to Connect:", lead_names)
    
    # Get the selected lead records
    selected_idx = lead_names.index(selected_name)
    lead = st.session_state.demo_history[selected_idx]
    history = lead["history"]
    
    # Determine the status and next step
    is_due = False
    days_since_str = ""
    next_stage = 1
    
    if history:
        newest = sorted(history, key=lambda x: x["timestamp"], reverse=True)[0]
        contact_date = datetime.strptime(newest["timestamp"], "%Y-%m-%d %H:%M:%S")
        days_since = (datetime.now() - contact_date).days
        next_stage = newest["stage"] + 1
        
        if days_since >= threshold_days:
            is_due = True
            st.markdown(f"""
            <div class="outreach-badge badge-due">
                <span>⚠️ FOLLOW-UP IS DUE</span>
                <span>Last contact was {days_since} days ago via {newest['channel']} (Stage {newest['stage']})</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="outreach-badge badge-ok">
                <span>✅ RECENTLY CONTACTED</span>
                <span>Last contact was {days_since} day(s) ago (Stage {newest['stage']})</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="outreach-badge" style="background: rgba(148, 163, 184, 0.1); border: 1px solid rgba(148, 163, 184, 0.3); color: var(--text-muted);">
            <span>⚪ NEW LEAD</span>
            <span>No previous outreach recorded. Ready for initial contact (Stage 1).</span>
        </div>
        """, unsafe_allow_html=True)

    # 1. Custom Follow-Up Template Builder
    st.markdown("#### ✉️ GENERATE STAGE-APPROPRIATE MESSAGE")
    
    if next_stage == 1:
        campaign_title = "Initial Outreach: B2B Partnership Proposal"
        subject = f"Collaboration Proposal: Eye Finder & {lead['business_name']}"
        body = (
            f"Hello Team {lead['business_name']},\n\n"
            f"I hope this finds you well. We are reaching out from our healthcare network to discuss a strategic partnership. "
            f"We have identified your facility at {lead['address']} as a premier {lead['category']} in the region.\n\n"
            f"Please let us know a suitable time to connect.\n\n"
            f"Best regards,\nEye Finder Sales Team"
        )
    elif next_stage == 2:
        campaign_title = "Follow-up 1: Quick Check-in"
        subject = f"Re: Collaboration Proposal: Eye Finder & {lead['business_name']}"
        body = (
            f"Hello Team {lead['business_name']},\n\n"
            f"I wanted to follow up briefly on the partnership proposal I sent over a few days ago. "
            f"I understand your schedule is busy, but I'd love to know if you've had a chance to review it.\n\n"
            f"Do you have 5 minutes for a quick introductory call next week?\n\n"
            f"Best regards,\nEye Finder Sales Team"
        )
    else:
        campaign_title = f"Follow-up {next_stage-1}: Offer Demonstration"
        subject = f"Complimentary equipment/demo inquiry for {lead['business_name']}"
        body = (
            f"Dear Director,\n\n"
            f"Just dropping a final note to check if there is any interest in exploring eye care clinical tools for {lead['business_name']}. "
            f"We'd be glad to arrange a virtual demonstration at your convenience.\n\n"
            f"Should you want to touch base, my details are below.\n\n"
            f"Best regards,\nEye Finder Sales Team"
        )

    st.markdown(f"**Target Stage:** `Stage {next_stage} ({campaign_title})`")
    st.markdown(f"**Subject:** `{subject}`")
    editable_body = st.text_area("Message Preview:", value=body, height=180, key=f"preview_msg_{selected_idx}_{next_stage}")

    # Action Buttons
    act_col1, act_col2 = st.columns(2)
    with act_col1:
        if st.button("📲 LOG & SEND WHATSAPP", key="demo_wa_btn", use_container_width=True):
            # Log the outreach action in simulation state
            new_log = {
                "channel": "WhatsApp",
                "campaign_type": campaign_title,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "stage": next_stage,
                "status": "SENT"
            }
            st.session_state.demo_history[selected_idx]["history"].insert(0, new_log)
            st.success(f"Log updated: Stage {next_stage} WhatsApp recorded!")
            st.rerun()
            
    with act_col2:
        if st.button("📨 LOG & COMPOSE EMAIL", key="demo_email_btn", use_container_width=True):
            # Log the outreach action in simulation state
            new_log = {
                "channel": "Email",
                "campaign_type": campaign_title,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "stage": next_stage,
                "status": "SENT"
            }
            st.session_state.demo_history[selected_idx]["history"].insert(0, new_log)
            st.success(f"Log updated: Stage {next_stage} Email recorded!")
            st.rerun()

    # 2. Interactive Timeline display
    st.markdown("---")
    st.markdown("#### ⏳ LEAD OUTREACH TIMELINE")
    
    if not history:
        st.info("No communications have occurred yet. The timeline is clean.")
    else:
        st.markdown("<div class='timeline-container'>", unsafe_allow_html=True)
        # Sort history to display oldest-to-newest chronologically in timeline
        chrono_history = sorted(history, key=lambda x: x["timestamp"])
        for idx, entry in enumerate(chrono_history):
            st.markdown(f"""
            <div class="timeline-node completed">
                <div class="timeline-label">✓ STAGE {entry['stage']} • {entry['channel']} ({entry['timestamp']})</div>
                <div class="timeline-title">{entry['campaign_type']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Preview the *next* stage as a pending placeholder
        st.markdown(f"""
        <div class="timeline-node pending">
            <div class="timeline-label" style="color: var(--warning-accent);">⚡ STAGE {next_stage} (PENDING)</div>
            <div class="timeline-title" style="color: var(--text-muted);">Ready to initiate follow-up outreach</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# INFORMATION BOX ON INTEGRATION
# ---------------------------------------------------------
st.markdown("---")
st.info("""
💡 **How this integrates into the main code:** 
We will update `record_outreach()` and the `outreach_history.json` schema to store a sequential `stage` integer for each message. 
Then, in the main **Smart Outreach** UI, the logic will automatically calculate the next stage for the chosen lead, choose the appropriate follow-up subject/body, and display the due indicators on the dashboard without breaking any of the existing code.
""")
