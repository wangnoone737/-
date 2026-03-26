import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from io import BytesIO
from openpyxl import load_workbook

# [v8.8-Final] 통합 파일 업로드 및 전도사별 개인 설정 복구
st.set_page_config(page_title="Strategic Master v8.8", layout="wide")

class FinalEngineV88:
    STEPS = ["마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 전도사 인정"]

    @st.cache_data(show_spinner=False)
    def fast_scan(file_content, sheet_name):
        """엑셀 데이터를 메모리에서 즉시 스캔 (속도 최적화)"""
        wb = load_workbook(BytesIO(file_content), data_only=True)
        ws = wb[sheet_name]
        return " ".join([str(c.value) for r in ws.iter_rows() for c in r if c.value])

    @staticmethod
    def generate_unique_report(name, adm, text, sit, strat):
        """수강생 고유 데이터를 기반으로 문장을 생성"""
        curr_step = next((s for s in reversed(FinalEngineV88.STEPS) if s in text), "관찰 단계")
        pos_hits = re.findall(r'(감사|확신|인정|기쁨|성장|변화)', text)
        neg_hits = re.findall(r'(의심|불안|부모|친구|바쁨|세상|영상|유튜브)', text)
        
        if len(neg_hits) > len(pos_hits):
            psy_status = f"현재 {name} 님은 외부적 환경 요인({', '.join(set(neg_hits[:2]))})에 의한 심리적 간섭이 강합니다."
        elif len(pos_hits) > 0:
            psy_status = f"{name} 님은 {curr_step} 과정의 말씀을 자기화하려는 의지가 '{pos_hits[0]}' 등의 표현에서 드러납니다."
        else:
            psy_status = f"{curr_step} 단계의 핵심 목표에 대한 개인적 피드백 확인이 필요합니다."

        risk_score = 60 if any(k in sit for k in ['비방', '영상', '유튜브']) else 30
        risk_score += (len(neg_hits) * 7) - (len(pos_hits) * 3)
        risk_score = max(10, min(99, risk_score + (len(text) % 5)))

        report = f"## 🔱 {name} 수강생 정밀 전략\n\n"
        report += f"### 📌 데이터 진단: {psy_status}\n\n"
        report += f"### ⚡ 담당 관리자({adm['id']}) 맞춤 가이드\n"
        report += f"- **성향 대응:** {adm['mbti']} 및 {adm['ennea']} 에너지를 활용하여 " + ("논리적 확신" if 'T' in adm['mbti'] else "정서적 공감") + " 위주로 접근하십시오.\n"
        report += f"- **전략 연계:** 기수 전략인 '{strat[:10]}...'을 수강생 상황에 맞게 변형하여 적용하십시오.\n\n"
        report += f"### 🚩 분석 결과: 위기 지수 {risk_score}점"
        
        return report, risk_score

# --- UI 설정 (통합 파일 업로드 칸 복구) ---
with st.sidebar:
    st.header("⚙️ 전략 엔진 v8.8")
    
    # [복구] 전체 출석부 통합 업로드 칸
    st.subheader("📁 데이터 소스")
    main_file = st.file_uploader("전체 출석부 파일 업로드 (xlsx)", type=["xlsx"])
    
    st.divider()
    
    # 전도사별 개인 설정 (성별, MBTI 등)
    st.subheader("👤 담당자별 세부 설정")
    admins = {}
    for t in ["A", "B", "C"]:
        with st.expander(f"{t}전도사/반 설정"):
            g = st.radio("성별", ["남", "여"], key=f"v88_g_{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"v88_m_{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"v88_e_{t}")
            admins[t] = {'id': t, 'gender': g, 'mbti': m, 'ennea': e}

# --- 메인 화면 ---
st.title("🏛️ 전략 시뮬레이션 시스템 v8.8")
l, r = st.columns([1, 1.2])

with l:
    mode = st.radio("분석 모드", ["기수 전체 상황 및 전략", "개인 상황 및 전략"], horizontal=True)
    target = st.text_input("수강생 성명") if mode == "개인 상황 및 전략" else ""
    sit_in = st.text_area("🌐
