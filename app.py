import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import time
from datetime import timezone, timedelta

# 1. 앱 설정 및 데이터 (기존과 동일)
try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

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

# 2. 구글 시트 연결 (생략 - 기존 코드와 동일)
# ... (get_sheet 함수 등)

# --- 메인 화면 ---
st.subheader("🏗️ TBM 안전 점검")

c1, c2 = st.columns(2)
with c1:
    selected_team = st.selectbox("부서 선택", list(team_data.keys()), key="dept_s")

with c2:
    # 🌟 핵심 수정 부분: 명단 선택과 직접 입력을 결합
    name_options = ["(직접 입력)"] + team_data[selected_team]
    search_name = st.selectbox("성함 검색/선택", name_options, key="name_search")

# 🌟 선택한 값이 "(직접 입력)"일 때만 입력창이 나타나고, 
# 명단에서 이름을 고르면 그 이름이 자동으로 저장값(final_name)이 됩니다.
if search_name == "(직접 입력)":
    final_name = st.text_input("성함을 직접 입력하세요", key="manual_name").strip()
else:
    final_name = search_name
    st.info(f"선택된 성함: **{final_name}**")

# 나머지 로직 (작업 선택, 점검표, 서명 등)
selected_job = st.selectbox("금일 작업명 선택", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"], key="job_s")

# ... (중략: 데이터 저장 시 final_name 변수를 사용하여 sheet.append_row 수행)

if st.button("점검 완료 및 저장"):
    if not final_name:
        st.warning("⚠️ 성함을 선택하거나 입력해 주세요.")
    else:
        # 저장 로직 실행
        # sheet.append_row([... final_name ...])
        st.success(f"{final_name}님 저장 완료!")
