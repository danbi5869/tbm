import streamlit as st
from PIL import Image
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import time
from datetime import timezone, timedelta

# 1. 앱 설정 및 데이터 세팅 (기존과 동일)
# ... (생략)

# 2. 구글 시트 연결
# ... (생략)

# --- 메인 TBM 점검 화면 ---
if sheet:
    tab1, tab2, tab3 = st.tabs(["📝 TBM 점검", "📊 점검 현황", "⚙️ 관리자"])

    with tab1:
        st.subheader("🏗️ TBM 안전 점검")
        
        c1, c2 = st.columns(2)
        with c1:
            selected_team = st.selectbox("부서 선택", list(team_data.keys()), key="dept_s")
        
        with c2:
            # ✅ [핵심 수정] multiselect를 사용하여 검색 + 자유 입력을 구현
            # max_selections=1로 설정하여 딱 한 명의 이름만 담기게 합니다.
            user_input = st.multiselect(
                "성함 검색 또는 직접 입력",
                options=team_data[selected_team],
                default=None,
                max_selections=1,
                placeholder="이름 검색 또는 직접 입력 후 Enter",
                key="name_hybrid_input"
            )
            
            # 리스트 형태([이름])로 반환되므로 첫 번째 요소를 가져옵니다.
            final_name = user_input[0] if user_input else ""

        if final_name:
            st.info(f"확인된 성함: **{final_name}**")

        # --- 나머지 점검 로직 ---
        selected_job = st.selectbox("금일 작업명 선택", ["", "공통작업", "분해작업", "중량물취급", "전기작업", "세척작업", "조립작업", "시험/가동"], key="job_s")

        # (중략: 점검표 및 서명 캔버스 코드)
        st.markdown("---")
        st.write("✒️ **서명**")
        canvas_result = st_canvas(stroke_width=3, stroke_color="#000000", background_color="#f8f9fa", height=130, width=310, drawing_mode="freedraw", key="canvas_main")

        # --- 저장 버튼 ---
        if st.button("점검 완료 및 저장"):
            if not final_name:
                st.warning("⚠️ 성함을 입력하거나 선택해 주세요.")
            elif not selected_job:
                st.warning("⚠️ 작업명을 선택해 주세요.")
            elif canvas_result.json_data and len(canvas_result.json_data["objects"]) == 0:
                st.warning("⚠️ 서명을 완료해 주세요.")
            else:
                with st.spinner('데이터 저장 중...'):
                    try:
                        kst = timezone(timedelta(hours=9))
                        now = datetime.datetime.now(kst)
                        # ✅ 여기서 final_name(검색어 혹은 직접 입력값)이 시트에 저장됩니다.
                        sheet.append_row([
                            now.strftime('%Y-%m-%d'), 
                            selected_team, 
                            final_name, 
                            selected_job, 
                            "정상", 
                            now.strftime('%H:%M:%S'), 
                            "✅ 완료", 
                            ""
                        ])
                        st.success(f"🎉 {final_name}님, 점검 기록이 완료되었습니다!")
                        st.balloons(); time.sleep(2); st.rerun()
                    except Exception as e:
                        st.error(f"저장 오류: {e}")
