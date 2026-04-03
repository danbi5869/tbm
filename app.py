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

# [UI 디자인 - 톤다운 버전]
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        
        /* 톤다운된 지시사항 박스 (차분한 블루/그레이) */
        .notice-box {
            background-color: #f0f4f8; /* 연한 블루 그레이 */
            border-left: 5px solid #4a7c92; /* 차분한 청록색 계열 */
            padding: 18px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        
        /* 버튼 색상도 약간 차분하게 변경 (너무 밝은 레드 -> 약간 묵직한 레드) */
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.8em;
            background-color: #d32f2f; 
            color: white;
            font-weight: bold;
            font-size: 1.1em;
            border: none;
        }
        
        /* 탭 폰트 설정 */
        .stTabs [data-baseweb="tab"] {
            font-weight: 600;
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

# --- [체크리스트 초기 데이터] ---
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
        
        # 톤다운된 텍스트 출력
        display_text = st.session_state.safety_notice.replace("\n", "<br>")
        st.markdown(f"""
            <div class="notice-box">
                <h4 style="margin-top:0; color:#2c3e50; border-bottom: 1px solid #d1d8e0; padding-bottom: 8px; margin-bottom: 12px;">📋 안전 지시사항</h4>
                <p style="margin-bottom:0; font-size:1.0em; line-height:1.7; color: #34495e;">{display_text}</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        team_list = ["운영", "기술", "입출창", "중요장치장", "전기/제동장", "전기", "판토", "제동", "정비", "차체/수선장", "출입문", "차체", "냉방장치", "회전기장", "TM", "CM", "대차장", "댐퍼/에어스프링", "기초제동1", "기초제동2", "윤축/축상장", "윤축", "축상", "차륜", "탐상"]
        selected_team = st.selectbox("소속 부서", team_list, key="dept_sel")
        input_name = st.text_input("성함", key="name_input", placeholder="성함을 입력하세요")
        job_name = st.text_input("금일 작업명", key="job_input", placeholder="작업명을 입력하세요")

        st.markdown("---")
        edited_df = st.data_editor(df_init, hide_index=True, use_container_width=True, key="editor")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=150, width=330, drawing_mode="freedraw", key="canvas_main")

        if st.button("점검 완료 및 저장"):
            if not input_name or not job_name:
                st.warning("⚠️ 성함과 작업명을 먼저 입력해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명을 완료해 주세요.")
            else:
                with st.spinner('데이터 저장 중...'):
                    now = datetime.datetime.now()
                    new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, job_name, "정상" if edited_df[h_check].all() else "조치 필요", now.strftime('%H:%M:%S'), "✅ 완료"]
                    sheet.append_row(new_row)
                    st.success(f"🎊 저장 완료! ({input_name}님)")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

    # --- [TAB 2: 전체 점검 현황] ---
    with tab2:
        st.subheader("📊 점검 현황 조회")
        c_date, c_name = st.columns(2)
        with c_date: s_date = st.date_input("📅 날짜 선택", datetime.date.today())
        s_date_str = s_date.isoformat()
        
        try:
            raw_data = sheet.get_all_values()
            if len(raw_data) > 1:
                all_df = pd.DataFrame(raw_data[1:], columns=[h.strip() for h in raw_data[0]])
                if '서명' in all_df.columns: all_df = all_df.rename(columns={'서명': '서명확인'})
                if '성함' in all_df.columns: all_df = all_df.rename(columns={'성함': '이름'})

                d_filtered = all_df[all_df['날짜'] == s_date_str]
                if not d_filtered.empty:
                    names = sorted(d_filtered['이름'].unique().tolist())
                    with c_name: s_name = st.selectbox("👤 이름별 조회", ["전체 보기"] + names)
                    f_df = d_filtered if s_name == "전체 보기" else d_filtered[d_filtered['이름'] == s_name]
                    st.metric(f"{s_date_str} 점검 인원", f"{len(f_df)}명")
                    st.dataframe(f_df[['날짜', '시간', '소속', '이름', '작업명', '상태', '서명확인']], use_container_width=True, hide_index=True)
                else:
                    st.info(f"{s_date_str}에 완료된 점검 기록이 없습니다.")
        except: st.error("데이터 로딩 오류")

    # --- [TAB 3: 관리자 설정] ---
    with tab3:
        st.subheader("⚙️ 관리자 전용 설정")
        if not st.session_state.admin_logged_in:
            admin_pw = st.text_input("관리자 비밀번호를 입력하세요", type="password")
            if st.button("인증하기"):
                if admin_pw == "admin@123":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("비밀번호 불일치")
        else:
            st.success("🔓 관리자 모드 활성화 중")
            updated_notice = st.text_area("📢 안전 지시사항 내용 수정", st.session_state.safety_notice, height=200)
            c_adm1, c_adm2 = st.columns(2)
            with c_adm1:
                if st.button("내용 저장"):
                    st.session_state.safety_notice = updated_notice
                    st.success("수정되었습니다.")
                    time.sleep(1); st.rerun()
            with c_adm2:
                if st.button("로그아웃"):
                    st.session_state.admin_logged_in = False
                    st.rerun()
