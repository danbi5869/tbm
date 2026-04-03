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

# --- [🆕 고급 UI 디자인: CSS 스타일링] ---
st.markdown(f"""
    <style>
        /* 기본 숨기기 설정 */
        header {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        .block-container {{ padding-top: 1rem !important; }}
        
        /* 🎨 표 전체 스타일 정의 */
        .tbm-table-container {{
            width: 100%;
            margin-top: 15px;
            margin-bottom: 15px;
            border-collapse: separate;
            border-spacing: 0;
            border: 1px solid #ddd;
            border-radius: 8px; /* 표 전체 둥근 모서리 */
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* 은은한 그림자 */
        }}
        
        /* 표 헤더 (작업명, 점검내용, 확인) */
        .tbm-header {{
            background-color: #f0f2f6; /* 연한 그레이 배경 */
            color: #333;
            font-weight: bold;
            text-align: center;
            padding: 12px;
            font-size: 0.95rem;
            border-bottom: 2px solid #ddd;
        }}
        
        /* 표 행 (Row) 설정 */
        .tbm-row {{
            background-color: white;
            transition: background-color 0.2s; /* 부드러운 전환 */
        }}
        .tbm-row:hover {{
            background-color: #f8f9fa; /* 마우스 오버 시 배경색 변경 */
        }}
        
        /* 표 셀 (Cell) 설정 - 완벽한 가운데 정렬 */
        .tbm-cell {{
            padding: 12px 10px;
            text-align: center; /* 가로 중앙 정렬 */
            vertical-align: middle !important; /* 세로 중앙 정렬 */
            border-bottom: 1px solid #eee;
            font-size: 0.85rem;
            color: #555;
            line-height: 1.4;
        }}
        
        /* 마지막 행 테두리 제거 */
        .tbm-row:last-child .tbm-cell {{
            border-bottom: none;
        }}
        
        /* 체크박스 컨테이너 (정렬용) */
        .checkbox-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
        }}

        /* 하단 버튼 스타일 */
        .stButton>button {{
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
""", unsafe_allow_html=True)

# 2. 구글 시트 연결 로직 (이전과 동일)
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
        job_name = st.text_input("금일 작업명", placeholder="진행할 작업명을 입력하세요")

        st.markdown("---")
        st.write("✅ **점검 항목 확인**")
        
        # --- [🆕 표 형식 체크리스트 구현 시작] ---
        # 1. 표의 헤더 생성
        h1, h2, h3 = st.columns([1.5, 3, 1])
        h1.markdown("<div class='tbm-header'>작업명</div>", unsafe_allow_html=True)
        h2.markdown("<div class='tbm-header'>점검내용</div>", unsafe_allow_html=True)
        h3.markdown("<div class='tbm-header'>확인</div>", unsafe_allow_html=True)

        check_results = []
        
        # 2. 데이터 행 생성
        for i, item in enumerate(check_data):
            # st.columns 안의 모든 요소는 CSS로 중앙 정렬됨
            with st.container(): # 각 행을 컨테이너로 묶음
                row_c1, row_c2, row_c3 = st.columns([1.5, 3, 1])
                
                # '작업명' 셀 (Bold 처리)
                row_c1.markdown(f"<div class='checkbox-container' style='min-height:70px;'><b>{item['작업명']}</b></div>", unsafe_allow_html=True)
                
                # '점검내용' 셀
                row_c2.markdown(f"<div class='checkbox-container' style='min-height:70px; text-align:left;'>{item['내용']}</div>", unsafe_allow_html=True)
                
                # '확인' 체크박스 셀
                with row_c3:
                    # Streamlit 체크박스를 중앙에 배치하기 위한 trick
                    st.write("") # 상단 여백
                    st.write("") # 상단 여백
                    res = st.checkbox("", key=f"row_{i}")
                    check_results.append(res)
            # 행 구분선
            st.markdown("<div style='border-bottom:1px solid #eee; margin: 0 10px;'></div>", unsafe_allow_html=True)
        # --- [표 형식 체크리스트 끝] ---

        st.markdown("---")
        status = "정상" if all(check_results) else "조치 필요"
        remark = st.text_area("특이사항 (비고)", placeholder="내용을 입력하세요.")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#f0f2f6",
            height=150, width=330, drawing_mode="freedraw", key="canvas_main"
        )

        if st.button("점검 완료 및 저장"):
            if selected_team == "선택하세요" or not input_name or not job_name:
                st.warning("⚠️ 모든 정보를 입력해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명이 완료되지 않았습니다.")
            else:
                now = datetime.datetime.now()
                new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, job_name, status, now.strftime('%H:%M:%S'), remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success("🎉 저장 완료!今日もご安全に!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    with tab2:
        st.subheader("📊 오늘 현황")
        # 현황판 로직은 이전과 동일
