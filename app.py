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

# 페이지 설정 (주소창 타이틀 및 레이아웃)
st.set_page_config(page_title="TBM 스마트 체크리스트", page_icon=img, layout="centered")

# [2. 세션 상태 초기화]
if "page" not in st.session_state:
    st.session_state.page = "main"
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "safety_notice" not in st.session_state:
    st.session_state.safety_notice = "1. 개인 보호구 착용 철저\n2. 작업 전 주변 위험요소 제거\n3. 상호 안전 확인 후 작업 개시"

# [3. 데이터 정의]
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

specific_checks = {
    "분해작업": [{"항목": "분해", "점검내용": "부품 낙하 방지 조치", "확인": False}, {"항목": "잔압", "점검내용": "시스템 내 잔압 제거", "확인": False}],
    "중량물취급": [{"항목": "줄걸이", "점검내용": "슬링벨트 상태 점검", "확인": False}, {"항목": "통제", "점검내용": "하부 출입통제 확인", "확인": False}],
    "전기작업": [{"항목": "절연", "점검내용": "절연장갑/화 착용", "확인": False}, {"항목": "검전", "점검내용": "정전 상태 확인", "확인": False}],
    "세척작업": [{"항목": "MSDS", "점검내용": "세척제 보호구 착용", "확인": False}, {"항목": "환기", "점검내용": "배기장치 가동 확인", "확인": False}],
    "조립작업": [{"항목": "토크", "점검내용": "지정 토크값 준수", "확인": False}, {"항목": "간섭", "점검내용": "구동부 이물질 확인", "확인": False}],
    "시험/가동": [{"항목": "신호", "점검내용": "운전/정지 신호수 배치", "확인": False}, {"항목": "비상", "점검내용": "E-Stop 버튼 확인", "확인": False}]
}

# [4. 구글 시트 연결]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
@st.cache_resource
def get_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        # 구글 시트 ID 확인 필요
        return client.open_by_key("1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc").get_worksheet(0)
    except:
        return None

sheet = get_sheet()

# [5. 스타일 디자인 - 앱 최적화 스타일 추가]
st.markdown("""
    <style>
        /* 1. 기본 메뉴 및 헤더 숨기기 */
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        #MainMenu { visibility: hidden !important; }
        
        /* 2. 배경 및 레이아웃 */
        .stApp { background-color: #F0F8FF; }
        
        .main-header { 
            background-color: #1E3A8A; 
            padding: 1.2rem 0.5rem; 
            border-radius: 0 0 20px 20px; 
            margin-bottom: 1.5rem; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            text-align: center;
        }
        .main-header h1 { 
            color: white !important; 
            font-size: clamp(1.1rem, 5.5vw, 2.2rem) !important; 
            margin: 0; 
            white-space: nowrap !important;
            letter-spacing: -1px;
        }
        
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        
        .notice-box { 
            background-color: #DBEAFE; 
            border-left: 5px solid #1E3A8A; 
            padding: 15px 20px; 
            border-radius: 12px; 
            color: #1E3A8A; 
            font-size: 16px; 
            text-align: left;
            margin-bottom: 20px;
            width: 95%; 
            max-width: 420px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* 큰 버튼 스타일 */
        div.stButton > button { 
            width: 100% !important; 
            max-width: 420px !important; 
            min-height: 4.5rem;
            border-radius: 12px; 
            font-size: 18px !important; 
            font-weight: 700 !important; 
            margin: 8px 0 !important; 
            border: 2.5px solid #1E3A8A !important;
            background-color: white !important;
            color: #1E3A8A !important;
            transition: 0.2s;
        }
        div.stButton > button:hover { background-color: #1E3A8A !important; color: white !important; }

        /* 네비게이션용 작은 버튼 스타일 */
        div.stButton > button:has(div:contains("메인으로")),
        div.stButton > button:has(div:contains("현황 확인")),
        div.stButton > button:has(div:contains("⬅️")) { 
            height: 2.5rem !important; 
            min-height: 2.5rem !important; 
            font-size: 14px !important; 
            margin: 0 !important; 
            padding: 0 10px !important;
            border-radius: 8px !important;
            width: auto !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #E2E8F0 !important;
            color: #475569 !important;
        }

        /* 가로 배치 간격 조정 */
        div[data-testid="stHorizontalBlock"] { gap: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# [6. 화면 전환 로직]

# 메인 화면
if st.session_state.page == "main":
    st.markdown('<div class="main-header"><h1>⛑️ TBM 안전점검 시스템</h1></div>', unsafe_allow_html=True)
    
    # 모바일 주소창 제거 가이드 (확장형)
    with st.expander("📱 주소창 없이 앱처럼 깔끔하게 쓰려면?"):
        st.info("**아이폰(Safari):** 하단 공유 버튼(⎋) 클릭 → '홈 화면에 추가'\n\n**안드로이드(Chrome):** 우측 상단 메뉴(⋮) 클릭 → '홈 화면에 추가' 또는 '앱 설치'")

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    display_text = st.session_state.safety_notice.replace("\n", "<br>")
    st.markdown(f'''
        <div class="notice-box">
            <b>📢 금일 안전 지시사항</b><br>{display_text}
        </div>
    ''', unsafe_allow_html=True)
    
    if st.button("📝 금일 TBM 점검 작성"):
        st.session_state.page = "tbm_write"; st.rerun()
        
    if st.button("📊 실시간 점검 현황 확인"):
        st.session_state.page = "tbm_status"; st.rerun()
        
    if st.button("⚙️ 시스템 관리자 페이지"):
        st.session_state.page = "tbm_admin"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# 📝 점검 작성 페이지
elif st.session_state.page == "tbm_write":
    nav_col1, nav_col2, nav_spacer = st.columns([1, 1, 2]) 
    with nav_col1:
        if st.button("⬅️ 메인으로"):
            st.session_state.page = "main"; st.rerun()
    with nav_col2:
        if st.button("📊 현황 확인"):
            st.session_state.page = "tbm_status"; st.rerun()
            
    st.markdown("---")
    st.subheader("🏗️ TBM 점검 작성")
    
    c1, c2 = st.columns(2)
    with c1: selected_team = st.selectbox("부서 선택", list(team_data.keys()))
    with c2: 
        final_name = st.text_input("성함 입력", placeholder="성함 입력").strip()
        if final_name:
            matches = [n for n in team_data[selected_team] if final_name in n]
            if matches: st.caption(f"💡 명단 확인: {', '.join(matches)}")

    selected_job = st.selectbox("금일 작업명", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"])

    st.write("**✅ 공통 안전점검 사항**")
    col_config = {
        "작업명": st.column_config.TextColumn("항목", width=60), 
        "점검내용": st.column_config.TextColumn("점검내용", width=220), 
        "확인": st.column_config.CheckboxColumn("확인", width=40)
    }
    common_list = [
        {"작업명": "작업계획", "점검내용": "작업순서 및 역할 분담 완료", "확인": False},
        {"작업명": "보호구착용", "점검내용": "안전모/화/장갑 등 착용", "확인": False},
        {"작업명": "공구점검", "점검내용": "사용 공구 상태 이상없음", "확인": False},
        {"작업명": "작업장정리", "점검내용": "바닥 미끄럼/장애물 제거", "확인": False},
        {"작업명": "위험구역설정", "점검내용": "출입통제, 안전표지 설치", "확인": False},
        {"작업명": "전원차단확인", "점검내용": "LOTO 적용 확인", "확인": False},
        {"작업명": "비상대응확인", "점검내용": "소화기/비상연락망 확인", "확인": False}
    ]
    
    df_common = st.data_editor(pd.DataFrame(common_list), hide_index=True, width='stretch', column_config=col_config)

    if selected_job and selected_job not in ["", "공통작업"]:
        st.write(f"**⚠️ {selected_job} 추가 점검**")
        st.data_editor(pd.DataFrame(specific_checks[selected_job]), hide_index=True, width='stretch', column_config=col_config)

    st.write("**✒️ 최종 확인 서명**")
    st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=130, width=310, drawing_mode="freedraw", key="canvas_tbm")

    if st.button("점검 완료 및 저장하기"):
        if not final_name or not selected_job or not df_common["확인"].all():
            st.warning("⚠️ 필수 항목(이름, 작업명, 모든 점검 확인)을 체크해 주세요.")
        else:
            with st.spinner('구글 시트에 저장 중...'):
                try:
                    kst = timezone(timedelta(hours=9))
                    now = datetime.datetime.now(kst)
                    sheet.append_row([now.strftime('%Y-%m-%d'), selected_team, final_name, selected_job, "정상", now.strftime('%H:%M:%S'), "✅ 완료", ""])
                    st.success("✅ 점검 결과가 저장되었습니다!")
                    st.balloons()
                    time.sleep(2)
                    st.session_state.page = "main"; st.rerun()
                except:
                    st.error("구글 시트 저장에 실패했습니다. 네트워크를 확인해 주세요.")

# 📊 현황 확인 페이지
elif st.session_state.page == "tbm_status":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    st.subheader("📊 실시간 점검 현황")
    
    try:
        raw_data = sheet.get_all_values()
        if len(raw_data) > 1:
            df_all = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            col1, col2 = st.columns(2)
            with col1:
                s_date = st.date_input("날짜 선택", datetime.datetime.now(timezone(timedelta(hours=9))).date())
            with col2:
                s_name = st.text_input("이름 검색", placeholder="검색할 이름 입력").strip()
            
            df_f = df_all[df_all['날짜'] == s_date.isoformat()]
            if s_name:
                name_col = df_all.columns[2] 
                df_f = df_f[df_f[name_col].str.contains(s_name, na=False)]
            
            if not df_f.empty:
                st.write(f"🔎 검색 결과: {len(df_f)}건")
                st.dataframe(df_f.iloc[::-1], width='stretch', hide_index=True)
            else:
                st.info("해당 조건의 데이터가 없습니다.")
        else:
            st.info("저장된 점검 데이터가 없습니다.")
    except Exception as e:
        st.error(f"데이터를 불러올 수 없습니다: {e}")

# ⚙️ 관리자 페이지
elif st.session_state.page == "tbm_admin":
    if st.button("⬅️ 메인으로 돌아가기"):
        st.session_state.page = "main"; st.rerun()
    
    if not st.session_state.admin_logged_in:
        st.subheader("⚙️ 관리자 로그인")
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if pw == "admin@123": 
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    else:
        st.subheader("⚙️ 시스템 설정")
        new_notice = st.text_area("📢 공지사항 수정", st.session_state.safety_notice, height=150)
        if st.button("공지사항 업데이트"):
            st.session_state.safety_notice = new_notice
            st.success("공지사항이 저장되었습니다.")
        
        st.markdown("---")
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False
            st.rerun()
