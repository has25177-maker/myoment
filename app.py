import streamlit as st
import math

st.set_page_config(page_title="묘멘트", page_icon="🐱", layout="wide")

# -------------------------------
# 상태값 초기화
# -------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# -------------------------------
# CSS
# -------------------------------
st.markdown("""
<style>

body {
    background-color: #f8f1e8;
}

/* 중앙 버튼 */
.center-btn {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background-color: #ffe5d6;
    border: 4px solid #d69c7b;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 75px;
    margin: auto;
    cursor: pointer;
}

/* 메뉴 컨테이너 */
.menu-container {
    width: 600px;
    height: 500px;
    margin: auto;
    position: relative;
}

/* 원형 메뉴 버튼 */
.menu-item {
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
}

/* 투명 클릭 버튼 (클릭 처리용) */
.transparent-btn {
    position: absolute;
    width: 110px;
    height: 110px;
    background: rgba(0,0,0,0);
    border-radius: 50%;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------
# 페이지 이동 함수
# -------------------------------
def go(page_name):
    st.session_state.page = page_name


# -------------------------------
# 홈 화면
# -------------------------------
def page_home():
    st.markdown("<h1 style='text-align:center; color:#8a5a3c;'>🐾 묘멘트</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")

    # 중앙 고양이 버튼 (Streamlit 버튼)
    if st.button("🐱", key="center_btn",
                 help="메뉴 열기/닫기",
                 use_container_width=False):
        st.session_state.menu_open = not st.session_state.menu_open

    # CSS 중앙 버튼 스타일 적용
    st.markdown("""
        <script>
            var btn = window.parent.document.querySelectorAll('button[kind="secondary"]')[0];
            if(btn){
                btn.className = "center-btn";
            }
        </script>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # 메뉴 컨테이너
    st.markdown('<div class="menu-container">', unsafe_allow_html=True)

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
            x = radius * math.cos(angle) + 250
            y = radius * math.sin(angle) + 250

            # 아이콘 표시
            st.markdown(
                f"""
                <div class="menu-item" style="left:{x}px; top:{y}px;">
                    {icon}
                </div>
                """,
                unsafe_allow_html=True
            )

            # 클릭 버튼
            btn_key = f"{name}_btn"
            clicked = st.button("", key=btn_key)
            st.markdown(
                f"""
                <script>
                    var el = window.parent.document.querySelector('button[key="{btn_key}"]');
                    if(el) {{
                        el.className = "transparent-btn";
                        el.style.left = "{x}px";
                        el.style.top = "{y}px";
                        el.style.position = "absolute";
                        el.style.transform = "translate(0, -110px)";
                    }}
                </script>
                """,
                unsafe_allow_html=True
            )

            if clicked:
                go(name)

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------
# 기능 페이지들
# -------------------------------
def page_health():
    st.title("📒 건강 기록")
    st.write("식사량 · 음수량 · 배변 · 행동 · 이상증세 · 특이사항 기록")

def page_ai():
    st.title("📊 AI 분석")
    st.write("기록 기반 고양이 변화 감지 기능")

def page_emergency():
    st.title("🚑 AI 응급처치")
    st.write("증상 입력 → 응급 조치 + 병원 안내")

def page_guide():
    st.title("📚 집사 가이드")
    st.write("약 먹이기, 모래 관리, 대표 질병 등")

def page_food():
    st.title("🍙 음식 사전")
    st.write("사람 음식 검색 → 고양이 취식 여부 안내")

def page_market():
    st.title("🛍️ 마켓")
    st.write("AI 맞춤 사료·간식 추천")


# -------------------------------
# 라우팅
# -------------------------------
page = st.session_state.page

if page == "home":
    page_home()
elif page == "건강 기록":
    page_health()
elif page == "AI 분석":
    page_ai()
elif page == "AI 응급":
    page_emergency()
elif page == "집사 가이드":
    page_guide()
elif page == "음식 사전":
    page_food()
elif page == "마켓":
    page_market()
