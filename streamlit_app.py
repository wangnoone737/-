import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Advanced Strategy Simulator", page_icon="🛡️", layout="wide")

# 2. 분석 엔진
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def analyze_student(row, admin_info, situation, strategy):
        # [핵심 개선] 컬럼명에 상관없이 데이터를 찾아내는 로직
        def find_value(row_data, keywords):
            # 1. 키워드 일치 확인
            for k in row_data.keys():
                if any(kw in str(k) for kw in keywords):
                    return str(row_data[k]).strip()
            # 2. 키워드가 전혀 없을 경우 첫 번째 열을 '이름'으로 가정 (방어적 코드)
            if '이름' in keywords:
                return str(list(row_data.values())[0]).strip()
            return ""

        name = find_value(row, ['이름', '성명', '수강생', '성함', 'NAME', 'Name'])
        mbti = find_value(row, ['MBTI', '성향', 'mbti']).upper()
        raw_step = find_value(row, ['단계', '과정', '레벨', 'STEP'])
        feedback = find_value(row, ['피드백', '특이사항', '비고', '내용'])
        
        if not mbti or mbti in ['NAN', ''] or not raw_step:
            return None, "⚠️ 데이터 보강 필요", f"{name}님: 분석 정보(MBTI/단계)가 부족합니다."

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 인식 실패", "단계 열을 '4상' 혹은 '4' 형태로 입력해주세요."

        # [유튜브 및 상황 분석 가중치]
        risk_weight = 0
        if "youtube.com" in situation or "youtu.be" in situation:
            # 영상 노출 시 4~6단계(비판적 사고 시작 단계) 수강생에게 더 높은 위기 가중치 부여
            risk_weight += 20 if 4 <= step_num <= 7 else 10
        
        base_score = 55 + (step_num * 2) + risk_weight
        if step_level == "하": base_score += 15
        elif step_level == "상": base_score -= 10

        # 전략 키워드 매칭
        strategy_benefit = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '교육', '팩트']): strategy_benefit += 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청']): strategy_benefit += 10

        final_risk = base_score - strategy_benefit
        stage_name = IntegratedEngine.STAGE_MAP.get(step_num, "분석 중")
        
        return min(max(final_risk, 0), 100), f"{stage_name} ({step_level})", f"{name}님은 현재 {stage_name} 단계의 외부 자극에 노출되었습니다."

# 3. 사이드바 (모든 기능 유지)
with st.sidebar:
    st.header("📂 데이터 설정")
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 설정"):
            file = st.file_uploader(f"{label}반 파일", type=["xlsx", "csv"], key=f"f_{label}")
            mbti = st.selectbox(f"{label} MBTI", ["모름", "ISTJ", "ENFP", "ENTJ", "INFJ", "ESTP"], key=f"m_{label}")
            ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            gen = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            admins.append({'label': label, 'file': file, 'mbti': mbti, 'ennea': ennea, 'gender': gen})

# 4. 메인 화면
st.title("🏛️ 전도사-수강생 전략 시뮬레이터")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 입력")
    situation = st.text_area("🌐 발생 상황 (유튜브 링크 등)", placeholder="여기에 유튜브 링크나 발생 상황을 적어주세요.", height=100)
    strategy_input = st.text_area("🛡️ 대응 전략", placeholder="강사/전도사의 구체적 계획을 적어주세요.", height=100)
    run_btn = st.button("AI 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직 (유연한 인원 분석)
if run_btn:
    final_data = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                df = pd.read_excel(admin['file']) if admin['file'].name.endswith('xlsx') else pd.read_csv(admin['file'])
                # 행마다 분석 실행
                for _, row in df.iterrows():
                    res = row.to_dict()
                    risk, stage, advice = IntegratedEngine.analyze_student(res, admin, situation, strategy_input)
                    
                    # 중복 방지를 위해 '이름' 추출 시도
                    name_key = next((k for k in res.keys() if any(kw in str(k) for kw in ['이름', '성명', '수강생'])), list(res.keys())[0])
                    
                    final_data.append({
                        'name': str(res[name_key]), 'admin': admin['label'], 
                        'risk': risk, 'stage': stage, 'advice': advice
                    })
            except Exception as e:
                st.error(f"파일 처리 중 오류: {e}")

    if final_data:
        # 중복 제거 및 결과 출력
        df_display = pd.DataFrame(final_data).drop_duplicates(subset=['name'])
        
        with col_chart:
            valid_risks = [r['risk'] for r in df_display.to_dict('records') if r['risk'] is not None]
            if valid_risks:
                avg = 100 - (sum(valid_risks) / len(valid_risks))
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
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px;">
                        <h4>{res['name']} <small>({res['admin']}반)</small></h4>
                        <p style="font-size:0.85em;"><b>지표:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.8em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color};">위기: {int(r_val) if r_val else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
