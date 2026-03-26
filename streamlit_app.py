import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="Strategic Risk Advisor v3", page_icon="🧬", layout="wide")

# 2. 분석 엔진: 단계별 심층 의미 분석
class AdvancedLogic:
    # 단계별 정의 (사용자 제공 기획 반영)
    STAGE_MAP = {
        1: "마음사기 (전도사의 수용성 확보)",
        2: "수강 목적성 (스스로의 의지/동기)",
        3: "영 인지 (보이지 않는 존재 인정)",
        4: "성경 인정 (교재에 대한 신뢰)",
        5: "선악구분 (말씀의 진위 분별)",
        6: "시대구분 (자신의 위치 이해)",
        7: "말씀 인정 (전해지는 내용 수용)",
        8: "종교 세계 인식 (현실 종교관 이해)",
        9: "약속의 목자 인정 (메신저 신뢰)",
        10: "약속한 성전 인정 (신천지 수용)"
    }

    @staticmethod
    def calculate_risk(row, admin_info, situation):
        # [A] 기본 변수 설정
        name = str(row.get('이름', '알 수 없음'))
        mbti = str(row.get('MBTI', '')).upper().strip()
        raw_step = str(row.get('단계', '')) # 예: "4상", "1중" 또는 "4"
        feedback = str(row.get('피드백', ''))

        # 정보 부족 판단
        if not mbti or mbti == 'NAN' or not raw_step:
            return None, "⚠️ 성향/단계 입력 필요", "데이터 부족으로 분석 불가"

        # [B] 단계 데이터 파싱 (숫자와 상중하 분리)
        try:
            import re
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 형식 오류", "단계 데이터(예: 4상) 확인 필요"

        # [C] 위기 지수 계산 로직
        score = 60 # 기본값
        
        # 1. 단계별 가중치 (고단계일수록 외부 비판 상황에서 충격이 큼)
        score += (step_num * 3)
        if step_level == "하": score += 15 # 해당 단계 정착이 안 됐을 때 위기 상승
        elif step_level == "상": score -= 10 # 정착이 잘 됐을 때 위기 하락

        # 2. 텍스트 마이닝 (피드백 분석)
        neg_words = ['의심', '비판', '유튜브', '반대', '가족', '졸음', '부족']
        for w in neg_words:
            if w in feedback: score += 10

        # 3. 전도사 매칭 (성향 궁합)
        a_mbti = admin_info.get('mbti', '모름')
        if a_mbti != "모름" and len(mbti) == 4:
            if mbti[2] == a_mbti[2]: score -= 15 # T-T, F-F 공감 시 안정
            if mbti[0] != a_mbti[0]: score -= 5  # E-I 보완 시 안정

        # [D] 추천 대응 생성
        current_stage_desc = AdvancedLogic.STAGE_MAP.get(step_num, "정의되지 않은 단계")
        if step_level == "하":
            advice = f"현재 {step_num}단계({current_stage_desc})의 '하' 수준입니다. 기초를 다시 다지는 면담이 시급합니다."
        else:
            advice = f"{current_stage_desc} '상/중' 수준으로, 현재 전략인 '{situation[:10]}...' 상황에 맞춘 논리적 대응이 유효합니다."

        return min(max(score, 0), 100), current_stage_desc + f" ({step_level})", advice

# 3. 사이드바 설정
with st.sidebar:
    st.header("📂 데이터 관리")
    file_att = st.file_uploader("수강생 통합 파일 (Excel)", type=["xlsx"])
    
    st.markdown("---")
    admins = []
    for lbl in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {lbl} 성향 설정"):
            mbti = st.selectbox(f"{lbl} MBTI", ["모름", "ISTJ", "ENFP", "ENTJ", "ISFJ", "INFJ", "ESTP", "기타"], key=f"mbti_{lbl}")
            ennea = st.selectbox(f"{lbl} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"en_{lbl}")
            admins.append({'label': lbl, 'mbti': mbti, 'ennea': ennea})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이터 v3 : 단계별 심층 분석")

c1, c2 = st.columns([1, 1.2])
with c1:
    situation = st.text_area("🌐 발생 상황", placeholder="예: 4단계 진행 중 외부 비판 영상 노출", height=100)
    plan = st.text_area("🛡️ 대응 전략", placeholder="예: 1:1 면담 및 말씀 인정 교육 강화", height=100)
    run_btn = st.button("AI 정밀 시뮬레이션 가동 🚀", use_container_width=True)

if run_btn and file_att:
    df = pd.read_excel(file_att)
    
    # 결과 계산 (중복 루프 제거)
    results = []
    for _, row in df.iterrows():
        # 담당 전도사 찾기 (파일 내 '전도사' 컬럼이 있다고 가정, 없으면 A로 고정)
        admin_label = str(row.get('전도사', 'A')).strip()
        selected_admin = next((a for a in admins if a['label'] == admin_label), admins[0])
        
        risk, stage_info, advice = AdvancedLogic.calculate_risk(row, selected_admin, situation)
        results.append({'risk': risk, 'stage': stage_info, 'advice': advice, 'data': row})

    # 전체 통계
    valid_risks = [r['risk'] for r in results if r['risk'] is not None]
    if valid_risks:
        with c2:
            avg_safety = 100 - (sum(valid_risks) / len(valid_risks))
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=avg_safety,
                title={'text': "🛡️ 기수 평균 안전도"},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
            ))
            st.plotly_chart(fig, use_container_width=True)

    # 개별 카드 출력
    st.markdown("---")
    cols = st.columns(3)
    for i, res in enumerate(results):
        with cols[i % 3]:
            risk = res['risk']
            row = res['data']
            
            if risk is None: # 분석 불가 상태
                st.error(f"### {row.get('이름', '알 수 없음')}\n{res['stage']}\n\n{res['advice']}")
            else:
                color = "#ef4444" if risk > 70 else "#f59e0b" if risk > 40 else "#3b82f6"
                st.markdown(f"""
                    <div style="background:white; border-top:6px solid {color}; padding:15px; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:320px;">
                        <h3 style="margin:0;">{row.get('이름','-')} <small>({row.get('MBTI','-')})</small></h3>
                        <p style="color:#666; font-size:0.9em;"><b>현재 지표:</b> {res['stage']}</p>
                        <hr style="margin:10px 0;">
                        <p style="font-size:0.85em;"><b>📋 피드백 요약:</b> {str(row.get('피드백',''))[:50]}...</p>
                        <div style="background:#f0f7ff; padding:10px; border-radius:5px; margin-top:10px;">
                            <b style="color:#1e40af;">💡 AI 처방:</b><br>
                            <span style="font-size:0.85em;">{res['advice']}</span>
                        </div>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:15px; font-size:1.2em;">위기 지수: {risk}점</div>
                    </div>
                """, unsafe_allow_html=True)
elif run_btn:
    st.error("분석할 엑셀 파일을 먼저 업로드해 주세요!")
