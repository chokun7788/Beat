import streamlit as st
import pandas as pd
from datetime import date
import os
from pathlib import Path

st.title("🚨 แจ้งเตือนมิจฉาชีพ")

DATA_FILE = "fraud_reports.csv"
EVIDENCE_FOLDER = "evidence"

# สร้างโฟลเดอร์ evidence ถ้ายังไม่มี
os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

# โหลดข้อมูลเก่า
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "ชื่อบัญชี", "เลขบัญชี", "ธนาคาร", "จำนวนเงิน", "รายละเอียด", "วันที่", "ไฟล์หลักฐาน"
    ])

# --- ฟอร์มแจ้งเตือน ---
with st.form("fraud_report_form"):
    account_name = st.text_input("ชื่อบัญชี")
    bank_account = st.text_input("เลขบัญชีธนาคาร")
    bank_name = st.text_input("ธนาคาร")
    amount = st.number_input("จำนวนเงินที่โดน", min_value=0.0, step=0.01)
    details = st.text_area("รายละเอียดเหตุการณ์")
    report_date = st.date_input("วันที่โดนโกง", date.today())
    evidence_file = st.file_uploader("อัปโหลดหลักฐาน (รูป)", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("บันทึกรายงาน")

    if submitted:
        # จัดการเก็บไฟล์หลักฐาน
        evidence_path = ""
        if evidence_file:
            file_ext = evidence_file.name.split(".")[-1]
            safe_name = f"{bank_account}_{report_date}.{file_ext}"
            evidence_path = os.path.join(EVIDENCE_FOLDER, safe_name)
            
            with open(evidence_path, "wb") as f:
                f.write(evidence_file.getbuffer())

        # บันทึกลง DataFrame
        new_data = pd.DataFrame([{
            "ชื่อบัญชี": account_name,
            "เลขบัญชี": bank_account,
            "ธนาคาร": bank_name,
            "จำนวนเงิน": amount,
            "รายละเอียด": details,
            "วันที่": report_date,
            "ไฟล์หลักฐาน": evidence_path
        }])
        
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("✅ บันทึกรายงานเรียบร้อย")

# --- ค้นหา ---
st.subheader("🔍 ค้นหารายงานมิจฉาชีพ")
keyword = st.text_input("พิมพ์ชื่อบัญชี / เลขบัญชี / ธนาคาร เพื่อตรวจสอบ")

if keyword:
    results = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)]
else:
    results = df

if not results.empty:
    for idx, row in results.iterrows():
        st.write(f"**ชื่อบัญชี:** {row['ชื่อบัญชี']}")
        st.write(f"**เลขบัญชี:** {row['เลขบัญชี']}")
        st.write(f"**ธนาคาร:** {row['ธนาคาร']}")
        st.write(f"**จำนวนเงิน:** {row['จำนวนเงิน']}")
        st.write(f"**รายละเอียด:** {row['รายละเอียด']}")
        st.write(f"**วันที่:** {row['วันที่']}")
        
        # โชว์รูป
        if os.path.exists(row['ไฟล์หลักฐาน']) and row['ไฟล์หลักฐาน'] != "":
            st.image(row['ไฟล์หลักฐาน'], width=250)
        st.markdown("---")
else:
    st.info("ไม่พบข้อมูลที่ตรงกับการค้นหา")
