import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Final Master Simulator v5.5", page_icon="🛡️", layout="wide")

# 2. 분석 엔진
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def identify_student_by_sheet(row_dict, sheet_name):
        """[핵심 수정] '단계' 등 지표 키워드를 제외 리스트에 추가하여 이름 오인식 차단"""
        s_name_str = str(sheet_name).strip()
        
        # [업데이트] '단계' 및 지표 관련 단어를 제외 키워드에 추가
        exclude_kw = [
            '인도자', '교사', '섬김이', '기본정보', '상세정보', '항목', '내용', 
            '피드백', 'Sheet', '시트', '단계', '과정', '레벨', '상태', '점수'
        ]
        
        # 시트명 자체가 제외 키워드를 포함하면 즉시 제외
        if any(ex in s_name_str for ex in exclude_kw):
            return None

        # 시트명 정제 및 어절 분리
        s_name_cleaned = re.sub(r'(nan|None|알수없음|none|NAN)', '', s_name_str)
        s_parts = re.split(r'[_ \-]', s_name_cleaned)
        
        # 행 데이터 추출 (중복 제거)
        row_values = set(str(v).strip() for v in row_dict.values() if pd.notna(v) and str(v).strip() != "")
        
        for part in s_parts:
            part = part.strip()
            # 추출된 어절이 제외 키워드이거나 너무 짧으면 스킵
            if not part or any(ex == part for ex in exclude_kw): continue
            if part.lower() in ['nan', 'none', '']: continue
            if len(part) < 2: continue 
            
            # 시트명의 특정 어절이 행 데이터(출석 정보 등)와 100% 일치할 때만 이름으로 확정
            if part in row_values:
                return part
        return None

    @staticmethod
    def get_val(row_data, keywords):
        for k in row_data.keys():
            if any(kw in str(k) for kw in keywords):
                return str(row_data[k]).strip()
        return ""

    @staticmethod
    def calculate_risk(row, name, situation, strategy):
        mbti = IntegratedEngine.get_val(row, ['MBTI', '성향', 'mbti']).upper()
        raw_step = IntegratedEngine.get_val(row, ['단계', '과정', '레벨'])
        
        if not mbti or mbti in ['NAN', ''] or not raw_step:
            return None, "⚠️ 데이터 누락", f"{name}님: 분석에 필요한 핵심 정보가 부족합니다."

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 형식 오류", "단계 정보를 '4상' 형태로 기재해 주세요."

        yt_plus = 15 if any(kw in situation for kw in ["youtube.com", "youtu.be"]) else 0
        base = 55 + (step_num * 2) + yt_plus
        
        strat_b = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '팩트', '근거']): strat_b = 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']): strat_b = 10
        
        final_score = min(max(base - strat_b, 0), 100)
        return final_score, f"{IntegratedEngine.STAGE_MAP.get(step_num, '분석')} ({step_level})", f"{name}님 밀착 분석 완료."

# 3. 사이드바 설정 (17개 MBTI 등 기존 기능 완전 유지)
with st.sidebar:
    st.header("📂 데이터 통합 설정")
    st.subheader("1. 공통 출석부")
    common_file = st.file_uploader("전체 출석부 파일", type=["xlsx", "csv"], key="c_att")
    st.markdown("---")
    
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                  "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 설정"):
            a_file = st.file_uploader(f"{label}반 파일 (Excel)", type=["xlsx"], key=f"f_{label}")
            a_mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"m_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            admins.append({'label': label, 'file': a_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v5.5")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 및 전략")
    situation = st.text_area("🌐 발생 상황 (유튜브 링크 가능)", height=100)
    strategy_input = st.text_area("🛡️ 대응 전략 (논리/공감 등)", height=100)
    run_btn = st.button("AI 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직 (정밀화된 필터링 적용)
if run_btn:
    all_data = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                xl = pd.ExcelFile(admin['file'])
                for sheet in xl.sheet_names:
                    df = xl.parse(sheet)
                    df.columns = [str(c).strip() for c in df.columns]
                    
                    for _, row in df.iterrows():
                        d = row.to_dict()
                        # [업데이트] '단계' 등 지표 단어가 이름으로 오인되는 것 방지
                        student_name = IntegratedEngine.identify_student_by_sheet(d, sheet)
                        
                        if student_name:
                            risk, stage, advice = IntegratedEngine.calculate_risk(d, student_name, situation, strategy_input)
                            all_data.append({
                                'name': student_name, 'admin': admin['label'],
                                'risk': risk, 'stage': stage, 'advice': advice,
                                'mbti': IntegratedEngine.get_val(d, ['MBTI', '성향']).upper()
                            })
            except Exception as e:
                st.error(f"{admin['label']} 분석 오류: {e}")

    if all_data:
        df_display = pd.DataFrame(all_data).drop_duplicates(subset=['name'])
        
        with col_chart:
            risks = [r['risk'] for r in df_display.to_dict('records') if r['risk'] is not None]
            if risks:
                avg = 100 - (sum(risks) / len(risks))
                st.plotly_chart(go.Figure(go.Indicator(
                    mode="gauge+number", value=avg,
                    title={'text': f"🛡️ 기수 안전도 ({len(df_display)}명)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
                )), use_container_width=True)

        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(df_display.to_dict('records')):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:220px;">
                        <h4 style="margin:0;">{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="font-size:0.85em; margin-top:5px;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.8em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:10px;">위기: {int(r_val) if r_val else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("수강생을 찾지 못했습니다. 파일과 설정을 확인해 주세요.")
