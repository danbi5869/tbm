import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# 1. 앱 설정 및 모바일 아이콘 강제 지정
try:
    img = Image.open("safety_mascot.png")
    # GitHub의 이미지 원본 주소를 여기에 넣으면 모바일 홈 화면 아이콘으로 강제 인식됩니다.
    # '본인아이디' 부분을 실제 본인의 GitHub ID로 꼭 변경하세요!
    icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png"
except:
    img = "⛑️"
    icon_url = ""

st.set_page_config(
    page_title="TBM 점검",
    page_icon=img,
    layout="centered"
)

# 모바일 홈 화면용 메타 태그 삽입
if icon_url:
    st.markdown(f'<link rel="apple-touch-icon" href="{icon_url}">', unsafe_allow_html=True)
    st.markdown(f'<link rel="shortcut icon" href="{icon_url}">', unsafe_allow_html=True)

# 2. 인증 및 권한 설정
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

# --- [소속 및 명단 데이터] ---
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

sheet = get_sheet()

if sheet:
    tab1, tab2 = st.tabs(["📝 TBM 점검하기", "📊 전체 점검 현황"])

    with tab1:
        st.header("🏗️ TBM 점검 및 안전일지")
        col1, col2 = st.columns(2)
        with col1:
            selected_team = st.selectbox("소속 선택", list(team_data.keys()), key="team_select")
        with col2:
            member_list = team_data[selected_team]
            selected_name = st.selectbox("성함 선택", member_list, key="name_select")

        st.markdown("---")
        st.subheader(f"📍 {selected_team} - {selected_name}님 점검")
        q1 = st.checkbox("✅ 개인보호구 착용 상태 확인", key="q1")
        q2 = st.checkbox("✅ 작업 전 위험요인 파악 및 공유", key="q2")
        q3 = st.checkbox("✅ 사용 장비 점검 완료", key="q3")
        status = "정상" if (q1 and q2 and q3) else "조치 필요"
        remark = st.text_area("특이사항 (비고)", key="remark")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color="#000000",
            background_color="#eeeeee", height=150, width=300, drawing_mode="freedraw", key="canvas_main",
        )

        if st.button("점검 완료 및 시트 저장", width="stretch", key="save_btn"):
            if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명을 완료해야 저장할 수 있습니다.")
            else:
                now_time = datetime.datetime.now().strftime('%H:%M:%S')
                today_date = datetime.date.today().isoformat()
                new_row = [today_date, selected_team, selected_name, status, now_time, remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success(f"🎉 {selected_name}님, 저장 완료!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    with tab2:
        st.header("📊 전체 점검 현황")
        st.write(f"📅 기준일: {datetime.date.today().isoformat()}")
        try:
            records = sheet.get_all_records()
            if records:
                df = pd.DataFrame(records)
                df.columns = [col.strip() for col in df.columns]
                today_str = datetime.date.today().isoformat()
                if '날짜' in df.columns:
                    today_df = df[df['날짜'] == today_str]
                    st.metric("오늘 점검 완료", f"{len(today_df)}명")
                    if not today_df.empty:
                        show_cols = [c for c in ['시간', '소속', '이름', '상태', '비고'] if c in today_df.columns]
                        st.dataframe(today_df[show_cols], width="stretch")
                    else:
                        st.info("오늘 아직 점검 기록이 없습니다.")
                else:
                    st.error("'날짜' 열을 찾을 수 없습니다.")
            else:
                st.warning("데이터가 없습니다.")
        except Exception as e:
            st.error(f"데이터 로딩 오류: {e}")
