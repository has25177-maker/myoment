import streamlit as st

st.set_page_config(page_title="묘멘트", page_icon="🐱", layout="centered")

# -------------------------
# 상태 초기화
# -------------------------
if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

# -------------------------
# CSS (이모지 버튼 원형 배치)
# -------------------------
MENU_CSS = """
<style>
/* 전체 감성 */
body {
    font-family: "Helvetica", "Apple SD Gothic Neo", sans-serif;
}

/* 중앙 고양이 버튼 */
.center-btn {
    width: 110px;
    height: 110px;
    background-color: #ffe9ec;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 60px;
    border: 3px solid #ffced5;
    cursor: pointer;
    margin: 0 auto;
    transition: 0.3s;
}
.center-btn:hover {
    background-color: #ffd4da;
}

/* 원형 메뉴 공통 스타일 */
.menu-btn {
    width: 80px;
    height: 80px;
    background-color: white;
    border-radius: 50%;
    border: 2px solid #ffcbd3;
    position: absolute;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 35px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    transition: 0.3s;
}
.menu-btn:hover {
    transform: scale(1.1);
}

/* 6개 원형 메뉴 버튼 좌표 */
.btn1 { transform: translate(-140px, -140px); }
.btn2 { transform: translate(0px, -190px); }
.btn3 { transform: translate(140px, -140px); }
.btn4 { transform: translate(140px, 40px); }
.btn5 { transform: translate(0px, 120px); }
.btn6 { transform: translate(-140px, 40px); }

/* 버튼 감싸는 컨테이너 */
.menu-container {
    position: relative;
    height: 350px;
}
</style>
"""
st.markdown(MENU_CSS, unsafe_allow_html=True)

# -------------------------
# 페이지 라우팅
# -------------------------
def set_page(page):
    st.session_state.page = page

if "page" not in st.session_state:
    st.session_state.page = "홈"

# -------------------------
# 🐾 홈 화면
# -------------------------
def page_home():
    st.title("🐾 묘멘트")
    st.write("반려묘 건강 순간을 기록하고 감지하는 케어 플랫폼")

    st.write("")
    st.write("")
    st.write("### 메인 메뉴")

    # 중앙 버튼 클릭 → 상태 토글
    if st.session_state.menu_open:
        if st.button("🐱", key="center", help="메뉴 닫기", 
                     use_container_width=False, type="primary"):
            st.session_state.menu_open = False
    else:
        if st.button("🐱", key="center2", help="메뉴 열기",
                     use_container_width=False, type="primary"):
            st.session_state.menu_open = True

    # 중앙 버튼 HTML로 재정의(이쁘게)
    st.markdown(
        """
        <div style="text-align:center;">
            <div class="center-btn" onclick="document.getElementById('click-center').click()">🐱</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.button("", key="click-center", on_click=lambda: toggle_menu(), disabled=True)

    # 메뉴 펼쳐졌을 때: 6개의 원형 버튼 생성
    if st.session_state.menu_open:
        st.markdown('<div class="menu-container">', unsafe_allow_html=True)

        # 버튼 1 ~ 6
        st.markdown(
            '<div class="menu-btn btn1" onclick="document.getElementById(\'btn1\').click()">📝</div>',
            unsafe_allow_html=True)
        st.button("", key="btn1", on_click=lambda: set_page("기록하기"), disabled=True)

        st.markdown(
            '<div class="menu-btn btn2" onclick="document.getElementById(\'btn2\').click()">📊</div>',
            unsafe_allow_html=True)
        st.button("", key="btn2", on_click=lambda: set_page("AI 분석"), disabled=True)

        st.markdown(
            '<div class="menu-btn btn3" onclick="document.getElementById(\'btn3\').click()">🚑</div>',
            unsafe_allow_html=True)
        st.button("", key="btn3", on_click=lambda: set_page("응급 가이드"), disabled=True)

        st.markdown(
            '<div class="menu-btn btn4" onclick="document.getElementById(\'btn4\').click()">📚</div>',
            unsafe_allow_html=True)
        st.button("", key="btn4", on_click=lambda: set_page("집사 가이드"), disabled=True)

        st.markdown(
            '<div class="menu-btn btn5" onclick="document.getElementById(\'btn5\').click()">🍽️</div>',
            unsafe_allow_html=True)
        st.button("", key="btn5", on_click=lambda: set_page("음식 사전"), disabled=True)

        st.markdown(
            '<div class="menu-btn btn6" onclick="document.getElementById(\'btn6\').click()">🛒</div>',
            unsafe_allow_html=True)
        st.button("", key="btn6", on_click=lambda: set_page("마켓"), disabled=True)

        st.markdown('</div>', unsafe_allow_html=True)

# 메뉴 토글용 함수
def toggle_menu():
    st.session_state.menu_open = not st.session_state.menu_open

# -------------------------
# 다른 빈 페이지(후에 채워넣기)
# -------------------------
def temp_page(name):
    st.title(name)
    st.write("이 화면은 아직 개발 전이에요. 기능 합칠 때 완성됩니다.")

# -------------------------
# 라우팅 실행
# -------------------------
if st.session_state.page == "홈":
    page_home()
elif st.session_state.page == "기록하기":
    temp_page("기록하기")
elif st.session_state.page == "AI 분석":
    temp_page("AI 분석")
elif st.session_state.page == "응급 가이드":
    temp_page("응급 가이드")
elif st.session_state.page == "집사 가이드":
    temp_page("집사 가이드")
elif st.session_state.page == "음식 사전":
    temp_page("음식 사전")
elif st.session_state.page == "마켓":
    temp_page("마켓")
