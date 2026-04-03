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

# [3. 구글 시트 연결]
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

# [4. 스타일 디자인 - 모바일 1줄 제목 및 수직 정렬 최적화]
st.markdown("""
    <style>
        .stApp { background-color: #F0F8FF; }
        header { visibility: hidden !important; }
        
        /* 헤더: 제목 1줄 유지 및 크기 자동 조절 */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.2rem 0.5rem; 
            border-radius: 0 0 15px 15px; 
            margin-bottom: 1.5rem; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .main-header h1 { 
            color: white !important; 
            font-size: clamp(1.2rem, 5vw, 2.2rem) !important; /* 최소 1.2rem, 화면의 5%, 최대 2.2rem */
            margin: 0; 
            white-space: nowrap; /* 줄바꿈 방지 */
            overflow: hidden;
            text-overflow: ellipsis;
            letter-spacing: -1px; /* 글자 간격 살짝 좁힘 */
        }
        
        /* 중앙 정렬용 컨테이너 */
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        /* 공지 박스: 버튼 너비와 일치시킴 */
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 18px; 
            border-radius: 10px; 
            color: #1E3A8A; 
            font-size: 16px; 
            text-align: left;
            margin-bottom: 15px;
            width: 90%; /* 모바일 대응 */
            max-width: 350px; /* 버튼과 너비 통일 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            line-height: 1.5;
        }

        /* 버튼 스타일: 공지 박스 너비와 정확히 일치 */
        div.stButton {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        
        div.stButton > button { 
            width: 90% !important; 
            max-width: 350px !important; 
            border-radius: 12px; 
            height: 4.5rem; 
            font-size: 18px !important; 
            font-weight: 700 !important; 
            margin-bottom: 12px !important;
            border: 2.5px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A !important;
            transition: 0.2s;
        }
        
        div.stButton > button:hover { background-color: #1E3A8A !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# [5. 메인 화면 로직]
if st.session_state.page == "main":
    # 제목 부분 (1줄 고정)
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    
    # 전체 중앙 정렬 시작
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 1. 공지사항 (중앙 정렬 및 너비 고정)
    display_text = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-box">
            <b style="font-size: 1.1rem;">📢 금일 안전 지시사항</b><br><br>{display_text}
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. 버튼들 (공지 박스 바로 밑으로 수직 정렬)
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
        
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()
        
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True) # 컨테이너 끝

# [기타 페이지 로직은 기존 소스코드와 동일하게 유지]
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("🏗️ TBM 점검 작성")
    # ... 후략 ...
