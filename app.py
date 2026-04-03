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

# --- [고급 UI 디자인: 격자 테두리 및 중앙 정렬 CSS] ---
st.markdown(f"""
    <style>
        header {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        .block-container {{ padding-top: 1rem !important; }}
        
        /* 테이블 스타일: 테두리 합치기 및 중앙 정렬 */
        .tbm-grid {{
            width: 100%;
            border-collapse: collapse; /* 테두리 겹치기 */
            margin-bottom: 20px;
        }}
        
        .tbm-grid th, .tbm-grid td {{
            border: 1px solid #444444; /* 진한 테두리 */
            padding: 12px 8px;
            text-align: center; /* 가로 중앙 */
            vertical-align: middle; /* 세로 중앙 */
            font-size: 0.85rem;
        }}
        
        .tbm-grid th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}

        /* 체크박스 정렬용 컨테이너 */
        .centered-checkbox {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
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

# 2. 구글 시트 연결 (기존 설정 유지)
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

# --- [데이터 구성] ---
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
        
        c1, c2 = st.columns(2)
        with c1: selected_team = st.selectbox("소속 부서", teams)
        with c2: input_name = st.text_input("성함", placeholder="이름 입력")
        job_name = st.text_input("금일 작업명", placeholder="작업명을 입력하세요")

        st.markdown("---")
        
        # --- [격자 테두리 표 구현] ---
        # 헤더 출력 (HTML)
        st.markdown("""
            <table class="tbm-grid">
                <thead>
                    <tr>
                        <th style="width: 25%;">작업명</th>
                        <th style="width: 60%;">점검내용</th>
                        <th style="width: 15%;">확인</th>
                    </tr>
                </thead>
            </table>
        """, unsafe_allow_html=True)

        check_results = []
        
        # 각 행 출력 (Streamlit columns로 HTML 효과 재현)
        for i, item in enumerate(check_data):
            # 행 간격을 좁히기 위해 테두리가 있는 컨테이너 효과
            col1, col2, col3 = st.columns([1.5, 3.5, 1])
            
            with col1:
                st.markdown(f"<div style='border: 1px solid #444; padding: 10px; height: 85px; display: flex; align-items: center; justify-content: center; font-weight: bold;'>{item['작업명']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='border: 1px solid #444; padding: 10px; height: 85px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 0.85rem;'>{item['내용']}</div>", unsafe_allow_html=True)
            with col3:
                # 체크박스를 칸 정중앙에 배치
                st.markdown("<div style='border: 1px solid #444; height: 85px; display: flex; align-items: center; justify-content: center;'>", unsafe_allow_html=True)
                res = st.checkbox("", key=f"row_{i}", label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)
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
            if selected_team == "선택하세요" or not input_name or not job_name:
                st.warning("⚠️ 모든 빈칸을 채워주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명이 필요합니다.")
            else:
                now = datetime.datetime.now()
                new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, job_name, status, now.strftime('%H:%M:%S'), remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success("🎉 저장 성공!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    with tab2:
        st.subheader("📊 오늘 현황")
        # (현황판 로직 생략)
