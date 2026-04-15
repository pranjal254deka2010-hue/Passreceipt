import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os

# --- 1. SECURITY CONFIG ---
# You can change this password whenever you want
ADMIN_PASSWORD = "OPI_Secure_2026" 

def check_password():
    """Returns True if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>OPI Admin Login</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Enter Password", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("🚫 Incorrect Password")
        return False
    return True

# --- 2. APP START ---
if check_password():
    st.set_page_config(page_title="OPI Receipt Portal", layout="centered")

    # Database Setup
    PAY_LOG = "receipt_history.csv"
    if not os.path.exists(PAY_LOG):
        pd.DataFrame(columns=["Date", "Receipt_No", "Student", "Purpose", "Amount"]).to_csv(PAY_LOG, index=False)

    # Header
    st.markdown("<h1 style='text-align: center; color: #002e63;'>OXFORD PARAMEDICAL INSTITUTE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: bold;'>Fees Management System | Dhupdhara Campus</p>", unsafe_allow_html=True)

    menu = st.sidebar.selectbox("Dashboard", ["Generate Receipt", "Payment History", "Logout"])

    if menu == "Logout":
        del st.session_state["password_correct"]
        st.rerun()

    elif menu == "Generate Receipt":
        st.subheader("📝 New Payment Entry")
        with st.form("receipt_form"):
            name = st.text_input("Full Student Name")
            purpose = st.selectbox("Purpose of Payment", ["Admission Fee", "Monthly Fee", "Registration Fee", "Exam Fee", "Other"])
            months = st.text_input("For Month/Period (e.g. May-June)", value="N/A")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            mode = st.selectbox("Payment Mode", ["Cash", "UPI/Online", "Cheque"])
            
            submit = st.form_submit_button("Generate Official PDF")

        if submit and name:
            receipt_no = f"OPI-R-{datetime.now().strftime('%y%m%H%M')}"
            today = datetime.now().strftime("%d-%m-%Y")

            # Save to CSV
            new_data = pd.DataFrame([[today, receipt_no, name, purpose, amount]], columns=["Date", "Receipt_No", "Student", "Purpose", "Amount"])
            new_data.to_csv(PAY_LOG, mode='a', header=False, index=False)

            # PDF GENERATION
            pdf = FPDF()
            pdf.add_page()
            pdf.rect(5, 5, 200, 287) # Simple Border

            # Logo handling
            if os.path.exists("logo.png"):
                pdf.image("logo.png", 10, 10, 30)

            # Header
            pdf.set_font("Arial", 'B', 16)
            pdf.set_xy(45, 15)
            pdf.cell(0, 10, "OXFORD PARAMEDICAL INSTITUTE", ln=True)
            pdf.set_font("Arial", '', 10)
            pdf.set_xy(45, 22)
            pdf.cell(0, 10, "Dhupdhara, Goalpara, Assam - 783123", ln=True)

            pdf.ln(30)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "FEES RECEIPT", ln=True, align='C')
            pdf.ln(10)

            # Details
            pdf.set_font("Arial", '', 12)
            pdf.cell(100, 10, f"Receipt No: {receipt_no}")
            pdf.cell(0, 10, f"Date: {today}", ln=True, align='R')
            pdf.ln(5)
            pdf.cell(0, 12, f"Student: {name.upper()}", border='B', ln=True)
            pdf.cell(0, 12, f"Purpose: {purpose} ({months})", border='B', ln=True)
            pdf.cell(0, 12, f"Payment Mode: {mode}", border='B', ln=True)
            
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 15, f"TOTAL PAID: Rs. {amount:,.2f}", border=1, ln=True, align='C', fill=False)

            # Signature
            if os.path.exists("signature.png"):
                pdf.image("signature.png", 150, 160, 40)
            
            pdf.ln(40)
            pdf.cell(0, 10, "__________________________", ln=True, align='R')
            pdf.cell(0, 5, "Authorized Signatory      ", ln=True, align='R')

            pdf_out = pdf.output(dest='S').encode('latin-1')
            st.success("✅ Receipt Saved and Generated!")
            st.download_button("Download PDF", pdf_out, f"Receipt_{name}.pdf")

    elif menu == "Payment History":
        st.subheader("💰 Collection Records")
        if os.path.exists(PAY_LOG):
            df = pd.read_csv(PAY_LOG)
            st.metric("Total Collection", f"₹{df['Amount'].sum():,.2f}")
            st.dataframe(df, use_container_width=True)
            st.download_button("Export Excel (CSV)", df.to_csv(index=False), "OPI_Collection.csv")
