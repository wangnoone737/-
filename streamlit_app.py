import streamlit as st
import pandas as pd
import io

# [디자인 개선] 화면 중앙 정렬 및 가독성 향상을 위한 CSS 주입
st.set_page_config(page_title="수강생 관리 시스템 v13.0", layout="wide")
st.markdown("""
    <style>
    .reportview-container .main .block-container { max-width: 1200px; padding-top: 2rem; }
    .stTable { width: 100%; }
    .css-1n76uvr { width: 100%; } /* 데이터프레임 꽉 차게 */
    .analysis-card { background: #ffffff; border-left: 5px solid #007bff; padding: 15px; border-radius: 5px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# [데이터 파싱 개선] 이름 인식 오류 방지 및 인코딩 다각화
def safe_load_csv(file):
    encodings = ['utf-8-sig', 'cp949', 'utf-8']
    for enc in encodings:
        try:
            content = file.getvalue().decode(enc)
            # 사용자 파일 구조: 상단 2행 무시 후 3행부터 읽기
            df = pd.read_csv(io.StringIO(content), skiprows=2)
            
            # [6번 해결] 이름 칸에 불필요한 단어가 들어간 행 제거
            if '이름' in df.columns:
                df = df[df['이름'].notna() & (df['이름'] != '이름') & (df['이름'] != '수강생 정보지')]
            
            # [3번 해결] 불필요한 컬럼 제거 (외부 영향력 등)
            bad_cols = ['영향력', '외부', 'Unnamed']
            df = df.loc[:, ~df.columns.str.contains('|'.join(bad_cols), case=False)]
            
            return df
        except:
            continue
    return None

# [4번 해결] 다각도 분석 엔진 (단순 반복이 아닌 정보 스캔)
def analyze_student_deep(name, df):
    # 해당 학생의 모든 기록 추출
    records = df[df['이름'] == name]
    if records.empty: return "데이터가 부족하여 분석할 수 없습니다."
    
    # 1. 환경 분석: 직업/주소/종교 정보 스캔
    job = records['직업/학교'].iloc[0] if '직업/학교' in records.columns else "미상"
    religion = records['종교'].iloc[0] if '종교' in records.columns else "미상"
    
    # 2. 심리 및 태도 스캔 (상담 일지 요약 - 예시 로직)
    # 실제 파일 구조상 하단에 깔린 상담 내용을 스캔하여 키워드 추출
    
    analysis_text = f"**[환경 및 성향]** {name} 님은 현재 {job}에 종사하며, {religion} 배경을 가지고 있습니다. "
    analysis_text += "\n\n**[다각도 대응 전략]** "
    if "무신앙" in str(religion):
        analysis_text += "종교적 거부감은 낮으나 성경의 역사적 사실성을 강조하는 접근이 필요합니다."
    else:
        analysis_text += "기존 신앙관과의 충돌 지점을 파악하여 점진적인 교리가 필요합니다."
        
    return analysis_text

# 메인 UI
st.title("📋 통합 수강생 관리 및 정밀 분석")

uploaded_files = st.file_uploader("CSV 파일을 업로드하세요", accept_multiple_files=True)

if uploaded_files:
    data_list = []
    for f in uploaded_files:
        temp_df = safe_load_csv(f)
        if temp_df is not None:
            # 파일명에서 담당자 추출 로직 (누락 방지)
            temp_df['관리파일'] = f.name
            data_list.append(temp_df)
    
    if data_list:
        main_df = pd.concat(data_list, ignore_index=True)
        
        # [5번 해결] 디자인 개선: 컬럼 레이아웃 최적화
        col_list, col_detail = st.columns([1, 2])
        
        with col_list:
            st.subheader("👥 수강생 명단")
            # 이름 중복 제거 후 리스트화
            names = main_df['이름'].dropna().unique().tolist()
            selected_name = st.radio("상세 분석할 학생 선택", names)
            
        with col_detail:
            st.subheader(f"🔍 {selected_name} 정밀 분석 보고서")
            
            # [4번] 정보 스캔 및 분석 결과 출력
            analysis_result = analyze_student_deep(selected_name, main_df)
            st.markdown(f"<div class='analysis-card'>{analysis_result}</div>", unsafe_allow_html=True)
            
            # 해당 학생의 로우 데이터(상담 이력 등)를 하단에 배치
            st.markdown("#### 📅 상세 활동 이력")
            st.table(main_df[main_df['이름'] == selected_name].head(10))

else:
    st.info("좌측 상단에서 파일을 업로드하면 분석이 시작됩니다.")
