import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Final Master Strategy Simulator", page_icon="🛡️", layout="wide")

# 2. 분석 엔진 (누적 로직 통합)
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def identify_student_by_sheet(row_dict, sheet_name):
        """[핵심] 시트명 내 어절이 행 데이터(출석부 본문)와 일치하는지 검증"""
        # 관리자 시트는 분석 제외
        exclude_kw = ['인도자', '교사', '섬김이', '기본정보', '상세정보', '관리', 'Sheet', '시트']
        if any(ex in sheet_name for ex in exclude_kw):
            return None

        # 행 데이터 중 유효한 텍스트만 추출
        row_values = [str(v).strip() for v in row_dict.values() if pd.notna(v) and str(v).strip() != ""]
        
        # 시트명을 어절 단위로 분리 (예: '260326_홍길동' -> ['260326', '홍길동'])
        s_parts = re.split(r'[_ \-]', sheet_name)
        
        for part in s_parts:
            part = part.strip()
            if len(part) < 2: continue # 한 글자 이름 등 방지 (필요시 조정)
            
            # 시트명의 특정 어절이 행 데이터(출석 정보 기록 칸 등)에 존재한다면 수강생으로 확정
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
        mbti = IntegratedEngine.get_val(row, ['MBTI', '성향']).upper()
        raw_step = IntegratedEngine.get_val(row, ['단계', '과정', '레벨'])
        
        if not mbti or not raw_step:
            return None, "⚠️ 데이터 누락", "MBTI 또는 단계 정보가 없습니다."

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 형식 오류", "단계 정보를 '4상' 형태로 기재하세요."

        # 상황 가중치 (유튜브 등)
        yt_plus = 15 if any(kw in situation for kw in ["youtube.com", "youtu.be"]) else 0
        base = 55 + (step_num * 2) + yt_plus
        
        # 전략 보너스 (MBTI 기반)
        bonus = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '팩트', '근거']): bonus = 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']): bonus = 10
        
        final_score = min(max(base - bonus, 0), 100)
        stage_name = f"{IntegratedEngine.STAGE_MAP.get(step_num, '과정')} ({step_level})"
        return final_score, stage_name, f"{name}님에 대한 AI 분석이 완료되었습니다."

# 3. 사이드바 (기능 누적 확인 완료)
with st.sidebar:
    st.header("📂 데이터 통합 설정")
    st.subheader("1. 공통 출석부")
    common_file = st.file_uploader("전체 출석부 (선택사항)", type=["xlsx", "csv"], key="common")
    st.markdown("---")
    
    # 17개 MBTI 풀 리스트
    mbti_options = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                    "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 상세 설정"):
            a_file = st.file_uploader(f"{label}반 파일 (Excel)", type=["xlsx"], key=f"f_{label}")
            a_mbti = st.selectbox(f"{label} MBTI", mbti_options, key=f"m_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            admins.append({'label': label, 'file': a_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v5.3")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 분석 시나리오")
    situation = st.text_area("🌐 발생 상황 (유튜브 링크 등 포함 가능)", height=100)
    strategy_input = st.text_area("🛡️ 대응 전략 (키워드 매칭: 논리, 공감 등)", height=100)
    run_btn = st.button("AI 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직 (최적화된 이름 매칭)
if run_btn:
    final_data = []
    
    for admin in admins:
        if admin['file'] is not None:
            try:
                xl = pd.ExcelFile(admin['file'])
                for sheet in xl.sheet_names:
                    df = xl.parse(sheet)
                    # 데이터 프레임의 모든 열 이름을 문자열로 정규화
                    df.columns = [str(c).strip() for c in df.columns]
                    
                    for _, row in df.iterrows():
                        r_dict = row.to_dict()
                        # [누적 보완] 시트명-행데이터 교차 검증으로 이름 식별
                        student_name = IntegratedEngine.identify_student_by_sheet(r_dict, sheet)
                        
                        if student_name:
                            risk, stage, advice = IntegratedEngine.calculate_risk(r_dict, student_name, situation, strategy_input)
                            final_data.append({
                                'name': student_name, 'admin': admin['label'],
                                'risk': risk, 'stage': stage, 'advice': advice,
                                'mbti': IntegratedEngine.get_val(r_dict, ['MBTI', '성향']).upper()
                            })
            except Exception as e:
                st.error(f"{admin['label']} 전도사 파일 분석 중 오류: {e}")

    if final_data:
        # 최종 중복 제거 (수강생 이름 기준)
        display_df = pd.DataFrame(final_data).drop_duplicates(subset=['name'])
        
        with col_chart:
            risks = [r['risk'] for r in display_df.to_dict('records') if r['risk'] is not None]
            if risks:
                avg_safety = 100 - (sum(risks) / len(risks))
                st.plotly_chart(go.Figure(go.Indicator(
                    mode="gauge+number", value=avg_safety,
                    title={'text': f"🛡️ 기수 통합 안전도 ({len(display_df)}명)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
                )), use_container_width=True)

        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(display_df.to_dict('records')):
            with cols[i % 3]:
                r_val = res['risk']
                card_color = "#ef4444" if r_val and r_val > 70 else "#f59e0b" if r_val and r_val > 40 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {card_color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:220px;">
                        <h4 style="margin:0;">{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="font-size:0.85em; margin-top:5px;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.8em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{card_color}; margin-top:10px; font-size:1.1em;">위기 지수: {int(r_val) if r_val is not None else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("조건에 맞는 수강생을 찾지 못했습니다. 시트 이름과 행 데이터 내의 이름이 일치하는지 확인해주세요.")
