import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="혈액검사 결과 요약", layout="wide")
st.title("🐾 혈액검사 결과 요약 (개/고양이 전용)")

species = st.selectbox("동물 선택", ["dog", "cat"])

uploaded_file = st.file_uploader("혈액검사 PDF 업로드", type=["pdf"])

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_lab_results(text, ref_ranges):
    results = []
    for test, (low, high) in ref_ranges.items():
        pattern = rf"{test}\s+([0-9]+\.?[0-9]*)"
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1))
            if value < low:
                status = "🔵 낮음"
            elif value > high:
                status = "🔴 높음"
            else:
                status = "🟢 정상"

            results.append({
                "항목": test,
                "결과": value,
                "기준치": f"{low}–{high}",
                "판정": status
            })
    return pd.DataFrame(results)

if uploaded_file:
    raw_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📊 검사 결과")
    df = parse_lab_results(raw_text, REFERENCE_RANGES[species])

    if df.empty:
        st.warning("인식된 검사 항목이 없습니다.")
    else:
        st.dataframe(df, use_container_width=True)

        abnormal = df[df["판정"] != "🟢 정상"]

        st.subheader("📝 보호자용 요약 설명")
        if abnormal.empty:
            st.success("모든 검사 수치가 기준 범위 내에 있습니다.")
        else:
            for _, row in abnormal.iterrows():
                st.write(
                    f"- **{row['항목']}** 수치가 기준치({row['기준치']})보다 "
                    f"{'높게' if '높음' in row['판정'] else '낮게'} 측정되었습니다. "
                    "임상 증상에 따라 추적 검사가 권장될 수 있습니다."
                )

        st.markdown("---")
        st.caption(
            "본 결과서는 보호자 이해를 돕기 위한 참고 자료이며 "
            "최종 판단은 담당 수의사의 임상 소견을 기준으로 합니다."
        )
