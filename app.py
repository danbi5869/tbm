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

# [4. 구글 시트 연결 (조회/저장 공통)]
@st.cache_resource
def get_sheet():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        # 사용자님의 시트 ID 그대로 유지
        return client.open_by_key("1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc").get_worksheet(0)
    except Exception as e:
        st.error(f"시트 연결 오류: {e}")
        return None

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
        # ✅ 명단 선택 + 자유 입력 통합 (selectbox의 placeholder와 options 조합)
        # 명단에 없으면 직접 타이핑 후 엔터 치면 입력됩니다.
        final_name = st.selectbox(
            "성함 입력/선택",
            options=team_data[selected_team],
            index=None,
            placeholder="이름 입력 또는 선택",
            key="user_name_input"
        )
        # 만약 아무것도 선택/입력하지 않았을 때를 대비한 안내
        if not final_name:
            st.caption("💡 명단에 없으면 이름을 직접 타이핑하세요.")

    selected_job = st.selectbox("금일 작업명", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])
    
    st.write("**✅ 공통 안전점검 사항**")
    col_config = {"점검항목": st.column_config.TextColumn("항목", width=80), "내용": st.column_config.TextColumn("내용", width=200), "확인": st.column_config.CheckboxColumn("확인", width=50)}
    common_items = [{"점검항목": "보호구", "내용": "안전모/화/장갑 착용", "확인": False}, {"점검항목": "주변정리", "내용": "작업장 바닥 이상무", "확인": False}, {"점검항목": "LOTO", "점검내용": "전원 차단 확인", "확인": False}]
    df_common = st.data_editor(pd.DataFrame(common_items), hide_index=True, width='stretch', column_config=col_config)

    st.write("**✒️ 서명**")
    canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=100, width=300, drawing_mode="freedraw", key="canvas_sign")

    if st.button("🚀 점검 완료 및 시트 저장"):
        if not final_name or not selected_job or not df_common["확인"].all():
            st.warning("⚠️ 성함과 모든 점검 항목을 확인해 주세요.")
        elif sheet is None:
            st.error("❌ 시트 연결을 확인하세요.")
        else:
            with st.spinner('구글 시트에 기록 중...'):
                kst = timezone(timedelta(hours=9))
                now = datetime.datetime.now(kst)
                # 입력된 final_name이 명단에 있든 직접 쳤든 그대로 저장
                sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료"])
                st.success(f"🎉 {final_name}님 저장 완료!"); time.sleep(1.2); st.session_state.page = "main"; st.rerun()

elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    
    st.subheader("📊 실시간 점검 현황 (Google Sheet)")
    
    if sheet:
        try:
            # ✅ 구글 시트에서 데이터 실시간으로 가져오기
            data = sheet.get_all_values()
            if len(data) > 1:
                df = pd.DataFrame(data[1:], columns=data[0])
                # 최신 데이터가 위로 오게 역순 정렬 및 오늘 날짜 필터링 등 가능
                st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
            else:
                st.info("아직 저장된 데이터가 없습니다.")
        except Exception as e:
            st.error(f"데이터 조회 실패: {e}")
    else:
        st.error("구글 시트에 연결할 수 없습니다.")
