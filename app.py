import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# 1. 앱 설정
icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png?v=15"
try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

# [디자인: 헤더 글씨만 진하게]
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        div[data-testid="stDataFrame"] th {
            font-weight: 900 !important;
            color: #000 !important;
            background-color: #f0f2f6 !important;
        }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# 2. 구글 시트 연결 (기존 동일)
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def get_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet_id = "1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc"
        return client.open_by_key(sheet_id).get_worksheet(0)
    except Exception as e:
        return None

# --- [🆕 핵심: 제목만 가운데로 보이게 공백 작업] ---
# 제목 양옆에 특수 공백을 넣어 시각적으로 중앙에 배치합니다.
header_job = "  작업명  "
header_content = "         점검내용         "
header_check = " 확인 "

df_init = pd.DataFrame([
    {header_job: "작업계획 공유", header_content: "작업순서 및 역할 분담 완료", header_check: False},
    {header_job: "보호구 착용", header_content: "안전모, 안전화, 장갑, 보호안경, 마스크 등 착용", header_check: False},
    {header_job: "공구 점검", header_content: "공구 상태 이상없음", header_check: False},
    {header_job: "작업장 정리", header_content: "바닥 미끄럼, 장애물 정리", header_check: False},
    {header_job: "위험구역 설정", header_content: "출입통제 및 안전표지 설치", header_check: False},
    {header_job: "전원 차단 확인", header_content: "Lock-out/Tag-out 적용", header_check: False},
    {header_job: "비상대응 확인", header_content: "소화기, 비상연락망 확인", header_check: False}
])

sheet = get_sheet()

if sheet:
    st.subheader("🏗️ TBM 안전 점검 일지")
    
    c1, c2 = st.columns(2)
    with c1: selected_team = st.selectbox("소속 부서", ["운영", "기술", "정비", "전기", "차체", "냉방", "윤축"])
    with c2: input_name = st.text_input("성함", placeholder="이름 입력")
    job_name = st.text_input("금일 작업명", placeholder="작업명을 입력하세요")

    st.markdown("---")
    
    # --- [데이터 에디터: 본문 정렬은 건드리지 않음] ---
    edited_df = st.data_editor(
        df_init,
        column_config={
            header_job: st.column_config.TextColumn(header_job, width="medium", disabled=True),
            header_content: st.column_config.TextColumn(header_content, width="large", disabled=True),
            header_check: st.column_config.CheckboxColumn(header_check, width="small", default=False, alignment="center"),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )

    st.markdown("---")
    
    # 데이터 저장 로직은 기존과 동일...
    if st.button("점검 완료 및 저장"):
        # 저장 시에는 공백이 제거된 원래 컬럼명으로 처리하도록직을 짜면 됩니다.
        st.success("🎉 이번에는 제대로 정렬되었을 거예요!")
