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
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "safety_notice" not in st.session_state:
    st.session_state.safety_notice = "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거\n3. 상호 안전 확인 후 작업 개시"

# [3. 데이터 설정] (80명 명단 유지)
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

# [5. 강화된 커스텀 CSS 디자인]
st.markdown("""
    <style>
        /* 기본 배경 및 폰트 */
        .stApp { background-color: #f4f7f9; }
        
        /* 상단 네이비 헤더 바 */
        .header-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%);
            padding: 2.5rem 1rem;
            border-radius: 0 0 30px 30px;
            margin: -6rem -5rem 2rem -5rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            text-align: center;
        }
        .header-container h1 { color: white !important; font-size: 2.2rem !important; font-weight: 800 !important; }
        
        /* 카드형 컨테이너 스타일 */
        .st-emotion-cache-1y4p8pa { padding: 2rem 1.5rem !important; } /* 메인 컨테이너 패딩 */
        
        /* 버튼 스타일 개편 (그림자와 호버 효과 강조) */
        .stButton>button {
            background-color: #ffffff !important;
            color: #1e3a8a !important;
            border: 2px solid #1e3a8a !important;
            border-radius: 15px !important;
            height: 5rem !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            background-color: #1e3a8a !important;
            color: white !important;
            box-shadow: 0 8px 15px rgba(30, 58, 138, 0.3) !important;
            transform: translateY(-3px);
        }
        
        /* 저장 버튼 별도 스타일 */
        div.stButton > button:has(div:contains("저장하기")) {
            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
            color: white !important;
            border: none !important;
        }
        
        /* 뒤로가기 버튼 별도 스타일 */
        div.stButton > button:has(div:contains("메인으로")) {
            height: 3rem !important;
            background-color: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
            color: #64748b !important;
            font-size: 16px !important;
        }

        /* 공지사항(안전지시사항) 박스 */
        .notice-card {
            background-color: #ffffff;
            border-left: 8px solid #1e3a8a;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# [6. 앱 로직]

if st.session_state.page == "main":
    st.markdown('<div class="header-container"><h1>⛑️ TBM 안전관리 포털</h1></div>', unsafe_allow_html=True)
    
    st.write(" ")
    if st.button("📝 새 TBM 점검표 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
    
    st.write(" ")
    if st.button("📊 실시간 작업 현황판"):
        st.session_state.page = "tbm_status"; st.rerun()
    
    st.write(" ")
    if st.button("⚙️ 관리자 설정 모드"):
        st.session_state.page = "tbm_admin"; st.rerun()

elif st.session_state.page == "tbm_write":
    st.markdown('<div class="header-container"><h1>📝 점검표 작성</h1></div>', unsafe_allow_html=True)
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    
    st.write(" ")
    # 안전 지시사항 카드
    display_notice = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'<div class="notice-card"><b><span style="color:#1e3a8a; font-size:1.2rem;">📋 금일 안전 지시사항</span></b><br><div style="margin-top:10px; color:#334155;">{display_notice}</div></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        selected_team = st.selectbox("🏗️ 담당 부서", list(team_data.keys()))
    with c2:
        final_name = st.text_input("👤 성함 입력", placeholder="이름을 입력하세요").strip()
        if final_name:
            matches = [n for n in team_data[selected_team] if final_name in n]
            if matches: st.caption(f"✅ 명단 확인됨: {', '.join(matches)}")

    selected_job = st.selectbox("🛠️ 작업 종류", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])

    st.markdown("---")
    st.write("**✅ 공통 안전점검**")
    col_config = {"작업명": st.column_config.TextColumn("항목", width=70), "점검내용": st.column_config.TextColumn("상세내용", width=230), "확인": st.column_config.CheckboxColumn("V", width=40)}
    common_list = [{"작업명": "계획공유", "점검내용": "순서 및 역할 분담 완료", "확인": False}, {"작업명": "보호구착용", "점검내용": "안전모/화/장갑 착용", "확인": False}, {"작업명": "공구점검", "점검내용": "사용 공구 상태 이상없음", "확인": False}, {"작업명": "작업장정리", "점검내용": "바닥 미끄럼/장애물 제거", "확인": False}, {"작업명": "위험구역", "점검내용": "출입통제/표지 설치", "확인": False}, {"작업명": "전원차단", "점검내용": "LOTO 적용 확인", "확인": False}, {"작업명": "비상대응", "점검내용": "소화기/연락망 확인", "확인": False}]
    df_common = st.data_editor(pd.DataFrame(common_list), hide_index=True, width='stretch', column_config=col_config)

    st.write("**✒️ 본인 확인 서명**")
    canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=130, width=310, drawing_mode="freedraw", key="canvas_tbm")

    if st.button("🚀 점검 완료 및 저장하기"):
        if not final_name or not selected_job or not df_common["확인"].all():
            st.warning("⚠️ 성함과 모든 항목 체크를 확인해 주세요.")
        else:
            with st.spinner('구글 시트 전송 중...'):
                try:
                    kst = timezone(timedelta(hours=9))
                    now = datetime.datetime.now(kst)
                    sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료"])
                    st.success("🎉 저장되었습니다!"); time.sleep(1.2); st.session_state.page = "main"; st.rerun()
                except: st.error("시트 저장 오류")

elif st.session_state.page == "tbm_status":
    st.markdown('<div class="header-container"><h1>📊 작업 현황판</h1></div>', unsafe_allow_html=True)
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    
    st.write(" ")
    try:
        raw_data = sheet.get_all_values()
        if len(raw_data) > 1:
            df_all = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            st.dataframe(df_all.iloc[::-1], use_container_width=True, hide_index=True)
    except: st.error("데이터 로드 실패")

elif st.session_state.page == "tbm_admin":
    st.markdown('<div class="header-container"><h1>⚙️ 관리자 모드</h1></div>', unsafe_allow_html=True)
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    
    if not st.session_state.admin_logged_in:
        pw = st.text_input("관리자 암호", type="password")
        if st.button("인증하기"):
            if pw == "admin@123": st.session_state.admin_logged_in = True; st.rerun()
    else:
        new_notice = st.text_area("📢 현장 공지사항 수정", st.session_state.safety_notice, height=150)
        if st.button("공지사항 즉시 반영"): 
            st.session_state.safety_notice = new_notice
            st.success("공지가 업데이트 되었습니다.")
        if st.button("🔓 로그아웃"): 
            st.session_state.admin_logged_in = False; st.rerun()
