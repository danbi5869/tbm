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
        try:
            settings_sheet = spreadsheet.get_worksheet(0) # 일단 첫번째 시트 사용
        except:
            settings_sheet = data_sheet 
        return data_sheet, settings_sheet
    except:
        return None, None

data_sheet, settings_sheet = get_sheets()

def load_notice():
    try:
        val = settings_sheet.acell('Z1').value # 구글 시트 Z1 셀 확인
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

# 팀 데이터 (기존 데이터 유지)
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

# [4. 스타일 디자인 - 헤더 부분 집중 수정]
st.markdown("""
    <style>
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .stApp { background-color: #F0F8FF; }
        
        /* 메인 헤더 박스 */
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.5rem 0.5rem; 
            border-radius: 0 0 25px 25px; 
            text-align: center; 
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        
        /* 이모티콘 스타일 */
        .header-emoji {
            font-size: 3.5rem !important;
            margin-bottom: 0.5rem;
            display: block;
        }

        /* TBM 텍스트 스타일 */
        .header-title-main { 
            color: white !important; 
            font-size: 2.2rem !important; 
            font-weight: 800 !important;
            margin: 0;
            line-height: 1.1;
        }

        /* 안전점검 시스템 텍스트 스타일 */
        .header-title-sub { 
            color: #DBEAFE !important; 
            font-size: 1.4rem !important; 
            font-weight: 600 !important;
            margin: 0;
            line-height: 1.4;
        }
        
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 15px; 
            border-radius: 12px; 
            margin-bottom: 20px;
            width: 95%;
            max-width: 420px;
        }

        div.stButton > button { 
            width: 100% !important; 
            max-width: 420px !important; 
            min-height: 4.5rem;
            border-radius: 15px; 
            font-weight: 700; 
            font-size: 1.1rem !important;
            border: 2px solid #1E3A8A;
            background-color: white;
            color: #1E3A8A;
        }
    </style>
""", unsafe_allow_html=True)

# [5. 화면 전환 로직]

if st.session_state.page == "main":
    # 이모티콘과 글자를 분리하여 2줄(실제로는 3줄 레이아웃)로 구성
    st.markdown('''
        <div class="main-header">
            <span class="header-emoji">⛑️</span>
            <h1 class="header-title-main">TBM</h1>
            <p class="header-title-sub">안전점검 시스템</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # 모바일 주소창 제거 가이드
    with st.expander("📱 앱처럼 사용하기 (주소창 숨기기)"):
        st.info("설정(⋮ 또는 공유) -> '홈 화면에 추가'를 누르면 앱처럼 쓸 수 있습니다.")

    # 중앙 정렬 컨테이너
    st.markdown('<div style="display: flex; flex-direction: column; align-items: center;">', unsafe_allow_html=True)
    
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
    st.markdown('</div>', unsafe_allow_html=True)

# 📝 점검 작성 페이지
elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("🏗️ TBM 점검 작성")
    
    c1, c2 = st.columns(2)
    with c1: selected_team = st.selectbox("부서 선택", list(team_data.keys()))
    with c2: 
        final_name = st.text_input("성함 입력", placeholder="성함").strip()

    selected_job = st.selectbox("금일 작업명", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])

    st.write("**✅ 공통 안전점검 사항**")
    col_config = {"작업명": st.column_config.TextColumn("항목", width=60), "점검내용": st.column_config.TextColumn("내용", width=220), "확인": st.column_config.CheckboxColumn("V", width=40)}
    common_list = [{"작업명": "계획/보호구", "점검내용": "역할분담 및 개인보호구 착용", "확인": False}, {"작업명": "공구/정리", "점검내용": "공구상태 및 작업장 정리정돈", "확인": False}, {"작업명": "위험/전원", "점검내용": "LOTO 및 위험구역 통제", "확인": False}]
    
    df_common = st.data_editor(pd.DataFrame(common_list), hide_index=True, width='stretch', column_config=col_config)

    st.write("**✒️ 최종 확인 서명**")
    st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=130, width=310, drawing_mode="freedraw", key="canvas_tbm")

    if st.button("점검 완료 및 저장"):
        if not final_name or not selected_job:
            st.warning("⚠️ 이름과 작업명을 확인해 주세요.")
        else:
            with st.spinner('저장 중...'):
                try:
                    kst = timezone(timedelta(hours=9))
                    now = datetime.datetime.now(kst)
                    data_sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료", ""])
                    st.success("✅ 저장되었습니다!")
                    time.sleep(1)
                    st.session_state.page = "main"; st.rerun()
                except:
                    st.error("구글 시트 저장 실패 (Z열 확인 필요)")

# 📊 현황 확인 페이지
elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("📊 실시간 점검 현황")
    try:
        raw_data = data_sheet.get_all_values()
        if len(raw_data) > 1:
            df_all = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            st.dataframe(df_all.iloc[::-1], hide_index=True)
    except:
        st.error("데이터 로드 실패")

# ⚙️ 관리자 페이지
elif st.session_state.page == "tbm_admin":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    if not st.session_state.admin_logged_in:
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == "admin@123": st.session_state.admin_logged_in = True; st.rerun()
    else:
        st.subheader("⚙️ 관리자 설정")
        current_saved_notice = load_notice()
        new_notice = st.text_area("📢 공지사항 수정", current_saved_notice, height=150)
        if st.button("💾 구글 시트에 영구 저장"):
            try:
                settings_sheet.update_acell('Z1', new_notice) # Z열 열 추가 확인 필요!
                st.session_state.safety_notice = new_notice
                st.success("✅ 저장 성공!")
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}\n(구글시트에 Z열까지 열 추가가 필요합니다)")
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False; st.rerun()
