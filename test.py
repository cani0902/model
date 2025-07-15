import streamlit as st
import pandas as pd


# 📌 데이터 로딩 함수
@st.cache_data
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ0rXK4SMIQZS0_U2uVXMw8qJ6BThe1wB-lapp0XOE5NV2HNf29js3_WCq4tzE42EEi8odSGkQM_Cuv/pub?output=csv"
    df = pd.read_csv(sheet_url)
    df['Input'] = df['OK'] + df['NG']
    df['양품율'] = round(df['OK'] / df['Input'] * 100, 1)
    return df


# 📊 페이지 설정
st.set_page_config(page_title="생산 데이터 확인", layout="wide")
st.title("📊 모델별 생산 데이터 확인 시스템")

# 📄 데이터 불러오기
df = load_data()
models = df['Model'].unique()

# 📌 사이드바 구성
st.sidebar.title("📌 옵션 선택")
selected_model = st.sidebar.selectbox("모델 선택", options=models)
show_total = st.sidebar.button("📊 전체 모델 총합 보기")

# ✅ 전체 모델 총합 보기
if show_total:
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

# ✅ 선택한 모델 보기
else:
    model_df = df[df['Model'] == selected_model]

    # 양품율에 % 기호 붙이기
    model_df_display = model_df.copy()
    model_df_display['양품율'] = model_df_display['양품율'].apply(lambda x: f"{x}%" if pd.notnull(x) else "")

    st.subheader(f"📋 {selected_model} - 라인별 시간대별 데이터")
    st.dataframe(model_df_display[['Line', 'Time', 'OK', 'NG', 'Input', '양품율']], use_container_width=True)

    st.subheader(f"📈 {selected_model} 총합")
    total_ok = model_df['OK'].sum()
    total_ng = model_df['NG'].sum()
    total_input = total_ok + total_ng
    total_yield = round((total_ok / total_input) * 100, 1) if total_input else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 OK", total_ok)
    col2.metric("총 NG", total_ng)
    col3.metric("총 Input", total_input)
    col4.metric("양품율 (%)", f"{total_yield}%")

