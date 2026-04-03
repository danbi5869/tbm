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

# [UI 디자인]
st.markdown("""
    <style>
        header {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        div[data-testid="stDataFrame"] th {
            font-weight: 900 !important;
            color: #000 !important;
            background-color: #f0f2f6 !important;
            text-align: center !important;
        }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
            font-size: 1.2em;
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

# --- [표 제목 설정] ---
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
    # 세션 상태를 이용해 탭 위치 제어
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = 0

    tab1, tab2 = st.tabs(["📝 TBM 점검하기", "📊 전체 점검 현황"])

    with tab1:
        st.subheader("🏗️ TBM 안전 점검 일지")
        
        c1, c2 = st.columns(2)
        team_list = ["운영", "기술", "입출창", "중요장치장", "전기/제동장", "전기", "판토", "제동", "정비", "차체/수선장", "출입문", "차체", "냉방장치", "회전기장", "TM", "CM", "대차장", "댐퍼/에어스프링", "기초제동1", "기초제동2", "윤축/축상장", "윤축", "축상", "차륜", "탐상"]
        selected_team = st.selectbox("소속 부서", team_list, key="dept_sel")
        input_name = st.text_input("성함", key="name_input", placeholder="성함을 입력하세요")
        job_name = st.text_input("금일 작업명", key="job_input", placeholder="작업명을 입력하세요")

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
            num_rows="fixed",
            key="editor"
        )

        st.markdown("---")
        
        all_checked = edited_df[h_check].all() 
        status = "정상" if all_checked else "조치 필요"
        remark = st.text_area("특이사항 (비고)", key="remark_input")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(
            stroke_width=3, stroke_color="#000000", background_color="#f0f2f6",
            height=150, width=330, drawing_mode="freedraw", key="canvas_main"
        )

        # 저장 버튼 및 알림 로직
        if st.button("점검 완료 및 저장"):
            if not input_name or not job_name:
                st.warning("⚠️ 성함과 작업명을 먼저 입력해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 하단 서명란에 서명을 해주세요.")
            else:
                with st.spinner('데이터를 저장 중입니다...'):
                    now = datetime.datetime.now()
                    new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, job_name, status, now.strftime('%H:%M:%S'), remark, "✅ 완료"]
                    try:
                        sheet.append_row(new_row)
                        # ✅ 명확한 완료 문구 표시
                        st.success(f"✅ 점검 완료되었습니다! ({input_name}님)")
                        st.balloons()
                        # 잠시 대기 후 화면 갱신
                        time.sleep(2)
                        st.rerun() 
                    except Exception as e:
                        st.error(f"저장 중 오류가 발생했습니다: {e}")

    with tab2:
        st.subheader("📊 금일 점검 현황")
        today_str = datetime.date.today().isoformat()
        
        try:
            raw_data = sheet.get_all_values()
            if len(raw_data) > 1:
                header = [h.strip() for h in raw_data[0]]
                valid_cols = [i for i, h in enumerate(header) if h != ""]
                clean_header = [header[i] for i in valid_cols]
                data_rows = [[row[i] for i in valid_cols] for raw_data in raw_data[1:]]
                
                # 데이터가 없는 경우를 위한 방어 로직
                all_df = pd.DataFrame(raw_data[1:], columns=header)
                all_df.columns = [c.strip() for c in all_df.columns]
                
                if '서명' in all_df.columns:
                    all_df = all_df.rename(columns={'서명': '서명확인'})

                if '날짜' in all_df.columns:
                    today_df = all_df[all_df['날짜'] == today_str]
                    st.metric("오늘 완료 인원", f"{len(today_df)}명")
                    
                    if not today_df.empty:
                        display_cols = ['날짜', '시간', '소속', '이름', '작업명', '상태', '서명확인']
                        # 열 이름이 '이름' 대신 '성함'으로 저장되었을 경우를 대비
                        if '이름' not in today_df.columns and '성함' in today_df.columns:
                            today_df = today_df.rename(columns={'성함': '이름'})
                        
                        available_cols = [c for c in display_cols if c in today_df.columns]
                        st.dataframe(today_df[available_cols], use_container_width=True, hide_index=True)
                    else:
                        st.info("오늘 점검을 완료한 인원이 아직 없습니다.")
            else:
                st.warning("저장된 데이터가 없습니다.")
        except Exception as e:
            st.error(f"현황판 로딩 중 오류: {e}")
