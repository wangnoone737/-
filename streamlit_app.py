import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re, os
from openpyxl import load_workbook

# [v8.1] 안전도 100점 만점, 이해도 개념 정립, '모름' 에너지 문법 오류 해결 완료
st.set_page_config(page_title="Strategic Master v8.1", layout="wide")

class MasterEngineV81:
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
        # 1. 현황(단계) 추출
        curr_step = next((s for s in reversed(MasterEngineV81.STEPS) if s in text), "단계 미확인")
        
        # 2. 이해도(전체 맥락 수용도) 분석
        pos = len(re.findall(r'(확실|통달|믿음|인정|깨달음|감사)', text))
        neg = len(re.findall(r'(의심|혼란|불안|모름|질문|거부)', text))
        und_level = "상" if pos > neg + 2 else "하" if neg > pos else "중"
        
        # 3. MBTI 및 위기지수
        m_match = re.search(r'(I|E)(S|N)(T|F)(J|P)', text, re.I)
        s_mbti = m_match.group(0).upper() if m_match else "미기입"
        risk = 75 if any(k in sit for k in ['비방', '영상', '유튜브']) else 40
        if und_level == "하": risk += 20
        
        # 4. 애니어그램 문법 오류 해결 ('모름' 처리)
        ennea_txt = f"{adm['ennea']}형의 에너지를" if adm['ennea'] != "모름" else "강력한 영적 리더십을"

        report = f"### 🧬 {adm['id']}전도사님({adm['gender']}) 맞춤 심층 분석\n\n"
        report += f"**[현황]** {curr_step} 단계 진행 중 | **[이해도]** 누적 데이터 기반 '{und_level}' 수준\n"
        report += f"**[수강생 성향]** {s_mbti} (전체 데이터 통합 분석 결과)\n\n"
        report += "--- \n"
        report += f"1. **관계 전략:** {'동성 간의 밀착 정서 케어' if adm['gender']=='여' else '공적인 신뢰 관계 유지'}를 통해 심리적 안전망을 확보하십시오.\n"
        report += f"2. **소통 전략:** {adm['mbti']} 성향을 활용한 " + ("객관적 논리 반증" if 'T' in adm['mbti'] else "따뜻한 공감과 위로") + "가 현재 수강생에게 필요합니다.\n"
        report += f"3. **동기 부여:** {ennea_txt} 투입하여 외부 자극을 이겨낼 비전을 제시하십시오."
        
        return int(min(risk, 100)), report

# --- UI 및 설정 ---
with st.sidebar:
    st.header("⚙️ v8.1 전략 설정")
    admins = []
    for t in ["A", "B", "C"]:
        with st.expander(f"👤 {t} 프로필 설정"):
            f = st.file_uploader(f"{t}반 데이터", type=["xlsx"], key=f"f{t}")
            g = st.radio("성별", ["남", "여"], key=f"g{t}", horizontal=True)
            m = st.selectbox("MBTI", ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"], key=f"m{t}")
            e = st.selectbox("애니어그램", ["모름"] + [f"{i}번" for i in range(1, 10)], key=f"e{t}")
            admins.append({'id': t, 'file': f, 'gender': g, 'mbti': m, 'ennea': e})

st.title("🏛️ 전략 시뮬레이션 시스템 v8.1")
l, r = st.columns([1, 1.2])

with l:
    mode = st.radio("분석 범위", ["전체 기수 스캔", "특정 개인 딥다이브"], horizontal=True)
    target = st.text_input("수강생 이름") if mode == "특정 개인 딥다이브" else ""
    sit = st.text_area("🌐 발생 상황", height=80)
    st_in = st.text_area("🛡️ 대응 전략", height=80)
    
    if st.button("AI 통합 분석 가동 🚀", use_container_width=True):
        active = [a for a in admins if a['file']]
        if not active: st.error("파일을 업로드해 주세요.")
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
                    txt = MasterEngineV81.get_data(path, s_n)
                    risk, rpt = MasterEngineV81.deep_analyze(txt, a, sit, st_in)
                    if mode == "특정 개인 딥다이브":
                        if name == target: final_res.append({'name': name, 'id': a['id'], 'risk': risk, 'report': rpt, 'type': 'deep'}); break
                    else: final_res.append({'name': name, 'id': a['id'], 'risk': risk, 'report': rpt, 'type': 'total'})
                if os.path.exists(path): os.remove(path)
            st.session_state['res81'] = final_res
            bar.empty()

if 'res81' in st.session_state and st.session_state['res81']:
    df = pd.DataFrame(st.session_state['res81']).drop_duplicates(subset=['name'])
    with r:
        if df.iloc[0]['type'] == 'deep':
            res = df.iloc[0]
            st.success(f"## {res['name']} 심층 리포트\n\n{res['report']}\n\n**최종 위기 지수: {res['risk']} / 100**")
        else:
            # 안전도 지표 (100점 만점)
            avg_safety = 100 - df['risk'].mean()
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=avg_safety, 
                                                   gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"}},
                                                   title={'text': "🛡️ 기수 전체 안전도"})), use_container_width=True)
            for item in df.to_dict('records'):
                with st.expander(f"➔ {item['name']} ({item['id']}반) | 위기: {item['risk']}점"):
                    st.markdown(item['report'])
