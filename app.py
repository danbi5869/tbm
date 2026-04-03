import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# 1. 앱 설정 및 아이콘
icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png?v=15"

try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

# [UI 디자인: 헤더 정렬 강제 주입]
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        
        /* 1. 모든 데이터프레임의 헤더(th)를 강제로 가운데 정렬 */
        [data-testid="stDataFrame"] th {
            text-align: center !important;
            justify-content: center !important;
            display: flex-column !important;
            font-weight: 900 !important;
            color: #000 !important;
            background-color: #f0f2f6 !important;
        }

        /* 2. 헤더 내부의 텍스트 컨테이너까지 정렬 */
        [data-testid="stHeaderRowCellContents"] {
            justify-content: center !important;
            text-align: center !important;
            width: 100% !important;
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

# 2. 구글 시트 연결
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
        st.error(f"구글 시트 연결 실패: {e}")
        return None

# --- [표 데이터 구성] ---
# 텍스트 열의 alignment="center"를 헤더에만 적용하기 위해 column_config를 정밀 조정합니다.
df_init = pd.DataFrame([
    {"작업명": "작업계획 공유", "점검내용": "작업순서 및 역할 분담 완료", "확인": False},
    {"작업명": "보호구 착용", "점검내용": "안전모, 안전화, 장갑, 보호안경, 마스크 등 착용", "확인": False},
    {"작업명": "공구 점검", "점검내용": "공구 상태 이상없음", "확인": False},
    {"작업명": "작업장 정리", "점검내용": "바닥 미끄럼, 장애물 정리", "확인": False},
    {"작업명": "위험구역 설정", "점검내용": "출입통제 및 안전표지 설치", "확인": False},
    {"작업명": "전원 차단 확인", "점검내용": "Lock-out/Tag-out 적용", "확인": False},
    {"작업명": "비상대응 확인", "점검내용": "소화기, 비상연락망 확인", "확인": False}
])

sheet = get_sheet()

if sheet:
    tab1, tab2 = st.tabs(["📝 TBM 점검", "📊 현황판"])

    with tab1:
        st.subheader("🏗️ TBM 안전 점검 일지")
        
        c1, c2 = st.columns(2)
        with c1: selected_team = st.selectbox("소속 부서", ["운영", "기술", "정비", "전기", "차체", "냉방", "윤축 등..."])
        with c2: input_name = st.text_input("성함")
        job_name = st.text_input("금일 작업명")

        st.markdown("---")
        
        # --- [💡 해결책: column_config의 alignment 설정 활용] ---
        # alignment="center"를 주면 헤더와 본문이 같이 정렬되는 경우가 많지만, 
        # 최신 Streamlit 버전에서는 헤더 정렬을 가장 잘 지원하는 옵션입니다.
        edited_df = st.data_editor(
            df_init,
            column_config={
                "작업명": st.column_config.TextColumn(
                    "작업명", 
                    width="medium", 
                    disabled=True,
                    alignment="center" # 헤더 정렬을 위해 center 지정
                ),
                "점검내용": st.column_config.TextColumn(
                    "점검내용", 
                    width="large", 
                    disabled=True,
                    alignment="center" # 헤더 정렬을 위해 center 지정
                ),
                "확인": st.column_config.CheckboxColumn(
                    "확인", 
                    width="small", 
                    default=False,
                    alignment="center"
                ),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed"
        )

        st.markdown("---")
        
        all_checked = edited_df["확인"].all()
        status = "정상" if all_checked else "조치 필요"
        remark = st.text_area("특이사항 (비고)")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#f0f2f6",
            height=150, width=330, drawing_mode="freedraw", key="canvas_main"
        )

        if st.button("점검 완료 및 저장"):
            # 저장 로직 (이전과 동일)
            pass
