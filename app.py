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

# [UI 디자인: 헤더(제목)만 가운데 정렬 및 강조]
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        
        /* ✅ 표의 맨 윗줄(헤더)만 가운데 정렬하고 글씨를 진하게 만듭니다 */
        div[data-testid="stDataFrame"] th {
            background-color: #f0f2f6 !important;
            font-weight: 900 !important;
            color: #000 !important;
            text-align: center !important; /* 헤더만 가운데 정렬 */
        }

        /* 본문 셀은 기본 정렬(왼쪽)을 유지하도록 설정 (필요시) */
        div[data-testid="stDataFrame"] td {
            vertical-align: middle !important;
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
teams = ["선택하세요", "운영", "기술", "입출창", "중요장치장", "전기/제동장", "전기", "판토", "제동", "정비", "차체/수선장", "출입문", "차체", "냉방장치", "회전기장", "TM", "CM", "대차장", "댐퍼/에어스프링", "기초제동1", "기초제동2", "윤축/축상장", "윤축", "축상", "차륜", "탐상"]

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
        with c1: selected_team = st.selectbox("소속 부서", teams)
        with c2: input_name = st.text_input("성함", placeholder="이름 입력")
        job_name = st.text_input("금일 작업명", placeholder="작업명을 입력하세요")

        st.markdown("---")
        st.write("✅ **점검 항목 확인**")

        # --- [업데이트: 본문 정렬은 유지하고 헤더만 CSS로 조정] ---
        edited_df = st.data_editor(
            df_init,
            column_config={
                "작업명": st.column_config.TextColumn("작업명", width="medium", disabled=True),
                "점검내용": st.column_config.TextColumn("점검내용", width="large", disabled=True),
                "확인": st.column_config.CheckboxColumn("확인", width="small", default=False, alignment="center"), # 체크박스는 중앙이 사용하기 편합니다
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
            if selected_team == "선택하세요" or not input_name or not job_name:
                st.warning("⚠️ 모든 정보를 입력해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명이 필요합니다.")
            else:
                now = datetime.datetime.now()
                new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, job_name, status, now.strftime('%H:%M:%S'), remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success("🎉 저장 완료! 안전한 하루 되세요.")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    with tab2:
        st.subheader("📊 오늘 현황")
