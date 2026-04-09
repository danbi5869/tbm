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

# [4. 스타일 디자인 - 너비 100% 일치 핵심]
st.markdown("""
    <style>
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .stApp { background-color: #F0F8FF; }
        
        /* 헤더 박스 */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.5rem 0.5rem; 
            border-radius: 0 0 30px 30px; 
            text-align: center; 
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .header-tbm { color: white !important; font-size: 2.5rem !important; font-weight: 900 !important; margin: 0; }
        .header-sub-text { color: #FFFFFF !important; font-size: 1.1rem !important; margin: 0; }
        
        /* 중앙 정렬 컨테이너 */
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }

        /* 공지사항 박스와 버튼 너비 동일화 (350px 고정) */
        .unified-width {
            width: 90% !important;
            max-width: 350px !important;
            box-sizing: border-box;
        }

        /* 공지사항 박스 스타일 */
        .notice-box { 
            background-color: #DBEAFE; 
            border: 2px solid #1E3A8A; 
            padding: 15px; 
            border-radius: 15px; 
            margin-bottom: 10px;
            text-align: left;
        }

        /* 버튼 스타일 */
        div.stButton > button { 
            width: 100% !important; /* 컨테이너 너비에 맞춤 */
            min-height: 4rem;
            border-radius: 15px; 
            font-weight: 700; 
            font-size: 1rem !important;
            border: 2px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A;
            margin-bottom: 10px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            /* 글자 잘림 방지 */
            white-space: normal !important;
            word-break: keep-all !important;
        }
        div.stButton > button:hover {
            background-color: #1E3A8A !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# [5. 메인 화면 로직]
if st.session_state.page == "main":
    st.markdown('''
        <div class="main-header">
            <h1 class="header-tbm">⛑️ TBM</h1>
            <p class="header-sub-text">안전점검 시스템</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # 컨테이너 시작
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    # 1. 공지사항 박스 (unified-width 클래스 적용)
    current_notice = load_notice()
    display_text = current_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-box unified-width">
            <b style="color:#1E3A8A;">📢 금일 안전 지시사항</b><br>
            <span style="color:#1E3A8A; font-size:0.9rem; line-height:1.4;">{display_text}</span>
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. 버튼들 (컬럼을 사용하지 않고 직접 배치하여 너비를 통일)
    # 각 버튼을 감싸는 div에 unified-width를 적용하여 너비를 맞춥니다.
    st.markdown('<div class="unified-width">', unsafe_allow_html=True)
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"
        st.rerun()
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"
        st.rerun()
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True) # 버튼 감싸는 div 끝
    
    st.markdown('</div>', unsafe_allow_html=True) # 전체 컨테이너 끝

# [6. 작성 페이지]
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    st.subheader("📝 TBM 점검 작성")
    
    c1, c2 = st.columns(2)
    with c1: selected_team = st.selectbox("부서 선택", list(team_data.keys()))
    with c2: final_name = st.text_input("성함 입력").strip()
    
    selected_job = st.selectbox("금일 작업명", ["공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])
    
    st.write("**✅ 공통 안전점검 사항**")
    # SyntaxError 방지를 위해 깔끔하게 정리된 데이터 구조
    check_items = [
        {"항목": "계획/보호구", "내용": "역할분담 및 개인보호구 착용"},
        {"항목": "공구/정리", "내용": "공구상태 및 작업장 정리정돈"},
        {"항목": "위험/전원", "내용": "LOTO 및 위험구역 통제"}
    ]
    df_items = pd.DataFrame(check_items)
    df_items["확인"] = False
    edited_df = st.data_editor(df_items, hide_index=True, use_container_width=True)

    st.write("**✒️ 최종 확인 서명**")
    canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=150, key="canvas")

    if st.button("점검 완료 및 제출"):
        if not final_name:
            st.warning("성함을 입력해주세요.")
        else:
            try:
                kst = timezone(timedelta(hours=9))
                now = datetime.datetime.now(kst)
                data_sheet.append_row([
                    now.strftime('%Y-%m-%d'), 
                    selected_team, 
                    final_name, 
                    selected_job, 
                    "정상", 
                    now.strftime('%H:%M:%S'), 
                    "✅ 완료"
                ])
                st.success("점검 완료!")
                time.sleep(1)
                st.session_state.page = "main"
                st.rerun()
            except:
                st.error("저장 실패")

# [7. 현황 확인 페이지]
elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    st.subheader("📊 실시간 현황")
    try:
        raw_data = data_sheet.get_all_values()
        if len(raw_data) > 1:
            df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
    except:
        st.error("데이터 로드 실패")

# [8. 관리자 페이지]
elif st.session_state.page == "tbm_admin":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    
    if not st.session_state.admin_logged_in:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == "admin@123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("오류")
    else:
        st.subheader("⚙️ 공지사항 수정")
        new_notice = st.text_area("내용 입력", load_notice(), height=150)
        if st.button("💾 저장하기"):
            try:
                settings_sheet.update_acell('Z1', new_notice)
                st.success("저장되었습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("실패")
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False
