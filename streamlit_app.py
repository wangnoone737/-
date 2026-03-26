import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Strategic Relationship Simulator", page_icon="🛡️", layout="wide")

# 2. 분석 엔진: 단계별 의미 및 성향 매칭
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def analyze_student(row, admin_info, situation):
        name = str(row.get('이름', '알 수 없음')).strip()
        mbti = str(row.get('MBTI', '')).upper().strip()
        raw_step = str(row.get('단계', '')).strip()
        feedback = str(row.get('피드백', ''))
        
        # 데이터 누락 체크
        if not mbti or mbti in ['NAN', ''] or not raw_step or raw_step in ['NAN', '']:
            return None, "⚠️ 정보 입력 필요", f"{name}님: MBTI 혹은 단계(예: 4상) 데이터가 없습니다."

        # 단계 파싱
        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 형식 오류", "단계 열에 '4상', '1중' 형태로 입력해주세요."

        # 위기 지수 계산
        base_score = 55
        base_score += (step_num * 2)
        if step_level == "하": base_score += 15
        elif step_level == "상": base_score -= 10

        # 텍스트 마이닝
        neg_keywords = ['의심', '비판', '유튜브', '반대', '가족', '졸음', '힘듦']
        for word in neg_keywords:
            if word in feedback: base_score += 12

        # 전도사 매칭
        match_benefit = 0
        a_mbti = admin_info.get('mbti', '모름')
        if a_mbti != "모름" and len(mbti) == 4:
            if mbti[2] == a_mbti[2]: match_benefit += 15
            if mbti[0] != a_mbti[0]: match_benefit += 5
        
        final_risk = base_score - match_benefit
        stage_name = IntegratedEngine.STAGE_MAP.get(step_num, "미정의 단계")
        
        if step_level == "하":
            advice = f"현재 {stage_name} 단계 수용도가 낮습니다. {admin_info['mbti']} 전도사님의 밀착 케어가 시급합니다."
        else:
            advice = f"{stage_name} 인지가 안정적입니다. {mbti} 특성에 맞춘 정서적 피드백을 강화하세요."

        return min(max(final_risk, 0), 100), f"{stage_name} ({step_level})", advice

# 3. 사이드바: 입력 인터페이스 복구
with st.sidebar:
    st.header("📂 데이터 및 관리자 설정")
    st.subheader("1. 공통 출석부")
    common_file = st.file_uploader("전체 출석부 업로드", type=["xlsx", "csv"], key="common")
    
    st.markdown("---")
    admins = []
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                 "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 관리 섹션", expanded=False):
            admin_file = st.file_uploader(f"{label}반 수강생 파일", type=["xlsx", "csv"], key=f"file_{label}")
            a_mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"mbti_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"en_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"gen_{label}")
            admins.append({'label': label, 'file': admin_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면
st.title("🏛️ 전도사-수강생 관계 역동 시뮬레이터")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 전략 시나리오")
    situation = st.text_area("🌐 발생 상황", placeholder="예: 7단계 진행 중 비판 유튜브 노출", height=100)
    strategy = st.text_area("🛡️ 대응 계획", placeholder="예: 전도사 중심의 1:1 감성 소통", height=100)
    run_btn = st.button("정밀 시뮬레이션 시작 🚀", use_container_width=True)

# 5. 실행 로직 (중복 제거 및 에러 수정)
if run_btn:
    raw_student_list = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                ext = admin['file'].name.split('.')[-1]
                df = pd.read_excel(admin['file']) if ext == 'xlsx' else pd.read_csv(admin['file'])
                
                for _, row in df.iterrows():
                    student_data = row.to_dict()
                    student_data['담당전도사'] = admin['label']
                    student_data['admin_info'] = admin
                    raw_student_list.append(student_data)
            except Exception as e:
                st.error(f"파일 처리 오류: {e}")

    if raw_student_list:
        # [핵심] 이름 기준으로 중복 제거하여 정확히 6명만 추출
        df_final = pd.DataFrame(raw_student_list).drop_duplicates(subset=['이름'], keep='first')
        
        processed_results = []
        for _, row in df_final.iterrows():
            risk, stage_info, advice = IntegratedEngine.analyze_student(row, row['admin_info'], situation)
            
            # 고영향력 판단
            mbti_val = str(row.get('MBTI', '')).upper()
            raw_step = str(row.get('단계', '0'))
            step_num = int(re.findall(r'\d+', raw_step)[0]) if re.findall(r'\d+', raw_step) else 0
            inf_power = "⭐ 고영향력" if 'E' in mbti_val and step_num >= 4 else ""
            
            processed_results.append({
                'name': row.get('이름', '미상'),
                'mbti': mbti_val,
                'admin': row['담당전도사'],
                'risk': risk,
                'stage': stage_info,
                'advice': advice,
                'inf': inf_power,
                'feedback': str(row.get('피드백', ''))
            })

        # 차트 출력 (에러 수정됨)
        with col_chart:
            valid_risks = [s['risk'] for s in processed_results if s['risk'] is not None]
            if valid_risks:
                avg_safety = 100 - (sum(valid_risks) / len(valid_risks))
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=avg_safety,
                    title={'text': f"🛡️ 전체 {len(processed_results)}명 예상 안전도"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
                ))
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)

        # 카드 출력
        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(processed_results):
            with cols[i % 3]:
                risk_val = res['risk']
                card_color = "#ef4444" if risk_val and risk_val > 70 else "#f59e0b" if risk_val and risk_val > 40 else "#3b82f6"
                
                st.markdown(f"""
                    <div style="background:white; border-top:6px solid {card_color}; padding:15px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                        <h3 style="margin:0;">{res['name']} <small style="font-size:0.6em; color:gray;">(담당: {res['admin']})</small></h3>
                        <p style="color:orange; font-size:0.8em; font-weight:bold; margin:5px 0;">{res['inf']}</p>
                        <p style="font-size:0.85em;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <div style="background:#f8fafc; padding:10px; border-radius:8px; margin-top:10px; font-size:0.85em;">
                            <b>💡 AI 대응 조언:</b><br>{res['advice']}
                        </div>
                        <div style="text-align:right; font-weight:bold; color:{card_color}; margin-top:15px; font-size:1.1em;">위기 지수: {risk_val if risk_val is not None else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
