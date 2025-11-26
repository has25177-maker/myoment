import streamlit as st
import math
import pandas as pd

# -------------------------------------------------
# 🔧 글로벌 설정
# -------------------------------------------------
st.set_page_config(page_title="묘멘트", page_icon="🐱", layout="wide")

# 페이지 상태값 초기화
if "page" not in st.session_state:
    st.session_state.page = "home"

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False


# -------------------------------------------------
# 🎨 전체 UI 공통 스타일
# -------------------------------------------------
GLOBAL_CSS = """
<style>
body {
    background-color: #f8f1e8;
    font-family: "Apple SD Gothic Neo", "Helvetica", sans-serif;
}

/* 중앙 고양이 버튼 */
.center-cat {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background-color: #ffe5d6;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 75px;
    border: 4px solid #d69c7b;
    cursor: pointer;
    margin: auto;
}

/* 원형 메뉴 버튼 */
.menu-btn {
    position: absolute;
    width: 110px;
    height: 110px;
    border-radius: 50%;
    background-color: #ffffff;
    border: 3px solid #d69c7b;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 45px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    cursor: pointer;
}

/* 제목 스타일 */
h1 {
    color: #8a5a3c;
    font-weight: 800;
}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# -------------------------------------------------
# 📌 페이지 이동 함수
# -------------------------------------------------
def go(page_name):
    st.session_state.page = page_name


# -------------------------------------------------
# 🏠 홈 화면
# -------------------------------------------------
def page_home():
    st.write("")
    st.write("")
    st.markdown("<h1 style='text-align:center;'>🐾 묘멘트</h1>", unsafe_allow_html=True)

    # 중앙 컨테이너
    st.markdown("<div style='height:400px; position:relative;'>", unsafe_allow_html=True)

    # 중앙 고양이 버튼
    st.markdown(
        f"""
        <div class="center-cat" onclick="window.location.href='/?menu=toggle'">
            🐱
        </div>
        """,
        unsafe_allow_html=True
    )

    # 메뉴 상태 토글
    query = st.query_params.get("menu", None)
    if query == "toggle":
        st.session_state.menu_open = not st.session_state.menu_open

    # 메뉴 버튼 원형 배치
    if st.session_state.menu_open:
        items = [
            ("📒", "건강 기록"),
            ("📊", "AI 분석"),
            ("🚑", "AI 응급"),
            ("📚", "집사 가이드"),
            ("🍙", "음식 사전"),
            ("🛍️", "마켓")
        ]

        radius = 220
        angle_step = 360 / len(items)

        for i, (icon, name) in enumerate(items):
            angle = math.radians(i * angle_step - 90)
            x = radius * math.cos(angle) + 300
            y = radius * math.sin(angle) + 300

            st.markdown(
                f"""
                <div class="menu-btn"
                     style="left:{x}px; top:{y}px;"
                     onclick="window.location.href='/?page={name}'">
                     {icon}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)



# -------------------------------------------------
# 📒 건강 기록 페이지
# -------------------------------------------------
def page_health():
    st.title("📒 건강 기록")

    st.write("고양이의 일상 기록을 간편하게 버튼으로 입력하세요.")

    meal = st.slider("🍽️ 식사량 (%)", 0, 100, 50)
    water = st.slider("💧 음수량 (ml)", 0, 500, 120)
    poop = st.selectbox("💩 배변 상태", ["정상", "단단함", "무름", "혈변", "설사"])
    behavior = st.selectbox("🏃 행동 변화", ["정상", "활동 감소", "과다 활동", "구토", "숨기", "식욕 저하"])
    memo = st.text_input("📝 특이사항 메모")

    if st.button("기록 저장"):
        st.success("기록이 저장되었습니다.")


# -------------------------------------------------
# 📊 AI 분석 페이지
# -------------------------------------------------
def page_ai():
    st.title("📊 AI 분석")

    st.write("기록 데이터를 기반으로 고양이의 미묘한 변화를 감지합니다.")

    st.info("🔔 현재 AI 분석 기능은 데모 버전입니다.\n변화 추정: 식사량 감소 가능성 12% 감지.")


# -------------------------------------------------
# 🚑 AI 응급처치 페이지
# -------------------------------------------------
def page_emergency():
    st.title("🚑 AI 응급처치")

    symptom = st.text_input("증상을 입력하세요 (예: 구토, 설사, 무기력 등)")
    if st.button("AI 분석하기"):
        st.warning("🩺 '구토' 관련 응급처치 안내 표시")
        st.info("📍 근처 동물병원: 1. 해피동물병원 (1.2km)")


# -------------------------------------------------
# 📚 집사 가이드
# -------------------------------------------------
def page_guide():
    st.title("📚 집사 가이드")

    st.subheader("응급처치, 약 먹이기, 모래 관리, 사료 선택, 목욕, 질병 증상 등")
    st.write("고양이 집사에게 필요한 기본 지식을 모아둔 백과사전.")


# -------------------------------------------------
# 🍙 음식 사전
# -------------------------------------------------
def page_food():
    st.title("🍙 음식 사전")

    food = st.text_input("검색할 음식 이름을 입력하세요")
    if st.button("검색"):
        st.error(f"‘{food}’ 은(는) 고양이에게 위험할 수 있습니다.")


# -------------------------------------------------
# 🛍️ 마켓
# -------------------------------------------------
def page_market():
    st.title("🛍️ 묘멘트 마켓")

    st.write("AI 분석을 바탕으로 맞춤 사료·간식을 추천합니다.")
    st.success("✨ 추천: 최적화된 저지방 사료 / 민감성 간식")


# -------------------------------------------------
# 🔀 페이지 라우팅
# -------------------------------------------------
route = st.query_params.get("page", "home")

if route == "home":
    page_home()
elif route == "건강 기록":
    go("건강 기록")
    page_health()
elif route == "AI 분석":
    page_ai()
elif route == "AI 응급":
    page_emergency()
elif route == "집사 가이드":
    page_guide()
elif route == "음식 사전":
    page_food()
elif route == "마켓":
    page_market()
