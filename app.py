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

# [3. 구글 시트 연결] (기존 로직 유지)
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

# [4. 스타일 디자인 - 제목 1줄 & 박스/버튼 크기 통일]
st.markdown("""
    <style>
        .stApp { background-color: #F0F8FF; }
        header { visibility: hidden !important; }
        
        /* 1. 헤더 제목: 1줄 고정 및 반응형 크기 */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.2rem 0.5rem; 
            border-radius: 0 0 20px 20px; 
            margin-bottom: 2rem; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .main-header h1 { 
            color: white !important; 
            /* 화면 너비에 따라 1.1rem에서 2.2rem 사이로 자동 조절 */
            font-size: clamp(1.1rem, 5.5vw, 2.2rem) !important; 
            margin: 0; 
            white-space: nowrap !important; /* 강제 1줄 */
            letter-spacing: -1px;
        }

        /* 2. 중앙 정렬 컨테이너 */
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        /* 3. 공지 박스와 버튼 크기 동일 설정 (380px) */
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 18px 25px; 
            border-radius: 12px; 
            color: #1E3A8A; 
            font-size: 16px; 
            text-align: left;
            margin-bottom: 15px;
            width: 90%; 
            max-width: 380px; /* 버튼과 동일한 최대 너비 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* 4. 모든 버튼 스타일 통일 */
        div.stButton {
            display: flex;
            justify-content: center;
            width: 100% !important;
        }
        
        div.stButton > button { 
            width: 90% !important; 
            max-width: 380px !important; /* 공지 박스와 동일한 너비 */
            border-radius: 12px; 
            height: 4.5rem; 
            font-size: clamp(15px, 4vw, 19px) !important; /* 글자 1줄 유지용 크기 조절 */
            font-weight: 700 !important; 
            margin: 8px 0 !important;
            border: 2.5px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A !important;
            white-space: nowrap !important; /* 버튼 글씨 1줄 고정 */
        }
        
        div.stButton > button:hover { background-color: #1E3A8A !important; color: white !important; }
        
        /* 메인 페이지 전용 버튼 (가독성 보정) */
        div.stButton > button p { margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# [5. 메인 화면 로직]
if st.session_state.page == "main":
    # 제목 1줄 유지
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    
    # 전체 중앙 정렬 시작
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 1. 공지사항 (버튼과 같은 크기)
    display_text = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-box">
            <b>📢 금일 안전 지시사항</b><br>{display_text}
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. 버튼들 (공지 박스와 크기 똑같이 세로로 나열)
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
        
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()
        
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# [6. 나머지 페이지 로직] (기존 코드와 동일하게 유지하되 스타일 영향만 받음)
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("🏗️ TBM 점검 작성")
    # ... (생략된 기존 작업 내용 로직)
