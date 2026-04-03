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
    st.session_state.safety_notice = "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거\n3. 상호 안전 확인 후 작업 개시"

# [3. 기존 데이터 유지]
team_data = {
    "운영": ["김한규", "김병배", "엄기태", "한효석", "신기영", "한진희", "노단비", "박진용"],
    "기술": ["황종연"], "입출창": ["이천형", "전동길", "허유정", "서대영"],
    "중요장치장": ["송진수", "임대권", "이준혁", "김명철"], "전기/제동장": ["손해진", "주승용"],
    "전기": ["이경민", "금창욱", "권혁진", "임의진", "박태규"], "판토": ["유문일", "이현우"],
    "제동": ["오성윤", "허성우", "김원경", "전창근", "서준영", "이진호"], "정비": ["김성태", "배욱"],
    "차체/수선장": ["최덕수", "반상민"], "출입문": ["김지훈", "추동일", "한지훈", "백승주", "최창열", "윤성현"],
    "차체": ["박노갑", "박종환", "최규현"], "냉방장치": ["김정혁", "김기훈", "설태길"],
    "회전기장": ["박기하", "이성보"], "TM": ["박석희", "오현택", "유상훈"],
    "CM": ["안상복", "김태경"], "대차장": ["임청용", "정호영"],
    "댐퍼/에어스프링": ["정성목", "이태수"], "기초제동1": ["우원진", "연제동", "이창록"],
    "기초제동2": ["김영일", "정진영", "허재혁"], "윤축/축상장": ["김성수", "이성문"],
    "윤축": ["정승욱", "나용환", "박주현"], "축상": ["박상언", "윤종혁", "방건동", "박준수"],
    "차륜": ["지민석", "곽동영", "안형륜", "이동호"], "탐상": ["박윤찬", "이동호"]
}

# [4. 구글 시트 연결]
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

# [5. 스타일 디자인 - 정중앙 정렬 완성형 CSS]
st.markdown("""
    <style>
        /* 배경 및 기본 레이아웃 */
        .stApp { background-color: #F0F8FF; }
        header { visibility: hidden !important; }
        .main-header { background-color: #1E3A8A; padding: 1.5rem 0; border-radius: 0 0 20px 20px; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .main-header h1 { color: white !important; text-align: center; font-size: 2rem; margin: 0; }
        
        /* 1. 버튼 컨테이너 강제 중앙 정렬 */
        div.stButton {
            display: flex;
            justify-content: center;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* 2. 버튼 개별 디자인 (너비 고정 및 중앙 고정) */
        .stButton>button { 
            width: 90% !important; 
            max-width: 380px; /* 공지 박스 너비와 일치시킴 */
            border-radius: 12px; 
            height: 4.8rem; 
            font-size: 19px !important; 
            font-weight: 700 !important; 
            margin: 8px 0 !important; /* 위아래 간격 */
            transition: 0.2s;
            background-color: #ffffff; 
            border: 2.5px solid #1E3A8A; 
            color: #1E3A8A !important;
        }
        
        .stButton>button:hover { 
            background-color: #1E3A8A !important; 
            color: white !important; 
        }

        /* 3. 공지사항 박스 (글자 길이에 맞게 + 중앙 정렬) */
        .notice-wrapper {
            display: flex;
            justify-content: center;
            width: 100%;
            margin-bottom: 25px;
        }
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 15px 25px; 
            border-radius: 10px; 
            color: #1E3A8A; 
            font-size: 17px; 
            display: inline-block; 
            text-align: left;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            max-width: 90%;
            min-width: 300px;
        }

        /* 기타 특수 버튼들 */
        div.stButton > button:has(div:contains("메인으로")) { max-width: 150px; height: 2.5rem; background-color: #E2E8F0 !important; color: #475569 !important; border: none !important; }
        div.stButton > button:has(div:contains("저장하기")) { max-width: 380px; background-color: #DC2626 !important; color: white !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# [6. 화면 전환 로직]

if st.session_state.page == "main":
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    
    # 공지사항
    display_text = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-wrapper">
            <div class="notice-box">
                <b>📢 금일 안전 지시사항</b><br>{display_text}
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # 버튼들 (이제 columns 없이도 CSS가 중앙으로 밀어넣습니다)
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
        
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()
        
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"; st.rerun()

# 📝 점검 작성 페이지 (기존 로직 유지)
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("🏗️ TBM 점검 작성")
    # ... (이하 작성 페이지 코드는 동일하므로 생략하거나 기존 코드 붙여넣기)
