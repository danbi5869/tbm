import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="현장 TBM 안전점검", layout="centered")

# 2. [명단 데이터] 관리자님이 말씀하신 80명 수준의 팀원 명단 (최종 정비)
WORKER_DATA = {
    "운영팀": ["김한규", "김병배", "엄기태", "한효석", "신기영", "한진희", "노단비", "박진용"],
    "기술/정비": ["황종연", "김성태", "배욱", "이민호", "박준수"],
    "입출창": ["이천형", "전동길", "허유정", "서대영", "강현우"],
    "중요장치장": ["송진수", "임대권", "이준혁", "김명철", "조상현"],
    "차체수선장": ["최덕수", "반상민", "유재석", "박명수"],
    "출입문": ["김지훈", "추동일", "한지훈", "백승주", "최창열", "윤성현", "이정재"],
    "차체": ["윤종혁", "박종환", "최규현", "정우성"],
    "냉방장치": ["김정혁", "김기훈", "설태길", "차태현"],
    "회전기장/TM/CM": ["박기하", "이성보", "박석희", "오현택", "유상훈", "안상복", "김태경", "이승기"],
    "대차장": ["임청용", "정호영", "강호동"],
    "제동/현가": ["정성목", "이태수", "우원진", "조인호", "정준혁", "문주호", "박재호", "이정희", "김대현", "장동건"]
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
