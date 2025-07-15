import streamlit as st
import pandas as pd

# 🗂️ 구글 스프레드시트 csv 링크
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0rXK4SMIQZS0_U2uVXMw8qJ6BThe1wB-lapp0XOE5NV2HNf29js3_WCq4tzE42EEi8odSGkQM_Cuv/pub?output=csv"

if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.session_state["refresh_triggered"] = True

# 새로고침이 눌린 경우 rerun 실행
if st.session_state.get("refresh_triggered", False):
    st.session_state["refresh_triggered"] = False
    st.rerun()

# 📦 데이터 로딩 함수 (캐시 적용)
@st.cache_data
def load_data():
    df = pd.read_csv(sheet_url)

    # 🧹 빈 값 있는 행 제거
    df = df.dropna(subset=["Model", "Line", "Time", "OK", "NG"])

    # 🔢 계산 필드 추가
    df['OK'] = df['OK'].astype(int)
    df['NG'] = df['NG'].astype(int)
    df['Input'] = df['OK'] + df['NG']
    df['양품율'] = round(df['OK'] / df['Input'] * 100, 1)
    return df

# 📊 앱 UI 시작
st.set_page_config(page_title="생산 데이터 확인", layout="wide")
st.title("📊 모델별 생산 데이터 확인 시스템")

# 📥 데이터 로딩
df = load_data()
models = df['Model'].unique()

# 🧭 사이드바 메뉴
selected_model = st.sidebar.selectbox("모델 선택", options=models)
view_total = st.sidebar.button("📋 전체 모델 총합 보기")

# 🖼️ 선택 모델 테이블
if not view_total:
    st.subheader(f"📋 {selected_model} - 라인별 시간대별 데이터")

    model_df = df[df['Model'] == selected_model].copy()
    model_df['양품율'] = model_df['양품율'].apply(lambda x: f"{x}%" if pd.notnull(x) else "")

    st.dataframe(model_df[['Line', 'Time', 'OK', 'NG', 'Input', '양품율']], use_container_width=True)

    # 📈 총합 메트릭
    total_ok = model_df['OK'].sum()
    total_ng = model_df['NG'].sum()
    total_input = total_ok + total_ng
    total_yield = round((total_ok / total_input) * 100, 1) if total_input else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 OK", total_ok)
    col2.metric("총 NG", total_ng)
    col3.metric("총 Input", total_input)
    col4.metric("양품율 (%)", f"{total_yield}%")

# 🧾 전체 모델 총합 보기
if view_total:
    st.subheader("📊 전체 모델 총합 비교")
    summary = []
    for model_name in models:
        temp = df[df['Model'] == model_name]
        ok = temp['OK'].sum()
        ng = temp['NG'].sum()
        input_ = ok + ng
        yield_ = round((ok / input_) * 100, 1) if input_ else 0.0
        summary.append([model_name, ok, ng, input_, f"{yield_}%"])

    result_df = pd.DataFrame(summary, columns=['Model', '총 OK', '총 NG', '총 Input', '양품율 (%)'])
    st.dataframe(result_df, use_container_width=True)
