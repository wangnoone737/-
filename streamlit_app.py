import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 1. 페이지 설정
st.set_page_config(page_title="Total Strategy Simulator Pro", page_icon="🛡️", layout="wide")

# 2. 분석 엔진
class IntegratedEngine:
    STAGE_MAP = {
        1: "마음사기", 2: "수강 목적성 심기", 3: "영 인지", 4: "성경 인정",
        5: "선악구분", 6: "시대구분", 7: "말씀 인정", 8: "종교 세계 인식",
        9: "약속의 목자 인정", 10: "약속한 성전 인정"
    }

    @staticmethod
    def find_value(row_data, keywords):
        for k in row_data.keys():
            if any(kw in str(k) for kw in keywords):
                return str(row_data[k]).strip()
        return ""

    @staticmethod
    def is_actual_student(row_data):
        """출석 데이터 유무와 이름 키워드로 실제 수강생인지 판별"""
        # 첫 번째 열 데이터를 이름으로 가정
        name = str(list(row_data.values())[0]).strip()
        
        # 제외 키워드 (관리자 및 항목명)
        exclude_list = [
            '인도자', '교사', '섬김이', '기본정보', '고민', '관심사', 
            '경제력', '건강상태', '종교', '수강환경', 'nan', 'NAN', '항목', '내용'
        ]
        if any(ex in name for ex in exclude_list) or not name or name == 'None':
            return False

        # 출석 관련 기록이 있는지 확인 (사용자 제안 로직)
        attendance_hit = 0
        for k, v in row_data.items():
            val_str = str(v).strip()
            if pd.notna(v) and val_str != "" and val_str != 'nan':
                # 열 이름에 날짜나 출석 관련 키워드가 있는 경우
                if any(kw in str(k) for kw in ['월', '일', '회', '출석', '체크']):
                    attendance_hit += 1
        
        return attendance_hit > 0

    @staticmethod
    def analyze_student(row, admin_info, situation, strategy):
        name = str(list(row.values())[0]).strip()
        mbti = IntegratedEngine.find_value(row, ['MBTI', '성향', 'mbti']).upper()
        raw_step = IntegratedEngine.find_value(row, ['단계', '과정', '레벨'])
        
        if not mbti or not raw_step:
            return None, "⚠️ 데이터 부족", f"{name}님: MBTI/단계 정보 누락"

        try:
            step_num = int(re.findall(r'\d+', raw_step)[0])
            step_level = "상" if "상" in raw_step else "중" if "중" in raw_step else "하"
        except:
            return None, "⚠️ 단계 인식 불가", "단계 정보를 '4상' 형태로 확인하세요."

        # 유튜브 및 상황 가중치
        yt_weight = 15 if ("youtube.com" in situation or "youtu.be" in situation) else 0
        base_score = 55 + (step_num * 2) + yt_weight
        
        # 전략 보너스 (MBTI 기반)
        strat_benefit = 0
        if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '팩트', '근거']): strat_benefit += 10
        if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '면담', '경청']): strat_benefit += 10

        final_risk = base_score - strat_benefit
        return min(max(final_risk, 0), 100), f"{IntegratedEngine.STAGE_MAP.get(step_num, '분석')} ({step_level})", f"{name}님 맞춤 관리가 권장됩니다."

# 3. 사이드바 (모든 전도사 설정 및 17개 MBTI 적용)
with st.sidebar:
    st.header("📂 데이터 통합 설정")
    st.subheader("1. 공통 출석부")
    common_file = st.file_uploader("전체 출석부 업로드", type=["xlsx", "csv"], key="common_att")
    st.markdown("---")
    
    admins = []
    # [수정] 17개 전체 MBTI 리스트 구성
    mbti_full_list = ["모름", "ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", 
                      "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
    
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 상세 설정", expanded=False):
            a_file = st.file_uploader(f"{label}반 개별 파일", type=["xlsx", "csv"], key=f"f_{label}")
            # [수정 확인] 이제 17개 옵션이 모두 나타납니다.
            a_mbti = st.selectbox(f"{label} MBTI", mbti_full_list, key=f"m_{label}")
            a_ennea = st.selectbox(f"{label} 애니어그램", ["모름"] + [str(i) for i in range(1, 10)], key=f"e_{label}")
            a_gender = st.radio(f"{label} 성별", ["모름", "남", "여"], key=f"g_{label}")
            admins.append({'label': label, 'file': a_file, 'mbti': a_mbti, 'ennea': a_ennea, 'gender': a_gender})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v4.6")
col_inp, col_chart = st.columns([1, 1.2])

with col_inp:
    st.subheader("🎯 시나리오 및 전략")
    situation = st.text_area("🌐 발생 상황 (유튜브 링크 등)", height=100)
    strategy_input = st.text_area("🛡️ 대응 전략 (강사/전도사 계획)", height=100)
    run_btn = st.button("AI 시뮬레이션 가동 🚀", use_container_width=True)

# 5. 실행 로직
if run_btn:
    raw_records = []
    for admin in admins:
        if admin['file'] is not None:
            try:
                df = pd.read_excel(admin['file']) if admin['file'].name.endswith('xlsx') else pd.read_csv(admin['file'])
                for _, row in df.iterrows():
                    d = row.to_dict()
                    # 출석 기반 실 수강생 필터링
                    if IntegratedEngine.is_actual_student(d):
                        d['_admin_info'] = admin
                        raw_records.append(d)
            except Exception as e:
                st.error(f"파일 처리 중 오류: {e}")

    if raw_records:
        results = []
        for d in raw_records:
            risk, stage, advice = IntegratedEngine.analyze_student(d, d['_admin_info'], situation, strategy_input)
            name = str(list(d.values())[0]).strip()
            results.append({
                'name': name, 'admin': d['_admin_info']['label'],
                'risk': risk, 'stage': stage, 'advice': advice,
                'mbti': IntegratedEngine.find_value(d, ['MBTI', '성향']).upper()
            })

        df_res = pd.DataFrame(results).drop_duplicates(subset=['name'])
        
        with col_chart:
            v_risks = [r['risk'] for r in df_res.to_dict('records') if r['risk'] is not None]
            if v_risks:
                avg = 100 - (sum(v_risks) / len(v_risks))
                st.plotly_chart(go.Figure(go.Indicator(
                    mode="gauge+number", value=avg,
                    title={'text': f"🛡️ 기수 안전도 ({len(df_res)}명)"},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#22c55e"}}
                )), use_container_width=True)

        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(df_res.to_dict('records')):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val and r_val > 70 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:220px;">
                        <h4 style="margin:0;">{res['name']} <small>({res['admin']}반)</small></h4>
                        <p style="font-size:0.85em;"><b>성향:</b> {res['mbti']} | <b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.8em; color:#555;">{res['advice']}</p>
                        <div style="text-align:right; font-weight:bold; color:{color};">위기: {int(r_val) if r_val else '-'}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("수강생 데이터가 없습니다. 파일을 확인하거나 사이드바에 파일을 업로드해주세요.")
