import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import time

# 1. 앱 설정
icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png?v=15"
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

# ✅ 요청하신 작업명 리스트
job_options = ["", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"]

# [UI 디자인 - 톤다운]
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        .notice-box {
            background-color: #f0f4f8;
            border-left: 5px solid #4a7c92;
            padding: 18px;
            border-radius: 8px;
            margin-bottom: 25px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.8em;
            background-color: #d32f2f; 
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
    except:
        return None

# 체크리스트 초기 설정
h_job, h_content, h_check = " 작업명 ", " 점검내용 ", "확인"
df_init = pd.DataFrame([
    {h_job: "작업계획 공유", h_content: "작업순서 및 역할 분담 완료", h_check: False},
    {h_job: "보호구 착용", h_content: "안전모, 안전화, 장갑, 보호구 착용", h_check: False},
    {h_job: "공구 점검", h_content: "사용 공구 상태 이상없음", h_check: False},
    {h_job: "작업장 정리", h_content: "바닥 미끄럼, 장애물 정리", h_check: False},
    {h_job: "위험구역 설정", h_content: "출입통제 및 안전표지 설치", h_check: False},
    {h_job: "전원 차단 확인", h_content: "Lock-out/Tag-out 적용", h_check: False},
    {h_job: "비상대응 확인", h_content: "소화기, 비상연락망 확인", h_check: False}
])

sheet = get_sheet()

if sheet:
    tab1, tab2, tab3 = st.tabs(["📝 TBM 점검하기", "📊 전체 점검 현황", "⚙️ 관리자 설정"])

    # --- [TAB 1: TBM 점검하기] ---
    with tab1:
        st.subheader("🏗️ TBM 안전 점검 일지")
        display_text = st.session_state.safety_notice.replace("\n", "<br>")
        st.markdown(f'<div class="notice-box"><h4 style="margin-top:0; color:#2c3e50;">📋 안전 지시사항</h4><p>{display_text}</p></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            selected_team = st.selectbox("소속 부서", list(team_data.keys()), key="dept_sel")
        with c2:
            member_options = [""] + team_data[selected_team]
            input_name = st.selectbox(
                "성함 선택", 
                member_options, 
                index=0, 
                format_func=lambda x: "성함을 입력/선택하세요" if x == "" else x,
                key="name_sel"
            )
        
        # ✅ [수정] 금일 작업명도 선택형(selectbox)으로 변경
        selected_job = st.selectbox(
            "금일 작업명", 
            job_options, 
            index=0, 
            format_func=lambda x: "작업명을 선택하세요" if x == "" else x,
            key="job_sel"
        )

        st.markdown("---")
        edited_df = st.data_editor(df_init, hide_index=True, use_container_width=True, key="editor")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=150, width=330, drawing_mode="freedraw", key="canvas_main")

        if st.button("점검 완료 및 저장"):
            if not input_name or not selected_job:
                st.warning("⚠️ 성함과 작업명을 모두 선택해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명을 완료해 주세요.")
            else:
                with st.spinner('데이터 저장 중...'):
                    now = datetime.datetime.now()
                    new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, selected_job, "정상" if edited_df[h_check].all() else "조치 필요", now.strftime('%H:%M:%S'), "✅ 완료"]
                    sheet.append_row(new_row)
                    st.success(f"🎊 저장 완료! ({input_name}님)")
                    st.balloons()
                    time.sleep(2); st.rerun()

    # --- [TAB 2: 전체 점검 현황] ---
    with tab2:
        st.subheader("📊 점검 현황 검색")
        c_date, c_search = st.columns(2)
        with c_date: 
            s_date = st.date_input("📅 날짜 선택", datetime.date.today())
        with c_search:
            name_query = st.text_input("👤 이름 검색", placeholder="성함 입력 (예: 노)")
            
        s_date_str = s_date.isoformat()
        
        if name_query: 
            try:
                raw_data = sheet.get_all_values()
                if len(raw_data) > 1:
                    all_df = pd.DataFrame(raw_data[1:], columns=[h.strip() for h in raw_data[0]])
                    if '성함' in all_df.columns: all_df = all_df.rename(columns={'성함': '이름'})
                    df_filtered = all_df[(all_df['날짜'] == s_date_str) & (all_df['이름'].str.contains(name_query, na=False))]

                    if not df_filtered.empty:
                        st.metric(f"'{name_query}' 검색 결과", f"{len(df_filtered)}건")
                        st.dataframe(df_filtered[['날짜', '시간', '소속', '이름', '작업명', '상태']], use_container_width=True, hide_index=True)
                    else:
                        st.info("조회된 기록이 없습니다.")
            except: st.error("로딩 오류")
        else:
            st.info("💡 조회하고자 하는 성함을 입력해 주세요.")

    # --- [TAB 3: 관리자 설정] ---
    with tab3:
        st.subheader("⚙️ 관리자 설정")
        if not st.session_state.admin_logged_in:
            admin_pw = st.text_input("비밀번호", type="password")
            if st.button("인증"):
                if admin_pw == "admin@123":
                    st.session_state.admin_logged_in = True; st.rerun()
                else: st.error("틀림")
        else:
            updated_notice = st.text_area("공지 수정", st.session_state.safety_notice, height=200)
            if st.button("저장"):
                st.session_state.safety_notice = updated_notice; st.rerun()
            if st.button("로그아웃"):
                st.session_state.admin_logged_in = False; st.rerun()
