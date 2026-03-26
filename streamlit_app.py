import streamlit as st
import pandas as pd
import io

# 1. 페이지 설정 및 NanoBanana 스타일 테마 적용
st.set_page_config(page_title="Data Intelligence Dashboard v8.8", layout="wide")

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 설정 */
    .stApp { background-color: #f8f9fa; }
    
    /* 사이드바 스타일: 입력 가독성 극대화 */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #eef0f2;
        padding-top: 2rem;
    }
    
    /* 카드형 컨테이너 디자인 */
    .content-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 24px;
        border: 1px solid #f0f2f5;
    }
    
    /* 헤더 및 텍스트 스타일 */
    .section-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 사이드바: 모든 핵심 입력 기능 (전략, 비디오, 파일)
with st.sidebar:
    st.markdown("<div class='section-title'>⚙️ Control Panel</div>", unsafe_allow_html=True)
    
    # 분석 전략 입력
    st.subheader("1. Analysis Strategy")
    user_strategy = st.text_area(
        "분석 지침 및 전략",
        placeholder="데이터 분석 시 적용할 전략을 입력하세요...",
        height=150
    )
    
    # 비디오 링크 입력
    st.subheader("2. Video Source")
    video_url = st.text_input(
        "비디오 URL",
        placeholder="https://youtube.com/..."
    )
    
    # 파일 업로드
    st.subheader("3. Data Upload")
    uploaded_file = st.file_uploader("수강생 명단 (CSV)", type=['csv'])
    
    st.divider()
    run_btn = st.button("RUN ANALYSIS", use_container_width=True, type="primary")

# 3. 메인 화면: 결과 대시보드
st.title("📊 Analysis Intelligence")

if run_btn:
    # 대시보드 레이아웃 구성
    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        # 비디오 섹션
        if video_url:
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🎥 Reference Video</div>", unsafe_allow_html=True)
            st.video(video_url)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 전략 요약 섹션
        if user_strategy:
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🎯 Strategy Overview</div>", unsafe_allow_html=True)
            st.info(user_strategy)
            st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        if uploaded_file:
            # [핵심 로직] 파일 원본 텍스트 스캔 (전도사 정보 보존용)
            raw_bytes = uploaded_file.getvalue()
            decoded_text = raw_bytes.decode('utf-8-sig', errors='ignore')
            lines = decoded_text.split('\n')
            
            # 1단계: 상단 '전도사/교사' 정보 추출
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>👤 Staff Information</div>", unsafe_allow_html=True)
            
            staff_info_found = False
            for line in lines[:10]: # 상단 10줄 집중 스캔
                if any(k in line for k in ['전도사', '교사', '인도자', '실제인도자']):
                    clean_line = line.replace(',', ' ').strip()
                    if clean_line:
                        st.write(f"🔹 **{clean_line}**")
                        staff_info_found = True
            
            if not staff_info_found:
                st.caption("파일 상단에서 담당자 정보를 찾을 수 없습니다.")
            st.markdown("</div>", unsafe_allow_html=True)

            # 2단계: 수강생 명단 데이터프레임 처리
            try:
                # '이름' 컬럼이 있는 행을 찾아 데이터 시작점으로 설정
                header_row = 0
                for i, line in enumerate(lines):
                    if '이름' in line:
                        header_row = i
                        break
                
                df = pd.read_csv(io.StringIO(decoded_text), skiprows=header_row)
                # 데이터 정제: 불필요한 빈 열 제거
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')].dropna(subset=['이름'])
                
                st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>📋 Student Data List</div>", unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"데이터 본문을 처리하는 중 오류가 발생했습니다: {e}")

else:
    # 초기 안내 화면
    st.markdown("""
        <div style='text-align: center; padding: 80px 20px; border: 2px dashed #dce1e6; border-radius: 20px; background-color: #fff;'>
            <h2 style='color: #b0b8c1;'>분석 준비 완료</h2>
            <p style='color: #8b95a1;'>사이드바에서 전략, 비디오 링크, 파일을 입력한 후 <b>RUN ANALYSIS</b> 버튼을 클릭하세요.</p>
        </div>
    """, unsafe_allow_html=True)
