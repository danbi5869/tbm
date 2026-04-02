import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# 1. 인증 및 권한 설정
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def get_sheet():
    try:
        # Streamlit Cloud의 Secrets에 저장된 정보를 불러옵니다.
        creds_info = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # 관리 중인 구글 시트 ID (어제 확인한 ID)
        sheet_id = "1ubTkHSTQbN4adDuPueDO_jqj8XN1RYbh1j5H-NnBBRc"
        return client.open_by_key(sheet_id).get_worksheet(0)
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None

# 앱 화면 구성
st.title("🏗️ TBM 점검 기록 시스템")

# 시트 연결
sheet = get_sheet()

if sheet:
    st.success("✅ 구글 시트 연결 성공 (쓰기 권한 확보)")

    # 입력 폼 예시 (기존 코드가 있다면 이 부분을 활용해 데이터를 받으세요)
    with st.form("tbm_form"):
        user_team = st.selectbox("소속 팀", ["공무팀", "안전팀", "현장1팀", "현장2팀"])
        user_name = st.text_input("이름")
        status = st.radio("점검 상태", ["정상", "조치 필요"])
        remark = st.text_area("비고(특이사항)")
        
        submitted = st.form_submit_button("기록 저장하기")
        
        if submitted:
            if not user_name:
                st.warning("이름을 입력해 주세요.")
            else:
                # 저장할 데이터 리스트 생성
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_row = [
                    datetime.date.today().isoformat(), # 날짜
                    user_team,                         # 소속
                    user_name,                         # 이름
                    status,                            # 상태
                    now,                               # 체크시간
                    remark                             # 비고
                ]
                
                try:
                    sheet.append_row(new_row)
                    st.success("🎉 구글 시트에 데이터가 성공적으로 저장되었습니다!")
                    st.balloons()
                except Exception as e:
                    st.error(f"저장 중 오류 발생: {e}")
