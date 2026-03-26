import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from io import BytesIO
from openpyxl import load_workbook

# [v8.8-Final-Fixed] 문법 오류 수정 및 통합 파일 업로드 구조
st.set_page_config(page_title="Strategic Master v8.8", layout="wide")

class FinalEngineV88:
    STEPS = ["마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 전도사 인정"]

    @st.cache_data(show_spinner=False)
    def fast_scan(file_content, sheet_name):
        """엑셀 데이터를 메모리에서 즉시 스캔"""
        wb = load_workbook(BytesIO(file_content), data_only=True)
        ws = wb[sheet_name]
        return " ".join([str(c.value) for r in ws.iter_rows() for c in r if c.value])

    @staticmethod
    def generate_unique_report(name, adm, text, sit, strat):
        """수강생 고유 데이터를 기반으로 리포트 생성"""
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
        report += f"- **전략 연계:** 기수 전략을 수강생 상황에 맞게 변형하여 적용하십시오.\n\n"
        report += f"### 🚩 분석 결과: 위기 지수 {risk_score}점"
        
        return report, risk_score

# --- UI 설정 (스크린샷에 나타난 오류 지점 수정) ---
with st.sidebar:
    st.header("⚙️ 시스템 설정 v8.8")
    
    # 1. 파일 업로드 칸 (전체 출석부)
    st.subheader("📁 데이터 소스")
    main_file = st.file_uploader("전체 출석부 파일 업로드 (xlsx)", type=["xlsx"])
    
    st.divider()
    
    # 2. 전도사별 개인 설정
    st.subheader("👤 담당자별 세부 설정")
    admins = {}
    for t in ["A", "B", "C"]:
        with st.expander(f"{t}전도사/반 설정"):
            g = st.radio("성별", ["남", "여"], key=f"v88_g_{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"v88_m_{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"v88_e_{t}")
            admins[t] = {'id': t, 'gender': g, 'mbti': m, 'ennea': e}

# --- 메인 화면 ---
st.title("🏛️ 연동비 163기 관리 대시보드")
l, r = st.columns([1, 1.2])

with l:
    mode = st.radio("분석 모드", ["기수 전체 상황 및 전략", "개인 상황 및 전략"], horizontal=True)
    target = st.text_input("수강생 성명") if mode == "개인 상황 및 전략" else ""
    
    # [SyntaxError 해결 지점] 따옴표와 괄호를 명확히 닫았습니다.
    sit_in = st.text_area("🌐 발생 상황", height=100, placeholder="현재 상황을 입력하세요.")
    strat_in = st.text_area("🛡️ 대응 전략", height=100, placeholder="수립한 전략을 입력하세요.")
    
    if st.button("정밀 분석 실행", use_container_width=True):
        if not main_file:
            st.error("전체 출석부 파일을 업로드해 주세요.")
        else:
            file_bytes = main_file.getvalue()
            xl = pd.ExcelFile(main_file)
            final_res = []
            
            for s_n in xl.sheet_names:
                name = re.sub(r'[^가-힣]', '', s_n)
                if len(name) < 2 or any(k in name for k in ['출석', '양식', '기본', '단계']): continue
                
                # 기본 A전도사 설정 적용 (필요시 로직 확장 가능)
                current_adm = admins["A"]
                
                full_txt = FinalEngineV88.fast_scan(file_bytes, s_n)
                rpt, risk = FinalEngineV88.generate_unique_report(name, current_adm, full_txt, sit_in, strat_in)
                
                if mode == "개인 상황 및 전략":
                    if name == target:
                        final_res.append({'name': name, 'rpt': rpt, 'risk': risk, 'type': 'deep'})
                        break
                else:
                    final_res.append({'name': name, 'rpt': rpt, 'risk': risk, 'type': 'total'})
            
            st.session_state['v88_final'] = final_res

# --- 결과 출력 ---
if 'v88_final' in st.session_state:
    data = st.session_state['v88_final']
    with r:
        if not data:
            st.warning("일치하는 수강생 데이터가 없습니다.")
        elif data[0]['type'] == 'deep':
            st.success(data[0]['rpt'])
        else:
            avg_val = sum([x['risk'] for x in data]) / len(data) if data else 0
            st.plotly_chart(go.Figure(go.Indicator(
                mode="gauge+number", value=100-avg_val, 
                title={'text': "🛡️ 전체 안전도"})), use_container_width=True)
            for item in data:
                with st.expander(f"➔ {item['name']} (위기: {item['risk']}점)"):
                    st.markdown(item['rpt'])
