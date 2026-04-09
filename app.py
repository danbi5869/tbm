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

# [2. 구글 시트 연결]
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

# [4. 스타일 디자인 - 너비 400px 일치 핵심]
st.markdown("""
    <style>
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .stApp { background-color: #F0F8FF; }
        
        /* 메인 헤더 박스 */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.8rem 0.5rem; 
            border-radius: 0 0 30px 30px; 
            text-align: center; 
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .header-tbm { color: white !important; font-size: 3rem !important; font-weight: 900 !important; margin: 0; }
        .header-sub-text { color: #FFFFFF !important; font-size: 1.3rem !important; margin: 0; letter-spacing: 2px; }

        /* 공지사항 박스와 버튼 너비 동일화 (400px 고정) */
        .unified-box {
            width: 100% !important;
            max-width: 400px !important;
            box-sizing: border-box !important;
            margin: 0 auto 15px auto !important;
        }

        .notice-box { 
            background-color: #DBEAFE; 
            border: 2px solid #1E3A8A; 
            padding: 15px; 
            border-radius: 12px; 
            text-align: left;
        }

        /* 버튼 스타일 강제 고정 */
        div.stButton > button { 
            width: 100% !important;
            max-width: 400px !important;
            min-height: 4.5rem;
            border-radius: 15px; 
            font-weight: 700; 
            font-size: 1.1rem !important;
            border: 2px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            display: block !important;
            margin: 0 auto !important;
        }
        div.stButton > button:hover {
            background-color: #1E3A8A !important;
            color: white !important;
        }

        /* 중앙 정렬 */
        .center-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# 팀 데이터
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

# [5. 메인 화면 로직]
if st.session_state.page == "main":
    st.markdown('''
        <div class="main-header">
            <h1 class="header-tbm">⛑️ TBM</h1>
            <p class="header-sub-text">안전점검 시스템</p>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="center-container">', unsafe_allow_html=True)
    
    # 1. 공지사항 박스 (unified-box 클래스로 너비 400px 고정)
    current_notice = load_notice()
    display_text = current_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-box unified-box">
            <b>📢 금일 안전 지시사항</b><br>{display_text}
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. 버튼 (CSS에서 width 100%, max-width 400px로 일치됨)
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"
        st.rerun()
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"
        st.rerun()
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# [6. 작성 페이지]
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    st.subheader("🏗️ TBM 점검 작성")
    
    selected_team = st.selectbox("부서 선택", list(team_data.keys()))
    final_name = st.text_input("성함 입력").strip()
    selected_job = st.selectbox("작업명", ["공통", "분해", "중량물", "전기", "세척", "조립", "시험"])
    
    st.write("**✅ 체크리스트**")
    items = pd.DataFrame([
        {"항목": "보호구", "내용": "개인보호구 착용", "확인": False},
        {"항목": "공구/정리", "내용": "작업장 정리정돈", "확인": False}
    ])
    st.data_editor(items, hide_index=True, use_container_width=True)
    
    st.write("**✒️ 최종 확인 서명**")
    st_canvas(stroke_width=3, stroke_color="#000", background_color="#f8f9fa", height=150, key="canvas_main")
    
    if st.button("제출하기"):
        if final_name:
            st.success("점검표가 제출되었습니다.")
            time.sleep(1)
            st.session_state.page = "main"
            st.rerun()
        else:
            st.warning("성함을 입력해 주세요.")

# [7. 현황 페이지]
elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    st.subheader("📊 실시간 점검 현황")
    try:
        raw_data = data_sheet.get_all_values()
        if len(raw_data) > 1:
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
        else:
            st.info("표시할 데이터가 없습니다.")
    except:
        st.error("데이터 로드 실패")

# [8. 관리자 페이지]
elif st.session_state.page == "tbm_admin":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    if not st.session_state.admin_logged_in:
