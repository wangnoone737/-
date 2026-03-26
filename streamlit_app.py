import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from openpyxl import load_workbook

st.set_page_config(page_title="Strategic Master v8.7", layout="wide")

class UltraEngineV87:
    STEPS = ["마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def deep_scan(file, sheet_name):
        try:
            wb = load_workbook(file, data_only=True)
            ws = wb[sheet_name]
            all_data = [str(c.value) for r in ws.iter_rows() for c in r if c.value]
            full_text = " ".join(all_data)
            return full_text
        except: return ""

    @staticmethod
    def generate_mega_report(name, adm, text, sit, strat):
        # 1. 시계열 심리 분석 (Trend)
        pos_keys = ['감사', '깨달음', '인정', '소망', '기쁨', '확신']
        neg_keys = ['의심', '불안', '바쁨', '가족', '세상', '혼란', '지침']
        
        # 앞부분(과거)과 뒷부분(현재) 분리 스캔
        mid = len(text)//2
        past_text, now_text = text[:mid], text[mid:]
        
        p_trend = sum(1 for k in pos_keys if k in now_text) - sum(1 for k in pos_keys if k in past_text)
        n_trend = sum(1 for k in neg_keys if k in now_text) - sum(1 for k in neg_keys if k in past_text)

        # 2. 페르소나 및 결핍 분석
        needs = []
        if '가족' in text or '부모' in text: needs.append("가족적 유대 및 지지")
        if '진리' in text or '이유' in text: needs.append("논리적 해답 및 지적 충족")
        if '성공' in text or '미래' in text: needs.append("비전 및 삶의 방향성")
        need_str = ", ".join(needs) if needs else "정서적 안정과 소속감"

        # 3. 맞춤형 전략 수립 (말이 아주 많은 버전)
        curr_step = next((s for s in reversed(UltraEngineV87.STEPS) if s in text), "확인 중")
        
        # 상성 분석
        rel_guide = f"{adm['gender']}전도사님의 섬세함을 살린 '그림자 케어'가 필수입니다." if adm['gender'] == '여' else f"{adm['gender']}전도사님의 권위와 신뢰를 바탕으로 '명확한 가이드'를 제시하십시오."
        
        mbti_talk = {
            'T': "현재 수강생은 논리적 정합성을 확인하고 싶어 합니다. '왜'라는 질문에 성경적 근거로 답하십시오.",
            'F': "현재 수강생은 마음의 안식처를 찾고 있습니다. 성경 지식보다 전도사님의 진심 어린 위로가 먼저입니다.",
            '모름': "수강생의 성향이 파악되지 않았으니, 다양한 질문을 통해 반응점을 먼저 찾으십시오."
        }.get(adm['mbti'][2] if len(adm['mbti']) > 2 else '모름', "개별 맞춤 상담이 필요합니다.")

        # 4. 위기 지수 (데이터 밀도 기반)
        risk = 70 if any(k in sit for k in ['비방', '영상', '유튜브']) else 30
        if n_trend > 0: risk += 15 # 부정적 흐름 증가 시 가점
        if p_trend < 0: risk += 10 # 긍정적 흐름 감소 시 가점
        risk_val = min(risk + (len(text)%10), 100)

        # 리포트 구성
        rpt = f"## 🔱 {name} 수강생 초정밀 전 생애주기 리포트\n\n"
        rpt += f"### 1. 심리 변화 흐름 (Trend Analysis)\n"
        rpt += f"- **변화 양상:** {'최근 긍정적 신호가 강화되고 있으나 안심은 금물입니다.' if p_trend >= 0 and n_trend <= 0 else '최근 부정적 키워드가 증가하며 심리적 방어벽이 높아지고 있습니다.'}\n"
        rpt += f"- **핵심 결핍:** {name} 님은 현재 **[{need_str}]**에 대한 갈급함이 상담 기록 곳곳에서 드러납니다.\n\n"
        rpt += f"### 2. 단계별 정밀 진단 [현재: {curr_step}]\n"
        rpt += f"- **분석 결과:** {curr_step} 과정에서 요구되는 확신보다 주변 환경(가족/친구)에 의한 흔들림이 더 큽니다. {sit[:20]}... 상황은 이 결점을 파고들 가능성이 높습니다.\n\n"
        rpt += f"### 3. {adm['id']}전도사 전용 1:1 대응 화법\n"
        rpt += f"- **관계 설정:** {rel_guide}\n"
        rpt += f"- **상성 대화법:** {mbti_talk}\n"
        rpt += f"- **에너지 투입:** {adm['ennea'] if adm['ennea'] != '모름' else '영적'} 에너지를 활용하여, 수강생이 가장 불안해하는 부분을 역으로 공략하십시오.\n\n"
        rpt += f"### 4. 최종 전략 결론 (위기: {risk_val}점)\n"
        rpt += f"- **행동 지침:** 기수 전체 전략인 '{strat[:30]}...'을 {name} 님에게 적용할 때는, 반드시 개인의 결핍 요소인 [{need_str}]을 채워주는 방식으로 변주해야 성공 확률이 높습니다."
        
        return rpt, risk_val

# --- UI 레이아웃 ---
with st.sidebar:
    st.header("⚙️ 전략 엔진 v8.7")
    main_file = st.file_uploader("📂 공통 출석부 업로드", type=["xlsx"])
    st.markdown("---")
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t}전도사 설정"):
            f = st.file_uploader(f"{t}반 파일", type=["xlsx"], key=f"f_{t}")
            g = st.radio("성별", ["남", "여"], key=f"g_{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"m_{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"e_{t}")
            admins.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 시스템 v8.7")
l, r = st.columns([1, 1.2])

with l:
    mode = st.radio("분석 선택", ["기수 전체 상황 및 전략", "개인 상황 및 전략"], horizontal=True)
    target = st.text_input("수강생 이름") if mode == "개인 상황 및 전략" else ""
    sit_in = st.text_area("🌐 발생 상황", height=80)
    strat_in = st.text_area("🛡️ 대응 전략", height=80)
    
    if st.button("분석", use_container_width=True):
        active_admins = [a for a in admins if a['file']]
        if not active_admins: st.error("파일을 업로드하세요.")
        else:
            final_data = []
            bar = st.progress(0)
            for i, adm in enumerate(active_admins):
                tmp_p = f"v87_tmp_{adm['id']}.xlsx"
                with open(tmp_p, "wb") as f_out: f_out.write(adm['file'].getbuffer())
                xl = pd.ExcelFile(tmp_p)
                for s_n in xl.sheet_names:
                    name = re.sub(r'[^가-힣]', '', s_n)
                    if len(name) < 2 or any(k in name for k in ['출석', '양식', '기본', '단계']): continue
                    
                    full_txt = UltraEngineV87.deep_scan(tmp_p, s_n)
                    rpt, risk = UltraEngineV87.generate_mega_report(name, adm, full_txt, sit_in, strat_in)
                    
                    if mode == "개인 상황 및 전략":
                        if name == target: final_data.append({'name': name, 'report': rpt, 'risk': risk, 'type': 'deep'}); break
                    else:
                        final_data.append({'name': name, 'report': rpt, 'risk': risk, 'type': 'total'})
                os.remove(tmp_p)
            st.session_state['v87_res'] = final_data
            bar.empty()

if 'v87_res' in st.session_state:
    res_list = st.session_state['v87_res']
    with r:
        if res_list[0]['type'] == 'deep':
            st.success(res_list[0]['report'])
        else:
            avg_safety = 100 - (sum([x['risk'] for x in res_list]) / len(res_list))
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=avg_safety, gauge={'axis': {'range': [0, 100]}}, title={'text': "🛡️ 기수 통합 안전도"})), use_container_width=True)
            for r_item in res_list:
                with st.expander(f"➔ {r_item['name']} 분석 리포트 (위기: {r_item['risk']}점)"):
                    st.markdown(r_item['report'])
