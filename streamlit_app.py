import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="AI Adaptive Strategy Simulator", page_icon="🧠", layout="wide")

# 2. 분석 엔진 (지능형 피드백 및 가이드 로직)
class AdaptiveEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def identify_student(row_dict, sheet_name):
        s_name_str = str(sheet_name).strip()
        exclude_kw = ['인도자', '교사', '섬김이', '기본정보', '상세정보', '항목', '내용', '피드백', 'Sheet', '시트', '단계', '과정', '레벨']
        if any(ex in s_name_str for ex in exclude_kw): return None

        s_name_cleaned = re.sub(r'(nan|None|알수없음|none|NAN)', '', s_name_str)
        s_parts = re.split(r'[_ \-]', s_name_cleaned)
        row_values = set(str(v).strip() for v in row_dict.values() if pd.notna(v) and str(v).strip() != "")
        
        for part in s_parts:
            part = part.strip()
            if not part or any(ex == part for ex in exclude_kw) or len(part) < 2: continue
            if part in row_values: return part
        return None

    @staticmethod
    def get_val(row_data, keywords):
        for k in row_data.keys():
            if any(kw in str(k).upper() for kw in [kw.upper() for kw in keywords]):
                return str(row_data[k]).strip()
        return ""

    @staticmethod
    def detailed_analysis(row, name, situation, strategy):
        # 1. 필수 정보 추출
        mbti = AdaptiveEngine.get_val(row, ['MBTI', '성향']).upper()
        raw_step = AdaptiveEngine.get_val(row, ['단계', '과정', '레벨'])
        
        # 2. 추가 정보 추출 (피드백 고도화용)
        concern = AdaptiveEngine.get_val(row, ['고민', '어려움', '이슈'])
        env = AdaptiveEngine.get_val(row, ['환경', '상황', '가족', '직장'])
        personality = AdaptiveEngine.get_val(row, ['성격', '특징', '장점'])

        # 분석에 필요한 필수 요소 체크리스트
        missing_info = []
        if not mbti or mbti in ['NAN', '']: missing_info.append("MBTI(성향)")
        if not raw_step: missing_info.append("현재 단계(숫자 포함)")
        if not concern: missing_info.append("개인적 고민")
        if not env: missing_info.append("수강 환경(직장/가족)")

        if not mbti or not raw_step:
            return None, "⚠️ 분석 불가", f"필수 정보({', '.join(missing_info)})가 부족합니다.", missing_info

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 형식 오류", "단계 정보를 '4상' 형태로 수정해 주세요.", missing_info

        # --- 위기 지수 계산 ---
        yt_weight = 15 if any(kw in situation for kw in ["youtube.com", "youtu.be"]) else 0
        base = 55 + (step_num * 2) + yt_weight
        
        # 추가 정보 반영 (내용이 있을 경우 위기 지수 미세 조정)
        if concern and any(kw in concern for kw in ['의심', '불안', '반대']): base += 5
        if env and any(kw in env for kw in ['핍박', '바쁨', '교대']): base += 5
        
        # 전략 보너스
        bonus = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '팩트', '근거']): bonus += 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']): bonus += 10
        
        final_score = min(max(base - bonus, 0), 100)
        stage_display = f"{AdaptiveEngine.STAGE_MAP.get(step_num, '과정')} ({step_level})"
        
        # 전략 피드백 생성
        feedback = f"현재 {name}님은 {mbti} 성향과 {stage_display} 단계를 고려할 때 "
        feedback += "논리적 접근이 유효합니다." if 'T' in mbti else "정서적 유대가 중요합니다."
        if yt_weight > 0: feedback += " (유튜브 노출에 따른 긴급 관리가 필요합니다.)"

        return final_score, stage_display, feedback, missing_info

# 3. UI 및 실행 (누적 검토 완료)
with st.sidebar:
    st.header("📂 데이터 통합 설정")
    st.subheader("1. 공통 출석부")
    common_file = st.file_uploader("전체 출석부 파일", type=["xlsx", "csv"], key="com_att")
    st.markdown("---")
    
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 설정"):
            a_file = st.file_uploader(f"{label}반 엑셀 파일", type=["xlsx"], key=f"f_{label}")
            a_mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"m_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            admins.append({'label': label, 'file': a_file, 'mbti': a_mbti, 'ennea': a_ennea})

st.title("🏛️ 전략 시뮬레이션 시스템 v5.6")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 입력")
    situation = st.text_area("🌐 발생 상황", placeholder="예: 유튜브에서 신천지 영상을 접함", height=80)
    strategy_input = st.text_area("🛡️ 대응 전략", placeholder="예: 말씀으로 논리적 해결 시도", height=80)
    run_btn = st.button("AI 정밀 분석 가동 🚀", use_container_width=True)

if run_btn:
    all_res = []
    for admin in admins:
        if admin['file']:
            try:
                xl = pd.ExcelFile(admin['file'])
                for sheet in xl.sheet_names:
                    df = xl.parse(sheet)
                    df.columns = [str(c).strip() for c in df.columns]
                    for _, row in df.iterrows():
                        r_dict = row.to_dict()
                        student_name = AdaptiveEngine.identify_student(r_dict, sheet)
                        if student_name:
                            risk, stage, advice, missing = AdaptiveEngine.detailed_analysis(r_dict, student_name, situation, strategy_input)
                            all_res.append({
                                'name': student_name, 'admin': admin['label'],
                                'risk': risk, 'stage': stage, 'advice': advice,
                                'missing': missing, 'mbti': AdaptiveEngine.get_val(r_dict, ['MBTI', '성향']).upper()
                            })
            except Exception as e:
                st.error(f"오류: {e}")

    if all_res:
        df_final = pd.DataFrame(all_res).drop_duplicates(subset=['name'])
        with col_chart:
            v_risks = [r['risk'] for r in df_final.to_dict('records') if r['risk'] is not None]
            if v_risks:
                avg = 100 - (sum(v_risks) / len(v_risks))
                st.plotly_chart(go.Figure(go.Indicator(
                    mode="gauge+number", value=avg,
                    title={'text': "🛡️ 기수 통합 안전도"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
                )), use_container_width=True)

        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(df_final.to_dict('records')):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                        <h4 style="margin:0;">{res['name']} <small>({res['admin']}반)</small></h4>
                        <p style="font-size:0.85em; margin-top:5px;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.85em; color:#333; line-height:1.4;">{res['advice']}</p>
                        <div style="background:#f8fafc; padding:8px; border-radius:5px; margin-top:10px;">
                            <p style="font-size:0.75em; color:#64748b; margin:0;">💡 <b>추가 정보 가이드:</b></p>
                            <p style="font-size:0.75em; color:#334155; margin:0;">{', '.join(res['missing']) + '이 입력되면 더 자세한 분석이 가능합니다.' if res['missing'] else '모든 데이터가 확보되었습니다.'}</p>
                        </div>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:10px;">위기: {int(r_val) if r_val else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("분석할 수강생 데이터가 없습니다.")
