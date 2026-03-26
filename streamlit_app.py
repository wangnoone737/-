import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Refined Cross-Check Simulator", page_icon="🛡️", layout="wide")

# 2. 분석 엔진 (이름 오인식 로직 완전 차단)
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def identify_student_by_sheet(row_dict, sheet_name):
        """[핵심 수정] 시트명 내 불필요한 단어를 제거하고 이름 판별"""
        s_name_str = str(sheet_name).strip()
        
        # [방어벽 1] 시트명 자체에 관리자 직책이 있는 경우 무조건 제외
        exclude_kw = ['인도자', '교사', '섬김이', '기본정보', '상세정보', '항목', '내용', '피드백', 'Sheet', '시트']
        if any(ex in s_name_str for ex in exclude_kw):
            return None

        # [방어벽 2] 시트명에서 시스템 불필요 단어 제거 및 어절 분리
        # 'nan' 등을 공백으로 대체 후 분리
        s_name_cleaned = re.sub(r'(nan|None|알수없음|none|NAN)', '', s_name_str)
        s_parts = re.split(r'[_ \-]', s_name_cleaned)
        
        # 행 데이터 중 유효한 텍스트만 추출
        row_values = set(str(v).strip() for v in row_dict.values() if pd.notna(v) and str(v).strip() != "")
        
        for part in s_parts:
            part = part.strip()
            # [방어벽 3] 추출된 어절이 유효한 이름인지 한 번 더 검증
            if not part or part.lower() in ['nan', 'none', '']: continue
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
        mbti = IntegratedEngine.get_val(row, ['MBTI', '성향', 'mbti']).upper()
        raw_step = IntegratedEngine.get_val(row, ['단계', '과정', '레벨'])
        
        if not mbti or mbti in ['NAN', ''] or not raw_step:
            return None, "⚠️ 데이터 누락", f"{name}님: MBTI/단계 정보가 부족합니다."

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 인식 실패", "단계 정보를 '4상' 형태로 기재하세요."

        # 유튜브 및 상황 가중치 (누적 로직 반영)
        yt_plus = 15 if any(kw in situation for kw in ["youtube.com", "youtu.be"]) else 0
        base = 55 + (step_num * 2) + yt_plus
        
        # 전략 보너스 (T-논리 / F-공감)
        strat_b = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '팩트', '근거']): strat_b = 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청', '마음']): strat_b = 10
        
        final_score = min(max(base - strat_b, 0), 100)
        stage_display = f"{IntegratedEngine.STAGE_MAP.get(step_num, '분석')} ({step_level})"
        return final_score, stage_display, f"{name}님에 대한 분석이 완료되었습니다."

# 3. 사이드바 (기능 누적 확인: 17개 MBTI, 출석부 입력 등)
with st.sidebar:
    st.header("📂 데이터 통합 설정")
    
    # 공통 출석부 (누락 방지)
    st.subheader("1. 공통 출석부")
    common_file = st.file_uploader("전체 출석부 파일 업로드", type=["xlsx", "csv"], key="common_att")
    
    st.markdown("---")
    
    # 17개 MBTI 풀 리스트
    mbti_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                  "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 상세 설정", expanded=False):
            # 전도사별 개별 파일 업로드 (xlsx 권장)
            a_file = st.file_uploader(f"{label}반 파일 (Excel)", type=["xlsx"], key=f"f_{label}")
            # 전도사 개인정보 (애니어그램, 성별 등 활성화 확인)
            a_mbti = st.selectbox(f"{label} MBTI", mbti_list, key=f"m_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            admins.append({'label': label, 'file': a_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v5.4")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 및 전략")
    situation = st.text_area("🌐 발생 상황 (유튜브 링크 등 포함 가능)", height=100)
    strategy_input = st.text_area("🛡️ 대응 전략 (키워드 매칭: 논리, 공감 등)", height=100)
    run_btn = st.button("AI 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직 (정밀화된 시트 대조 적용)
if run_btn:
    all_raw_data = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                # 엑셀 파일 내 모든 시트를 순회하며 분석
                xl = pd.ExcelFile(admin['file'])
                for sheet in xl.sheet_names:
                    df = xl.parse(sheet)
                    # 열 이름 공백 제거 및 문자열 정규화
                    df.columns = [str(c).strip() for c in df.columns]
                    
                    for _, row in df.iterrows():
                        d = row.to_dict()
                        # [핵심 보완] 시트명 내 불필요한 단어(' nan') 제거 후 수강생 식별
                        student_name = IntegratedEngine.identify_student_by_sheet(d, sheet)
                        
                        if student_name:
                            risk, stage, advice = IntegratedEngine.calculate_risk(d, student_name, situation, strategy_input)
                            all_raw_data.append({
                                'name': student_name, 'admin': admin['label'],
                                'risk': risk, 'stage': stage, 'advice': advice,
                                'mbti': IntegratedEngine.get_val(d, ['MBTI', '성향']).upper()
                            })
            except Exception as e:
                st.error(f"{admin['label']} 전도사 파일 분석 중 오류: {e}")

    if all_raw_data:
        # 중복 제거 (이름 기준) 후 정확히 6명(기수 인원)만 분석
        df_display = pd.DataFrame(all_raw_data).drop_duplicates(subset=['name'])
        
        # 기수 통합 안전도 차트
        with col_chart:
            risks = [r['risk'] for r in df_display.to_dict('records') if r['risk'] is not None]
            if risks:
                avg = 100 - (sum(risks) / len(risks))
                st.plotly_chart(go.Figure(go.Indicator(
                    mode="gauge+number", value=avg,
                    title={'text': f"🛡️ 기수 안전도 ({len(df_display)}명 분석)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e" if avg > 70 else "#f59e0b"}}
                )), use_container_width=True)

        st.markdown("---")
        # 수강생 결과 카드 출력
        cols = st.columns(3)
        for i, res in enumerate(df_display.to_dict('records')):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#f59e0b" if r_val and r_val > 40 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:220px;">
                        <h4 style="margin:0;">{res['name']} <small>(담당: {res['admin']})</small></h4>
                        <p style="font-size:0.85em; margin-top:5px;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.8em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:10px; font-size:1.1em;">위기 지수: {int(r_val) if r_val is not None else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("수강생을 찾지 못했습니다. 사이드바에서 파일을 업로드하고 버튼을 눌러주세요.")
