import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from io import BytesIO
from openpyxl import load_workbook

# [v8.8-Ultimate] 통합 업로드 + 개별 업로드 완벽 공존 버전
st.set_page_config(page_title="Strategic Master v8.8", layout="wide")

class FinalEngineV88:
    STEPS = ["마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 전도사 인정"]

    @st.cache_data(show_spinner=False)
    def fast_scan(file_content, sheet_name):
        wb = load_workbook(BytesIO(file_content), data_only=True)
        ws = wb[sheet_name]
        return " ".join([str(c.value) for r in ws.iter_rows() for c in r if c.value])

    @staticmethod
    def generate_unique_report(name, adm, text, sit, strat):
        curr_step = next((s for s in reversed(FinalEngineV88.STEPS) if s in text), "관찰 단계")
        pos_hits = re.findall(r'(감사|확신|인정|기쁨|성장|변화)', text)
        neg_hits = re.findall(r'(의심|불안|부모|친구|바쁨|세상|영상|유튜브)', text)
        
        if len(neg_hits) > len(pos_hits):
            psy_status = f"현재 {name} 님은 외부적 환경 요인({', '.join(set(neg_hits[:2]))})에 의한 심리적 간섭이 강합니다."
        elif len(pos_hits) > 0:
            psy_status = f"{name} 님은 {curr_step} 과정의 말씀을 자기화하려는 의지가 뚜렷합니다."
        else:
            psy_status = f"{curr_step} 단계의 피드백이 부족하여 밀착 확인이 필요합니다."

        risk_score = 60 if any(k in sit for k in ['비방', '영상', '유튜브']) else 30
        risk_score += (len(neg_hits) * 7) - (len(pos_hits) * 3)
        risk_score = max(10, min(99, risk_score + (len(text) % 5)))

        report = f"## 🔱 {name} 수강생 정밀 전략\n\n"
        report += f"### 📌 진단: {psy_status}\n\n"
        report += f"### ⚡ 담당자({adm['id']}) 가이드: {adm['mbti']}/{adm['ennea']}\n"
        report += f"- 전략인 '{strat[:10]}...'을 적용하여 대응하십시오.\n\n"
        report += f"### 🚩 위기 지수: {risk_score}점"
        
        return report, risk_score

# --- UI 설정 (통합 + 개별 업로드 모두 배치) ---
with st.sidebar:
    st.header("⚙️ 전략 엔진 v8.8")
    
    # 1. [기능 A] 전체 출석부 통합 업로드 (최상단 고정)
    st.subheader("📁 통합 데이터 소스")
    main_combined_file = st.file_uploader("전체 통합 출석부 (xlsx)", type=["xlsx"], key="main_all")
    
    st.divider()
    
    # 2. [기능 B] 전도사별 개별 설정 및 파일 업로드
    st.subheader("👤 담당자별 개별 설정")
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"{t}전도사 설정 및 개별 파일"):
            # 개별 파일 업로드 칸 (통합 파일이 없을 때 사용하거나 덮어쓰기용)
            f = st.file_uploader(f"{t}반 전용 파일", type=["xlsx"], key=f"v88_f_{t}")
            g = st.radio("성별", ["남", "여"], key=f"v88_g_{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"v88_m_{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"v88_e_{t}")
            admins.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

# --- 메인 분석 화면 ---
st.title("🏛️ 전략 시뮬레이션 시스템 v8.8")
l, r = st.columns([1, 1.2])

with l:
    mode = st.radio("분석 선택", ["기수 전체", "개인 전략"], horizontal=True)
    target = st.text_input("수강생 이름") if mode == "개인 전략" else ""
    sit_in = st.text_area("🌐 발생 상황", height=80)
    strat_in = st.text_area("🛡️ 대응 전략", height=80)
    
    if st.button("정밀 분석 실행", use_container_width=True):
        final_res = []
        
        # 1. 통합 파일이 있는지, 아니면 개별 파일들이 있는지 확인
        active_files = []
        if main_combined_file:
            # 통합 파일이 있으면 모든 전도사에게 이 파일을 할당 (기본 로직)
            for adm in admins:
                active_files.append({'adm': adm, 'file': main_combined_file})
        else:
            # 통합 파일이 없으면 개별적으로 올린 파일들만 수집
            for adm in admins:
                if adm['file']:
                    active_files.append({'adm': adm, 'file': adm['file']})
        
        if not active_files:
            st.error("통합 파일 또는 개별 파일을 업로드해 주세요.")
        else:
            for item in active_files:
                adm = item['adm']
                file_bytes = item['file'].getvalue()
                xl = pd.ExcelFile(item['file'])
                for s_n in xl.sheet_names:
                    name = re.sub(r'[^가-힣]', '', s_n)
                    if len(name) < 2 or any(k in name for k in ['출석', '양식', '기본', '단계']): continue
                    
                    full_txt = FinalEngineV88.fast_scan(file_bytes, s_n)
                    rpt, risk = FinalEngineV88.generate_unique_report(name, adm, full_txt, sit_in, strat_in)
                    
                    if mode == "개인 전략":
                        if name == target:
                            final_res.append({'name': name, 'rpt': rpt, 'risk': risk, 'type': 'deep'})
                    else:
                        final_res.append({'name': name, 'rpt': rpt, 'risk': risk, 'type': 'total'})
            
            st.session_state['v88_final'] = final_res

# --- 결과 출력 ---
if 'v88_final' in st.session_state:
    data = st.session_state['v88_final']
    with r:
        if not data: st.warning("데이터를 찾을 수 없습니다.")
        elif data[0]['type'] == 'deep': st.success(data[0]['rpt'])
        else:
            avg_val = sum([x['risk'] for x in data]) / len(data) if data else 0
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-avg_val, title={'text': "🛡️ 전체 안전도"})), use_container_width=True)
            for item in data:
                with st.expander(f"➔ {item['name']} (위기: {item['risk']}점)"):
                    st.markdown(item['rpt'])
