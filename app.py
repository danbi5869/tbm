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

# [4. 스타일 디자인 - 모든 글씨 1줄 고정]
st.markdown("""
    <style>
        .stApp { background-color: #F0F8FF; }
        header { visibility: hidden !important; }
        
        /* 헤더 제목 1줄 */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1rem 0.2rem; 
            border-radius: 0 0 15px 15px; 
            margin-bottom: 1.5rem; 
            text-align: center;
        }
        .main-header h1 { 
            color: white !important; 
            font-size: clamp(1rem, 4.2vw, 1.8rem) !important; 
            margin: 0; 
            white-space: nowrap; 
            letter-spacing: -1.2px;
        }
        
        /* 버튼 컨테이너 간격 조절 */
        div[data-testid="stHorizontalBlock"] {
            gap: 4px !important;
        }

        /* [핵심] 버튼 글씨 1줄 고정 및 크기 조절 */
        div.stButton > button { 
            width: 100% !important; 
            border-radius: 8px; 
            height: 3.8rem; 
            font-size: clamp(11px, 2.8vw, 15px) !important; /* 모바일 대응 작은 폰트 */
            font-weight: 800 !important; 
            padding: 0px 2px !important;
            border: 2px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A !important;
            white-space: nowrap !important; /* 무조건 1줄 */
            letter-spacing: -0.8px; /* 글자 사이를 좁힘 */
            overflow: hidden;
        }
        
        div.stButton > button:hover { background-color: #1E3A8A !important; color: white !important; }

        /* 공지사항 박스 */
        .notice-container {
            display: flex;
            justify-content: center;
            width: 100%;
            margin-bottom: 15px;
        }
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 12px; 
            border-radius: 10px; 
            color: #1E3A8A; 
            font-size: 14px; 
            width: 98%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# [5. 메인 화면 로직]
if st.session_state.page == "main":
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    
    # 1. 공지사항
    display_text = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-container">
            <div class="notice-box">
                <b style="font-size: 15px;">📢 금일 안전 지시사항</b><br>{display_text}
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. 버튼 세 개 가로 배치 (글씨 1줄 유지)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 점검 작성"):
            st.session_state.page = "tbm_write"; st.rerun()
            
    with col2:
        if st.button("📊 현황 확인"):
            st.session_state.page = "tbm_status"; st.rerun()
            
    with col3:
        if st.button("⚙️ 관리자"):
            st.session_state.page = "tbm_admin"; st.rerun()

# [페이지 전환 로직 동일]
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("🏗️ TBM 점검 작성")
    # ... 후략
