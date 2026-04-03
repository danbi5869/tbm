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

# [디자인: 헤더 스타일]
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
        return None

# --- [표 제목 설정: 공백을 넣어 시각적 중앙 정렬] ---
h_job = "  작업명  "
h_content = "         점검내용         "
h_check = " 확인 "

df_init = pd.DataFrame([
    {h_job: "작업계획 공유", h_content: "작업순서 및 역할 분담 완료", h_check: False},
    {h_job: "보호구 착용", h_content: "안전모, 안전화, 장갑, 보호안경, 마스크 등 착용", h_check: False},
    {h_job: "공구 점검", h_content: "공구 상태 이상없음", h_check: False},
    {h_job: "작업장 정리", h_content: "바닥 미끄럼, 장애물 정리", h_check: False},
    {h_job: "위험구역 설정", h_content: "출입통제 및 안전표지 설치", h_check: False},
    {h_job: "전원 차단 확인", h_content: "Lock-out/Tag-out 적용", h_check: False},
    {h_job: "비상대응 확인", h_content: "소화기, 비상연락망 확인", h_check: False}
])

sheet = get_sheet()

if sheet:
    st.subheader("🏗️ TBM 안전 점검 일지")
    
    c1, c2 = st.columns(2)
    # 팀 명단은 요약된 정보 기반으로 자동 세팅
    team_list = ["운영", "기술", "입출창", "중요장치장", "전기/제동장", "전기", "판토", "제동", "정비", "차체/수선장", "출입문", "차체", "냉방장치", "회전기장", "TM", "CM", "대차장", "댐퍼/에어스프링", "기초제동1", "기초제동2", "윤축/축상장", "윤축", "축상", "차륜", "탐상"]
    with c1: selected_team = st.selectbox("소속 부서", team_list)
    with c2: input_name = st.text_input("성함")
    job_name = st.text_input("금일 작업명")

    st.markdown("---")
    
    edited_df = st.data_editor(
        df_init,
        column_config={
            h_job: st.column_config.TextColumn(h_job, width="medium", disabled=True),
            h_content: st.column_config.TextColumn(h_content, width="large", disabled=True),
            h_check: st.column_config.CheckboxColumn(h_check, width="small", default=False, alignment="center"),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )

    st.markdown("---")
    
    # --- [해결 포인트: 공백 제거 후 체크 여부 확인] ---
    all_checked = edited_df[h_check].all() 
    status = "정상" if all_checked else "조치 필요"
    remark = st.text_area("특이사항 (비고)")

    st.write("✒️ **서명**")
    canvas_result = st_canvas(
        stroke_width=3, stroke_color="#000000", background_color="#f0f2f6",
        height=150, width=330, drawing_mode="freedraw", key="canvas_main"
    )

    if st.button("점검 완료 및 저장"):
        if not input_name or not job_name:
            st.warning("⚠️ 성함과 작업명을 입력해 주세요.")
        elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
            st.warning("⚠️ 서명이 누락되었습니다.")
        else:
            now = datetime.datetime.now()
            # 저장할 데이터 한 줄 만들기
            new_row = [
                now.strftime('%Y-%m-%d'), 
                selected_team, 
                input_name, 
                job_name, 
                status, 
                now.strftime('%H:%M:%S'), 
                remark, 
                "서명완료"
            ]
            try:
                sheet.append_row(new_row)
                st.success("🎉 구글 시트에 안전하게 저장되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"저장 실패: {e}")
