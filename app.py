import pandas as pd
import streamlit as st

st.set_page_config(page_title="Thời khóa biểu", layout="wide")
st.title("📅 Thời khoá biểu thông minh")

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None)

    # CONFIG
    classes = df.iloc[1, 2:].dropna().tolist()
    start_col = 2
    day_map = {"T2": "Thứ 2", "T3": "Thứ 3", "T4": "Thứ 4", "T5": "Thứ 5", "T6": "Thứ 6", "T7": "Thứ 7"}

    # PARSE
    records = []
    current_day = None
    for idx, row in df.iterrows():
        col_b = str(row[1]).strip() if pd.notna(row[1]) else ""
        if col_b in day_map:
            current_day = day_map[col_b]
            continue
        if col_b.startswith("Tiết"):
            parts = col_b.split()
            period = int(parts[1])
            session = parts[2] if len(parts) > 2 else ""
            for j, class_name in enumerate(classes, start=start_col):
                val = row[j]
                if pd.isna(val) or str(val).strip() == "-x-":
                    continue
                text = str(val).strip().split()
                subject = " ".join(text[:-1]) if len(text) > 1 else text[0]
                teacher = text[-1] if len(text) > 1 else ""
                records.append({
                    "Class": class_name,
                    "Day": current_day,
                    "Session": session,
                    "Period": period,
                    "Subject": subject,
                    "Teacher": teacher
                })

    timetable = pd.DataFrame(records)

    # Chọn lớp
    class_choice = st.selectbox("Chọn lớp:", classes)

    df_class = timetable[timetable["Class"] == class_choice]

    # Pivot -> bảng theo thứ/tiết
    pivot = df_class.pivot_table(index=["Session", "Period"], 
                                 columns="Day", 
                                 values="Subject", 
                                 aggfunc=lambda x: " / ".join(x)).fillna("")

    # Đặt lại tên cột/hàng dễ nhìn
    pivot = pivot.reset_index().sort_values(by=["Session", "Period"])
    pivot = pivot.rename(columns={"Session": "Buổi", "Period": "Tiết"})

    st.subheader(f"📘 Thời khoá biểu lớp {class_choice}")
    st.dataframe(pivot, use_container_width=True)

    # Xuất CSV
    csv = timetable.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("⬇️ Tải toàn bộ CSV", csv, "thoikhoabieu_chuan.csv", "text/csv")
