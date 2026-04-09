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

# [2. 구글 시트 연결 및 공지사항 로드]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_sheets():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key("1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc")
        data_sheet = spreadsheet.get_worksheet(0)
        return data_sheet, data_sheet
    except:
        return None, None

data_sheet, settings_sheet = get_sheets()

def load_notice():
    try:
        val = settings_sheet.acell('Z1').value 
        return val if val else "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거"
    except:
        return "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거"

# [3. 세션 상태 초기화]
if "page" not in st.session_state:
    st.session_state.page = "main"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "safety_notice" not in st.session_state:
    st.session_state.safety_notice = load_notice()

# [4. 스타일 디자인 - 버튼 자체를 중앙으로 이동]
st.markdown("""
    <style>
        /* 기본 레이아웃 설정 */
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .stApp { background-color: #F0F8FF; }
        
        /* 메인 헤더 (상단 파란색 박스) */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.8rem 0.5rem; 
            border-radius: 0 0 30px 30px; 
            text-align: center; 
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .header-top { display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 5px; }
        .header-emoji { font-size: 2.8rem !important; }
        .header-tbm { color: white !important; font-size: 3rem !important; font-weight: 900 !important; margin: 0; }
        .header-sub-box { display: inline-block; background-color: rgba(255, 255, 255, 0.15); padding: 5px 20px; border-radius: 50px; border: 1px solid rgba(255, 255, 255, 0.3); margin-top: 5px; }
        .header-sub-text { color: #FFFFFF !important; font-size: 1.2rem !important; font-weight: 500 !important; margin: 0; letter-spacing: 1px; }
        
        /* 핵심: 버튼 자체를 화면 가운데로 배치 */
        div.stButton {
            display: flex !important;
            justify-content: center !important; /* 가로 중앙 정렬 */
            width: 100% !important;
            margin: 0 auto !important;
        }
        
        div.stButton > button { 
            width: 85% !important; /* 버튼 너비 설정 */
            max-width: 350px !important; 
            min-height: 4.8rem;
            border-radius: 18px; 
            font-weight: 700; 
            font-size: 1.15rem !important;
            border: 2.5px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: 0.2s;
            display: block !important;
            margin: 10px 0 !important; /* 위아래 간격 */
        }

        div.stButton > button:hover {
            background-color: #1E3A8A !important;
            color: white !important;
            transform: translateY(-2px);
        }
        
        /* 공지사항 박스 중앙 배치 */
        .center-wrapper {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 18px; 
            border-radius: 12px; 
            margin-bottom: 25px;
            width: 85%;
            max-width: 350px;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# [5. 메인 화면 로직]
if st.session_state.page == "main":
    st.markdown('''
        <div class="main-header">
            <div class="header-top">
                <span class="header-emoji">⛑️</span>
                <span class="header-tbm">TBM</span>
            </div>
            <div class="header-sub-box">
                <p class="header-sub-text">안전점검 시스템</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # 공지사항 중앙 배치
    current_notice = load_notice()
    display_text = current_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="center-wrapper">
            <div class="notice-box">
                <b style="color:#1E3A8A;">📢 금일 안전 지시사항</b><br>
                <p style="margin-top: 8px; color: #1E3A8A;">{display_text}</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # 버튼 섹션 (CSS에서 정중앙 정렬 강제함)
    st.button("📝 금일 TBM 점검 작성", on_click=lambda: setattr(st.session_state, 'page', 'tbm_write'))
    st.button("📊 실시간 점검 현황 확인", on_click=lambda: setattr(st.session_state, 'page', 'tbm_status'))
    st.button("⚙️ 시스템 관리자 페이지", on_click=lambda: setattr(st.session_state, 'page', 'tbm_admin'))

# --- 페이지 이동 로직 (간소화) ---
elif st.session_state.page == "tbm_write":
    st.button("⬅️ 메인으로", on_click=lambda: setattr(st.session_state, 'page', 'main'))
    st.subheader("🏗️ TBM 점검 작성")
    # ... (기존 입력 폼 코드) ...

elif st.session_state.page == "tbm_status":
    st.button("⬅️ 메인으로", on_click=lambda: setattr(st.session_state, 'page', 'main'))
    st.subheader("📊 실시간 점검 현황")
    # ... (기존 데이터 시트 코드) ...

elif st.session_state.page == "tbm_admin":
    st.button("⬅️ 메인으로", on_click=lambda: setattr(st.session_state, 'page', 'main'))
    # ... (기존 관리자 로그인 코드) ...
