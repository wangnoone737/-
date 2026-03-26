import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="Center Risk Simulator", page_icon="🏛️", layout="wide")

# 2. 디자인 테마
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #3b82f6; margin-bottom: 1rem; }
    .student-card { background: white; padding: 1.2rem; border-radius: 1rem; border-top: 5px solid #ef4444; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1rem; min-height: 200px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ 센터 위기 관리 전략 시뮬레이터")
st.markdown("---")

# 3. 사이드바: 데이터 업로드
with st.sidebar:
    st.header("📂 데이터 주입")
    file_att = st.file_uploader("1. 출석부 파일 (CSV)", type="csv")
    file_admin = st.file_uploader("2. 전도사반 파일 (CSV/Excel)", type="csv")
    st.info("💡 파일을 업로드하면 6명의 수강생 데이터가 로드됩니다.")

# 4. 데이터 로직 (6명 고정)
def get_student_data():
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

df_students = get_student_data()

# 5. 메인 화면: 상황 및 전략 입력
c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("🎯 전략 시뮬레이션 설정")
    situation = st.text_area("🌐 상황 (유튜브 링크 또는 사건)", placeholder="예: 비판 영상 공유됨")
    plan = st.text_area("🛡️ 대응 전략 (강사/전도사 계획)", placeholder="예: 개별 상담 및 믿음 강조")
    run_btn = st.button("분석 실행 🚀", use_container_width=True)

with c2:
    st.subheader("📊 기수 전반 위기 리포트")
    if run_btn:
        avg_risk = 65.5
        fig = px.gauge(value=avg_risk, title="🔥 기수 전체 흔들림 정도", gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#ef4444"}})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""
            <div class="metric-card">
                <h4>🧠 AI 집단 심리 분석</h4>
                <p>영상의 논조가 '단계별 지식'을 공격할 때, 심리적 흔들림이 발생할 수 있습니다.</p>
                <p>현재 대응 계획은 고위험군의 이탈을 관리하는 데 초점이 맞춰져 있습니다.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("👈 왼쪽에서 상황을 입력하고 버튼을 눌러주세요.")

# 6. 하단: 개별 수강생 상세 분석
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
                    <p style="font-size: 0.85em; color: #4b5563;"><b>AI 예측:</b> 상황 발생 시 내적 갈등 지수 상승 우려</p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.write("분석을 실행하면 수강생별 맞춤 카드가 생성됩니다.")
