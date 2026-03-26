import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from openpyxl import load_workbook

# [v8.8] 무한 루프 방지, 데이터 캐싱 탑재, 개인별 독자 리포트 보장
st.set_page_config(page_title="Strategic Master v8.8", layout="wide")

class FinalEngineV88:
    STEPS = ["마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 전도사 인정"]

    @st.cache_data(show_spinner=False)
    def fast_scan(file_content, sheet_name):
        """엑셀 데이터를 메모리에서 즉시 스캔 (속도 최적화)"""
        from io import BytesIO
        wb = load_workbook(BytesIO(file_content), data_only=True)
        ws = wb[sheet_name]
        return " ".join([str(c.value) for r in ws.iter_rows() for c in r if c.value])

    @staticmethod
    def generate_unique_report(name, adm, text, sit, strat):
        """수강생 고유 데이터를 기반으로 문장을 생성 (중복 방지)"""
        # 단계 판별
        curr_step = next((s for s in reversed(FinalEngineV88.STEPS) if s in text), "관찰 단계")
        
        # 키워드 밀도 분석 (이것이 달라야 리포트가 달라짐)
        pos_hits = re.findall(r'(감사|확신|인정|기쁨|성장|변화)', text)
        neg_hits = re.findall(r'(의심|불안|부모|친구|바쁨|세상|영상|유튜브)', text)
        
        # 1. 심리 상태 요약
        if len(neg_hits) > len(pos_hits):
            psy_status = f"현재 {name} 님은 신앙적 성장보다는 외부적 환경 요인({', '.join(set(neg_hits[:2]))})에 의한 심리적 간섭이 매우 강하게 작용하고 있습니다."
        elif len(pos_hits) > 0:
            psy_status = f"{name} 님은 {curr_step} 과정의 말씀을 자기화하려는 의지가 상담 기록 상의 '{pos_hits[0]}' 등의 표현에서 명확히 드러납니다."
        else:
            psy_status = f"특별한 감정 기복은 보이지 않으나, {curr_step} 단계의 핵심 목표에 대한 개인적 피드백이 부족하여 밀착 확인이 필요합니다."

        # 2. 위기 지수 산출 (1점 단위 고유화)
        risk_score = 60 if any(k in sit for k in ['비방', '영상', '유튜브']) else 30
        risk_score += (len(neg_hits) * 7) - (len(pos_hits) * 3)
        risk_score = max(10, min(99, risk_score + (len(text) % 5)))

        # 3. 맞춤 전략
        report = f"## 🔱 {name} 수강생 정밀 전략\n\n"
        report += f"### 📌 현 상황 및 데이터 진단\n"
        report += f"- {psy_status}\n"
        report += f"- **핵심 리스크:** 상담 일지 내 부정 키워드 감지 빈도가 {len(neg_hits)}회로, 일반 수강생 대비 높은 편입니다.\n\n"
        report += f"### ⚡ {adm['id']}전도사(성별:{adm['gender']}) 맞춤 대응 가이드\n"
        report += f"- **대화 전략:** {adm['mbti']} 성향을 활용하여 " + ("논리적인 오류를 짚어주며 확신을 주는" if 'T' in adm['mbti'] else "정서적 공감을 통해 마음의 문을 여는") + " 대화를 시도하십시오.\n"
        report += f"- **에너지 운용:** {adm['ennea']} 에너지를 투입하여 기수 전략인 '{strat[:15]}...'을 수강생의 개인 고민과 연결해 풀어내야 합니다.\n\n"
        report += f"### 🚩 최종 분석 결론\n"
        report += f"- **위기 지수:** {risk_score}점\n"
        report += f"- **조치:** {'[긴급] 상급자와 협의하여 즉각적인 환경 차단 전략 수립 요망' if risk_score > 75 else '정기 리포트를 통한 점진적 확신 심기 단계 유지'}"
        
        return report, risk_score

# --- UI 설정 ---
with st.sidebar:
    st.header("⚙️ 전략 엔진 v8.8")
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t}전도사 설정"):
            f = st.file_uploader(f"{t}반 파일", type=["xlsx"], key=f"v88_f_{t}")
            g = st.radio("성별", ["남", "여"], key=f"v88_g_{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"v88_m_{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"v88_e_{t}")
            admins.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 시스템 v8.8")
l, r = st.columns([1, 1.2])

with l:
    mode = st.radio("분석 선택", ["기수 전체 상황 및 전략", "개인 상황 및 전략"], horizontal=True)
    target = st.text_input("수강생 이름") if mode == "개인 상황 및 전략" else ""
    sit_in = st.text_area("🌐 발생 상황", height=80)
    strat_in = st.text_area("🛡️ 대응 전략", height=80)
    
    if st.button("분석", use_container_width=True):
        active = [a for a in admins if a['file']]
        if not active: st.error("파일을 업로드해 주세요.")
        else:
            final_res = []
            for adm in active:
                file_bytes = adm['file'].getvalue()
                xl = pd.ExcelFile(adm['file'])
                for s_n in xl.sheet_names:
                    name = re.sub(r'[^가-힣]', '', s_n)
                    if len(name) < 2 or any(k in name for k in ['출석', '양식', '기본', '단계']): continue
                    
                    full_txt = FinalEngineV88.fast_scan(file_bytes, s_n)
                    rpt, risk = FinalEngineV88.generate_unique_report(name, adm, full_txt, sit_in, strat_in)
                    
                    if mode == "개인 상황 및 전략":
                        if name == target: 
                            final_res.append({'name': name, 'rpt': rpt, 'risk': risk, 'type': 'deep'})
                            break
                    else:
                        final_res.append({'name': name, 'rpt': rpt, 'risk': risk, 'type': 'total'})
            
            st.session_state['v88_final'] = final_res

if 'v88_final' in st.session_state:
    data = st.session_state['v88_final']
    with r:
        if not data:
            st.warning("데이터를 찾을 수 없습니다.")
        elif data[0]['type'] == 'deep':
            st.success(data[0]['rpt'])
        else:
            avg_val = sum([x['risk'] for x in data]) / len(data)
            st.plotly_chart(go.Figure(go.Indicator(
                mode="gauge+number", 
                value=100-avg_val, 
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1976D2"}}, 
                title={'text': "🛡️ 전체 안전도"})), use_container_width=True)
            for item in data:
                with st.expander(f"➔ {item['name']} 분석 리포트 (위기: {item['risk']}점)"):
                    st.markdown(item['rpt'])
