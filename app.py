import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import time
from datetime import timezone, timedelta

# 1. 앱 설정
try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

# [세션 상태 관리]
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "safety_notice" not in st.session_state:
    st.session_state.safety_notice = "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거\n3. 상호 안전 확인 후 작업 개시"

# [데이터 세팅]
team_data = {
    "운영": ["김한규", "김병배", "엄기태", "한효석", "신기영", "한진희", "노단비", "박진용"],
    "기술": ["황종연"],
    "입출창": ["이천형", "전동길", "허유정", "서대영"],
    "중요장치장": ["송진수", "임대권", "이준혁", "김명철"],
    "전기/제동장": ["손해진", "주승용"],
    "전기": ["이경민", "금창욱", "권혁진", "임의진", "박태규"],
    "판토": ["유문일", "이현우"],
    "제동": ["오성윤", "허성우", "김원경", "전창근", "서준영", "이진호"],
    "정비": ["김성태", "배욱"],
    "차체/수선장": ["최덕수", "반상민"],
    "출입문": ["김지훈", "추동일", "한지훈", "백승주", "최창열", "윤성현"],
    "차체": ["박노갑", "박종환", "최규현"],
    "냉방장치": ["김정혁", "김기훈", "설태길"],
    "회전기장": ["박기하", "이성보"],
    "TM": ["박석희", "오현택", "유상훈"],
    "CM": ["안상복", "김태경"],
    "대차장": ["임청용", "정호영"],
    "댐퍼/에어스프링": ["정성목", "이태수"],
    "기초제동1": ["우원진", "연제동", "이창록"],
    "기초제동2": ["김영일", "정진영", "허재혁"],
    "윤축/축상장": ["김성수", "이성문"],
    "윤축": ["정승욱", "나용환", "박주현"],
    "축상": ["박상언", "윤종혁", "방건동", "박준수"],
    "차륜": ["지민석", "곽동영", "안형륜", "이동호"],
    "탐상": ["박윤찬", "이동호"]
}

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

# [스타일 설정]
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        .notice-box { background-color: #f0f4f8; border-left: 5px solid #4a7c92; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 0.9em; }
        .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #d32f2f; color: white; font-weight: bold; }
        .section-title { font-size: 1em; font-weight: bold; color: #2c3e50; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

if sheet:
    tab1, tab2, tab3 = st.tabs(["📝 TBM 점검", "📊 점검 현황", "⚙️ 관리자"])

    with tab1:
        st.subheader("🏗️ TBM 안전 점검")
        display_text = st.session_state.safety_notice.replace("\n", "<br>")
        st.markdown(f'<div class="notice-box"><b>📋 안전 지시사항</b><br>{display_text}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            selected_team = st.selectbox("부서 선택", list(team_data.keys()), key="dept_s")
        
        with c2:
            # ✅ [수정된 핵심 로직] 텍스트 입력창 하나만 배치
            final_name = st.text_input("성함 (조회/직접입력)", placeholder="이름을 입력하세요", key="name_input").strip()
            
            # 입력한 글자가 포함된 팀원이 명단에 있으면 추천 안내
            if final_name:
                matches = [n for n in team_data[selected_team] if final_name in n]
                if matches:
                    st.caption(f"💡 명단 확인됨: {', '.join(matches)}")

        selected_job = st.selectbox("금일 작업명 선택", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"], key="job_s")

        st.markdown("---")
        
        # ✅ 이전 그대로의 공통 안전점검 사항 표
        col_config = {"작업명": st.column_config.TextColumn("항목", width=60), "점검내용": st.column_config.TextColumn("점검내용", width=220), "확인": st.column_config.CheckboxColumn("확인", width=40)}
        st.markdown('<div class="section-title">✅ 공통 안전점검 사항</div>', unsafe_allow_html=True)
        common_list = [{"작업명": "계획", "점검내용": "순서 및 역할 분담 완료", "확인": False}, {"작업명": "보호구", "점검내용": "안전모/화/장갑 착용", "확인": False}, {"작업명": "공구", "점검내용": "사용 공구 상태 이상없음", "확인": False}, {"작업명": "정리", "점검내용": "바닥 미끄럼/장애물 제거", "확인": False}, {"작업명": "구역", "점검내용": "출입통제/표지 설치", "확인": False}, {"작업명": "전원", "점검내용": "LOTO 적용 확인", "확인": False}, {"작업명": "비상", "점검내용": "소화기/연락망 확인", "확인": False}]
        df_common = st.data_editor(pd.DataFrame(common_list), hide_index=True, use_container_width=True, key="ed_common", column_config=col_config)

        st.write("✒️ **서명**")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=130, width=310, drawing_mode="freedraw", key="canvas_main")

        if st.button("점검 완료 및 저장"):
            if not final_name: 
                st.warning("⚠️ 성함을 입력해 주세요.")
            elif not selected_job: 
                st.warning("⚠️ 작업명을 선택해 주세요.")
            elif not df_common["확인"].all(): 
                st.warning("⚠️ 모든 점검 항목에 체크해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0: 
                st.warning("⚠️ 서명을 완료해 주세요.")
            else:
                with st.spinner('저장 중...'):
                    try:
                        kst = timezone(timedelta(hours=9))
                        now = datetime.datetime.now(kst)
                        # ✅ 사용자가 친 '글자 그대로' 무조건 시트에 저장
                        sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료", ""])
                        st.success(f"🎉 {final_name}님 저장 완료!")
                        st.balloons(); time.sleep(2); st.rerun()
                    except Exception as e:
                        st.error(f"저장 실패: {e}")

    # (TAB 2, TAB 3 등 나머지 관리 기능은 이전 버전과 동일하게 유지)
