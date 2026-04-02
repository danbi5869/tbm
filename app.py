import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas

# 1. 앱 설정 및 아이콘 (캐시 방지를 위해 v 숫자를 높였습니다)
icon_url = "https://raw.githubusercontent.com/danbi5869/TBM-app/main/safety_mascot.png?v=15"

try:
    img = Image.open("safety_mascot.png")
except:
    img = "⛑️"

st.set_page_config(
    page_title="TBM 스마트 체크리스트",
    page_icon=img,
    layout="centered"
)

# [진짜 앱처럼 만들기: 주소창, 메뉴, 하단 로고 모두 제거]
st.markdown(f"""
    <style>
        /* 1. 상단 헤더, 메뉴, 하단 로고(Footer) 전체 숨기기 */
        header {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        
        /* 2. 하단 로고를 감싸는 컨테이너까지 제거 */
        .st-emotion-cache-16471hc {{display: none !important;}}
        .st-emotion-cache-ch5vc {{display: none !important;}}

        /* 3. 모바일 앱 느낌을 위해 여백 최소화 */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
        }}
        
        /* 4. 버튼 디자인 (모바일 터치 최적화) */
        .stButton>button {{
            width: 100%;
            border-radius: 12px;
            height: 3.5em;
            background-color: #FF4B4B;
            color: white;
            font-weight: bold;
            border: none;
        }}
    </style>
    <head>
        <link rel="apple-touch-icon" href="{icon_url}">
        <link rel="icon" type="image/png" href="{icon_url}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    </head>
""", unsafe_allow_html=True)

# 2. 구글 시트 인증 및 연결
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

# --- [데이터 구성: 소속 및 명단] ---
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

checklist_items = ["개인보호구 착용 상태 확인", "작업 전 위험요인 파악 및 공유", "사용 장비 점검 완료"]

sheet = get_sheet()

if sheet:
    tab1, tab2 = st.tabs(["📝 TBM 점검", "📊 현황판"])

    with tab1:
        # 상단 마스코트 표시
        try:
            st.image("safety_mascot.png", width=70)
        except:
            pass

        st.subheader("🏗️ 안전 점검 일지")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_team = st.selectbox("소속", list(team_data.keys()), key="team_select")
        with col2:
            member_list = team_data[selected_team]
            selected_name = st.selectbox("성함", member_list, key="name_select")

        st.markdown("---")
        
        # 체크리스트 자동 생성
        check_results = []
        for i, item in enumerate(checklist_items):
            res = st.checkbox(f" {item}", key=f"q_{i}")
            check_results.append(res)

        status = "정상" if all(check_results) else "조치 필요"
        remark = st.text_area("특이사항 (비고)", placeholder="내용을 입력하세요.", key="remark")

        st.write("✒️ **서명**")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color="#000000",
            background_color="#f0f2f6", height=150, width=330, drawing_mode="freedraw", key="canvas_main",
        )

        if st.button("점검 완료 및 저장"):
            if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명을 완료해야 저장할 수 있습니다.")
            else:
                now_time = datetime.datetime.now().strftime('%H:%M:%S')
                today_date = datetime.date.today().isoformat()
                new_row = [today_date, selected_team, selected_name, status, now_time, remark, "서명완료"]
                try:
                    sheet.append_row(new_row)
                    st.success(f"🎉 저장 완료!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 실패: {e}")

    with tab2:
        st.subheader("📊 오늘 점검 현황")
        try:
            records = sheet.get_all_records()
            if records:
                df = pd.DataFrame(records)
                today_str = datetime.date.today().isoformat()
                if '날짜' in df.columns:
                    today_df = df[df['날짜'] == today_str]
                    st.metric("오늘 완료", f"{len(today_df)}명")
                    st.dataframe(today_df.tail(10), use_container_width=True)
        except:
            st.info("기록을 불러올 수 없습니다.")
