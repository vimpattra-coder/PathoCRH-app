import streamlit as st
import pandas as pd
import datetime

# ตั้งค่าหน้าจอ

# สมมติฐานเวลาปัจจุบัน (เวลาประเทศไทย)
th_date = datetime.date(2026, 6, 4)

# ==============================================================================
# 1. จำลองข้อมูลเริ่มต้น
# ==============================================================================
if "df_data" not in st.session_state:
    data = {
        "Surgical No.": [
            "S690001", "S690002", "S690003", "S690005", "S690006", "S690007", "S690008", "S690009",
            "S690010", "S690011", "S690012"
        ],
        "HN": [
            "1111111", "1234567", "2345678", "5555667", "6667778", "7778889", "8889990", "9990001",
            "4445551", "4445552", "4445553"
        ],
        "ชื่อผู้ป่วย": [
            "นายสมชาย ใจดี", "นายสมชาย ดีใจ", "นางสมศรี มีสุข", "นายมานะ เก่งกาจ", "นางชูใจ รักเรียน", "นายปิติ สุขใจ", "นางสาววีระ ปัญญา", "นายสมนึก นอบน้อม",
            "นายวันชัย วันเดียวกัน", "นางสาวสมใจ วันเดียวกัน", "เด็กชายกิตติ วันเดียวกัน"
        ],
        "แพทย์เจ้าของเคส": ["VT", "PS", "KK", "NK", "VT", "PS", "KK", "NK", "VT", "PS", "KK"],
        "วันที่รับเนื้อ": [
            datetime.date(2026, 5, 1), datetime.date(2026, 5, 15), datetime.date(2026, 5, 20),
            datetime.date(2026, 5, 12), datetime.date(2026, 5, 13), datetime.date(2026, 5, 14),
            datetime.date(2026, 5, 15), datetime.date(2026, 5, 11),
            datetime.date(2026, 5, 18), datetime.date(2026, 5, 18), datetime.date(2026, 5, 18)
        ],
        "วันที่ออกผลล่าสุด": [
            datetime.date(2026, 5, 2), datetime.date(2026, 6, 1), datetime.date(2026, 6, 4),
            datetime.date(2026, 5, 12), datetime.date(2026, 5, 13), datetime.date(2026, 5, 14),
            datetime.date(2026, 5, 15), datetime.date(2026, 5, 11),
            datetime.date(2026, 5, 19), datetime.date(2026, 5, 19), datetime.date(2026, 6, 2)
        ],
        "Keep_Special": [None, "Consult/IHC", "Consult/IHC", None, None, None, None, None, None, "Consult/IHC", None],
        "หมายเหตุ/เหตุผล": ["เคสปกติ", "รอ Consult/IHC", "รอ Consult/IHC", "เคสปกติ", "เคสปกติ", "เคสปกติ", "เคสปกติ", "เคสปกติ", "เคสปกติ", "รอ Consult/IHC", "เคสปกติ"],
        "วันกำหนดทิ้งปรับปรุง": [None, None, None, None, None, None, None, None, None, None, None],
        "การทิ้งชิ้นเนื้อ": ["ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง", "ยังไม่ทิ้ง"],
        "วันที่กดทิ้ง": [None, None, None, None, None, None, None, None, None, None, None]
    }
    st.session_state.df_data = pd.DataFrame(data)

df = st.session_state.df_data
if len(df) == 11:

    new_row = {
        "Surgical No.": "S690013",
        "HN": "1234568",
        "ชื่อผู้ป่วย": "นายตัวอย่าง ผลยังไม่ออก",
        "แพทย์เจ้าของเคส": "VT",
        "วันที่รับเนื้อ": datetime.date(2026, 6, 4),
        "วันที่ออกผลล่าสุด": None,
        "Keep_Special": None,
        "หมายเหตุ/เหตุผล": "",
        "วันกำหนดทิ้งปรับปรุง": None,
        "การทิ้งชิ้นเนื้อ": "ยังไม่ทิ้ง",
        "วันที่กดทิ้ง": None
    }

    df = pd.concat(
        [df, pd.DataFrame([new_row])],
        ignore_index=True
    )

    st.session_state.df_data = df
# ==============================================================================
# 2. ฟังก์ชันคำนวณวันกำหนดทิ้งสุดท้าย และสถานะ
# ==============================================================================
def calculate_logic(row):

    if pd.isnull(row["วันที่ออกผลล่าสุด"]):
        return pd.Series(
            [None, "⚪ ผลยังไม่ออก"]
        )

    if pd.notnull(row["วันกำหนดทิ้งปรับปรุง"]):
        final_due = pd.to_datetime(
            row["วันกำหนดทิ้งปรับปรุง"]
        ).date()

    elif row["Keep_Special"] == "Consult/IHC":
        final_due = "-"

    else:
        final_due = (
            pd.to_datetime(row["วันที่ออกผลล่าสุด"]).date()
            + datetime.timedelta(days=15)
        )

    if row["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว":

        discard_date = row["วันที่กดทิ้ง"]

        if pd.notnull(discard_date):
            status = (
                f"⚫ ทิ้งแล้ว "
                f"({pd.to_datetime(discard_date).strftime('%d/%m/%Y')})"
            )
        else:
            status = "⚫ ทิ้งแล้ว"

    elif row["Keep_Special"] == "Consult/IHC":
        status = "🟡 รอผล Consult / IHC"

    elif isinstance(final_due, datetime.date):

        if final_due <= th_date:
            status = "🟢 ครบกำหนด (ทิ้งได้)"
        else:
            status = "🔵 ยังไม่ครบกำหนด"

    else:
        status = "🔵 ยังไม่ครบกำหนด"

    return pd.Series([final_due, status])

df[["กำหนดทิ้งสุดท้าย", "สถานะ"]] = df.apply(calculate_logic, axis=1)

# ส่วนหัวโปรแกรม
st.title("🔬 ระบบสรุปรายการทิ้ง Specimen ประจำวัน")
st.write(f"ประจำวันที่: {th_date.strftime('%d/%m/%Y')}")
st.markdown("---")

# ==============================================================================
# 3. ส่วนหลัก: ตารางค้นหาและจัดการเคส (ออกแบบใหม่ กะทัดรัดขึ้น)
# ==============================================================================
# จัด Layout หัวข้อตารางและช่องค้นหาให้อยู่บรรทัดเดียวกัน
header_col, search_col1, search_col2 = st.columns([2, 1.5, 1.5])

with header_col:
    st.subheader("📋 รายการสิ่งส่งตรวจทั้งหมด")

with search_col1:
    search_query = st.text_input("🔍 ค้นหา (SN/HN):", placeholder="พิมพ์เพื่อค้นหา...", label_visibility="collapsed")

with search_col2:
    date_range = st.date_input(
        "📅 ค้นหาวันที่รับเนื้อ:",
        value=None, # ค่าเริ่มต้นเป็นว่างเปล่า จะได้ไม่จำกัดวันที่ถ้าไม่ได้เลือก
        format="DD/MM/YYYY",
        label_visibility="collapsed"
    )

# ==============================================================================
# 3.1 เตรียมข้อมูล
# ==============================================================================

df["วันที่กดทิ้ง_temp"] = pd.to_datetime(
    df["วันที่กดทิ้ง"],
    errors="coerce"
)

mask_threw = (df["การทิ้งชิ้นเนื้อ"] == "ทิ้งแล้ว")

active_mask = ~mask_threw

discarded_today = (
    mask_threw &
    (df["วันที่กดทิ้ง_temp"].dt.date == th_date)
)

# ตารางปกติ (ไม่แสดงเคสที่ทิ้งไปแล้วหลายวัน)
normal_df = df[active_mask | discarded_today].copy()

# ใช้สำหรับค้นหา (ค้นได้ทุกเคส)
search_df = df.copy()

if "วันที่กดทิ้ง_temp" in normal_df.columns:
    normal_df.drop(columns=["วันที่กดทิ้ง_temp"], inplace=True)

if "วันที่กดทิ้ง_temp" in search_df.columns:
    search_df.drop(columns=["วันที่กดทิ้ง_temp"], inplace=True)

# ==============================================================================
# 3.2 กรองข้อมูลตามการค้นหา
# ==============================================================================

is_searching = False

mask_search = pd.Series(
    True,
    index=search_df.index
)

if search_query:

    is_searching = True

    mask_search = mask_search & (
        search_df["Surgical No."].astype(str).str.contains(
            search_query,
            case=False,
            na=False
        )
        |
        search_df["HN"].astype(str).str.contains(
            search_query,
            case=False,
            na=False
        )
    )

if date_range:

    is_searching = True

    if isinstance(date_range, tuple) and len(date_range) == 2:

        start_date, end_date = date_range

        mask_search = mask_search & (
            (search_df["วันที่รับเนื้อ"] >= start_date)
            &
            (search_df["วันที่รับเนื้อ"] <= end_date)
        )

    else:

        mask_search = mask_search & (
            search_df["วันที่รับเนื้อ"] == date_range
        )

# ถ้ามีการค้นหา → ใช้ผลค้นหา
# ถ้าไม่ได้ค้นหา → ใช้รายการปกติ

if is_searching:
    filtered_df = search_df[mask_search].copy()
else:
    filtered_df = normal_df.copy()

# ==============================================================================
# 3.3 แสดงผลตารางหลัก
# ==============================================================================

display_cols = [
    "Surgical No.",
    "HN",
    "ชื่อผู้ป่วย",
    "แพทย์เจ้าของเคส",
    "วันที่รับเนื้อ",
    "วันที่ออกผลล่าสุด",
    "กำหนดทิ้งสุดท้าย",
    "สถานะ",
    "หมายเหตุ/เหตุผล"
]

display_df = filtered_df[
    [c for c in display_cols if c in filtered_df.columns]
].copy()

if "วันที่รับเนื้อ" in display_df.columns:
    display_df["วันที่รับเนื้อ"] = display_df["วันที่รับเนื้อ"].apply(
        lambda x: x.strftime('%d/%m/%Y')
        if isinstance(x, (datetime.date, pd.Timestamp))
        else "-"
    )

if "วันที่ออกผลล่าสุด" in display_df.columns:
    display_df["วันที่ออกผลล่าสุด"] = display_df["วันที่ออกผลล่าสุด"].apply(
        lambda x: x.strftime('%d/%m/%Y')
        if isinstance(x, (datetime.date, pd.Timestamp))
        else "-"
    )

def format_due_date_df(row):

    if row.get("Keep_Special") == "Consult/IHC":
        return "ยังไม่มีกำหนด"

    val = row.get("กำหนดทิ้งสุดท้าย")

    return (
        val.strftime('%d/%m/%Y')
        if isinstance(val, (datetime.date, pd.Timestamp))
        else "-"
    )

if "กำหนดทิ้งสุดท้าย" in display_df.columns:
    display_df["กำหนดทิ้งสุดท้าย"] = filtered_df.apply(
        format_due_date_df,
        axis=1
    )

display_df.index = range(1, len(display_df) + 1)

st.dataframe(
    display_df,
    use_container_width=True
)
#    3.4 ส่วนจัดการเคสเมื่อมีการค้นหา (แบบปุ่มตรง ไม่ใช้ Expander)

if is_searching and len(filtered_df) == 1:

    st.markdown("---")

    idx = filtered_df.index[0]
    row = filtered_df.iloc[0]

    st.success(
        f"พบเคส: {row['Surgical No.']} | "
        f"{row['ชื่อผู้ป่วย']} | "
        f"{row['สถานะ']}"
    )

    if row["การทิ้งชิ้นเนื้อ"] != "ทิ้งแล้ว":

        col1, col2 = st.columns(2)

        is_consult = (row["Keep_Special"] == "Consult/IHC")

        with col1:

            if not is_consult:

                if st.button(
                    "🟡 Consult / IHC",
                    key=f"consult_{idx}",
                    use_container_width=True
                ):
                    df.loc[idx, [
                        "Keep_Special",
                        "หมายเหตุ/เหตุผล",
                        "การทิ้งชิ้นเนื้อ",
                        "วันที่กดทิ้ง"
                    ]] = [
                        "Consult/IHC",
                        "รอ Consult/IHC",
                        "ยังไม่ทิ้ง",
                        None
                    ]

                    st.session_state.df_data = df
                    st.rerun()

            else:

                if st.button(
                    "🟢 Final เคสนี้",
                    key=f"final_{idx}",
                    use_container_width=True
                ):
                    df.loc[idx, [
                        "Keep_Special",
                        "หมายเหตุ/เหตุผล",
                        "วันที่ออกผลล่าสุด",
                        "วันกำหนดทิ้งปรับปรุง",
                        "การทิ้งชิ้นเนื้อ",
                        "วันที่กดทิ้ง"
                    ]] = [
                        None,
                        "Finalแล้ว หลัง Consult/IHC",
                        th_date,
                        th_date + datetime.timedelta(days=15),
                        "ยังไม่ทิ้ง",
                        None
                    ]

                    st.session_state.df_data = df
                    st.rerun()

        with col2:

            if st.button(
                "🔵 ผลเพิ่มเติม (+15 วัน)",
                key=f"extend_{idx}",
                use_container_width=True
            ):
                df.loc[idx, [
                    "Keep_Special",
                    "หมายเหตุ/เหตุผล",
                    "วันที่ออกผลล่าสุด",
                    "วันกำหนดทิ้งปรับปรุง",
                    "การทิ้งชิ้นเนื้อ",
                    "วันที่กดทิ้ง"
                ]] = [
                    None,
                    "ออกผลเพิ่มเติมแล้ว",
                    th_date,
                    th_date + datetime.timedelta(days=15),
                    "ยังไม่ทิ้ง",
                    None
                ]

                st.session_state.df_data = df
                st.rerun()

st.markdown("---")

# ==============================================================================
# 4. สิ่งส่งตรวจที่ต้องทิ้งวันนี้ (คงการทำงานเดิมไว้)
# ==============================================================================
st.subheader("🗑️ สิ่งส่งตรวจที่ต้องทิ้งวันนี้")

pending_discard_all = filtered_df[filtered_df["สถานะ"] == "🟢 ครบกำหนด (ทิ้งได้)"].copy()
if not pending_discard_all.empty:

    pending_discard = pending_discard_all.copy()   
    if not pending_discard.empty:
        display_discard = pending_discard.copy()
        
        display_discard["วันที่รับเนื้อ"] = pending_discard["วันที่รับเนื้อ"].apply(lambda x: x.strftime('%d/%m/%Y') if isinstance(x, (datetime.date, pd.Timestamp)) else "-")
        display_discard["กำหนดทิ้งสุดท้าย"] = pending_discard.apply(format_due_date_df, axis=1)

        if "all_selected" not in st.session_state: 
            st.session_state.all_selected = False
            
        if st.checkbox("📋 เลือกทั้งหมดที่แสดง", key="select_all_btn"):
            st.session_state.all_selected = True
        else:
            st.session_state.all_selected = False

        display_discard["เลือก"] = st.session_state.all_selected
        
        discard_cols = ["เลือก", "Surgical No.", "HN", "ชื่อผู้ป่วย", "วันที่รับเนื้อ", "กำหนดทิ้งสุดท้าย"]
        active_discard_cols = [c for c in discard_cols if c in display_discard.columns]
        
        config_dict = {
            "เลือก": st.column_config.CheckboxColumn("เลือกทิ้ง", default=False),
            "Surgical No.": st.column_config.TextColumn("Surgical No.", disabled=True),
            "HN": st.column_config.TextColumn("HN", disabled=True),
            "ชื่อผู้ป่วย": st.column_config.TextColumn("ชื่อผู้ป่วย", disabled=True),
            "วันที่รับเนื้อ": st.column_config.TextColumn("วันที่รับเนื้อ", disabled=True),
            "กำหนดทิ้งสุดท้าย": st.column_config.TextColumn("กำหนดทิ้ง", disabled=True),
        }
        
        edited_df = st.data_editor(
            display_discard[active_discard_cols],
            column_config={k: v for k, v in config_dict.items() if k in active_discard_cols},
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("🗑️ ยืนยันการทิ้งเคสที่เลือก", type="primary"):
            selected_cases = edited_df[edited_df["เลือก"] == True]
            if not selected_cases.empty:
                df.loc[df["Surgical No."].isin(selected_cases["Surgical No."]), ["การทิ้งชิ้นเนื้อ", "วันที่กดทิ้ง"]] = ["ทิ้งแล้ว", pd.Timestamp(th_date)]
                st.session_state.df_data = df
                st.success(f"ทิ้งเรียบร้อยแล้ว {len(selected_cases)} เคส")
                st.rerun()
            else:
                st.warning("กรุณาเลือกเคสที่ต้องการทิ้งก่อน")
    else:
        st.info("ไม่มีรายการทิ้งที่ตรงกับช่วงวันที่ หรือเงื่อนไขที่คุณหมอค้นหาครับ")
else:
    st.info("วันนี้ไม่มีรายการที่ต้องทิ้ง")