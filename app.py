import streamlit as st
import pandas as pd
from datetime import date

# ======================================
# 기본 설정
# ======================================
st.set_page_config(page_title="묘멘트", page_icon="🐱", layout="wide")

# ======================================
# CSS (반드시 맨 위에서 선언)
# ======================================
st.markdown("""
<style>

/* 배경 전체 */
body {
    background-color: #FAF4EF !important;
}

/* 메인 영역 색 */
section.main > div {
    background-color: #FAF4EF !important;
}

/* 텍스트 색 및 폰트 */
h1, h2, h3, h4, h5, h6, label, p, span, div {
    color: #5A4632 !important;
    font-family: "Apple SD Gothic Neo", "Helvetica Neue", sans-serif !important;
}

/* 사이드바 배경 */
[data-testid="stSidebar"] {
    background-color: #F4ECE6 !important;
}

/* 버튼 스타일 */
.stButton>button {
    background-color: #F6D7C3 !important;
    color: #5A4632 !important;
    border-radius: 8px;
    padding: 8px 16px;
    border: 0px;
}
.stButton>button:hover {
    background-color: #F1C7B0 !important;
}

/* 입력 폼 텍스트 색 */
input, textarea, select {
    color: #5A4632 !important;
}

</style>
""", unsafe_allow_html=True)

# ======================================
# 세션 상태
# ======================================
if "records" not in st.session_state:
    st.session_state.records = []

if "food_db" not in st.session_state:
    st.session_state.food_db = {
        "닭가슴살": {"가능": "소량 삶아서 가능", "주의": "양념 금지"},
        "소고기": {"가능": "기름 적은 부위 익혀서 가능", "주의": "양념 금지"},
        "돼지고기": {"가능": "익혀서 소량 가능", "주의": "기름·양념 주의"},
        "연어": {"가능": "익힌 연어만 소량 가능", "주의": "생연어·훈제 금지"},
        "초콜릿": {"가능": "불가", "주의": "테오브로민 독성"},
        "양파": {"가능": "불가", "주의": "적혈구 파괴"},
        "마늘": {"가능": "불가", "주의": "독성 성분"},
        "포도": {"가능": "불가", "주의": "신장 손상"},
    }

# ======================================
# 유틸 함수
# ======================================
def add_record(rec):
    st.session_state.records.append(rec)

def get_records_df():
    if len(st.session_state.records) == 0:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.records)

# ======================================
# 1. 건강 기록
# ======================================
def page_health_log():
    st.title("📒 건강 기록")

    col1, col2 = st.columns(2)

    with col1:
        date_v = st.date_input("기록 날짜", value=date.today())
        meal = st.radio("🍽 식사량", ["거의 안 먹음", "적게", "보통", "많이"], index=2)
        water = st.radio("💧 음수량", ["거의 안 마심", "적게", "보통", "많이"], index=2)
        poop = st.radio("💩 배변", ["정상", "단단함", "설사", "혈변", "안 봄"])

    with col2:
        activity = st.multiselect(
            "🏃 활동/행동",
            ["보통", "잠이 많음", "활동 감소", "활동 증가", "예민함", "숨음", "야옹 증가"],
            default=["보통"],
        )
        symptoms = st.multiselect("⚠️ 이상증세", ["구토", "기침", "호흡 이상", "절뚝거림", "분비물", "가려움", "기타"])

        vomit_color = ""
        vomit_content = ""
        if "구토" in symptoms:
            st.write("### 🤮 구토 상세")
            vomit_color = st.selectbox("색", ["투명", "노란색", "갈색", "붉은색", "기타"])
            vomit_content = st.selectbox("내용물", ["헤어볼", "사료", "거품", "액체", "기타"])

        memo = st.text_area("📝 메모", placeholder="특이사항")

    if st.button("기록 저장"):
        add_record({
            "날짜": date_v,
            "식사": meal,
            "음수": water,
            "배변": poop,
            "행동": ", ".join(activity),
            "증상": ", ".join(symptoms),
            "구토색": vomit_color,
            "구토내용": vomit_content,
            "메모": memo,
        })
        st.success("저장 완료!")

    st.markdown("---")
    st.subheader("📚 최근 기록")
    df = get_records_df()
    if df.empty:
        st.info("기록 없음")
    else:
        st.dataframe(df.tail(10), use_container_width=True)

# ======================================
# 2. AI 진단
# ======================================
def page_ai_diagnosis():
    st.title("📊 AI 진단")
    df = get_records_df()
    if df.empty:
        st.info("건강 기록이 필요합니다.")
        return

    recent = df.tail(7)
    warnings = []
    tips = []

    if (recent["식사"].isin(["거의 안 먹음", "적게"])).sum() >= 2:
        warnings.append("최근 식사량 감소가 반복됩니다.")
    if (recent["음수"].isin(["거의 안 마심", "적게"])).sum() >= 2:
        warnings.append("음수량 부족 경향이 있습니다.")
    if (recent["배변"].isin(["설사", "혈변", "안 봄"])).sum() >= 2:
        warnings.append("배변 이상 기록이 반복됩니다.")
    if recent["행동"].str.contains("활동 감소|숨음", na=False).sum() >= 2:
        warnings.append("무기력/숨음 경향이 있습니다.")
    if recent["증상"].str.contains("구토", na=False).sum() >= 2:
        warnings.append("구토 횟수가 많습니다.")

    if not warnings:
        st.success("최근 기록은 특별한 위험 신호가 없습니다.")
    else:
        st.subheader("⚠️ 주의 필요")
        for w in warnings:
            st.warning(w)

# ======================================
# 3. 집사 가이드
# ======================================
def page_guide():
    st.title("📚 집사 가이드")
    tabs = st.tabs([
        "기본", "약 먹이기", "격리", "목욕",
        "발톱", "노령묘", "중성화 이후", "다이어트", "질병 징후"
    ])

    contents = [
        ["안전한 공간", "밥/물/화장실 위치 고정", "환경 변화 최소화"],
        ["필 포켓", "가루는 극소량", "긍정 경험 연결"],
        ["냄새 교환", "격리 시작", "짧은 만남"],
        ["전용 샴푸", "짧게", "완전 건조"],
        ["한 발가락씩", "혈관 피하기", "터치 적응"],
        ["관절/신장 문제", "점프 줄이기", "정기검진"],
        ["넥카라", "상처 관찰", "식사 조절"],
        ["저칼로리 사료", "나눠주기", "급감량 금지"],
        ["방광염", "장 문제", "구강 문제", "호흡기"],
    ]

    for idx, tab in enumerate(tabs):
        with tab:
            for txt in contents[idx]:
                st.write("- " + txt)

# ======================================
# 4. 응급상황 AI
# ======================================
def page_ai_emergency():
    st.title("🚨 응급상황 AI")

    mode = st.selectbox("상황 선택", ["선택", "건강 응급", "심폐소생술", "재난", "실종"])

    if mode == "건강 응급":
        st.write("- 구토: 사료/물 잠시 치우기")
        st.write("- 설사: 지사제 X")
        st.write("- 호흡곤란: 즉시 병원")

    elif mode == "심폐소생술":
        st.write("- 의식 확인 → 호흡 확인 → 압박")

    elif mode == "재난":
        st.write("- 이동장 준비")
        st.write("- 창가에서 멀리")

    elif mode == "실종":
        st.write("- 조용히 50m 탐색")
        st.write("- 냄새 있는 물건 두기")

# ======================================
# 5. 음식 사전
# ======================================
def page_food_dict():
    st.title("🍙 음식 사전")

    db = st.session_state.food_db
    name = st.text_input("음식 검색")
    if st.button("검색"):
        name = name.strip()
        if name in db:
            info = db[name]
            if info["가능"] == "불가":
                st.error(f"❌ {name} : 절대 금지")
            else:
                st.success(f"⭕ {name} : {info['가능']}")
            st.write("주의:", info["주의"])
        else:
            st.warning("정보 없음")

    with st.expander("전체 목록"):
        st.dataframe(pd.DataFrame([
            {"음식": k, "가능": v["가능"], "주의": v["주의"]} for k, v in db.items()
        ]))

# ======================================
# 6. 마켓
# ======================================
def page_market():
    st.title("🛍️ 마켓 추천")

    df = get_records_df()
    if df.empty:
        st.info("건강 기록이 필요합니다.")
        return

    last = df.iloc[-1]

    if last["배변"] in ["설사", "혈변"]:
        st.write("- 장 건강용 사료 추천")
    elif last["음수"] in ["거의 안 마심", "적게"]:
        st.write("- 습식/수분 보충")
    elif last["식사"] in ["거의 안 먹음", "적게"]:
        st.write("- 향 강한 습식 추천")
    else:
        st.write("- 일반 균형형 사료 추천")

# ======================================
# 라우팅
# ======================================
menu = st.sidebar.radio(
    "메뉴",
    ["홈", "건강 기록", "AI 진단", "집사 가이드", "응급상황 AI", "음식 사전", "마켓"]
)

if menu == "홈":
    st.title("🐱 묘멘트")

    # 로컬 배너 이미지 사용
    try:
        st.image("banner.png")   # 프로젝트 폴더에 banner.png 넣어두기
    except:
        st.write("홈 이미지 준비 중... (banner.png 파일 없음)")

elif menu == "건강 기록":
    page_health_log()
elif menu == "AI 진단":
    page_ai_diagnosis()
elif menu == "집사 가이드":
    page_guide()
elif menu == "응급상황 AI":
    page_ai_emergency()
elif menu == "음식 사전":
    page_food_dict()
elif menu == "마켓":
    page_market()
