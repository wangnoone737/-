import streamlit as st
import pandas as pd
import io

# 1. 시각적 레이아웃 설정 (NanoBanana 테마 적용)
st.set_page_config(page_title="Data Analysis Dashboard", layout="wide")

st.markdown("""
    <style>
    /* 메인 배경 및 폰트 설정 */
    .stApp { background-color: #F0F2F6; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; width: 400px !important; }
    
    /* 카드형 UI 스타일 */
    .stat-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .header-style { color: #1E1E1E; font-weight: 800; font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. 사이드바: 모든 입력 기능 통합 (사용자 요구사항 반영)
with st.sidebar:
    st.markdown("<p class='header-style'>Input Controls</p>", unsafe_allow_html=True)
    
    # 전략 입력란
    strategy = st.text_area("Analysis Strategy", placeholder="분석 전략을 입력하세요...")
    
    # 비디오 링크 입력란
    video_url = st.text_input("Video URL", placeholder="https://youtube.com/...")
    
    # 파일 업로드 (전도사 정보 보존 로직 포함)
    uploaded_file = st.file_uploader("Upload Student Data (CSV)", type=['csv'])
    
    st.divider()
    run_analysis = st.button("🚀 Generate Analysis", use_container_width=True)

# 3. 메인 화면: 결과 대시보드 시각화
st.title("📊 Analysis Result Dashboard")

if run_analysis:
    col1, col2 = st.columns([1, 1])
    
    # [왼쪽 영역] 비디오 및 데이터 요약
    with col1:
        if video_url:
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            st.video(video_url)
            st.caption("참조 비디오 데이터")
            st.markdown("</div>", unsafe_allow_html=True)
        
        if strategy:
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            st.subheader("Target Strategy")
            st.info(strategy)
            st.markdown("</div>", unsafe_allow_html=True)

    # [오른쪽 영역] 데이터 분석 및 전도사 정보 (무결성 유지)
    with col2:
        if uploaded_file:
            # 전도사 정보가 담긴 상단부와 하단 데이터를 분리해서 인식
            raw_content = uploaded_file.getvalue().decode('utf-8-sig')
            
            # 전도사/교사 정보만 따로 추출하는 정밀 스캔
            lines = raw_content.split('\n')
            staff_info = [line for line in lines[:10] if any(k in line for k in ['전도사', '교사', '인도자'])]
            
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            st.subheader("Staff in Charge")
            if staff_info:
                for staff in staff_info:
                    clean_staff = staff.replace(',', ' ').strip()
                    if clean_staff: st.write(f"👤 {clean_staff}")
            else:
                st.warning("전도사 정보 필드를 스캔 중입니다.")
            st.markdown("</div>", unsafe_allow_html=True)

            # 수강생 상세 명단 분석
            try:
                # '이름' 컬럼을 찾아 데이터 시작점 포착
                df = pd.read_csv(io.StringIO(raw_content), skiprows=2) # 실제 구조에 맞춰 조정
                st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
                st.subheader("Student Intelligence")
                st.dataframe(df.head(10), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            except:
                st.error("데이터 구조를 분석하는 데 실패했습니다.")

else:
    # 초기 대기 화면 (Aesthetic Design)
    st.markdown("""
        <div style='text-align: center; padding: 100px;'>
            <h2 style='color: #BDC3C7;'>준비된 파일과 전략을 입력하고<br>'Generate Analysis' 버튼을 눌러주세요.</h2>
        </div>
    """, unsafe_allow_html=True)
