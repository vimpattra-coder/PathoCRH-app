import streamlit as st
import pandas as pd
import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(layout="wide")

# 1. หัวข้อและวันที่ (ดึงเวลาไทย)
st.title("ระบบสรุปรายการทิ้ง Specimen ประจำวัน 🔬")
th_date = (datetime.datetime.now() + datetime.timedelta(hours=7)).date()
st.write(f"ประจำวันที่: {th_date.strftime('%d/%m/%Y')}")

# 2. จำลองข้อมูล
if "df" not in st.session_state:
    data = {
        "Surgical No.": ["S690001", "S690002", "S690003", "S690004", "S690005", "S690006", "S690007", "S690008", "S690009", "S690010"],
        "HN": ["1234567", "1234567", "2345678", "3456789", "5556667", "6667778", "7778889", "8889990", "9990001", "9990002"],
        "ชื่อผู้ป่วย": ["นายสมชาย ดีใจ", "นายสมชาย ดีใจ", "นางสมศรี มีสุข", "นายสมศักดิ์ รักดี", "นายมานะ เก่งกาจ", "นางชูใจ รักเรียน", "นายปิติ สุขใจ", "นางสาววีระ ปัญญา", "นายสมนึก นอบน้อม", "นางสมหญิง รักสงบ"],
        "วันที่ออกผลล่าสุด": [datetime.date(2026, 6, 1), datetime.date(2026, 6, 1), datetime.date(2026, 5, 28), datetime.date(2026, 6, 2), datetime.date(2026, 5, 12), datetime.date(2026, 5, 13), datetime.date(2026, 5, 14), datetime.date(2026, 5, 15), datetime.date(2026, 5, 11), datetime.date(2026, 6, 2)],
        "แพทย์เจ้าของเคส": ["VT", "VT", "NK", "KK", "PS", "NK", "VT", "PS", "KK", "NK"],
        "หมายเหตุ/เหตุผล": [""]*10,
        "สถานะพิเศษ": [None]*10,
        "วันกำหนดทิ้งปรับปรุง": [None]*10,
        "การทิ้งชิ้นเนื้อ": ["ยังไม่ได้ทิ้ง"]*10,
        "วันที่กดทิ้ง": [None]*10
    }
    st.session_state.df = pd.DataFrame(data)

df = st.session_state.df
df["วันที่ออกผลล่าสุด"] = pd.to_datetime(df["วันที่ออกผลล่าสุด"]).dt.date
df["วันที่กดทิ้ง"] = pd.to_datetime(df["วันที่กดทิ้ง"])

# 3. คำนวณกำหนดทิ้ง
def calculate_final_date(row):
    if row["สถานะพิเศษ"] == "Consult/IHC": return "-"
    if pd.notnull(row["วันกำหนดทิ้งปรับปรุง"]): return row["วันกำหนดทิ้งปรับปรุง"]
    return row["วันที่ออกผลล่าสุด"] + datetime.timedelta(days=15)

df["กำหนดทิ้งสุดท้าย"] = df.apply(calculate_final_date, axis=1)

def get_status(row):
    if row["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว": return "⚫ ทิ้งเรียบร้อยแล้ว"
    if row["กำหนดทิ้งสุดท้าย"] == "-": return "⏳ ห้ามทิ้ง (รอ Consult/IHC)"
    d_limit = row["กำหนดทิ้งสุดท้าย"] if isinstance(row["กำหนดทิ้งสุดท้าย"], datetime.date) else datetime.date.today()
    return "🟢 ครบกำหนด (ทิ้งได้)" if th_date >= d_limit else "🔵 กำลังเก็บรักษา"

df["สถานะ"] = df.apply(get_status, axis=1)

# 4. ค้นหาและจัดการเคสรายบุคคล
st.subheader("🔍 ค้นหาและจัดการเคสรายบุคคล")
search_query = st.text_input("พิมพ์เลขเคส (SN) หรือเลข HN ที่ต้องการค้นหา:", placeholder="เช่น S690010").strip()

if search_query:
    mask = df["Surgical No."].str.contains(search_query, case=False, na=False) | df["HN"].str.contains(search_query, case=False, na=False)
    search_result = df[mask]
    
    if not search_result.empty:
        st.write("ผลการค้นหา:")
        cols_header = st.columns([1, 1, 2, 1.5, 1.5, 2, 2])
        cols_header[0].write("**เลขเคส (SN)**")
        cols_header[1].write("**HN**")
        cols_header[2].write("**ชื่อผู้ป่วย**")
        cols_header[3].write("**ออกผลล่าสุด**")
        cols_header[4].write("**กำหนดทิ้ง**")
        cols_header[5].write("**เงื่อนไข 1**")
        cols_header[6].write("**เงื่อนไข 2**")
        st.markdown("---")
        
        for idx, row in search_result.iterrows():
            cols = st.columns([1, 1, 2, 1.5, 1.5, 2, 2])
            cols[0].write(row["Surgical No."])
            cols[1].write(row["HN"])
            cols[2].write(row["ชื่อผู้ป่วย"])
            cols[3].write(row["วันที่ออกผลล่าสุด"].strftime('%d/%m/%Y'))
            
            # --- แก้ไขการแสดงผลช่องกำหนดทิ้ง ---
            if row["สถานะพิเศษ"] == "Consult/IHC":
                cols[4].write("ยังไม่มีกำหนด")
            else:
                due_date = row["กำหนดทิ้งสุดท้าย"]
                if isinstance(due_date, (datetime.date, pd.Timestamp)):
                    cols[4].write(due_date.strftime('%d/%m/%Y'))
                else:
                    cols[4].write("-")
            # --------------------------------
            
            is_consult = (row["สถานะพิเศษ"] == "Consult/IHC")
            
            if not is_consult:
                if cols[5].button("🟡 Consult / IHC", key=f"btn1_{idx}"):
                    df.loc[idx, ["สถานะพิเศษ", "หมายเหตุ/เหตุผล"]] = ["Consult/IHC", "รอ Consult/IHC"]
                    st.rerun()
            else:
                if cols[5].button("🟢 Final เคสนี้", key=f"btn_f_{idx}"):
                    df.loc[idx, ["สถานะพิเศษ", "หมายเหตุ/เหตุผล", "วันที่ออกผลล่าสุด", "วันกำหนดทิ้งปรับปรุง"]] = [
                        None, "Final แล้ว", th_date, th_date + datetime.timedelta(days=15)
                    ]
                    st.rerun()
            
            if cols[6].button("🔵 ผลเพิ่มเติม (+15 วัน)", key=f"btn2_{idx}"):
                df.loc[idx, ["สถานะพิเศษ", "หมายเหตุ/เหตุผล", "วันที่ออกผลล่าสุด", "วันกำหนดทิ้งปรับปรุง"]] = [
                    None, "ผลเพิ่มเติม", th_date, th_date + datetime.timedelta(days=15)
                ]
                st.rerun()
    else:
        st.warning("ไม่พบข้อมูล")

# 5. แสดงตารางหลัก (บังคับแสดงเป็น วัน/เดือน/ปี หรือ - เท่านั้น)
mask_threw = (df["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว") & (pd.notnull(df["วันที่กดทิ้ง"]))
active_mask = ~mask_threw
filtered_df = df[active_mask | (mask_threw & (df["วันที่กดทิ้ง"].dt.date == th_date))].copy()

display_df = filtered_df[["Surgical No.", "HN", "ชื่อผู้ป่วย", "แพทย์เจ้าของเคส", "วันที่ออกผลล่าสุด", "กำหนดทิ้งสุดท้าย", "สถานะ", "หมายเหตุ/เหตุผล"]].copy()

# แปลงวันที่ออกผลล่าสุดให้เป็น วัน/เดือน/ปี
display_df["วันที่ออกผลล่าสุด"] = display_df["วันที่ออกผลล่าสุด"].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, pd.Timestamp)) else "-")

# --- บังคับให้กำหนดทิ้งสุดท้ายเป็น วัน/เดือน/ปี เท่านั้น ถ้าไม่มีให้เป็น - ---
def force_date_format(x):
    if isinstance(x, (datetime.date, pd.Timestamp)):
        return x.strftime('%d/%m/%Y')
    else:
        return "-"

display_df["กำหนดทิ้งสุดท้าย"] = display_df["กำหนดทิ้งสุดท้าย"].apply(force_date_format)
# --------------------------------------------------------------------------

display_df.index = range(1, len(display_df) + 1)

st.subheader("📋 รายการสิ่งส่งตรวจทั้งหมดในระบบ")
st.dataframe(display_df, use_container_width=True)

# 6. สิ่งส่งตรวจที่ต้องทิ้งวันนี้ (บังคับแสดงวันที่เป็น วว/ดด/ปปปป)
st.subheader("🗑️ สิ่งส่งตรวจที่ต้องทิ้งวันนี้")
pending_discard = filtered_df[filtered_df["สถานะ"] == "🟢 ครบกำหนด (ทิ้งได้)"].copy()

if not pending_discard.empty:
    # 1. แปลงวันที่ให้เป็น string ในรูปแบบที่ต้องการก่อนแสดงผล
    pending_discard["กำหนดทิ้งสุดท้าย"] = pending_discard["กำหนดทิ้งสุดท้าย"].apply(
        lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, pd.Timestamp)) else str(x)
    )
    
    # 2. สร้างสถานะการเลือก
    if "all_selected" not in st.session_state: st.session_state.all_selected = False
    if st.checkbox("📋 เลือกทั้งหมดของวันนี้", key="select_all_btn"):
        st.session_state.all_selected = True
    else:
        st.session_state.all_selected = False

    pending_discard["เลือก"] = st.session_state.all_selected
    
    # 3. แสดง Data Editor
    edited_df = st.data_editor(
        pending_discard[["เลือก", "Surgical No.", "HN", "ชื่อผู้ป่วย", "กำหนดทิ้งสุดท้าย"]],
        column_config={
            "เลือก": st.column_config.CheckboxColumn("เลือกทิ้ง", default=False),
            "Surgical No.": st.column_config.TextColumn("Surgical No.", disabled=True),
            "HN": st.column_config.TextColumn("HN", disabled=True),
            "ชื่อผู้ป่วย": st.column_config.TextColumn("ชื่อผู้ป่วย", disabled=True),
            # เปลี่ยนเป็น TextColumn เพื่อให้แสดงผลตามที่เรา Format ไว้เป็น วว/ดด/ปปปป
            "กำหนดทิ้งสุดท้าย": st.column_config.TextColumn("กำหนดทิ้ง", disabled=True),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # 4. ยืนยันการทิ้ง (เหมือนเดิม)
    if st.button("🗑️ ยืนยันการทิ้งเคสที่เลือก", type="primary"):
        selected_cases = edited_df[edited_df["เลือก"] == True]
        if not selected_cases.empty:
            df.loc[df["Surgical No."].isin(selected_cases["Surgical No."]), ["การทิ้งชิ้นเนื้อ", "วันที่กดทิ้ง"]] = ["ทิ้งแล้ว", pd.Timestamp(th_date)]
            st.success(f"ทิ้งเรียบร้อยแล้ว {len(selected_cases)} เคส")
            st.rerun()
        else:
            st.warning("กรุณาเลือกเคสที่ต้องการทิ้งก่อน")
else:
    st.info("วันนี้ไม่มีรายการที่ต้องทิ้ง")