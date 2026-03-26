import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from openpyxl import load_workbook

# 1. 페이지 설정
st.set_page_config(page_title="Hierarchical Strategy Simulator", page_icon="🏗️", layout="wide")

# 2. 분석 엔진 (병합 셀 구조 분석형)
class StructuralEngine:
    STAGE_MAP = {i: f"{name}" for i, name in enumerate(["", "마음사기", "수강 목적성 심기", "영 인지", "성경 인정", "선악구분", "시대구분", "말씀 인정", "종교 세계 인식", "약속의 목자 인정", "약속한 성전 인정"])}

    @staticmethod
    def parse_hierarchical_sheet(file_path, sheet_name):
        """[핵심] 사용자 제안 로직: 병합 셀 구조에 따른 데이터 추출"""
        wb = load_workbook(file_path, data_only=True)
        ws = wb[sheet_name]
        
        extracted_data = {}
        merged_ranges = ws.merged_cells.ranges
        
        # 시트의 모든 셀을 순회하며 정보 추출
        for row in range(1, ws.max_row + 1):
            for col in range(1, ws.max_column + 1):
                cell = ws.cell(row=row, column=col)
                val = str(cell.value).strip() if cell.value else ""
                
                # 병합된 셀(대분류)인지 확인
                is_merged = False
                for r in merged_ranges:
                    if cell.coordinate in r:
                        is_merged = True
                        break
                
                # 사용자 논리 6, 7번: 열에 따른 항목/내용 구분 (홀수:항목, 짝수:내용)
                if val and not is_merged:
                    if col % 2 == 1: # 항목
                        content_cell = ws.cell(row=row, column=col+1)
                        c_val = str(content_cell.value).strip() if content_cell.value else ""
                        if c_val: extracted_data[val] = c_val
        return extracted_data

    @staticmethod
    def identify_student(row_dict, sheet_name):
        s_name = str(sheet_name).strip()
        exclude = ['인도자', '교사', '섬김이', '기본정보', '상세정보', '항목', '내용', 'Sheet', '시트', '단계', '과정']
        if any(ex in s_name for ex in exclude): return None
        
        s_parts = re.split(r'[_ \-]', re.sub(r'(nan|None|알수없음)', '', s_name))
        row_vals = set(str(v).strip() for v in row_dict.values() if v)
        
        for p in s_parts:
            if len(p) >= 2 and p in row_vals: return p
        return None

    @staticmethod
    def analyze_v5_8(data_dict, name, admin_info, situation, strategy):
        # 텍스트 합산 (맥락 파악)
        context = " ".join([f"{k}:{v}" for k, v in data_dict.items()])
        
        # 필수 정보 추출 (MBTI, 단계)
        mbti = ""
        for m in ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]:
            if m in context.upper(): mbti = m; break
        
        step_match = re.search(r'(\d+)\s*(단계|과정|레벨)', context)
        step_num = int(step_match.group(1)) if step_match else 0
        
        # 데이터 결손 체크
        missing = []
        if not mbti: missing.append("MBTI")
        if step_num == 0: missing.append("수강 단계")
        if not any(kw in context for kw in ['고민', '상황', '가족']): missing.append("배경 맥락")

        # 위기 지수 계산
        yt_plus = 15 if any(kw in situation for kw in ["youtube.com", "youtu.be"]) else 0
        ctx_risk = 10 if any(kw in context for kw in ['의심', '불안', '핍박', '인터넷']) else -5
        gender_risk = 5 if admin_info['gender'] != "모름" else 0
        
        base = 55 + (step_num * 2) + yt_plus + ctx_risk + gender_risk
        
        bonus = 0
        if mbti:
            if 'T' in mbti and any(w in strategy for w in ['논리', '설명', '팩트']): bonus = 12
            if 'F' in mbti and any(w in strategy for w in ['공감', '위로', '경청']): bonus = 12

        final = min(max(base - bonus, 0), 100)
        return final, StructuralEngine.STAGE_MAP.get(step_num, "분석중"), f"{name}님 시트 구조 분석 완료.", missing

# 3. 사이드바 (누락 방지)
with st.sidebar:
    st.header("📂 통합 설정 v5.8")
    st.subheader("1. 공통 파일")
    common_file = st.file_uploader("전체 출석부", type=["xlsx"], key="com")
    st.markdown("---")
    
    admins = []
    for label in ["A", "B", "C"]:
        with st.expander(f"👤 전도사 {label} 설정"):
            f = st.file_uploader(f"{label}반 파일", type=["xlsx"], key=f"f_{label}")
            g = st.radio(f"{label} 성별", ["남", "여", "모름"], index=2, key=f"g_{label}")
            admins.append({'label': label, 'file': f, 'gender': g})

# 4. 메인 화면
st.title("🏛️ 전략 시뮬레이션 시스템 v5.8")
c_inp, c_chart = st.columns([1, 1.2])

with c_inp:
    situation = st.text_area("🌐 발생 상황", height=80)
    strategy = st.text_area("🛡️ 대응 전략", height=80)
    run_btn = st.button("구조화 분석 가동 🚀", use_container_width=True)

if run_btn:
    final_results = []
    for admin in admins:
        if admin['file']:
            # 파일 임시 저장 후 openpyxl로 분석
            with open("temp.xlsx", "wb") as f:
                f.write(admin['file'].getbuffer())
            
            xl = pd.ExcelFile("temp.xlsx")
            for sheet in xl.sheet_names:
                # 1. 시트 구조 분석 (사용자 논리 적용)
                data_dict = StructuralEngine.parse_hierarchical_sheet("temp.xlsx", sheet)
                
                # 2. 이름 식별 (pandas 병용)
                df_temp = xl.parse(sheet)
                for _, row in df_temp.iterrows():
                    name = StructuralEngine.identify_student(row.to_dict(), sheet)
                    if name:
                        risk, stage, advice, missing = StructuralEngine.analyze_v5_8(data_dict, name, admin, situation, strategy)
                        final_results.append({'name': name, 'admin': admin['label'], 'risk': risk, 'stage': stage, 'advice': advice, 'missing': missing})
                        break
    
    if final_results:
        df_f = pd.DataFrame(final_results).drop_duplicates(subset=['name'])
        with c_chart:
            rs = [r['risk'] for r in df_f.to_dict('records') if r['risk']]
            if rs:
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=100-(sum(rs)/len(rs)), title={'text': "🛡️ 전체 안전도"}, gauge={'axis':{'range':[0,100]}})), use_container_width=True)

        st.markdown("---")
        cols = st.columns(3)
        for i, res in enumerate(df_f.to_dict('records')):
            with cols[i % 3]:
                r_val = res['risk']
                color = "#ef4444" if r_val > 70 else "#3b82f6"
                st.markdown(f"""
                    <div style="border-top:5px solid {color}; padding:15px; background:white; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:15px; min-height:280px;">
                        <h4 style="margin:0;">{res['name']} <small>({res['admin']}반)</small></h4>
                        <p style="font-size:0.85em;"><b>단계:</b> {res['stage']}</p>
                        <hr>
                        <p style="font-size:0.82em; color:#333;">{res['advice']}</p>
                        <div style="background:#f1f5f9; padding:8px; border-radius:5px; margin-top:10px;">
                            <p style="font-size:0.72em; color:#475569; margin:0;"><b>💡 구조 분석 가이드:</b></p>
                            <p style="font-size:0.72em; color:#1e293b; margin:0;">{', '.join(res['missing']) + ' 정보가 누락되었습니다.' if res['missing'] else '구조화된 모든 정보를 분석했습니다.'}</p>
                        </div>
                        <div style="text-align:right; font-weight:bold; color:{color}; margin-top:10px;">위기: {int(r_val)}점</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("시트 구조와 일치하는 데이터를 찾지 못했습니다.")
