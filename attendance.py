import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -----------------------------
# 📁 Folder Setup
# -----------------------------
folder_name = "attendance_data"

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

file_path = os.path.join(folder_name, "attendance.csv")

# -----------------------------
# 📊 Page Setup
# -----------------------------
st.set_page_config(page_title="Attendance Dashboard", layout="wide")
st.title("📊 Daily Huddle Attendance Dashboard")

# -----------------------------
# 📂 Load Data
# -----------------------------
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns=["Name", "Date", "Status"])

# -----------------------------
# ➕ Add Attendance (FORM)
# -----------------------------
st.subheader("➕ Mark Attendance")

with st.form("attendance_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Enter Name")

    with col2:
        date = st.date_input("Select Date", datetime.today())

    with col3:
        status = st.selectbox("Status", ["Present", "Absent"])

    submit = st.form_submit_button("Add Attendance")

# Duplicate check
def is_duplicate(name, date):
    return ((df["Name"] == name) & (df["Date"] == str(date))).any()

if submit:
    if name.strip() == "":
        st.warning("⚠️ Please enter name")

    elif is_duplicate(name, date):
        st.error("❌ Attendance already marked for this date")

    else:
        new_data = pd.DataFrame([[name, str(date), status]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(file_path, index=False)
        st.success("✅ Attendance Added")
        st.rerun()

# -----------------------------
# ✏️ EDIT SECTION
# -----------------------------
st.subheader("✏️ Edit Attendance")

if not df.empty:
    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button("💾 Save Changes"):
        edited_df.to_csv(file_path, index=False)
        st.success("✅ Changes Saved")
        st.rerun()
else:
    edited_df = df

# -----------------------------
# 📊 SUMMARY (AUTO UPDATE)
# -----------------------------
st.subheader("📊 Attendance Summary")

# Always use latest data
data_for_calc = edited_df if not edited_df.empty else df

if not data_for_calc.empty:
    total_days = data_for_calc.groupby("Name").size()
    present_days = data_for_calc[data_for_calc["Status"] == "Present"].groupby("Name").size()

    summary = pd.DataFrame({
        "Total Days": total_days,
        "Present Days": present_days
    }).fillna(0)

    summary["Attendance %"] = (summary["Present Days"] / summary["Total Days"]) * 100
    summary["Attendance %"] = summary["Attendance %"].round(2)

    st.dataframe(summary, use_container_width=True)

    # Chart
    st.subheader("📈 Attendance % Chart")
    st.bar_chart(summary["Attendance %"])

# -----------------------------
# 📋 RAW DATA
# -----------------------------
with st.expander("📋 Show Raw Data"):
    st.dataframe(data_for_calc)

# -----------------------------
# ⬇️ DOWNLOAD
# -----------------------------
st.subheader("⬇️ Download Data")

st.download_button(
    "Download Attendance CSV",
    data_for_calc.to_csv(index=False),
    "attendance.csv",
    "text/csv"
)

# -----------------------------
# 🧹 RESET
# -----------------------------
st.subheader("🧹 Reset All Data")

if st.button("Clear All Attendance"):
    empty_df = pd.DataFrame(columns=["Name", "Date", "Status"])
    empty_df.to_csv(file_path, index=False)
    st.warning("⚠️ All data cleared!")
    st.rerun()