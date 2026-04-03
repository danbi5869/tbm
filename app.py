import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import time
from datetime import timezone, timedelta

# [1. 앱 기본 설정]
try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

# [2. 세션 상태 초기화]
if "page" not in st.session_state:
    st.session_state.page = "main"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "safety_notice" not in st.session_state:
    st.session_state.safety_notice = "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거"

# [3. 데이터 설정]
team_data = {"운영": ["김한규", "노단비"], "기술": ["황종연"], "입출창": ["이천형"]} # (중략)

# [4. 구글 시트 연결]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
@st.cache_resource
def get_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc").get_worksheet(0)
    except: return None
sheet = get_sheet()

# [5. 스타일 디자인 - 모바일 한 줄 고정 및 스크롤 제거]
st.markdown("""
    <style>
        .stApp { background-color: #F0F8FF; }
        header { visibility: hidden !important; }

        /* [핵심] 상단 버튼 모바일 한 줄 강제 고정 */
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important; /* 줄바꿈 절대 금지 */
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 5px !important;
        }
        
        div[data-testid="column"] {
            width: fit-content !important;
            flex: unset !important;
            min-width: unset !important;
        }

        /* 버튼 디자인 축소 */
        .stButton>button {
            height: 2.2rem !important;
            padding: 0 10px !important;
            font-size: 13px !important;
            white-space: nowrap !important;
            border-radius: 8px !important;
        }

        /* 표 가로 스크롤 방지 및 글자 축소 */
        .stDataFrame div[data-testid="stTable"] {
            font-size: 11px !important;
        }
        
        /* 입력창 간격 조절 */
        .stSelectbox, .stTextInput { margin-top: -15px; }
    </style>
""", unsafe_allow_html=True)

# [6. 화면 전환 로직]
if st.session_state.page == "main":
    st.markdown('<h2 style="text-align:center; color:#1E3A8A;">⛑️ TBM 시스템</h2>', unsafe_allow_html=True)
    if st.button("📝 점검 작성", use_container_width=True):
        st.session_state.page = "tbm_write"; st.rerun()
    if st.button("📊 현황 확인", use_container_width=True):
        st.session_state.page = "tbm_status"; st.rerun()

# 📝 점검 작성 페이지
elif st.session_state.page == "tbm_write":
    # --- 상단 버튼 영역 (한 줄 고정) ---
    col_nav = st.columns([1, 1, 1]) 
    with col_nav[0]:
        if st.button("⬅️ 메인"):
            st.session_state.page = "main"; st.rerun()
    with col_nav[1]:
        if st.button("📊 현황"):
            st.session_state.page = "tbm_status"; st.rerun()
            
    st.divider()
    
    # 입력부
    c1, c2 = st.columns(2)
    with c1: selected_team = st.selectbox("부서", list(team_data.keys()))
    with c2: final_name = st.text_input("성함", placeholder="이름")

    selected_job = st.selectbox("작업명", ["공통작업", "분해", "중량물", "전기", "세척"])

    # 점검표 (가로 너비 최적화)
    st.write("**✅ 점검항목**")
    col_config = {
        "항목": st.column_config.TextColumn("항목", width=50),
        "내용": st.column_config.TextColumn("내용", width=180),
        "V": st.column_config.CheckboxColumn("V", width=30)
    }
    df_data = pd.DataFrame([
        {"항목": "보호구", "내용": "안전모/장갑 착용", "V": False},
        {"항목": "LOTO", "내용": "전원 차단 확인", "V": False},
        {"항목": "정리", "내용": "작업장 통로 확보", "V": False}
    ])
    st.data_editor(df_data, hide_index=True, use_container_width=True, column_config=col_config, height=150)

    # 서명
    st.write("**✒️ 서명**")
    st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=80, width=300, key="canvas_tbm")

    if st.button("✅ 점검 저장", use_container_width=True):
        st.success("저장되었습니다!")
        st.session_state.page = "main"; time.sleep(1); st.rerun()

# 📊 현황 확인 페이지
elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.write("### 📊 현황")
    # (현황 확인 로직 생략)
