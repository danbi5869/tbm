import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd # 데이터 표 표시용
from streamlit_drawable_canvas import st_canvas

# 1. 인증 및 권한 설정
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

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

# --- [정확한 소속 및 명단 데이터] ---
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

# --- 앱 화면 구성 ---
st.set_page_config(page_title="TBM 점검 기록부", layout="centered")
st.title("🏗️ TBM 점검 및 안전일지")

sheet = get_sheet()

if sheet:
    # 1. 소속 및 성함 선택
    col1, col2 = st.columns(2)
    with col1:
        selected_team = st.selectbox("소속 선택", list(team_data.keys()))
    with col2:
        member_list = team_data[selected_team]
        selected_name = st.selectbox("성함 선택", member_list)

    st.markdown("---")
    st.subheader(f"📍 {selected_team} - {selected_name}님 점검")
    
    # 2. 체크리스트
    q1 = st.checkbox("✅ 개인보호구 착용 상태 확인")
    q2 = st.checkbox("✅ 작업 전 위험요인 파악 및 공유")
    q3 = st.checkbox("✅ 사용 장비 점검 완료")
    
    status = "정상" if (q1 and q2 and q3) else "조치 필요"
    remark = st.text_area("특이사항 (비고)")

    # 3. 서명란
    st.write("✒️ **서명 (박스 안에 성함을 정자로 써주세요)**")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        width=300,
        drawing_mode="freedraw",
        key="canvas",
    )

    # 4. 저장 버튼
    if st.button("점검 완료 및 시트 저장", use_container_width=True):
        if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) == 0:
            st.warning("⚠️ 서명을 완료해야 저장할 수 있습니다.")
        else:
            now_time = datetime.datetime.now().strftime('%H:%M:%S')
            today_date = datetime.date.today().isoformat()
            
            new_row = [today_date, selected_team, selected_name, status, now_time, remark, "서명완료"]
            
            try:
                sheet.append_row(new_row)
                st.success(f"🎉 {selected_name}님, 저장이 완료되었습니다!")
                st.balloons()
                st.rerun() # 저장 후 목록 새로고침
            except Exception as e:
                st.error(f"저장 중 오류 발생: {e}")

    # 5. 참여 확인 기능 (오늘 기록 불러오기)
    st.markdown("---")
    st.subheader("📋 오늘의 나의 점검 기록")
    
    try:
        # 전체 데이터 불러오기
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            today_str = datetime.date.today().isoformat()
            
            # 오늘 날짜 + 선택한 이름과 일치하는 데이터만 필터링
            my_today_records = df[(df['날짜'] == today_str) & (df['이름'] == selected_name)]
            
            if not my_today_records.empty:
                st.write(f"✅ {selected_name}님은 오늘 점검을 완료하셨습니다.")
                # 필요한 열만 추출해서 표시
                display_df = my_today_records[['시간', '소속', '이름', '상태']]
                st.table(display_df)
            else:
                st.write("❔ 아직 오늘 기록된 점검 내역이 없습니다.")
        else:
            st.write("시트에 데이터가 없습니다.")
    except Exception as e:
        st.write("기록을 불러오는 중입니다...") # 시트 헤더가 없거나 초기 단계일 때
