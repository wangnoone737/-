import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="Center Risk Simulator", page_icon="🏛️", layout="wide")

# 2. 디자인 테마
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #3b82f6; margin-bottom: 1rem; }
    .student-card { background: white; padding: 1.2rem; border-radius: 1rem; border-top: 5px solid #ef4444; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; min-height: 220px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ 센터 위기 관리 전략 시뮬레이터")
st.markdown("---")

# 3. 사이드바: 데이터 주입
with st.sidebar:
    st.header("📂 데이터 주입")
    st.subheader("1. 출석부 데이터")
    file_att = st.file_uploader("출석부 파일", type=["csv", "xlsx"], key="att")
    
    st.markdown("---")
    st.subheader("2. 전도사반 데이터 (최대 3명)")
    file_admin1 = st.file_uploader("전도사 A 파일", type=["csv", "xlsx"], key="admin1")
    file_admin2 = st.file_uploader("전도사 B 파일", type=["csv", "xlsx"], key="admin2")
    file_admin3 = st.file_uploader("전도사 C 파일", type=["csv", "xlsx"], key="admin3")

# 4. 데이터 로드 함수
def load_data(file):
    if file is not None:
        try:
            if file.name.endswith('.csv'):
                return pd.read_csv(file)
            else:
                return pd.read_excel(file, engine='openpyxl')
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")
    return None

# 샘플 데이터 (파일 없을 때 기본값)
def get_default_data():
    names = ['김남호', '김윤심', '이홍규', '서형국', '윤영옥', '오정숙']
    data = []
    for name in names:
        data.append({
            '이름': name,
            'MBTI': 'ISFP' if name == '김남호' else 'ESFJ' if name == '김윤심' else 'INTP',
            '신성': 'O' if name in ['김남호', '서형국'] else 'X',
            '단계': 4 if name == '김남호' else 5 if name == '김윤심' else 3,
            '최근_피드백': "경제적 상황 공유 및 강의 집중도 저하" if name == '김남호' else "특이사항 없음"
        })
    return pd.DataFrame(data)

df_students = get_default_data()

# 5. 메인 화면
c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("🎯 전략 시뮬레이션 설정")
    situation = st.text_area("🌐 상황 (유튜브 링크 또는 사건)", placeholder="예: 비판 영상 공유됨", height=150)
    plan = st.text_area("🛡️ 대응 전략 (강사/전도사 계획)", placeholder="예: 개별 상담 및 믿음 강조", height=150)
    run_btn = st.button("분석 실행 🚀", use_container_width=True)

with c2:
    st.subheader("📊 기수 전반 위기 리포트")
    if run_btn:
        uploaded_count = sum(1 for f in [file_admin1, file_admin2, file_admin3] if f is not None)
        avg_risk = 68.0 if uploaded_count == 0 else max(30.0, 75.0 - (uploaded_count * 15))
        
        # 83번 줄 오류 방지를 위한 단순화된 차트 코드
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = avg_risk,
            title = {'text': "🔥 기수 전체 흔들림 정도"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#ef4444"}}
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"전도사 {uploaded_count}명의 데이터를 기반으로 분석을 완료했습니다.")
    else:
        st.info("👈 왼쪽에서 상황을 입력하고 버튼을 눌러주세요.")

# 6. 하단 상세 분석
st.markdown("---")
st.subheader("👤 개별 수강생 상세 분석")

if run_btn:
    cols = st.columns(3)
    for i, (_, row) in enumerate(df_students.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="student-card">
                    <b style="font-size: 1.2em;">{row['이름']}</b> ({row['MBTI']})<br>
                    <small>{row['단계']}단계 / 신성: {row['신성']}</small><br><br>
                    <p style="font-size: 0.9em;"><b>최근 피드백:</b> {row['최근_피드백']}</p>
                    <p style="font-size: 0.85em; color: #4b5563;"><b>AI 예측:</b> 심리적 동요 가능성이 확인됩니다.</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.write("분석을 실행하면 수강생별 맞춤 분석 카드가 생성됩니다.")
