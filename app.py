import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="현장 TBM 안전점검", layout="centered")

# 2. [명단 데이터] 80명 팀원 명단 (코드 내 직접 관리)
WORKER_DATA = {
    "운영팀": ["김한규", "김병배", "엄기태", "한효석", "신기영", "한진희", "노단비", "박진용"],
    "기술/정비": ["황종연", "김성태", "배욱"],
    "입출창": ["이천형", "전동길", "허유정", "서대영"],
    "중요장치장": ["송진수", "임대권", "이준혁", "김명철"],
    "차체수선장": ["최덕수", "반상민"],
    "출입문": ["김지훈", "추동일", "한지훈", "백승주", "최창열", "윤성현"],
    "차체": ["윤종혁", "박종환", "최규현"],
    "냉방장치": ["김정혁", "김기훈", "설태길"],
    "회전기장/TM/CM": ["박기하", "이성보", "박석희", "오현택", "유상훈", "안상복", "김태경"],
    "대차장": ["임청용", "정호영"],
    "제동/현가/제동": ["정성목", "이태수", "우원진", "조인호", "정준혁", "문주호", "박재호", "이정희", "김대현"]
}

# 3. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("👷 오늘의 TBM 안전 점검")
st.write("---")

# 4. 입력 폼 (소속, 날짜, 이름, 상태, 비고)
with st.form("tbm_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        sel_team = st.selectbox("소속 팀", list(WORKER_DATA.keys()))
    with col2:
        sel_name = st.selectbox("성함", WORKER_DATA[sel_team])
        
    date = st.date_input("날짜", datetime.now())
    
    st.write("---")
    st.subheader("✅ 안전 체크리스트")
    q1 = st.checkbox("1. 개인 보호구(안전모, 안전화 등)를 올바르게 착용했는가?")
    q2 = st.checkbox("2. 금일 작업 구간 내 위험 요인을 확인하고 공유했는가?")
    q3 = st.checkbox("3. 비상 대피로 및 소화기 위치를 숙지했는가?")
    q4 = st.checkbox("4. 작업에 임하기에 본인의 컨디션이 양호한가?")
    
    note = st.text_input("비고 (특이사항)", placeholder="특이사항이 있으면 입력하세요.")
    
    submit = st.form_submit_button("점검 완료 및 제출하기")

    if submit:
        if q1 and q2 and q3 and q4:
            try:
                existing_df = conn.read(ttl="0s")
                new_row = pd.DataFrame([{
                    "날짜": str(date),
                    "소속": sel_team,
                    "이름": sel_name,
                    "상태": "✅ 점검완료",
                    "체크시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "비고": note
                }])
                updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                
                st.success(f"{sel_name}님, 점검 정보가 기록되었습니다!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error("데이터 저장 실패! 구글 시트 주소 설정을 확인하세요.")
        else:
            st.warning("모든 체크리스트에 체크해야 제출할 수 있습니다.")

# 5. 참여 현황
st.write("---")
st.subheader("📊 오늘의 참여 현황")
try:
    live_df = conn.read(ttl="0s")
    if not live_df.empty:
        today_str = str(datetime.now().date())
        today_df = live_df[live_df['날짜'] == today_str]
        if not today_df.empty:
            st.dataframe(today_df[['이름', '소속', '체크시간', '상태']], use_container_width=True)
        else:
            st.info("아직 오늘 참여한 팀원이 없습니다.")
except:
    st.write("현황 데이터를 불러오는 중입니다...")
