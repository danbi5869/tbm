import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
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
    st.session_state.safety_notice = "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거\n3. 상호 안전 확인 후 작업 개시"

# [3. 구글 시트 연결] (기존 로직 동일)
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
@st.cache_resource
def get_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc").get_worksheet(0)
    except:
        return None

sheet = get_sheet()

# [4. 스타일 디자인 - 글자 크기에 딱 맞는 버튼 & 중앙 정렬]
st.markdown("""
    <style>
        .stApp { background-color: #F0F8FF; }
        header { visibility: hidden !important; }
        
        /* 헤더 제목: 무조건 1줄 & 중앙 */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.2rem 0.5rem; 
            border-radius: 0 0 20px 20px; 
            margin-bottom: 2rem; 
            text-align: center;
        }
        .main-header h1 { 
            color: white !important; 
            font-size: clamp(1rem, 5vw, 2.2rem) !important; 
            margin: 0; 
            white-space: nowrap !important;
            letter-spacing: -1px;
        }

        /* 중앙 정렬 컨테이너 */
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        /* 공지 박스: 버튼과 너비 통일 */
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 15px 20px; 
            border-radius: 12px; 
            color: #1E3A8A; 
            font-size: 16px; 
            text-align: left;
            margin-bottom: 20px;
            width: 95%; 
            max-width: 400px; /* 버튼 박스가 넉넉하도록 너비 상향 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* 버튼 스타일: 글자를 충분히 감싸는 넉넉한 크기 */
        div.stButton {
            display: flex;
            justify-content: center;
            width: 100% !important;
        }
        
        div.stButton > button { 
            width: 95% !important; 
            max-width: 400px !important; /* 공지 박스와 동일 */
            min-height: 4.5rem; /* 높이 확보 */
            border-radius: 12px; 
            /* 글자 크기를 버튼 박스에 딱 맞게 조절 */
            font-size: clamp(14px, 4vw, 18px) !important; 
            font-weight: 700 !important; 
            margin: 8px 0 !important;
            border: 2.5px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A !important;
            white-space: nowrap !important; /* 글자 1줄 고정 */
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 0 10px !important;
        }
        
        div.stButton > button:hover { background-color: #1E3A8A !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# [5. 메인 화면 로직]
if st.session_state.page == "main":
    # 제목 1줄
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    
    # 전체 중앙 정렬 컨테이너 시작
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 1. 공지사항
    display_text = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-box">
            <b style="font-size: 1.1rem;">📢 금일 안전 지시사항</b><br>{display_text}
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. 버튼들 (박스 크기를 글자에 맞춰 넉넉하게 설정)
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
        
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()
        
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # 컨테이너 끝

# [나머지 페이지 로직 생략 - 기존과 동일]
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("🏗️ TBM 점검 작성")
    # ... 후략
