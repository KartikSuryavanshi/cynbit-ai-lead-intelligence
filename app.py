import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from src.csv_processor import parse_csv
from src.data_store import LeadStore
from src.lead_analyzer import analyze_lead
from src.schemas import LeadInput

st.set_page_config(page_title="Cynbit Lead Intelligence", page_icon="✦", layout="wide")
st.markdown("""<style>.block-container{max-width:1200px;padding-top:2rem}.hero{padding:1.2rem 1.4rem;border-radius:18px;background:linear-gradient(135deg,#102a43,#0e7490);color:#fff;margin-bottom:1.2rem}</style>""", unsafe_allow_html=True)
store = LeadStore(os.getenv("CYNBIT_DB_PATH", "data/leads.db"))
if "leads" not in st.session_state: st.session_state.leads = store.all()
if "latest_analysis" not in st.session_state: st.session_state.latest_analysis = None
if "email_draft" not in st.session_state: st.session_state.email_draft = ""
st.markdown('<div class="hero"><h1>✦ Cynbit Lead Intelligence</h1><p>Review inbound enquiries, surface requirements, and prepare thoughtful human-reviewed follow-ups.</p></div>', unsafe_allow_html=True)
st.caption("Demonstration product • Synthetic/sample data only • No emails are sent automatically")
tab_dashboard, tab_intake, tab_batch, tab_about = st.tabs(["Dashboard", "Analyse enquiry", "CSV batch", "About this PoC"])

def refresh(): st.session_state.leads = store.all()

with tab_dashboard:
    rows = st.session_state.leads
    query = st.text_input("Search leads", placeholder="Search company, enquiry, or service…")
    priority = st.multiselect("Priority", ["High", "Medium", "Low", "Unknown"], default=["High", "Medium", "Low", "Unknown"])
    filtered = [row for row in rows if row["analysis"].get("priority") in priority and (not query or query.lower() in str(row).lower())]
    counts = pd.Series([row["analysis"].get("priority", "Unknown") for row in rows]).value_counts() if rows else pd.Series(dtype=int)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total leads", len(rows)); c2.metric("High priority", int(counts.get("High", 0))); c3.metric("Medium priority", int(counts.get("Medium", 0))); c4.metric("Needs review", sum(row["analysis"].get("follow_up_status") == "Needs review" for row in rows))
    if rows:
        left, right = st.columns(2)
        with left:
            chart = pd.DataFrame({"Priority": counts.index, "Leads": counts.values})
            st.plotly_chart(px.bar(chart, x="Priority", y="Leads", color="Priority", color_discrete_map={"High":"#dc2626","Medium":"#d97706","Low":"#0f766e","Unknown":"#64748b"}), use_container_width=True)
        with right:
            services = pd.Series([row["analysis"].get("service_category", "Unknown") for row in rows]).value_counts().reset_index(); services.columns = ["Service", "Leads"]
            st.plotly_chart(px.pie(services, names="Service", values="Leads", hole=.45), use_container_width=True)
        st.subheader("Recent leads")
        st.dataframe(pd.DataFrame([{ "Company": r["company_name"] or "—", "Enquiry": r["enquiry_text"][:90], "Service": r["analysis"].get("service_category"), "Priority": r["analysis"].get("priority"), "Score": r["analysis"].get("score"), "Created": r["created_at"][:19] } for r in filtered]), use_container_width=True, hide_index=True)
    else: st.info("No leads yet. Load the synthetic sample data from the CSV batch tab or analyse an enquiry.")

with tab_intake:
    with st.form("lead_form"):
        a, b = st.columns(2)
        customer = a.text_input("Customer name or identifier (optional)"); company = b.text_input("Company (optional)")
        category = a.selectbox("Service category", ["Not specified", "AI automation", "Software development", "Cloud infrastructure", "Digital marketing & SEO", "Training"])
        budget = b.text_input("Budget (only if explicitly known)", placeholder="Unknown"); timeline = a.text_input("Timeline (only if explicitly known)", placeholder="Unknown")
        enquiry = st.text_area("Customer enquiry", height=170, placeholder="Example: We need an internal AI assistant for our support team…")
        use_llm = st.checkbox("Use configured LLM provider", value=False, help="If unavailable or it fails, the app transparently falls back to deterministic demo mode.")
        submitted = st.form_submit_button("Analyse enquiry", type="primary")
    if submitted:
        try:
            lead = LeadInput(customer_name=customer, company_name=company, service_category=category, budget=budget or "Unknown", timeline=timeline or "Unknown", enquiry_text=enquiry)
            analysis, mode = analyze_lead(lead, use_llm); store.save(lead, analysis); refresh()
            st.session_state.latest_analysis = analysis
            st.session_state.email_draft = analysis.follow_up_email
            st.success(f"Analysis complete in {mode}. Review the draft before use.")
        except Exception as exc: st.error(str(exc))
    if st.session_state.latest_analysis:
        st.json(st.session_state.latest_analysis.model_dump(exclude={"follow_up_email"}))
        edited_email = st.text_area("Human-reviewable follow-up draft", key="email_draft", height=280)
        st.download_button("Download reviewed email", edited_email, "cynbit_follow_up_draft.txt", "text/plain")

with tab_batch:
    st.write("Upload a CSV with at least an `enquiry_text` column. Invalid rows are reported; duplicate company + enquiry pairs are skipped.")
    uploaded = st.file_uploader("CSV file", type="csv")
    if uploaded and st.button("Analyse CSV"):
        leads, errors = parse_csv(uploaded)
        if errors: st.warning("\n".join(errors))
        analyses = []
        for lead in leads:
            analysis, _ = analyze_lead(lead, False); store.save(lead, analysis); analyses.append({**lead.model_dump(), **analysis.model_dump()})
        refresh()
        if analyses:
            st.success(f"Analysed {len(analyses)} valid row(s) in deterministic demo mode."); st.download_button("Download analysis CSV", pd.DataFrame(analyses).to_csv(index=False), "cynbit_lead_analysis.csv", "text/csv")
    sample_path = Path(__file__).parent / "data" / "sample_leads.csv"
    st.download_button("Download synthetic sample CSV", sample_path.read_bytes(), "sample_leads.csv", "text/csv")

with tab_about:
    st.markdown("""### What this demonstrates
This proof of concept turns unstructured enquiries into validated lead records, with transparent priority scoring and a human-reviewable email draft. Demo mode is deterministic and labelled; it is not presented as an LLM result.

### Safety boundaries
No automatic outreach, no invented budget/timeline, no production accuracy claim, and no real customer data. Configure `OPENAI_API_KEY` only on the server/deployment secret store.

Use the reports folder for the opportunity analysis, technical approach, and implementation roadmap.
""")
