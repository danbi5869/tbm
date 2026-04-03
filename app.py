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
@st.cache_resource
def get_sheet():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc").get_worksheet(0)
    except: return None

sheet = get_sheet()

# [5. 🎨 클린 화이트 & 소프트 블루 CSS]
st.markdown("""
    <style>
        /* 배경: 아주 밝은 연그레이 (눈이 편함) */
        .stApp { background-color: #f8fafc; color: #1e293b; }
        header { visibility: hidden !important; }
        
        /* 메인 컨테이너: 화이트 카드 스타일 */
        .block-container { 
            background-color: #ffffff; 
            padding: 2.5rem !important; 
            border-radius: 24px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
            margin-top: 2rem;
        }
        
        /* 상단 제목 바: 부드러운 스카이블루 그라데이션 */
        .main-header { 
            background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
            padding: 2rem; border-radius: 20px; 
            margin-bottom: 2rem; text-align: center;
            border: 1px solid #bae6fd;
        }
        .main-header h1 { color: #0369a1 !important; font-size: 2rem; font-weight: 800; margin: 0; }
        
        /* 버튼 스타일: 둥글고 깨끗한 화이트 & 블루 테두리 */
        .stButton>button { 
            width: 100%; border-radius: 16px; height: 4.8rem; 
            font-size: 19px !important; font-weight: 700 !important; 
            transition: all 0.2s; 
            background-color: #ffffff; 
            color: #0369a1 !important;
            border: 1.5px solid #e0f2fe !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .stButton>button:hover { 
            background-color: #f0f9ff !important; 
            border: 1.5px solid #38bdf8 !important;
            color: #0284c7 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(56, 189, 248, 0.15) !important;
        }
        
        /* 공지사항 박스: 깔끔한 강조 형태 */
        .notice-box { 
            background-color: #f8fafc; 
            border: 1px solid #e2e8f0;
            border-left: 6px solid #38bdf8; 
            padding: 18px; border-radius: 12px; 
            margin-bottom: 25px; color: #475569;
        }
        
        /* 저장 버튼 (강조용 실선 블루) */
        div.stButton > button:has(div:contains("저장하기")) { 
            background-color: #0284c7 !important; 
            color: white !important; 
            border: none !important;
        }

        /* 테이블 및 입력창 테두리 부드럽게 */
        .stDataEditor, .stSelectbox, .stTextInput {
            border-radius: 12px !important;
        }
    </style>
""", unsafe_allow_html=True)

# [6. 화면 로직]

if st.session_state.page == "main":
    st.markdown('<div class="main-header"><h1>⛑️ TBM SMART PORTAL</h1></div>', unsafe_allow_html=True)
    st.write(" ")
    if st.button("📝 새 점검표 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
    st.write(" ")
    if st.button("📊 실시간 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()
    st.write(" ")
    if st.button("⚙️ 관리자 설정"):
        st.session_state.page = "tbm_admin"; st.rerun()

elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    
    st.subheader("📝 TBM 점검표 작성")
    display_text = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'<div class="notice-box"><b><span style="color:#0369a1;">📋 오늘의 안전 수칙</span></b><br>{display_text}</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: selected_team = st.selectbox("부서", list(team_data.keys()))
    with c2: 
        final_name = st.text_input("성함", placeholder="이름을 입력하세요").strip()
        if final_name and [n for n in team_data[selected_team] if final_name in n]:
            st.caption("✅ 등록된 팀원입니다.")

    selected_job = st.selectbox("작업 종류", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])

    st.markdown("---")
    st.write("**✅ 필수 안전점검**")
    col_config = {"작업명": st.column_config.TextColumn("항목", width=60), "점검내용": st.column_config.TextColumn("상세내용", width=220), "확인": st.column_config.CheckboxColumn("V", width=40)}
    common_list = [{"작업명": "계획", "점검내용": "역할 분담 및 순서 확인", "확인": False}, {"작업명": "보호구", "점검내용": "안전모/화/장갑 착용", "확인": False}, {"작업명": "공구", "점검내용": "사용 공구 이상 유무", "확인": False}, {"작업명": "환경", "점검내용": "바닥 정리 및 장애물 제거", "확인": False}]
    st.data_editor(pd.DataFrame(common_list), hide_index=True, width='stretch', column_config=col_config)

    st.write("**✒️ 본인 서명**")
    canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f1f5f9", height=120, width=300, drawing_mode="freedraw", key="canvas_tbm")

    if st.button("🚀 점검 완료 및 저장하기"):
        with st.spinner('시트 업데이트 중...'):
            try:
                kst = timezone(timedelta(hours=9))
                now = datetime.datetime.now(kst)
                sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료"])
                st.success("🎉 저장되었습니다!"); time.sleep(1); st.session_state.page = "main"; st.rerun()
            except: st.error("저장 실패")

elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("📊 작업 현황")
    try:
        raw_data = sheet.get_all_values()
        if len(raw_data) > 1:
            st.dataframe(pd.DataFrame(raw_data[1:], columns=raw_data[0]).iloc[::-1], use_container_width=True, hide_index=True)
    except: st.error("로드 실패")
