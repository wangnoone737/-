import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Strategic Relationship Simulator", page_icon="🛡️", layout="wide")

# 2. 분석 엔진
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def analyze_student(row, admin_info, situation, strategy):
        # 이름, MBTI, 단계, 피드백 데이터 추출
        name = str(row.get('이름', row.get('성명', '알 수 없음'))).strip()
        mbti = str(row.get('MBTI', '')).upper().strip()
        raw_step = str(row.get('단계', '')).strip()
        feedback = str(row.get('피드백', ''))
        
        # 필수 데이터 누락 시 처리
        if not mbti or mbti in ['NAN', ''] or not raw_step or raw_step in ['NAN', '']:
            return None, "⚠️ 정보 입력 필요", f"{name}님: MBTI 혹은 단계(예: 4상) 데이터가 없습니다."

        # 단계 파싱 (예: 4상 -> 4단계, 상)
        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 형식 오류", "단계 열에 '4상', '1중' 형태로 입력해주세요."

        # [위기 지수 계산 로직]
        base_score = 55 + (step_num * 2)
        if step_level == "하": base_score += 15
        elif step_level == "상": base_score -= 10

        # 피드백 기반 텍스트 마이닝
        neg_keywords = ['의심', '비판', '유튜브', '반대', '가족', '졸음', '힘듦']
        for word in neg_keywords:
            if word in feedback: base_score += 12

        # 전략(Strategy) 키워드와 성향 매칭
        # T형은 논리/설명 전략에, F형은 공감/면담 전략에 위기 지수가 더 하락함
        strategy_benefit = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '근거', '설명', '교육', '팩트']):
            strategy_benefit += 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']):
            strategy_benefit += 10

        # 전도사 매칭
        match_benefit = 0
        a_mbti = admin_info.get('mbti', '모름')
        if a_mbti != "모름" and len(mbti) == 4:
            if mbti[2] == a_mbti[2]: match_benefit += 10
            if mbti[0] != a_mbti[0]: match_benefit += 5
        
        final_risk = base_score - strategy_benefit - match_benefit
        stage_name = IntegratedEngine.STAGE_MAP.get(step_num, "미정의 단계")
        
        # 대응 조언 생성
        advice = f"현재 {stage_name}({step_level}) 상태입니다. "
        if step_level == "하":
            advice += f"담당 전도사({a_mbti})와의 신뢰 관계 회복이 최우선입니다."
        else:
            advice += "전략대로 밀착 관리를 진행하며 동요를 최소화하십시오."

        return min(max(final_risk, 0), 100), f"{stage_name} ({step_level})", advice

# 3. 사이드바 구성
with st.sidebar:
    st.header("📂 데이터 설정")
    st.subheader("1. 공통 데이터")
    common_file = st.file_uploader("전체 출석부", type=["xlsx", "csv"], key="common")
    
    st.markdown("---")
    admins = []
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                 "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 설정"):
            file = st.file_uploader(f"{label}반 파일", type=["xlsx", "csv"], key=f"f_{label}")
            mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"m_{label}")
            ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            admins.append({'label': label, 'file': file, 'mbti': mbti, 'ennea': ennea, 'gender': gender})

# 4. 메인 화면 (상황 및 전략 입력칸 복구)
st.title("🏛️ 전도사-수강생 관계 시뮬레이터")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 전략 시나리오 설정")
    situation = st.text_area("🌐 발생 상황", placeholder="예: 7단계 진행 중 외부 비판 노출", height=100)
    # [복구된 전략 입력칸]
    strategy_input = st.text_area("🛡️ 대응 전략 (강사/전도사의 계획)", placeholder="예: 1:1 면담을 통한 논리적 반박 및 정서적 위로", height=100)
    run_btn = st.button("시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직
if run_btn:
    raw_list = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                ext = admin['file'].name.split('.')[-1]
                df = pd.read_excel(admin['file']) if ext == 'xlsx' else pd.read_csv(admin['file'])
                
                # '이름' 혹은 '성명' 컬럼 확인
                name_col = next((c for c in df.columns if c in ['이름', '성명']), None)
                
                for _, row in df.iterrows():
                    d = row.to_dict()
                    target_name = d.get(name_col, '알수없음')
                    d['_target_name'] = target_name
                    d['담당전도사'] = admin['label']
                    d['admin_info'] = admin
                    raw_list.append(d)
            except Exception as e:
                st.error(f"파일 처리 오류: {e}")

    if raw_list:
        # 중복 제거 (정확히 수강생 인원수만큼만 표시)
        df_final = pd.DataFrame(raw_list).drop_duplicates(subset=['_target_name'], keep='first')
        
        processed = []
        for _, row in df_final.iterrows():
            risk, stage, advice = IntegratedEngine.analyze_student(row, row['admin_info'], situation, strategy_input)
            
            # 영향력 판단
            mbti_val = str(row.get('MBTI', '')).upper()
            raw_step = str(row.get('단계', '0'))
            step_num = int(re.findall(r'\d+', raw_step)[0]) if re.findall(r'\d+', raw_step) else 0
            inf_power = "⭐ 고영향력" if 'E' in mbti_val and step_num >= 4 else ""
            
            processed.append({
                'name': row['_target_name'], 
                'admin': row['담당전도사'], 
                'risk': risk, 
                'stage': stage, 
                'advice': advice,
                'inf': inf_power,
                'mbti': mbti_val,
                'feedback': str(row.get('피드백', ''))
            })

        with col_chart:
            valid_risks = [p['risk'] for p in processed if p['risk'] is not None]
            if valid_risks:
                avg = 100 - (sum(valid_risks) / len(valid_risks))
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=avg,
                    title={'text': f"🛡️ 전체 {len(processed)}명 안전도"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e" if avg > 70 else "#f59e0b"}}
                ))
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("👤 수강생별 정밀 분석 결과")
        cols = st.columns(3)
        for i, res in enumerate(processed):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#f59e0b" if r_val and r_val > 40 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                        <h4 style="margin:0;">{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="color:orange; font-size:0.8em; font-weight:bold; margin:5px 0;">{res['inf']}</p>
                        <p style="font-size:0.85em;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <div style="background:#f8fafc; padding:10px; border-radius:8px; margin-top:10px; font-size:0.85em;">
                            <b>💡 AI 대응 조언:</b><br>{res['advice']}
                        </div>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:15px; font-size:1.1em;">위기 지수: {int(r_val) if r_val is not None else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("파일을 업로드하고 전략을 입력한 뒤 버튼을 눌러주세요.")
