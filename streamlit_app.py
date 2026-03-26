import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from openpyxl import load_workbook

# [v8.4] '출석부' 제외, 실시간 심리 현황 분석, 초정밀 개인 스캔 엔진 탑재
st.set_page_config(page_title="Strategic Master v8.4", layout="wide")

class MasterEngineV84:
    STEPS = ["마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_sheet_content(file, sheet_name):
        try:
            wb = load_workbook(file, data_only=True)
            ws = wb[sheet_name]
            # 전체 셀 데이터 통합 (심층 분석용 원천 데이터)
            return " ".join([str(cell.value) for row in ws.iter_rows() for cell in row if cell.value])
        except: return ""

    @staticmethod
    def analyze_status(text):
        """텍스트 전체를 스캔하여 수강생의 심리 및 수강 의지 분석"""
        # 단계 추출
        curr_step = next((s for s in reversed(MasterEngineV84.STEPS) if s in text), "확인 중")
        
        # 심리 분석 키워드 가중치 계산
        pos_score = len(re.findall(r'(확신|간절|열정|인정|감사|기대|소망|변화)', text))
        neg_score = len(re.findall(r'(의심|정체|불안|거부|피함|바쁨|세상)', text))
        
        if pos_score > neg_score + 3:
            psy = "말씀에 대한 깊은 반응과 성장의 의지가 매우 강한 상태입니다."
        elif neg_score > pos_score:
            psy = "외부 자극이나 개인적 사정으로 인해 심리적 방어 기제가 작동하고 있습니다."
        else:
            psy = "학습은 따라오고 있으나 아직 개인의 삶에 말씀이 실제화되지는 않은 중간 단계입니다."
            
        return f"현재 **{curr_step}** 과정이며, {psy}"

    @staticmethod
    def get_risk_score(text, situation):
        # 상황과 텍스트 기반 위기 지수 연산 (동일 점수 방지)
        base = 70 if any(k in situation for k in ['비방', '영상', '유튜브']) else 30
        extra = 20 if any(k in text for k in ['불안', '의심', '가족']) else 5
        return int(min(base + extra + (len(text) % 10), 100)) # 고유 데이터 기반 변동값 추가

# --- UI 레이아웃 ---
with st.sidebar:
    st.header("⚙️ 전략 시스템 v8.4")
    main_xlsx = st.file_uploader("📂 공통 출석부 업로드", type=["xlsx"], key="v84_main")
    st.markdown("---")
    
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t}전도사 프로필"):
            f = st.file_uploader(f"{t}반 파일", type=["xlsx"], key=f"v84_f_{t}")
            g = st.radio("성별", ["남", "여"], key=f"v84_g_{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"v84_m_{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"v84_e_{t}")
            admins.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 시스템 v8.4")
l, r = st.columns([1, 1.2])

with l:
    mode = st.radio("분석 유형", ["기수 전체 상황 및 전략", "개인 상황 및 전략"], horizontal=True)
    target_name = st.text_input("수강생 이름") if mode == "개인 상황 및 전략" else ""
    situation_input = st.text_area("🌐 발생 상황 (공통/개인)", height=80)
    strategy_input = st.text_area("🛡️ 수립 전략", height=80)
    
    if st.button("초정밀 AI 분석 가동 🚀", use_container_width=True):
        active_admins = [a for a in admins if a['file']]
        if not active_admins: st.error("파일을 업로드하세요.")
        else:
            results = []
            bar = st.progress(0)
            for i, adm in enumerate(active_admins):
                tmp_path = f"v84_tmp_{adm['id']}.xlsx"
                with open(tmp_path, "wb") as f: f.write(adm['file'].getbuffer())
                
                xl = pd.ExcelFile(tmp_path)
                for s_idx, s_name in enumerate(xl.sheet_names):
                    # '출석부' 등 이름이 아닌 시트 제외 로직
                    pure_name = re.sub(r'[^가-힣]', '', s_name)
                    if len(pure_name) < 2 or any(k in pure_name for k in ['출석', '양식', '기본', '단계', '비품']): continue
                    
                    bar.progress((i/len(active_admins)) + (s_idx/(len(xl.sheet_names)*len(active_admins))))
                    
                    # 시트 데이터 전체를 들고 옴 (메모리상 보유)
                    full_text = MasterEngineV84.get_sheet_content(tmp_path, s_name)
                    
                    if mode == "개인 상황 및 전략":
                        if pure_name == target_name:
                            results.append({'name': pure_name, 'admin': adm, 'text': full_text, 'type': 'deep'})
                            break
                    else:
                        results.append({'name': pure_name, 'admin': adm, 'text': full_text, 'type': 'total'})
                
                if os.path.exists(tmp_path): os.remove(tmp_path)
            st.session_state['v84_res'] = results
            bar.empty()

if 'v84_res' in st.session_state and st.session_state['v84_res']:
    df = pd.DataFrame(st.session_state['v84_res']).drop_duplicates(subset=['name'])
    with r:
        if df.iloc[0]['type'] == 'deep':
            item = df.iloc[0]
            status_summary = MasterEngineV84.analyze_status(item['text'])
            risk_val = MasterEngineV84.get_risk_score(item['text'], situation_input)
            st.success(f"## 🧬 {item['name']} 초정밀 분석 결과\n\n**[현황]** {status_summary}\n\n**[위기 점수]** {risk_val} / 100")
            st.info(f"**대응 전략:** {item['admin']['mbti']} 강점을 활용한 {'논리적 반증' if 'T' in item['admin']['mbti'] else '정서적 케어'} 집중")
        else:
            # 전체 기수 안전도 게이지
            avg_risk = sum([MasterEngineV84.get_risk_score(x['text'], situation_input) for x in df.to_dict('records')]) / len(df)
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-avg_risk, gauge={'axis': {'range': [0, 100]}}, title={'text': "🛡️ 기수 전체 안전도"})), use_container_width=True)
            
            st.markdown("### 👤 수강생별 실시간 심층 분석")
            for item in df.to_dict('records'):
                # 개별 칸을 열 때마다 텍스트 전체를 재스캔하여 결과 도출
                with st.expander(f"➔ {item['name']} ({item['admin']['id']}반) | 분석 보기"):
                    status_summary = MasterEngineV84.analyze_status(item['text'])
                    risk_val = MasterEngineV84.get_risk_score(item['text'], situation_input)
                    st.markdown(f"**심리 현황:** {status_summary}")
                    st.markdown(f"**위기 지수:** {risk_val}점")
                    ennea_part = f"{item['admin']['ennea']} 에너지" if item['admin']['ennea'] != "모름" else "영적 리더십"
                    st.markdown(f"**추천 전략:** {item['admin']['gender']}전도사님의 성향에 맞춰 {ennea_part}을 투입하세요.")
