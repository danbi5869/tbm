import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# 1. 앱 설정
icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png?v=15"
try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

# [UI 디자인: 헤더 및 테이블 스타일]
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

# --- [표 제목 설정: 공백으로 중앙 정렬 효과] ---
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
    tab1, tab2 = st.tabs(["📝 TBM 점검하기", "📊 전체 점검 현황"])

    with tab1:
        st.subheader("🏗️ TBM 안전 점검 일지")
        
        c1, c2 = st.columns(2)
        team_list = ["운영", "기술", "입출창", "중요장치장", "전기/제동장", "전기", "판토", "제동", "정비", "차체/수선장", "출입문", "차체", "냉방장치", "회전기장", "TM", "CM", "대차장", "댐퍼/에어스프링", "기초제동1", "기초제동2", "윤축/축상장", "윤축", "축상", "차륜", "탐상"]
        with c1: selected_team = st.selectbox("소속 부서", team_list, key="dept_sel")
        with c2: input_name = st.text_input("성함", key="name_input")
        job_name = st.text_input("금일 작업명", key="job_input")

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

        if st.button("점검 완료 및 저장"):
            if not input_name or not job_name:
                st.warning("⚠️ 성함과 작업명을 입력해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명이 누락되었습니다.")
            else:
                now = datetime.datetime.now()
                new_row = [now.strftime('%Y-%m-%d'), selected_team, input_name, job_name, status, now.strftime('%H:%M:%S'), remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success(f"🎉 {input_name}님, 저장 완료!")
                    st.balloons()
                    st.rerun() # 저장 후 현황판 업데이트를 위해 새로고침
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    with tab2:
        st.subheader("📊 금일 점검 현황")
        today_str = datetime.date.today().isoformat()
        st.write(f"📅 기준일: {today_str}")

        try:
            records = sheet.get_all_records()
            if records:
                all_df = pd.DataFrame(records)
                # 컬럼명 공백 제거 (안전용)
                all_df.columns = [col.strip() for col in all_df.columns]
                
                # 오늘 날짜 데이터만 필터링 (날짜 컬럼 기준)
                if '날짜' in all_df.columns:
                    today_df = all_df[all_df['날짜'] == today_str]
                    
                    # 요약 지표
                    st.metric("오늘 완료 인원", f"{len(today_df)}명")
                    
                    if not today_df.empty:
                        # 필요한 열만 예쁘게 출력
                        display_cols = ['시간', '소속', '이름', '작업명', '상태', '비고']
                        available_cols = [c for c in display_cols if c in today_df.columns]
                        st.dataframe(today_df[available_cols], use_container_width=True, hide_index=True)
                    else:
                        st.info("아직 오늘 완료된 점검 기록이 없습니다.")
                else:
                    st.error("시트에서 '날짜' 열을 찾을 수 없습니다.")
            else:
                st.warning("데이터가 비어 있습니다.")
        except Exception as e:
            st.error(f"데이터 로딩 오류: {e}")
