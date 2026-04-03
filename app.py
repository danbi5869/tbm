import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import time

# 1. 앱 설정
icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png?v=15"
try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

# [세션 상태 관리]
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "safety_notice" not in st.session_state:
    st.session_state.safety_notice = "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거"

# [데이터 세팅]
team_data = {
    "운영": ["김한규", "김병배", "엄기태", "한효석", "신기영", "한진희", "노단비", "박진용"],
    "기술": ["황종연"],
    "입출창": ["이천형", "전동길", "허유정", "서대영"],
    "전기": ["이경민", "금창욱", "권혁진", "임의진", "박태규"],
    "정비": ["김성태", "배욱"],
    "차체": ["박노갑", "박종환", "최규현"],
    "냉방장치": ["김정혁", "김기훈", "설태길"],
    "윤축": ["정승욱", "나용환", "박주현"]
    # (나머지 부서는 생략하거나 필요시 추가)
}

specific_checks = {
    "분해작업": [{"항목": "분해", "점검내용": "부품 낙하 방지 조치", "확인": False}, {"항목": "잔압", "점검내용": "시스템 내 잔압 제거", "확인": False}],
    "전기작업": [{"항목": "절연", "점검내용": "절연장갑/화 착용", "확인": False}, {"항목": "검전", "점검내용": "정전 상태 확인", "확인": False}],
    "중량물취급": [{"항목": "줄걸이", "점검내용": "슬링벨트 상태 점검", "확인": False}, {"항목": "통제", "점검내용": "하부 출입통제 확인", "확인": False}]
}

job_options = ["", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"]

# ✅ 모바일 최적화 CSS (표의 텍스트 크기 조절 및 헤더 정렬)
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        .notice-box { background-color: #f0f4f8; border-left: 5px solid #4a7c92; padding: 12px; border-radius: 8px; margin-bottom: 15px; font-size: 0.9em; }
        .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
        .section-title { font-size: 1em; font-weight: bold; color: #2c3e50; margin-top: 15px; }
        
        /* 표 헤더 가운데 정렬 및 글자 크기 최적화 */
        div[data-testid="stDataEditor"] th {
            text-align: center !important;
            font-size: 0.85em !important;
        }
        /* 모바일에서 표 내용이 너무 크지 않게 조절 */
        div[data-testid="stDataEditor"] td {
            font-size: 0.85em !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. 구글 시트 연결
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
@st.cache_resource
def get_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc").get_worksheet(0)
    except: return None

sheet = get_sheet()

if sheet:
    tab1, tab2 = st.tabs(["📝 점검", "📊 현황"])

    with tab1:
        st.subheader("🏗️ TBM 점검")
        
        c1, c2 = st.columns(2)
        with c1: selected_team = st.selectbox("부서", list(team_data.keys()))
        with c2: input_name = st.selectbox("성함", [""] + team_data[selected_team])
        
        selected_job = st.selectbox("작업명", job_options)

        # ✅ [핵심] 컬럼 너비를 비율로 조정하여 스크롤 방지
        # width를 숫자로 주면 픽셀이 아니라 비중으로 작동합니다.
        mobile_column_config = {
            "작업명": st.column_config.TextColumn("항목", width=60), # 너비 최소화
            "점검내용": st.column_config.TextColumn("점검내용", width=200), # 내용에 가장 많은 공간 할당
            "확인": st.column_config.CheckboxColumn("확인", width=40) # 체크박스 너비 최소화
        }

        st.markdown('<div class="section-title">✅ 공통 점검</div>', unsafe_allow_html=True)
        common_list = [
            {"작업명": "계획", "점검내용": "순서 및 역할 분담", "확인": False},
            {"작업명": "보호구", "점검내용": "안전모/화/장갑 착용", "확인": False},
            {"작업명": "공구", "점검내용": "사용 공구 이상없음", "확인": False},
            {"작업명": "정리", "점검내용": "바닥 장애물 제거", "확인": False},
            {"작업명": "구역", "점검내용": "출입통제/표지 설치", "확인": False},
            {"작업명": "전원", "점검내용": "LOTO 적용 확인", "확인": False},
            {"작업명": "비상", "점검내용": "소화기/연락망 확인", "확인": False}
        ]
        
        df_common = st.data_editor(
            pd.DataFrame(common_list), 
            hide_index=True, 
            use_container_width=True, # 화면 폭에 맞춤
            key="common_editor",
            column_config=mobile_column_config
        )

        df_specific = None
        if selected_job in specific_checks:
            st.markdown(f'<div class="section-title">⚠️ {selected_job} 추가</div>', unsafe_allow_html=True)
            # 추가 항목용 컬럼 설정 (동일하게 적용)
            specific_config = {
                "항목": st.column_config.TextColumn("항목", width=60),
                "점검내용": st.column_config.TextColumn("점검내용", width=200),
                "확인": st.column_config.CheckboxColumn("확인", width=40)
            }
            df_specific = st.data_editor(
                pd.DataFrame(specific_checks[selected_job]), 
                hide_index=True, 
                use_container_width=True, 
                key="specific_editor",
                column_config=specific_config
            )

        st.write("✒️ **서명**")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=120, width=300, drawing_mode="freedraw", key="canvas_main")

        if st.button("점검 완료 저장"):
            if input_name and selected_job and df_common["확인"].all():
                now = datetime.datetime.now()
                sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, input_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료"])
                st.success("저장 완료!"); st.balloons(); time.sleep(1); st.rerun()
            else:
                st.warning("항목을 모두 확인해 주세요.")
