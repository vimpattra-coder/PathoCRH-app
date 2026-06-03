import streamlit as st
import pandas as pd
import datetime

# ตั้งค่าหน้าเว็บให้เป็นแบบขยายกว้างเต็มจอ
st.set_page_config(layout="wide")

# 1. ตั้งชื่อหัวข้อบนหน้าเว็บ
st.title("ระบบสรุปรายการทิ้ง Specimen ประจำวัน 🔬")
th_date = datetime.date.today() + datetime.timedelta(hours=7)
st.write(f"ประจำวันที่: {th_date.strftime('%d/%m/%Y')}")
# 2. จำลองข้อมูลสิ่งส่งตรวจและใช้ Session State บันทึกข้อมูล
if "df" not in st.session_state:
    data = {
        "เลขเคส (SN)": [
            "SN69-001", "SN69-002", 
            "SN69-003", "SN69-004", 
            "SN69-005", "SN69-006", "SN69-007", "SN69-008", "SN69-009",
            "SN69-010"  
        ],
        "HN": [
            "1234567", "1234567", 
            "2345678", "3456789", 
            "5556667", "6667778", "7778889", "8889990", "9990001",
            "9990002"  
        ],
        "ชื่อผู้ป่วย": [
            "นายสมชาย ดีใจ", "นายสมชาย ดีใจ", "นางสมศรี มีสุข", "นายสมศักดิ์ รักดี",
            "นายมานะ เก่งกาจ", "นางชูใจ รักเรียน", "นายปิติ สุขใจ", "นางสาววีระ ปัญญา", "นายสมนึก นอบน้อม",
            "นางสมหญิง รักสงบ"  
        ],
        "วันที่ออกผลล่าสุด": [
            datetime.date(2026, 6, 1), datetime.date(2026, 6, 1), datetime.date(2026, 5, 28), datetime.date(2026, 6, 2), 
            datetime.date(2026, 5, 12), datetime.date(2026, 5, 13), datetime.date(2026, 5, 14), datetime.date(2026, 5, 15), datetime.date(2026, 5, 11),
            datetime.date(2026, 6, 2)  
        ],
        "แพทย์เจ้าของเคส": ["VT", "VT", "NK", "KK", "PS", "NK", "VT", "PS", "KK", "NK"], 
        "หมายเหตุ/เหตุผล": ["", "", "", "", "", "", "", "", "", ""],
        "สถานะพิเศษ": [None, None, None, None, None, None, None, None, None, None], 
        "วันกำหนดทิ้งปรับปรุง": [None, None, None, None, None, None, None, None, None, None], 
        "การทิ้งชิ้นเนื้อ": [
            "ยังไม่ได้ทิ้ง", "ยังไม่ได้ทิ้ง", "ยังไม่ได้ทิ้ง", "ยังไม่ได้ทิ้ง",
            "ยังไม่ได้ทิ้ง", "ยังไม่ได้ทิ้ง", "ยังไม่ได้ทิ้ง", "ยังไม่ได้ทิ้ง", "ยังไม่ได้ทิ้ง",
            "ยังไม่ได้ทิ้ง"
        ],
        "วันที่กดทิ้ง": [None, None, None, None, None, None, None, None, None, None]
    }
    st.session_state.df = pd.DataFrame(data)

df = st.session_state.df

# แปลงฟอร์แมตวันที่ให้อยู่ในรูปแบบที่ถูกต้องสำหรับคำนวณ
df["วันที่ออกผลล่าสุด"] = pd.to_datetime(df["วันที่ออกผลล่าสุด"]).dt.date

# 3. สูตรคำนวณวันกำหนดทิ้งสุดท้าย
def calculate_final_date(row):
    if row["สถานะพิเศษ"] == "Consult/IHC":
        return "-"
    elif pd.notnull(row["วันกำหนดทิ้งปรับปรุง"]):
        return row["วันกำหนดทิ้งปรับปรุง"]
    else:
        return row["วันที่ออกผลล่าสุด"] + datetime.timedelta(days=15)

df["กำหนดทิ้งสุดท้าย"] = df.apply(calculate_final_date, axis=1)


# 4. ตรรกะกำหนดข้อความแสดง "สถานะ"
def check_status(row):
    if row["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว":
        return "⚫ ทิ้งเรียบร้อยแล้ว"
    elif row["กำหนดทิ้งสุดท้าย"] == "-":
        return "⏳ ห้ามทิ้ง (รอ Consult/IHC)"
    elif datetime.date.today() >= row["กำหนดทิ้งสุดท้าย"]:
        return "🟢 ครบกำหนด (ทิ้งได้)"
    else:
        return "🔵 กำลังเก็บรักษา"

df["สถานะ"] = df.apply(check_status, axis=1)


# 5. ส่วนระบบค้นหา (Search System)
st.subheader("🔍 ค้นหาและจัดการเคสรายบุคคล")
search_query = st.text_input("พิมพ์เลขเคส (SN) หรือเลข HN ที่ต้องการค้นหา:", placeholder="เช่น SN69-010 หรือ 9990002").strip()

if search_query:
    search_result = df[
        df["เลขเคส (SN)"].str.contains(search_query, case=False, na=False) | 
        df["HN"].str.contains(search_query, case=False, na=False)
    ]
    
    if not search_result.empty:
        st.markdown("**ผลการค้นหา:**")
        
        s_h1, s_h2, s_h3, s_h4, s_h5, s_h6, s_h7 = st.columns([1.2, 1.0, 1.8, 1.2, 1.2, 1.5, 1.5])
        with s_h1: st.markdown("**เลขเคส (SN)**")
        with s_h2: st.markdown("**HN**")
        with s_h3: st.markdown("**ชื่อผู้ป่วย**")
        with s_h4: st.markdown("**ออกผลล่าสุด**")
        with s_h5: st.markdown("**กำหนดทิ้ง**")
        with s_h6: st.markdown("**เงื่อนไข 1**") 
        with s_h7: st.markdown("**เงื่อนไข 2**") 
        st.markdown("---")
        
        for idx, row in search_result.iterrows():
            s_r1, s_r2, s_r3, s_r4, s_r5, s_r6, s_r7 = st.columns([1.2, 1.0, 1.8, 1.2, 1.2, 1.5, 1.5])
            with s_r1: st.write(row["เลขเคส (SN)"])
            with s_r2: st.write(row["HN"])
            with s_r3: st.write(row["ชื่อผู้ป่วย"])
            
            # แสดงผลวันที่ออกผลล่าสุดในโหมดค้นหา เป็น วัน/เดือน/ปี ค.ศ.
            with s_r4: st.write(row["วันที่ออกผลล่าสุด"].strftime('%d/%m/%Y'))
            
            with s_r5: 
                if isinstance(row["กำหนดทิ้งสุดท้าย"], datetime.date):
                    st.write(row["กำหนดทิ้งสุดท้าย"].strftime('%d/%m/%Y'))
                else:
                    st.write(f"**{row['กำหนดทิ้งสุดท้าย']}**")
            
            if row["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว":
                with s_r5:
                    st.markdown("<span style='color: gray;'>⚫ ทิ้งเรียบร้อยแล้ว</span>", unsafe_allow_html=True)
                with s_r6:
                    st.write("")
            else:
                with s_r6:
                    if row["สถานะพิเศษ"] == "Consult/IHC":
                        btn_final = st.button("🟢 Final เคสนี้", key=f"btn_fin_{idx}", use_container_width=True)
                        if btn_final:
                            today = datetime.date.today()
                            df.loc[idx, "สถานะพิเศษ"] = None
                            df.loc[idx, "วันที่ออกผลล่าสุด"] = today
                            df.loc[idx, "วันกำหนดทิ้งปรับปรุง"] = today + datetime.timedelta(days=15)
                            df.loc[idx, "หมายเหตุ/เหตุผล"] = f"ออกผล Final แล้วเมื่อ {today.strftime('%d/%m/%Y')} (Extend 15 วัน)"
                            st.toast(f"🟢 ปลดล็อกและออกผล Final เคส {row['เลขเคส (SN)']} เรียบร้อย")
                            st.rerun()
                    else:
                        btn_cnc = st.button("🟡 Consult / IHC", key=f"btn_cnc_{idx}", use_container_width=True)
                        if btn_cnc:
                            df.loc[idx, "สถานะพิเศษ"] = "Consult/IHC"
                            df.loc[idx, "วันกำหนดทิ้งปรับปรุง"] = None
                            df.loc[idx, "หมายเหตุ/เหตุผล"] = "อยู่ระหว่าง Consult หรือรอย้อม IHC"
                            st.toast(f"🔒 ล็อกเคส {row['เลขเคส (SN)']} เรียบร้อย")
                            st.rerun()
                        
                with s_r7:
                    btn_ext = st.button("🔵 ผลเพิ่มเติม (+15 วัน)", key=f"btn_ext_{idx}", use_container_width=True)
                    if btn_ext:
                        today = datetime.date.today()
                        df.loc[idx, "สถานะพิเศษ"] = None
                        df.loc[idx, "วันที่ออกผลล่าสุด"] = today
                        df.loc[idx, "วันกำหนดทิ้งปรับปรุง"] = today + datetime.timedelta(days=15)
                        df.loc[idx, "หมายเหตุ/เหตุผล"] = f"มีผลเพิ่มเติมเมื่อ {today.strftime('%d/%m/%Y')} (Extend 15 วัน)"
                        st.toast(f"🔄 อัปเดตผลล่าสุดและต่อเวลาเคส {row['เลขเคส (SN)']} สำเร็จ")
                        st.rerun()
        st.markdown("---")
    else:
        st.warning(f"❌ ไม่พบข้อมูลเลขเคส หรือ HN '{search_query}' ในระบบ")


# 6. คัดกรองวันถัดไปเคลียร์ออก
def filter_cases(row):
    if row["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว" and pd.notnull(row["วันที่กดทิ้ง"]):
        days_passed = (datetime.date.today() - row["วันที่กดทิ้ง"]).days
        if days_passed >= 1:
            return False
    return True

active_mask = df.apply(filter_cases, axis=1)
filtered_df = df[active_mask].copy() # ใช้ .copy() ป้องกันข้อผิดพลาดตอนกรองข้อมูล


# 📍 7. โซนเตรียมตารางหลักสำหรับแสดงผล (จุดที่แทรกแปลงวันที่ วัน/เดือน/ปี ค.ศ.) 📍
# สร้างตารางแยกเฉพาะสำหรับการโชว์ และเปลี่ยนรูปแบบแสดงผลวันที่ก่อนนำไปใส่ตาราง
display_df = filtered_df[["เลขเคส (SN)", "HN", "ชื่อผู้ป่วย", "แพทย์เจ้าของเคส", "วันที่ออกผลล่าสุด", "กำหนดทิ้งสุดท้าย", "สถานะ", "หมายเหตุ/เหตุผล"]].copy()

# แปลง 'วันที่ออกผลล่าสุด' เป็น วัน/เดือน/ปี
display_df["วันที่ออกผลล่าสุด"] = pd.to_datetime(display_df["วันที่ออกผลล่าสุด"]).dt.strftime('%d/%m/%Y')

# แปลง 'กำหนดทิ้งสุดท้าย' เป็น วัน/เดือน/ปี (ยกเว้นเคสที่เป็นเครื่องหมายลบ '-')
display_df["กำหนดทิ้งสุดท้าย"] = display_df["กำหนดทิ้งสุดท้าย"].apply(
    lambda x: x.strftime('%d/%m/%Y') if isinstance(x, datetime.date) else x
)


# แสดงผลตารางหลักทั้งหมดบนหน้าเว็บ
st.subheader("📋 รายการสิ่งส่งตรวจทั้งหมดในระบบ")
st.dataframe(display_df, use_container_width=True)


# 8. โซน: สิ่งส่งตรวจที่ต้องทิ้งวันนี้ 
st.subheader("🗑️ สิ่งส่งตรวจที่ต้องทิ้งวันนี้")
discard_today = filtered_df[
    (filtered_df["สถานะ"] == "🟢 ครบกำหนด (ทิ้งได้)") |
    (filtered_df["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว")
]

pending_discard = discard_today[discard_today["การทิ้งชิ้นเนื้อ"] == "ยังไม่ได้ทิ้ง"]

if not pending_discard.empty:
    
    def toggle_select_all():
        master_key = f"master_select_{len(pending_discard)}"
        if master_key in st.session_state:
            current_status = st.session_state[master_key]
            for _, r in pending_discard.iterrows():
                st.session_state[f"cb_{r['เลขเคส (SN)']}_{len(pending_discard)}"] = current_status

    select_all = st.checkbox(
        "📋 เลือกทั้งหมดของวันนี้", 
        value=False, 
        key=f"master_select_{len(pending_discard)}", 
        on_change=toggle_select_all
    )
    st.markdown(" ")

    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([0.8, 1.2, 1.2, 2.0, 1.2, 1.5])
    with h_col1: st.markdown("**เลือกทิ้ง**")
    with h_col2: st.markdown("**เลขเคส (SN)**")
    with h_col3: st.markdown("**HN**")
    with h_col4: st.markdown("**ชื่อผู้ป่วย**")
    with h_col5: st.markdown("**แพทย์**")
    with h_col6: st.markdown("**กำหนดทิ้งสุดท้าย**")
    st.markdown("---")
    
    selected_indices = []
    
    for idx, row in pending_discard.iterrows():
        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6 = st.columns([0.8, 1.2, 1.2, 2.0, 1.2, 1.5])
        
        sub_cb_key = f"cb_{row['เลขเคส (SN)']}_{len(pending_discard)}"
        if sub_cb_key not in st.session_state:
            st.session_state[sub_cb_key] = select_all
            
        with r_col1:
            is_checked = st.checkbox("เลือก", key=sub_cb_key, label_visibility="collapsed")
            if is_checked:
                selected_indices.append(idx)
                
        with r_col2: st.write(row["เลขเคส (SN)"])
        with r_col3: st.write(row["HN"])
        with r_col4: st.write(row["ชื่อผู้ป่วย"])
        with r_col5: st.write(row["แพทย์เจ้าของเคส"])
        with r_col6: 
            if isinstance(row["กำหนดทิ้งสุดท้าย"], datetime.date):
                st.write(row["กำหนดทิ้งสุดท้าย"].strftime('%d/%m/%Y'))
            else:
                st.write(row["กำหนดทิ้งสุดท้าย"])
                
    st.markdown("---")
    
    btn_disabled = len(selected_indices) == 0
    if st.button(f"🗑️ ยืนยันการทิ้งเคสที่เลือกไว้ ({len(selected_indices)} เคส)", use_container_width=True, type="primary", disabled=btn_disabled):
        for idx in selected_indices:
            df.loc[idx, "การทิ้งชิ้นเนื้อ"] = "ทิ้งแล้ว"
            df.loc[idx, "วันที่กดทิ้ง"] = datetime.date.today()
            
            target_sn = df.loc[idx, "เลขเคส (SN)"]
            del st.session_state[f"cb_{target_sn}_{len(pending_discard)}"]
            
        st.success(f"🗑️ ทำการบันทึกสถานะ 'ทิ้งแล้ว' สำหรับเคสที่เลือกเรียบร้อย")
        st.rerun()

else:
    already_discarded = discard_today[discard_today["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว"]
    if not already_discarded.empty:
        st.success("✅ ดำเนินการยืนยันการทิ้งชิ้นเนื้อของวันนี้เรียบร้อยครบถ้วน")
    else:
        st.info("วันนี้ไม่มีสิ่งส่งตรวจที่ครบกำหนดทิ้ง")