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

# [3. 사용자 데이터 (80명 명단)]
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

# 작업별 추가 점검 항목 복구
specific_checks = {
    "분해작업": [{"항목": "분해", "점검내용": "부품 낙하 방지 조치", "확인": False}, {"항목": "잔압", "점검내용": "시스템 내 잔압 제거", "확인": False}],
    "중량물취급": [{"항목": "줄걸이", "점검내용": "슬링벨트 상태 점검", "확인": False}, {"항목": "통제", "점검내용": "하부 출입통제 확인", "확인": False}],
    "전기작업": [{"항목": "절연", "점검내용": "절연장갑/화 착용", "확인": False}, {"항목": "검전", "점검내용": "정전 상태 확인", "확인": False}],
    "세척작업": [{"항목": "MSDS", "점검내용": "세척제 보호구 착용", "확인": False}, {"항목": "환기", "점검내용": "배기장치 가동 확인", "확인": False}],
    "조립작업": [{"항목": "토크", "점검내용": "지정 토크값 준수", "확인": False}, {"항목": "간섭", "점검내용": "구동부 이물질 확인", "확인": False}],
    "시험/가동": [{"항목": "신호", "점검내용": "운전/정지 신호수 배치", "확인": False}, {"항목": "비상", "점검내용": "E-Stop 버튼 확인", "확인": False}]
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

# [5. 스타일 설정]
st.markdown("""
    <style>
        .stApp { background-color: #F0F8FF; }
        .main-header { background-color: #1E3A8A; padding: 1.2rem; border-radius: 0 0 15px 15px; margin-bottom: 2rem; color: white; text-align: center; }
        .stButton > button { width: 100%; border-radius: 10px; height: 3.5rem; font-weight: 700; background-color: #ffffff; border: 2px solid #1E3A8A; color: #1E3A8A; }
    </style>
""", unsafe_allow_html=True)

# [6. 앱 로직]
if st.session_state.page == "main":
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()

elif st.session_state.page == "tbm_write":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    
    st.subheader("📝 점검표 작성")
    
    c1, c2 = st.columns(2)
    with c1:
        selected_team = st.selectbox("부서 선택", list(team_data.keys()))
    with c2:
        # ✅ [해결책] 타이핑 입력 완벽 지원 로직
        # 1. 사용자가 타이핑한 값을 받기 위해 selectbox 대신 전용 위젯 조합
        if "temp_name" not in st.session_state: st.session_state.temp_name = ""
        
        # 목록에 '직접 입력' 항목을 추가하여 타이핑 유도
        options = ["명단에서 선택"] + team_data[selected_team]
        choice = st.selectbox("성함 선택/검색", options, index=0)
        
        if choice == "명단에서 선택":
            final_name = st.text_input("성함 직접 입력", placeholder="명단에 없으면 여기에 타이핑", key="manual_name").strip()
        else:
            final_name = choice

    selected_job = st.selectbox("금일 작업명", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])
    
    # ✅ 공통 안전점검 사항 복구
    st.write("**✅ 공통 안전점검 사항**")
    col_config = {"작업명": st.column_config.TextColumn("항목", width=60), "점검내용": st.column_config.TextColumn("내용", width=220), "확인": st.column_config.CheckboxColumn("확인", width=40)}
    common_list = [{"작업명": "계획", "점검내용": "순서 및 역할 분담 완료", "확인": False}, {"작업명": "보호구", "점검내용": "안전모/화/장갑 착용", "확인": False}, {"작업명": "공구", "점검내용": "사용 공구 상태 이상없음", "확인": False}, {"작업명": "정리", "점검내용": "바닥 미끄럼/장애물 제거", "확인": False}, {"작업명": "구역", "점검내용": "출입통제/표지 설치", "확인": False}, {"작업명": "전원", "점검내용": "LOTO 적용 확인", "확인": False}, {"작업명": "비상", "점검내용": "소화기/연락망 확인", "확인": False}]
    df_common = st.data_editor(pd.DataFrame(common_list), hide_index=True, width='stretch', column_config=col_config)

    # ✅ 추가 점검 사항 복구
    if selected_job and selected_job not in ["", "공통작업"]:
        st.write(f"**⚠️ {selected_job} 추가 점검**")
        df_specific = st.data_editor(pd.DataFrame(specific_checks[selected_job]), hide_index=True, width='stretch', column_config=col_config)

    st.write("**✒️ 최종 확인 서명**")
    canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=130, width=310, drawing_mode="freedraw", key="canvas_sign")

    if st.button("🚀 점검 완료 및 저장"):
        if not final_name or not selected_job or not df_common["확인"].all():
            st.warning("⚠️ 성함과 모든 필수 점검 항목을 확인해 주세요.")
        else:
            with st.spinner('저장 중...'):
                try:
                    kst = timezone(timedelta(hours=9))
                    now = datetime.datetime.now(kst)
                    sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료"])
                    st.success(f"🎉 {final_name}님 저장 완료!"); time.sleep(1.2); st.session_state.page = "main"; st.rerun()
                except Exception as e: st.error(f"저장 실패: {e}")

elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("📊 실시간 점검 현황")
    if sheet:
        try:
            raw_data = sheet.get_all_values()
            if len(raw_data) > 1:
                df_all = pd.DataFrame(raw_data[1:], columns=raw_data[0])
                st.dataframe(df_all.iloc[::-1], use_container_width=True, hide_index=True)
        except: st.error("데이터 조회 실패")
