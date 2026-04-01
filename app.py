import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="현장 TBM 안전점검", layout="centered")

# 2. [명단 데이터] 관리자님이 말씀하신 80명 수준의 팀원 명단 (최종 정비)
WORKER_DATA = {
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
# 3. 구글 시트 연결
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"시트 연결 초기 설정 에러: {e}")

st.title("👷 오늘의 TBM 안전 점검")
st.write("---")

# 4. 입력 폼
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
                # 0. 시트에서 데이터 읽어오기 (없으면 빈 데이터프레임 생성)
                try:
                    existing_df = conn.read(ttl="0s")
                except:
                    existing_df = pd.DataFrame(columns=["날짜", "소속", "이름", "상태", "체크시간", "비고"])

                # 1. 새 데이터 생성
                new_row = pd.DataFrame([{
                    "날짜": str(date),
                    "소속": sel_team,
                    "이름": sel_name,
                    "상태": "✅ 점검완료",
                    "체크시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "비고": note
                }])
                
                # 2. 데이터 합치기
                if existing_df.empty:
                    updated_df = new_row
                else:
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                
                # 3. 구글 시트에 업데이트
                conn.update(data=updated_df)
                
                st.success(f"{sel_name}님, 안전하게 저장되었습니다!")
                st.balloons()
            except Exception as e:
                st.error(f"저장 실패! 에러 내용: {e}")
                st.info("💡 팁: 구글 시트가 '링크가 있는 모든 사용자 - 편집자'로 설정되어 있는지 확인해 주세요.")
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
