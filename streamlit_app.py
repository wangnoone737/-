import streamlit as st
import pandas as pd
import io

# 1. 8.8 버전 본연의 레이아웃 설정
st.set_page_config(page_title="NanoBanana Data Dashboard v8.8", layout="wide")

# 2. 사이드바 구성 (사용자 의도가 가장 잘 반영된 입력창)
with st.sidebar:
    st.title("Input Control")
    
    # 전략 입력
    st.subheader("Analysis Strategy")
    strategy_input = st.text_area("전략 및 지침을 입력하세요", height=200)
    
    # 비디오 URL
    st.subheader("Video URL")
    video_url = st.text_input("유튜브 또는 비디오 링크")
    
    # 파일 업로드
    st.subheader("File Upload")
    uploaded_file = st.file_uploader("수강생 명단 CSV 파일을 선택하세요", type=['csv'])
    
    st.divider()
    # 실행 버튼
    generate_btn = st.button("Generate Result", use_container_width=True)

# 3. 메인 화면 출력 로직
st.title("Analysis Result")

if generate_btn:
    # 8.8 버전 특유의 2분할 화면 구성
    col1, col2 = st.columns([1, 1])

    with col1:
        # 비디오 출력
        if video_url:
            st.video(video_url)
        
        # 전략 출력
        if strategy_input:
            st.info(f"**Current Strategy:**\n\n{strategy_input}")

    with col2:
        if uploaded_file:
            # [8.8 핵심 로직] 전도사/교사 정보 추출을 위한 원본 스캔
            raw_data = uploaded_file.getvalue().decode('utf-8-sig')
            lines = raw_data.split('\n')
            
            # 상단 10행 내에서 전도사, 교사, 인도자 키워드 추출
            st.subheader("Staff & Manager Info")
            found_staff = False
            for line in lines[:10]:
                if any(k in line for k in ['전도사', '교사', '인도자', '섬김이']):
                    st.write(f"✔️ {line.strip().replace(',', ' ')}")
                    found_staff = True
            
            if not found_staff:
                st.caption("담당자 정보를 찾을 수 없습니다.")

            st.divider()

            # 데이터 본문 로드 (이름 컬럼 기준 동적 스킵)
            try:
                header_index = 0
                for i, line in enumerate(lines):
                    if '이름' in line:
                        header_index = i
                        break
                
                df = pd.read_csv(io.StringIO(raw_data), skiprows=header_index)
                # 불필요 컬럼 제거
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
                st.subheader("Student Data List")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"데이터 로드 오류: {e}")

else:
    st.write("사이드바에 데이터를 입력하고 'Generate Result' 버튼을 눌러주세요.")
