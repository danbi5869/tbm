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

# [UI 디자인: 이미지의 표 양식을 모바일용으로 최적화]
st.markdown(f"""
    <style>
        header {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        .block-container {{ padding-top: 1rem !important; }}
        
        /* 표 헤더 스타일 */
        .table-header {{
            background-color: #333333;
            color: white;
            padding: 8px;
            text-align: center;
            font-weight: bold;
            border: 1px solid #ddd;
            font-size: 0.9rem;
        }}
        
        /* 표 셀 스타일 */
        .table-cell {{
            padding: 10px;
            border: 0.5px solid #eee;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 0.85rem;
        }}

        .stButton>button {{
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
        }}
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

# --- [표 데이터: 이미지와 100% 일치] ---
teams = ["선택하세요", "운영", "기술", "입출창", "중요장치장", "전기/제동장", "전기", "판토", "제동", "정비", "차체/수선장", "출입문", "차체", "냉방장치", "회전기장", "TM", "CM", "대차장", "댐퍼/에어스프링", "기초제동1", "기초제동2", "윤축/축상장", "윤축", "축상", "차륜", "탐상"]

check_data = [
    {"작업명": "작업계획 공유", "내용": "작업순서 및 역할 분담 완료"},
    {"작업명": "보호구 착용", "내용": "안전모, 안전화, 장갑, 보호안경, 마스크 등 착용"},
    {"작업명": "공구 점검", "내용": "공구 상태 이상없음"},
    {"작업명": "작업장 정리", "내용": "바닥 미끄럼, 장애물 정리"},
    {"작업명": "위험구역 설정", "내용": "출입통제 및 안전표지 설치"},
    {"작업명": "전원 차단 확인", "내용": "Lock-out/Tag-out 적용"},
    {"작업명": "비상대응 확인", "내용": "소화기, 비상연락망 확인"}
]

sheet = get_sheet()

if sheet:
    tab1, tab2 = st.tabs(["📝 TBM 점검", "📊 현황판"])

    with tab1:
        st.subheader("🏗️ TBM 안전 점검 일지")
        
        # 기본 정보 입력
        c1, c2 = st.columns(2)
        with c1: selected_team = st.selectbox("소속 부서", teams)
        with c2: input_name = st.text_input("성함", placeholder="이름 입력")
        target_job = st.text_input("금일 작업명", placeholder="진행할 작업명을 입력하세요")

        st.markdown("---")
        
        # --- [이미지 표 양식 구현] ---
        # 헤더
        h1, h2, h3 = st.columns([1.5, 3, 1])
        h1.markdown("<div class='table-header'>작업명</div>", unsafe_allow_html=True)
        h2.markdown("<div class='table-header'>점검내용</div>", unsafe_allow_html=True)
        h3.markdown("<div class='table-header'>확인</div>", unsafe_allow_html=True)

        check_results = []
        for i, item in enumerate(check_data):
            r1, r2, r3 = st.columns([1.5, 3, 1])
            # 행 구분선과 내용을 깔끔하게 배치
            r1.markdown(f"<div class='table-cell'><b>{item['작업명']}</b></div>", unsafe_allow_html=True)
            r2.markdown(f"<div class='table-cell'>{item['내용']}</div>", unsafe_allow_html=True)
            # 체크박스 위치 정렬
            with r3:
                st.write("") # 간격 조절용
                res = st.checkbox("", key=f"row_{i}")
                check_results.append(res)
        
        st.markdown("---")
        
        status = "정상" if all(check_results) else "조치 필요"
        remark = st.text_area("특이사항 (비고)")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#f0f2f6",
            height=150, width=330, drawing_mode="freedraw", key="canvas_main"
        )

        if st.button("점검 완료 및 저장"):
            if selected_team == "선택하세요" or not input_name or not target_job:
                st.warning("⚠️ 모든 빈칸을 입력해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명이 완료되지 않았습니다.")
            else:
                now = datetime.datetime.now()
                new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, target_job, status, now.strftime('%H:%M:%S'), remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success(f"🎉 저장 완료! 오늘도 안전한 하루 되세요.")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 오류: {e}")

    with tab2:
        st.subheader("📊 오늘 현황")
        # (현황판 로직은 기존과 동일)
