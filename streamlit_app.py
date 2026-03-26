import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from openpyxl import load_workbook

# [v8.3] 사용자 지정 용어 반영 및 전수 검산 완료
st.set_page_config(page_title="Strategic Master v8.3", layout="wide")

class MasterEngineV83:
    STEPS = ["마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"]

    @staticmethod
    def get_data(file, sheet):
        try:
            wb = load_workbook(file, data_only=True)
            ws = wb[sheet]
            return " ".join([str(c) for row in ws.iter_rows(values_only=True) for c in row if c])
        except: return ""

    @staticmethod
    def deep_analyze(text, adm, sit, strat):
        # 1. 현황 및 이해도 도출
        curr_step = next((s for s in reversed(MasterEngineV83.STEPS) if s in text), "단계 미확인")
        pos = len(re.findall(r'(확실|통달|믿음|인정|깨달음|감사)', text))
        neg = len(re.findall(r'(의심|혼란|불안|모름|질문|거부)', text))
        und_level = "상" if pos > neg + 2 else "하" if neg > pos else "중"
        
        # 2. 성향 및 위기 점수
        m_match = re.search(r'(I|E)(S|N)(T|F)(J|P)', text, re.I)
        s_mbti = m_match.group(0).upper() if m_match else "미기입"
        risk = 75 if any(k in sit for k in ['비방', '영상', '유튜브']) else 40
        if und_level == "하": risk += 20
        
        # 3. 문법 교정 (애니어그램)
        ennea_txt = f"{adm['ennea']}형의 에너지를" if adm['ennea'] != "모름" else "강력한 영적 리더십을"

        report = f"### 🧬 {adm['id']}전도사님 맞춤 전략\n\n"
        report += f"**[현황]** {curr_step} 단계 진행 중 | **[이해도]** 누적 데이터 기반 '{und_level}' 수준\n"
        report += f"**[수강생 성향]** {s_mbti}\n\n"
        report += "--- \n"
        report += f"1. **관계:** {'동성 정서 케어' if adm['gender']=='여' else '공적 신뢰 관계'} 주력\n"
        report += f"2. **소통:** {adm['mbti']} 강점 활용 " + ("객관적 논리 반증" if 'T' in adm['mbti'] else "따뜻한 공감 위로") + "\n"
        report += f"3. **동기 부여:** {ennea_txt} 투입하여 비전 제시"
        return int(min(risk, 100)), report

# --- UI 설정 ---
with st.sidebar:
    st.header("⚙️ v8.3 전략 설정")
    # 공통 출석부 (위치 사수)
    main_xlsx = st.file_uploader("📂 공통 출석부 업로드", type=["xlsx"], key="v83_main")
    st.markdown("---")
    
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t} 프로필"):
            f = st.file_uploader(f"{t} 파일", type=["xlsx"], key=f"f{t}")
            g = st.radio("성별", ["남", "여"], key=f"g{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"m{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"e{t}")
            admins.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 시스템 v8.3")
l, r = st.columns([1, 1.2])

with l:
    # [수정] 사용자 지정 용어 반영
    mode = st.radio("분석 선택", ["기수 전체 상황 및 전략", "개인 상황 및 전략"], horizontal=True)
    target = st.text_input("수강생 이름") if mode == "개인 상황 및 전략" else ""
    sit = st.text_area("🌐 발생 상황", height=80)
    st_in = st.text_area("🛡️ 대응 전략", height=80)
    
    if st.button("AI 분석 실행 🚀", use_container_width=True):
        active = [a for a in admins if a['file']]
        if not active: st.error("전도사 파일을 업로드해 주세요.")
        else:
            final_res = []
            bar = st.progress(0)
            for i, a in enumerate(active):
                path = f"tmp_{a['id']}.xlsx"
                with open(path, "wb") as f: f.write(a['file'].getbuffer())
                xl = pd.ExcelFile(path)
                for s_idx, s_n in enumerate(xl.sheet_names):
                    name = re.sub(r'[^가-힣]', '', s_n)
                    if len(name) < 2 or name in ['출석', '양식', '기본']: continue
                    bar.progress((i/len(active)) + (s_idx/(len(xl.sheet_names)*len(active))))
                    txt = MasterEngineV83.get_data(path, s_n)
                    risk, rpt = MasterEngineV83.deep_analyze(txt, a, sit, st_in)
                    if mode == "개인 상황 및 전략":
                        if name == target: final_res.append({'name': name, 'id': a['id'], 'risk': risk, 'report': rpt, 'type': 'deep'}); break
                    else: final_res.append({'name': name, 'id': a['id'], 'risk': risk, 'report': rpt, 'type': 'total'})
                if os.path.exists(path): os.remove(path)
            st.session_state['res83'] = final_res
            bar.empty()

if 'res83' in st.session_state and st.session_state['res83']:
    df = pd.DataFrame(st.session_state['res83']).drop_duplicates(subset=['name'])
    with r:
        if df.iloc[0]['type'] == 'deep':
            res = df.iloc[0]
            st.success(f"## {res['name']} 심층 리포트\n\n{res['report']}\n\n**위기: {res['risk']} / 100**")
        else:
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-df['risk'].mean(), gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"}}, title={'text': "🛡️ 전체 안전도"})), use_container_width=True)
            for item in df.to_dict('records'):
                with st.expander(f"➔ {item['name']} ({item['id']}) | 위기: {item['risk']}점"):
                    st.markdown(item['report'])
