import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# 1. 앱 설정 및 아이콘 (v15 유지)
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

# [UI 디자인 스타일 유지]
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
""", unsafe_allow_html=True)

# 2. 구글 시트 인증 및 연결
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

# --- [부서 목록만 유지] ---
teams = [
    "선택하세요", "운영", "기술", "입출창", "중요장치장", "전기/제동장", "전기", "판토", "제동", 
    "정비", "차체/수선장", "출입문", "차체", "냉방장치", "회전기장", "TM", "CM", 
    "대차장", "댐퍼/에어스프링", "기초제동1", "기초제동2", "윤축/축상장", "윤축", "축상", "차륜", "탐상"
]

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
        
        # --- [수정: 부서는 선택, 이름은 입력] ---
        col1, col2 = st.columns(2)
        with col1:
            selected_team = st.selectbox("소속 부서", teams)
        with col2:
            input_name = st.text_input("성함", placeholder="이름 입력")

        st.markdown("---")
        
        # 체크리스트 생성
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
            # 유효성 검사 (부서 미선택 또는 이름 미입력)
            if selected_team == "선택하세요" or not input_name:
                st.warning("⚠️ 부서를 선택하고 성함을 입력해 주세요.")
            elif canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명을 완료해야 저장할 수 있습니다.")
            else:
                now_time = datetime.datetime.now().strftime('%H:%M:%S')
                today_date = datetime.date.today().isoformat()
                new_row = [today_date, selected_team, input_name, status, now_time, remark, "서명완료"]
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
