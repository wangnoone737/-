import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Total Strategic Risk Advisor", page_icon="🛡️", layout="wide")

# 2. 분석 엔진 (이전 로직 완벽 유지)
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def analyze_student(row, admin_info, situation, strategy):
        # [개선] 컬럼명 유연화: 이름, MBTI, 단계, 피드백을 다양한 명칭에서 찾음
        def get_val(keys):
            for k in keys:
                if k in row: return str(row[k]).strip()
            return ""

        name = get_val(['이름', '성명', '수강생', '성함']) or "알 수 없음"
        mbti = get_val(['MBTI', 'mbti', '성향']).upper()
        raw_step = get_val(['단계', '과정', '레벨'])
        feedback = get_val(['피드백', '특이사항', '비고'])
        
        if not mbti or mbti in ['NAN', ''] or not raw_step or raw_step in ['NAN', '']:
            return None, "⚠️ 정보 입력 필요", f"{name}님: MBTI 혹은 단계(예: 4상) 데이터가 없습니다."

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 형식 오류", "단계 열에 '4상', '1중' 형태로 입력해주세요."

        # 계산 로직
        base_score = 55 + (step_num * 2)
        if step_level == "하": base_score += 15
        elif step_level == "상": base_score -= 10

        neg_keywords = ['의심', '비판', '유튜브', '반대', '가족', '졸음', '힘듦']
        for word in neg_keywords:
            if word in feedback: base_score += 12

        strategy_benefit = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '근거', '설명', '교육', '팩트']): strategy_benefit += 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']): strategy_benefit += 10

        match_benefit = 0
        a_mbti = admin_info.get('mbti', '모름')
        if a_mbti != "모름" and len(mbti) == 4:
            if mbti[2] == a_mbti[2]: match_benefit += 10
            if mbti[0] != a_mbti[0]: match_benefit += 5
        
        final_risk = base_score - strategy_benefit - match_benefit
        stage_name = IntegratedEngine.STAGE_MAP.get(step_num, "미정의 단계")
        
        return min(max(final_risk, 0), 100), f"{stage_name} ({step_level})", f"현재 {stage_name} 상태입니다. 밀착 관리를 진행하세요."

# 3. 사이드바 (전도사별 애니어그램, 성별 필드 유지)
with st.sidebar:
    st.header("📂 데이터 및 관리자 설정")
    common_file = st.file_uploader("전체 출석부 업로드", type=["xlsx", "csv"], key="common")
    st.markdown("---")
    
    admins = []
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                 "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 설정"):
            admin_file = st.file_uploader(f"{label}반 파일", type=["xlsx", "csv"], key=f"file_{label}")
            a_mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"mbti_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"en_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"gen_{label}")
            admins.append({'label': label, 'file': admin_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면 (상황 및 전략 입력칸 유지)
st.title("🏛️ 전도사-수강생 관계 시뮬레이터")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 전략 시나리오 설정")
    situation = st.text_area("🌐 발생 상황", placeholder="예: 7단계 진행 중 외부 비판 노출", height=80)
    strategy_input = st.text_area("🛡️ 대응 전략 (강사/전도사 계획)", placeholder="예: 1:1 면담을 통한 정서적 위로", height=80)
    run_btn = st.button("시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직 (6명 누락 방지 및 중복 해결)
if run_btn:
    all_raw_data = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                # 엑셀/CSV 유연하게 읽기
                df = pd.read_excel(admin['file']) if admin['file'].name.endswith('xlsx') else pd.read_csv(admin['file'])
                
                # [개선] 컬럼명 표준화
                df.columns = [c.strip() for c in df.columns]
                name_col = next((c for c in df.columns if c in ['이름', '성명', '수강생']), None)
                
                if name_col:
                    for _, row in df.iterrows():
                        record = row.to_dict()
                        record['_unique_key'] = str(record[name_col]).strip()
                        record['_admin_info'] = admin
                        all_raw_data.append(record)
                else:
                    st.error(f"전도사 {admin['label']} 파일에 '이름' 또는 '성명' 열이 없습니다.")
            except Exception as e:
                st.error(f"파일 처리 오류: {e}")

    if all_raw_data:
        # 중복 제거 (이름 기준) 후 정확한 인원 파악
        df_final = pd.DataFrame(all_raw_data).drop_duplicates(subset=['_unique_key'])
        
        results = []
        for _, row in df_final.iterrows():
            risk, stage, advice = IntegratedEngine.analyze_student(row, row['_admin_info'], situation, strategy_input)
            results.append({
                'name': row['_unique_key'], 'admin': row['_admin_info']['label'],
                'risk': risk, 'stage': stage, 'advice': advice,
                'mbti': str(row.get('MBTI', row.get('성향', '-'))).upper()
            })

        # 게이지 차트
        with col_chart:
            valid_risks = [r['risk'] for r in results if r['risk'] is not None]
            if valid_risks:
                avg_safety = 100 - (sum(valid_risks) / len(valid_risks))
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=avg_safety,
                    title={'text': f"🛡️ 기수 안전도 ({len(results)}명 분석)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e" if avg_safety > 70 else "#f59e0b"}}
                ))
                st.plotly_chart(fig, use_container_width=True)

        # 결과 카드 출력 (6명 모두 출력)
        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(results):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#f59e0b" if r_val and r_val > 40 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:260px;">
                        <h4 style="margin:0;">{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="font-size:0.85em; margin-top:5px;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr style="margin:10px 0;">
                        <p style="font-size:0.85em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:10px; font-size:1.1em;">위기 지수: {int(r_val) if r_val is not None else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
