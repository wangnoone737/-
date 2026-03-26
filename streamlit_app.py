import streamlit as st
import pandas as pd
import io

# 1. 페이지 테마 설정 (심미성과 기능성 동시 확보)
st.set_page_config(page_title="Integrated Data Intelligence", layout="wide")

# CSS를 통한 UI 복구 및 개선
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    /* 사이드바 너비 조절 및 스타일 */
    [data-testid="stSidebar"] { background-color: #ffffff; min-width: 350px; border-right: 1px solid #e0e0e0; }
    /* 입력란 라벨 스타일 */
    .stTextArea label, .stTextInput label { font-weight: bold; color: #4A4A4A; }
    /* 결과 카드 스타일 */
    .content-card {
        background-color: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .main-title { font-size: 26px; font-weight: 800; color: #1E1E1E; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. [핵심 기능 1] 사이드바 입력창 (사라졌던 모든 입력란 복구)
with st.sidebar:
    st.markdown("<p class='main-title'>Control Panel</p>", unsafe_allow_html=True)
    
    # 전략 입력 (Strategy)
    user_strategy = st.text_area("🎯 분석 전략 (Analysis Strategy)", 
                                 placeholder="여기에 분석 지침이나 전략을 입력하세요...", height=150)
    
    # 비디오 링크 (Video URL)
    video_link = st.text_input("🔗 비디오 소스 링크 (Video URL)", 
                               placeholder="https://www.youtube.com/watch?v=...")
    
    # 파일 업로드 (CSV File)
    uploaded_file = st.file_uploader("📂 수강생 데이터 업로드 (CSV)", type=['csv'])
    
    st.divider()
    process_btn = st.button("실행 및 결과 생성", use_container_width=True, type="primary")

# 3. [핵심 기능 2] 메인 대시보드 (디자인 개선 및 데이터 보존)
st.markdown("<h2 style='margin-bottom:30px;'>📊 통합 분석 리포트</h2>", unsafe_allow_html=True)

if process_btn:
    # 레이아웃 분할: 왼쪽(미디어/전략), 오른쪽(데이터/전도사 정보)
    left_col, right_col = st.columns([1, 1.2])

    with left_col:
        # 비디오 출력 섹션
        if video_link:
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.subheader("Video Reference")
            st.video(video_link)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 전략 요약 섹션
        if user_strategy:
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.subheader("Strategy Focus")
            st.info(user_strategy)
            st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        if uploaded_file:
            # [전도사 입력란 보존 로직]
            # 파일을 줄 단위로 읽어 상단의 전도사/교사 정보를 먼저 추출
            raw_bytes = uploaded_file.getvalue()
            raw_text = raw_bytes.decode('utf-8-sig', errors='ignore')
            lines = raw_text.split('\n')
            
            # 상단 10줄 내에서 담당자 정보 추출 (디자인 개선을 위해 카드화)
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            st.subheader("👤 담당 사명자 정보")
            staff_found = False
            for line in lines[:8]:
                if any(keyword in line for keyword in ['전도사', '교사', '인도자', '섬김이']):
                    cols = line.split(',')
                    clean_line = " | ".join([c.strip() for c in cols if c.strip()])
                    if clean_line:
                        st.write(f"✅ {clean_line}")
                        staff_found = True
            if not staff_found:
                st.write("상단 행에서 담당자 정보를 찾을 수 없습니다. (CSV 형식을 확인해 주세요)")
            st.markdown("</div>", unsafe_allow_html=True)

            # 수강생 명단 및 데이터 분석 (기능 훼손 방지)
            try:
                # 데이터 시작 지점을 '이름' 컬럼 기준으로 자동 감지
                header_idx = 0
                for i, line in enumerate(lines):
                    if '이름' in line:
                        header_idx = i
                        break
                
                df = pd.read_csv(io.StringIO(raw_text), skiprows=header_idx)
                # 불필요한 공백 열 제거 및 정제
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')].dropna(subset=['이름'])
                
                st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                st.subheader("📋 수강생 상세 분석 내역")
                st.dataframe(df, use_container_width=True, height=400)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"데이터 본문을 불러오는 중 오류가 발생했습니다: {e}")

else:
    # 초기 진입 화면 (가이드)
    st.markdown("""
        <div style='background-color: white; padding: 50px; border-radius: 15px; text-align: center; border: 2px dashed #d0d0d0;'>
            <h3 style='color: #888;'>사이드바에서 비디오, 전략, 파일을 입력한 후 버튼을 눌러주세요.</h3>
            <p style='color: #aaa;'>모든 입력 정보가 누락 없이 대시보드에 반영됩니다.</p>
        </div>
    """, unsafe_allow_html=True)
