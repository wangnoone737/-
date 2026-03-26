import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Ultimate Strategy Simulator", page_icon="🛡️", layout="wide")

# 2. 분석 엔진
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def get_sheet_names(file):
        """파일로부터 시트 이름을 추출 (수강생 이름 판별 근거)"""
        try:
            xl = pd.ExcelFile(file)
            return xl.sheet_names
        except:
            return []

    @staticmethod
    def identify_student(row_data, sheet_names):
        """[사용자 제안 로직] 행 데이터 내 단어와 시트 이름을 대조하여 실제 수강생 판별"""
        # 행의 모든 값을 문자열로 나열 (중복 제거)
        row_values = set(str(v).strip() for v in row_data.values() if pd.notna(v) and str(v).strip() != "")
        
        # 제외 키워드 (관리자 및 시스템 항목)
        exclude_kw = ['인도자', '교사', '섬김이', '기본정보', '상세정보', '항목', '내용', '피드백']
        
        for s_name in sheet_names:
            # 1. 시트 이름이 행 데이터 중 하나와 일치하고
            # 2. 그 시트 이름이 관리자 키워드를 포함하지 않을 때만 수강생으로 인정
            if s_name in row_values:
                if not any(ex in s_name for ex in exclude_kw):
                    return s_name
        return None

    @staticmethod
    def find_column_value(row_data, keywords):
        """다양한 열 이름에 대응하여 데이터 추출"""
        for k in row_data.keys():
            if any(kw in str(k) for kw in keywords):
                return str(row_data[k]).strip()
        return ""

    @staticmethod
    def analyze_risk(row, name, admin_info, situation, strategy):
        # 데이터 추출 (MBTI, 단계)
        mbti = IntegratedEngine.find_column_value(row, ['MBTI', '성향']).upper()
        raw_step = IntegratedEngine.find_column_value(row, ['단계', '과정', '레벨'])
        
        if not mbti or not raw_step:
            return None, "⚠️ 데이터 부족", f"{name}님: 분석에 필요한 MBTI/단계 정보가 없습니다."

        try:
            # 단계 숫자 및 상중하 추출
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 형식 오류", "단계 정보를 '4상' 혹은 '4' 형태로 입력해주세요."

        # 가중치 계산
        yt_weight = 15 if ("youtube.com" in situation or "youtu.be" in situation) else 0
        base_score = 55 + (step_num * 2) + yt_weight
        
        # 전략 보너스 (MBTI 기반)
        strat_benefit = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '팩트', '근거']): strat_benefit += 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']): strat_benefit += 10

        final_risk = base_score - strat_benefit
        stage_display = f"{IntegratedEngine.STAGE_MAP.get(step_num, '과정')} ({step_level})"
        
        return min(max(final_risk, 0), 100), stage_display, f"{name}님을 위한 전략적 대응이 준비되었습니다."

# 3. 사이드바 (기능 전수 검토 완료)
with st.sidebar:
    st.header("📂 데이터 통합 설정")
    
    # [누락 방지] 공통 출석부
    st.subheader("1. 공통 데이터")
    common_file = st.file_uploader("전체 출석부 업로드", type=["xlsx", "csv"], key="common_att")
    
    st.markdown("---")
    
    # [오류 방지] 17개 MBTI 리스트
    mbti_options = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                    "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 상세 설정", expanded=False):
            a_file = st.file_uploader(f"{label}반 파일 (Excel)", type=["xlsx"], key=f"f_{label}")
            a_mbti = st.selectbox(f"{label} MBTI", mbti_options, key=f"m_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            admins.append({'label': label, 'file': a_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v5.1")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 및 전략")
    situation = st.text_area("🌐 발생 상황 (유튜브 링크 등)", placeholder="분석할 상황이나 링크를 입력하세요.", height=100)
    strategy_input = st.text_area("🛡️ 대응 전략 (강사/전도사 계획)", placeholder="적용할 전략 키워드를 입력하세요.", height=100)
    run_btn = st.button("AI 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직 (누적 로직 통합)
if run_btn:
    processed_results = []
    
    for admin in admins:
        if admin['file'] is not None:
            try:
                # 1. 시트 이름 확보
                sheet_names = IntegratedEngine.get_sheet_names(admin['file'])
                # 2. 데이터 로드
                df = pd.read_excel(admin['file'])
                
                for _, row in df.iterrows():
                    row_dict = row.to_dict()
                    # 3. 시트명 대조를 통한 수강생 식별
                    student_name = IntegratedEngine.identify_student(row_dict, sheet_names)
                    
                    if student_name:
                        risk, stage, advice = IntegratedEngine.analyze_risk(row_dict, student_name, admin, situation, strategy_input)
                        processed_results.append({
                            'name': student_name,
                            'admin': admin['label'],
                            'risk': risk,
                            'stage': stage,
                            'advice': advice,
                            'mbti': IntegratedEngine.find_column_value(row_dict, ['MBTI', '성향']).upper()
                        })
            except Exception as e:
                st.error(f"전도사 {admin['label']} 파일 처리 중 오류: {e}")

    if processed_results:
        # 중복 제거 (이름 기준)
        final_df = pd.DataFrame(processed_results).drop_duplicates(subset=['name'])
        
        # 상단 게이지 차트
        with col_chart:
            valid_risks = [r['risk'] for r in final_df.to_dict('records') if isinstance(r['risk'], (int, float))]
            if valid_risks:
                avg_safety = 100 - (sum(valid_risks) / len(valid_risks))
                st.plotly_chart(go.Figure(go.Indicator(
                    mode="gauge+number", value=avg_safety,
                    title={'text': f"🛡️ 전체 안전도 ({len(final_df)}명 분석)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e" if avg_safety > 70 else "#f59e0b"}}
                )), use_container_width=True)

        # 수강생 결과 카드
        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(final_df.to_dict('records')):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#f59e0b" if r_val and r_val > 40 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:230px;">
                        <h4 style="margin:0;">{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="font-size:0.85em; margin-top:5px;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.8em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:10px; font-size:1.1em;">위기 지수: {int(r_val) if r_val is not None else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("시트 이름과 일치하는 수강생 데이터를 찾을 수 없습니다. 전도사별 엑셀 파일과 설정을 확인해주세요.")
