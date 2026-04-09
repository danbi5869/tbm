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
        
        # 첫 번째 탭: 점검 결과 저장용
        data_sheet = spreadsheet.get_worksheet(0)
        
        # 두 번째 탭: 설정 및 공지사항용 (없으면 생성하거나 첫 번째 탭의 특정 셀 사용)
        # 여기서는 편의상 첫 번째 탭의 100번째 행(Z100) 등에 저장하거나 별도 탭을 권장합니다.
        # 일단은 별도 탭(워크시트 이름 'Settings')이 있다고 가정하고 없으면 예외처리합니다.
        try:
            settings_sheet = spreadsheet.worksheet("Settings")
        except:
            # Settings 탭이 없으면 첫 번째 탭의 특정 위치를 사용하거나 에러 방지
            settings_sheet = data_sheet 
            
        return data_sheet, settings_sheet
    except:
        return None, None

data_sheet, settings_sheet = get_sheets()

# 공지사항을 시트에서 가져오는 함수
def load_notice():
    try:
        # Settings 탭의 A1 셀에 공지사항이 들어있다고 가정
        val = settings_sheet.acell('Z1').value # 구석진 Z1 셀을 공지사항 저장소로 활용
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

# 팀 데이터 (기존과 동일)
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

specific_checks = {
    "분해작업": [{"항목": "분해", "점검내용": "부품 낙하 방지 조치", "확인": False}, {"항목": "잔압", "점검내용": "시스템 내 잔압 제거", "확인": False}],
    "중량물취급": [{"항목": "줄걸이", "점검내용": "슬링벨트 상태 점검", "확인": False}, {"항목": "통제", "점검내용": "하부 출입통제 확인", "확인": False}],
    "전기작업": [{"항목": "절연", "점검내용": "절연장갑/화 착용", "확인": False}, {"항목": "검전", "점검내용": "정전 상태 확인", "확인": False}],
    "세척작업": [{"항목": "MSDS", "점검내용": "세척제 보호구 착용", "확인": False}, {"항목": "환기", "점검내용": "배기장치 가동 확인", "확인": False}],
    "조립작업": [{"항목": "토크", "점검내용": "지정 토크값 준수", "확인": False}, {"항목": "간섭", "점검내용": "구동부 이물질 확인", "확인": False}],
    "시험/가동": [{"항목": "신호", "점검내용": "운전/정지 신호수 배치", "확인": False}, {"항목": "비상", "점검내용": "E-Stop 버튼 확인", "확인": False}]
}

# [4. 스타일 디자인]
st.markdown("""
    <style>
        header { visibility: hidden !important; }
        .stApp { background-color: #F0F8FF; }
        .main-header { background-color: #1E3A8A; padding: 1.2rem 0.5rem; border-radius: 0 0 20px 20px; text-align: center; color: white; margin-bottom: 2rem;}
        .notice-box { background-color: #DBEAFE; border-left: 5px solid #1E3A8A; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
        div.stButton > button { width: 100%; max-width: 420px; min-height: 4.5rem; border-radius: 12px; font-weight: 700; border: 2px solid #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

# [5. 로직]
if st.session_state.page == "main":
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    
    # 실시간 공지 로드 (새로고침 시 반영되도록)
    current_notice = load_notice()
    display_text = current_notice.replace("\n", "<br>")
    
    st.markdown(f'''
        <div class="notice-box">
            <b>📢 금일 안전 지시사항</b><br>{display_text}
        </div>
    ''', unsafe_allow_html=True)
    
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"; st.rerun()

# [관리자 페이지 수정 핵심 부분]
elif st.session_state.page == "tbm_admin":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
        
    if not st.session_state.admin_logged_in:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == "admin@123": st.session_state.admin_logged_in = True; st.rerun()
    else:
        st.subheader("⚙️ 관리자 설정")
        # 현재 시트에 저장된 공지사항을 불러와서 표시
        current_saved_notice = load_notice()
        new_notice = st.text_area("공지 수정 (저장 시 모든 사용자에게 반영)", current_saved_notice, height=150)
        
        if st.button("💾 구글 시트에 영구 저장"):
            try:
                # 구글 시트의 Z1 셀에 저장
                settings_sheet.update_acell('Z1', new_notice)
                st.session_state.safety_notice = new_notice
                st.success("✅ 구글 시트에 저장되었습니다! 이제 모든 사용자에게 이 내용이 보입니다.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}")
                
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False; st.rerun()

# (점검 작성 및 현황 확인 페이지는 기존과 동일하여 생략... 전체 코드에 포함하여 사용하세요)
elif st.session_state.page == "tbm_write":
    # [기존 점검 작성 코드 유지]
    st.write("점검 작성 중...") # 실제 사용 시 기존 코드를 여기에 넣으세요.
    if st.button("메인으로"): st.session_state.page = "main"; st.rerun()

elif st.session_state.page == "tbm_status":
    # [기존 현황 확인 코드 유지]
    st.write("현황 확인 중...") # 실제 사용 시 기존 코드를 여기에 넣으세요.
    if st.button("메인으로"): st.session_state.page = "main"; st.rerun()
