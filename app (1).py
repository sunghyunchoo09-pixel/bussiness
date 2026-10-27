import streamlit as st
import pandas as pd
from data import FIELDS, ALL_SKILLS
from logic import validate, recommend

st.set_page_config(page_title="온라인 사업 추천", page_icon="💼")
st.title("💼 온라인 사업 추천 & 시작 가이드")
st.write("분야와 내 상황을 입력하면 어울리는 온라인 사업과 시작 방법을 알려줘요.")

# ---------- 입력 ----------
field = st.selectbox("관심 분야", ["전체"] + FIELDS)
col1, col2 = st.columns(2)
with col1:
    budget = st.number_input("창업 예산 (만원)", min_value=0, value=30, step=5)
with col2:
    hours = st.number_input("주당 투자 가능 시간", min_value=0, value=10, step=1)

level = st.slider("내 경험 수준 (1=완전 초보 ~ 5=전문가)", 1, 5, 2)
skills = st.multiselect("내가 가진 강점/기술 (선택)", ALL_SKILLS)

# ---------- 추천 ----------
if st.button("추천 받기", type="primary"):
    try:
        error = validate(budget, hours)
        if error:
            st.warning(error)
        else:
            results, notice = recommend(field, budget, hours, level, skills)
            if not results:
                st.warning(notice)
            else:
                st.success(f"조건에 맞는 사업 {len(results)}개 중 상위 3개를 추천해요.")
                report = []

                for rank, r in enumerate(results[:3], 1):
                    b = r["biz"]
                    st.subheader(f"{rank}위. {b['name']}  ({r['score']}점)")
                    st.progress(r["score"] / 100)
                    st.write(b["desc"])
                    for reason in r["reasons"]:
                        st.write("• " + reason)

                    with st.expander("🚀 시작 방법 보기"):
                        for i, step in enumerate(b["steps"], 1):
                            st.write(f"{i}. {step}")
                        st.warning("⚠️ " + b["caution"])

                    report.append(f"[{rank}위] {b['name']} ({r['score']}점)\n" + "\n".join(
                        f"  {i}. {s}" for i, s in enumerate(b["steps"], 1)))

                # 전체 점수 비교 차트
                st.subheader("전체 후보 점수 비교")
                df = pd.DataFrame({
                    "사업": [r["biz"]["name"] for r in results],
                    "점수": [r["score"] for r in results],
                }).set_index("사업")
                st.bar_chart(df)

                st.download_button(
                    "추천 결과 다운로드 (.txt)",
                    "\n\n".join(report).encode("utf-8"),
                    "recommend.txt",
                )
                st.caption("※ 비용·시간은 일반적인 대략값이에요. 실제 창업 전 최신 법규와 시장 상황을 꼭 확인하세요.")
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했어요: {e}")
