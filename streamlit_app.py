import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Total Strategy Simulator Pro", page_icon="🛡️", layout="wide")

# 2. 분석 엔진 (논리 구조 강화)
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def find_value(row_data, keywords):
        """컬럼명에 상관없이 데이터를 찾아내는 로직"""
        # 1. 키워드 포함 여부로 정확히 찾기
        for k in row_data.keys():
            if any(kw in str(k) for kw in keywords):
                return str(row_data[k]).strip()
        # 2. '이름' 관련인데 못 찾았다면 첫 번째 열을 무조건 이름으로 간주
        if '이름' in keywords or '성명' in keywords:
            return str(list(row_data.values())[0]).strip()
        return ""

    @staticmethod
    def analyze_student(row, admin_info, situation, strategy):
        name = IntegratedEngine.find_value(row, ['이름', '성명', '수강생', '성함'])
        mbti = IntegratedEngine.find_value(row, ['MBTI', '성향', 'mbti']).upper()
        raw_step = IntegratedEngine.find_value(row, ['단계', '과정', '레벨'])
        feedback = IntegratedEngine.find_value(row, ['피드백', '특이사항', '비고'])
        
        if not mbti or mbti in ['NAN', ''] or not raw_step:
            return None, "⚠️ 데이터 보강 필요", f"{name}님: 분석에 필요한 핵심 정보가 부족합니다."

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 인식 불가", "단계 열에 '4상' 혹은 '4' 형태로 입력해주세요."

        # 유튜브 링크 감지 시 위기 가중치 적용
        yt_weight = 15 if ("youtube.com" in situation or "youtu.be" in situation) else 0
        
        base_score = 55 + (step_num * 2) + yt_weight
        if step_level == "하": base_score += 15
        elif step_level == "상": base_score -= 10

        # 전략 키워드와 성향 매칭
        strat_benefit = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '근거', '설명', '교육', '팩트']): strat_benefit += 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']): strat_benefit += 10

        # 전도사 MBTI 매칭
        match_benefit = 0
        a_mbti = admin_info.get('mbti', '모름')
        if a_mbti != "모름" and len(mbti) == 4:
            if mbti[2] == a_mbti[2]: match_benefit += 10
            if mbti[0] != a_mbti[0]: match_benefit += 5

        final_risk = base_score - strat_benefit - match_benefit
        stage_name = IntegratedEngine.STAGE_MAP.get(step_num, "분석 중")
        
        return min(max(final_risk, 0), 100), f"{stage_name} ({step_level})", f"현재 {stage_name} 단계의 외부 자극 대응이 필요합니다."

# 3. 사이드바 (모든 기능 복구 및 유지)
with st.sidebar:
    st.header("📂 데이터 통합 설정")
    
    # [복구] 공통 출석부
    st.subheader("1. 공통 데이터")
    common_file = st.file_uploader("전체 출석부 파일 업로드", type=["xlsx", "csv"], key="common_att")
    
    st.markdown("---")
    
    # 전도사별 섹션 (A, B, C)
    admins = []
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                 "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 상세 설정", expanded=False):
            # [복구] 전도사별 개별 파일 업로드
            a_file = st.file_uploader(f"{label}반 개별 파일", type=["xlsx", "csv"], key=f"f_{label}")
            # [유지] 전도사 개인정보
            a_mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"m_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            
            admins.append({'label': label, 'file': a_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면 (상황 및 전략 입력창 유지)
st.title("🏛️ 전략 시뮬레이션 시스템 v3.1")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 및 전략")
    situation = st.text_area("🌐 발생 상황 (유튜브 링크 등)", placeholder="상황을 상세히 적거나 유튜브 링크를 첨부하세요.", height=100)
    strategy_input = st.text_area("🛡️ 대응 전략 (강사/전도사 계획)", placeholder="수행할 교육이나 면담 계획을 적어주세요.", height=100)
    run_btn = st.button("AI 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직
if run_btn:
    raw_records = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                # 엑셀/CSV 로딩
                df = pd.read_excel(admin['file']) if admin['file'].name.endswith('xlsx') else pd.read_csv(admin['file'])
                for _, row in df.iterrows():
                    d = row.to_dict()
                    # 이름 찾기 (열 제목 유연화 로직 적용)
                    d['_target_name'] = IntegratedEngine.find_value(d, ['이름', '성명', '수강생'])
                    d['_admin_info'] = admin
                    raw_records.append(d)
            except Exception as e:
                st.error(f"파일 처리 오류: {e}")

    if raw_records:
        # 중복 제거 (이름 기준)
        df_final = pd.DataFrame(raw_records).drop_duplicates(subset=['_target_name'])
        
        results = []
        for _, row in df_final.iterrows():
            risk, stage, advice = IntegratedEngine.analyze_student(row, row['_admin_info'], situation, strategy_input)
            results.append({
                'name': row['_target_name'], 'admin': row['_admin_info']['label'],
                'risk': risk, 'stage': stage, 'advice': advice,
                'mbti': IntegratedEngine.find_value(row, ['MBTI', '성향']).upper()
            })

        # 상단 차트
        with col_chart:
            valid_risks = [r['risk'] for r in results if r['risk'] is not None]
            if valid_risks:
                avg_safety = 100 - (sum(valid_risks) / len(valid_risks))
                st.plotly_chart(go.Figure(go.Indicator(
                    mode="gauge+number", value=avg_safety,
                    title={'text': f"🛡️ 전체 {len(results)}명 분석 결과"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e" if avg_safety > 70 else "#f59e0b"}}
                )), use_container_width=True)

        # 수강생별 카드 출력
        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(results):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#f59e0b" if r_val and r_val > 40 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                        <h4 style="margin:0;">{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="font-size:0.85em; margin-top:5px;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.8em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:10px; font-size:1.1em;">위기 지수: {int(r_val) if r_val is not None else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("사이드바에서 파일을 업로드하고 버튼을 눌러주세요.")
