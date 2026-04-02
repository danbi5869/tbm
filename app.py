import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import pandas as pd
from streamlit_drawable_canvas import st_canvas
from PIL import Image  # 이미지 처리를 위해 꼭 필요합니다!

# 1. 앱 설정 (방금 올린 마스코트 이미지 적용)
try:
    img = Image.open("safety_mascot.png") # 올리신 파일명과 똑같아야 합니다.
except:
    img = "⛑️" # 파일 로딩 실패 시 대신 나올 이모지

st.set_page_config(
    page_title="TBM 점검",
    page_icon=img, # 여기가 아이콘을 정하는 부분입니다!
    layout="centered"
)

# --- 이후 기존 코드(인증, 데이터 등)는 그대로 두시면 됩니다 ---
