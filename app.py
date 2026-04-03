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

specific_checks = {
    "분해작업": [{"항목": "분해", "점검내용": "부품 낙하 방지 조치", "확인": False}, {"항목": "잔압", "점검내용": "시스템 내 잔압 제거", "확인": False}],
    "중량물취급": [{"항목": "줄걸이", "점검내용": "슬링벨트 상태 점검", "확인": False}, {"항목": "통제", "점검내용": "하부 출입통제 확인", "확인": False}],
    "전기작업": [{"항목": "절연", "점검내용": "절연장갑/화 착용", "확인": False}, {"항목": "검전", "점검내용": "정전 상태 확인", "확인": False}],
    "세척작업": [{"항목": "MSDS", "점검내용": "세척제 보호구 착용", "확인": False}, {"항목": "환기", "점검내용": "배기장치 가동 확인", "확인": False}],
    "조립작업": [{"항목": "토크", "점검내용": "지정 토크값 준수", "확인": False}, {"항목": "간섭", "점검내용": "구동부 이물질 확인", "확인": False}],
    "시험/가동": [{"항목": "신호", "점검내용": "운전/정지 신호수 배치", "확인": False}, {"항목": "비상", "점검내용": "E-Stop 버튼 확인", "확인": False}]
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

# [5. 스타일 디자인]
st.markdown("""
    <style>
        .stApp { background-color: #F0F8FF; }
        header { visibility: hidden !important; }
        
        /* 상단 네비게이션 및 하단 버튼 그룹 한 줄 강제 고정 */
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 8px !important;
        }
        
        div[data-testid="column"] {
            width: fit-content !important;
            flex: 1 1 auto !important;
            min-width: unset !important;
        }

        /* 버튼 텍스트 줄바꿈 방지 */
        .stButton>button {
            white-space: nowrap !important;
            font-size: 14px !important;
        }

        /* 표 내부 글자 크기 조절 */
        [data-testid="stTable"] td, [data-testid="stTable"] th, .stDataFrame div {
            font-size: 12px !important;
            white-space: nowrap !important;
        }
    </style>
""", unsafe_allow_html=True)

# [6. 화면 전환 로직]
if st.session_state.page == "main":
    st.markdown('<h1 style="text-align:center; color:#1E3A8A;">⛑️ TBM 안전점검</h1>', unsafe_allow_html=True)
    if st.button("📝 금일 TBM 점검 작성", use_container_width=True):
        st.session_state.page = "tbm_write"; st.rerun()
    if st.button("📊 실시간 점검 현황 확인", use_container_width=True):
        st.session_state.page = "tbm_status"; st.rerun()
    if st.button("⚙️ 시스템 관리자 페이지", use_container_width=True):
        st.session_state.page = "tbm_admin"; st.rerun()

# 📝 점검 작성 페이지
elif st.session_state.page == "tbm_write":
    # 상단 네비게이션
    nav_col1, nav_col2, _ = st.columns([1, 1.2, 2]) 
    with nav_col1:
        if st.button("⬅️ 메인"): st.session_state.page = "main"; st.rerun()
    with nav_col2:
        if st.button("📊 현황 확인"): st.session_state.page = "tbm_status"; st.rerun()
            
    st.divider()
    st.subheader("🏗️ TBM 점검 작성")
    
    c1, c2 = st.columns(2)
    with c1: selected_team = st.selectbox("부서 선택", list(team_data.keys()))
    with c2: final_name = st.text_input("성함 입력", placeholder="성함 입력").strip()

    selected_job = st.selectbox("금일 작업명", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])

    st.write("**✅ 안전점검 사항**")
    col_config = {"작업명": st.column_config.TextColumn("항목", width=50), "점검내용": st.column_config.TextColumn("내용", width=200), "확인": st.column_config.CheckboxColumn("V", width=40)}
    common_list = [{"작업명": "보호구", "점검내용": "안전모/화/장갑 착용", "확인": False}, {"작업명": "공구", "점검내용": "상태 이상없음", "확인": False}, {"작업명": "LOTO", "점검내용": "전원 차단 확인", "확인": False}]
    df_common = st.data_editor(pd.DataFrame(common_list), hide_index=True, use_container_width=True, column_config=col_config)

    st.write("**✒️ 최종 확인 서명**")
    st_canvas(stroke_width=2, stroke_color="#000", background_color="#f8f9fa", height=100, width=310, key="canvas_tbm")

    # --- 하단 버튼 배치 (저장하기 옆에 점검현황 추가) ---
    st.write("") # 간격 확보
    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        save_btn = st.button("✅ 점검 완료 및 저장하기", use_container_width=True)
    with btn_col2:
        if st.button("📊 점검현황", use_container_width=True):
            st.session_state.page = "tbm_status"; st.rerun()

    if save_btn:
        if not final_name or not selected_job:
            st.warning("⚠️ 성함과 작업명을 입력해 주세요.")
        else:
            with st.spinner('저장 중...'):
                try:
                    kst = timezone(timedelta(hours=9))
                    now = datetime.datetime.now(kst)
                    sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료"])
                    st.success("✅ 저장되었습니다!")
                    st.session_state.page = "main"; time.sleep(1); st.rerun()
                except:
                    st.error("저장 실패")

# 📊 현황 확인 페이지
elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("📊 실시간 점검 현황")
    try:
        raw_data = sheet.get_all_values()
        if len(raw_data) > 1:
            df_all = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            st.dataframe(df_all.iloc[::-1], use_container_width=True, hide_index=True)
    except:
        st.error("데이터 로드 실패")

# ⚙️ 관리자 페이지
elif st.session_state.page == "tbm_admin":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    # (관리자 로직 유지)
