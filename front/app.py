import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("画像文書解析AI")

uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="アップロードされた画像", use_column_width=True)

    if st.button("解析実行"):
        with st.spinner("AIが解析中..."):
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post("http://localhost:8000/analyze-image", files=files)

            if response.status_code == 200:
                result = response.json()
                st.success("解析結果:")
                st.write(result["content"])
            else:
                st.error(f"解析失敗: {response.status_code}")
