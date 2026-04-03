import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# 1. App Configuration & Icon (Cache busting v15)
icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png?v=15"

try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(
    page_title="TBM 스마트 체크리스트",
    page_icon=img,
    layout="centered"
)

# [UI Design: Remove header, menu, and footer for a native app feel]
st.markdown(f"""
    <style>
        header {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        
        .st-emotion-cache-16471hc {{display: none !important;}}
        .st-emotion-cache-ch5vc {{display: none !important;}}

        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }}
        
        .stButton>button {{
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
            border: none;
        }}
    </style>
    <head>
        <link rel="apple-touch-icon" href="{icon_url}">
        <link rel="icon" type="image/png" href="{icon_url}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    </head>
""", unsafe_allow_html=True)

# 2. Google Sheets Authentication
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet_id = "1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc"
        return client.open_by_key(sheet_id).get_worksheet(0)
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None

# Checklist items
checklist_items = ["개인보호구 착용 상태 확인", "작업 전 위험요인 파악 및 공유", "사용 장비 점검 완료"]

sheet = get_sheet()

if sheet:
    tab1, tab2 = st.tabs(["📝 TBM 점검", "📊 현황판"])

    with tab1:
        try:
            st.image("safety_mascot.png", width=70)
        except:
            pass

        st.subheader("🏗️ 안전 점검 일지")
        
        # --- [REFACTORED: Manual Input Section] ---
        col1, col2 = st.columns(2)
        with col1:
            # Replaced selectbox with text_input
            input_team = st.text_input("소속 부서", placeholder="예: 운영, 정비 등")
        with col2:
            # Replaced selectbox with text_input
            input_name = st.text_input("성함", placeholder="이름 입력")

        st.markdown("---")
        
        # Checklist logic
        check_results = []
        for i, item in enumerate(checklist_items):
            res = st.checkbox(f" {item}", key=f"q_{i}")
            check_results.append(res)

        status = "정상" if all(check_results) else "조치 필요"
        remark = st.text_area("특이사항 (비고)", placeholder="내용을 입력하세요.", key="remark")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color="#000000",
            background_color="#f0f2f6", height=150, width=330, drawing_mode="freedraw", key="canvas_main",
        )

        if st.button("점검 완료 및 저장"):
            # Validation: Ensure names are not empty
            if not input_team or not input_name:
                st.warning("⚠️ 소속 부서와 성함을 모두 입력해 주세요.")
            elif canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명을 완료해야 저장할 수 있습니다.")
            else:
                now_time = datetime.datetime.now().strftime('%H:%M:%S')
                today_date = datetime.date.today().isoformat()
                new_row = [today_date, input_team, input_name, status, now_time, remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success(f"🎉 {input_name}님, 저장 완료!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    with tab2:
        st.subheader("📊 오늘 점검 현황")
        try:
            records = sheet.get_all_records()
            if records:
                df = pd.DataFrame(records)
                today_str = datetime.date.today().isoformat()
                if '날짜' in df.columns:
                    today_df = df[df['날짜'] == today_str]
                    st.metric("오늘 완료", f"{len(today_df)}명")
                    st.dataframe(today_df.tail(10), use_container_width=True)
        except:
            st.info("기록을 불러올 수 없습니다.")
