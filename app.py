import streamlit as st
import pandas as pd
from datetime import date
import base64

# ======================================
# 기본 설정
# ======================================
st.set_page_config(page_title="묘멘트", page_icon="🐱", layout="wide")

# ======================================
# 폰트 파일(base64) 로딩 (ChosunSg.TTF)
# ======================================
font_css = ""
try:
    with open("ChosunSg.TTF", "rb") as f:
        font_bytes = f.read()
    font_b64 = base64.b64encode(font_bytes).decode()
    font_css = f"""
    @font-face {{
        font-family: 'ChosunSg';
        src: url(data:font/ttf;base64,{font_b64}) format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    html, body, [class*="css"] {{
        font-family: 'ChosunSg', sans-serif !important;
    }}
    """
except Exception:
    # 폰트 파일 못 찾으면 기본 폰트 사용
    font_css = """
    html, body, [class*="css"] {
        font-family: sans-serif;
    }
    """

# ======================================
# 전역 스타일 (배경 + 버튼 + 입력창 + 라디오 색 등)
# ======================================
GLOBAL_STYLE = f"""
<style>
{font_css}

/* 전체 배경색 */
body, .main, [data-testid="stAppViewContainer"], 
[data-testid="stAppViewContainer"] > .main, 
.block-container {{
    background-color: #FEF7EB !important;
}}

/* 사이드바 배경색 */
[data-testid="stSidebar"] {{
    background-color: #F3E8DD !important;
}}

/* 제목 색 */
h1, h2, h3, h4, h5 {{
    color: #4A332D !important;
}}

/* 일반 텍스트 색 */
p, li, span, label {{
    color: #4A332D !important;
}}

/* 버튼 스타일 */
.stButton > button {{
    background-color: #E6B59D !important;
    color: #4A332D !important;
    border-radius: 10px;
    border: none;
    padding: 0.5rem 1.2rem;
    font-size: 1rem;
}}
.stButton > button:hover {{
    background-color: #D8C4B6 !important;
    color: #3A2920 !important;
}}

/* 입력창, 셀렉트박스 배경 */
input, textarea {{
    background-color: #FEF7EB !important;
    color: #4A332D !important;
    border-radius: 8px !important;
}}
div[data-baseweb="select"] > div {{
    background-color: #FEF7EB !important;
    border-radius: 8px !important;
}}

/* 라디오/체크박스 선택 색 (accent-color) */
input[type="radio"], input[type="checkbox"] {{
    accent-color: #E6B59D !important;
}}

/* 데이터프레임 카드 둥글게 (버전마다 클래스가 달라서 넓게 지정) */
[data-testid="stDataFrame"] {{
    border-radius: 10px !important;
}}

/* 사이드바 라디오 라벨 여백 */
section[data-testid="stSidebar"] label {{
    font-size: 0.95rem;
}}

/* 스크롤 막대도 살짝 톤 맞추기 (지원 브라우저에서만) */
::-webkit-scrollbar-thumb {{
    background-color: #E6B59D !important;
    border-radius: 10px;
}}
</style>
"""

st.markdown(GLOBAL_STYLE, unsafe_allow_html=True)

# ======================================
# 세션 상태 초기화
# ======================================
if "records" not in st.session_state:
    st.session_state.records = []

if "food_db" not in st.session_state:
    st.session_state.food_db = {
        "닭가슴살": {"가능": "소량 삶아서 가능", "주의": "양념·소금 없이 주세요."},
        "소고기": {"가능": "기름 적은 부위를 잘 익혀 소량 가능", "주의": "양념, 기름 많은 부위는 피하기."},
        "돼지고기": {"가능": "충분히 익힌 살코기만 소량 가능", "주의": "지방·양념이 많은 부위는 소화 부담."},
        "연어": {"가능": "익힌 연어만 간식 수준으로 가능", "주의": "생연어·훈제·양념 연어는 금지."},
        "사과": {"가능": "씨와 심을 제거한 과육만 소량 가능", "주의": "씨·심에는 독성 성분이 있어 제거 필수."},
        "수박": {"가능": "씨와 껍질을 제거한 과육만 소량 가능", "주의": "과당 때문에 너무 자주·많이 주지 않기."},
        "고구마": {"가능": "잘 익힌 고구마를 소량 간식으로 가능", "주의": "당분이 많아 비만·당뇨 시 주의."},
        "브로콜리": {"가능": "삶아서 소량 가능", "주의": "날로 많이 먹이면 가스 유발 가능성."},
        "우유": {"가능": "고양이 전용 락토프리 우유만 소량 가능", "주의": "일반 우유는 설사 유발 가능성이 큼."},
        "요거트": {"가능": "무가당 플레인만 아주 소량 가능", "주의": "설탕·향료·자일리톨 포함 제품은 금지."},
        "초콜릿": {"가능": "불가", "주의": "카카오 성분(테오브로민) 독성. 소량도 위험."},
        "양파": {"가능": "불가", "주의": "적혈구 파괴 → 빈혈 유발. 어떤 형태도 금지."},
        "마늘": {"가능": "불가", "주의": "양파와 비슷한 독성. 아주 소량도 금지."},
        "포도": {"가능": "불가", "주의": "원인 불명 신장 손상 가능성. 완전 금지."},
        "건포도": {"가능": "불가", "주의": "포도와 동일하게 신장 손상 위험."},
        "커피": {"가능": "불가", "주의": "카페인 독성. 사람 기준 소량도 고양이에겐 위험."},
        "알코올": {"가능": "불가", "주의": "작은 양도 위험. 절대 금지."},
    }


# 공통 유틸
def add_record(rec: dict):
    st.session_state.records.append(rec)


def get_records_df():
    if not st.session_state.records:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.records)


# ======================================
# 1. 건강 기록
# ======================================
def page_health_log():
    st.title("📁 건강 기록")

    col1, col2 = st.columns(2)

    with col1:
        rec_date = st.date_input("기록 날짜", value=date.today())

        meal = st.radio(
            "🍽 식사량",
            ["거의 안 먹음", "적게", "보통", "많이"],
            index=2,
        )

        water = st.radio(
            "💧 음수량",
            ["거의 안 마심", "적게", "보통", "많이"],
            index=2,
        )

        poop = st.radio(
            "💩 배변 상태",
            ["정상", "단단함", "설사", "혈변", "안 봄"],
            index=0,
        )

    with col2:
        activity = st.multiselect(
            "🏃 활동 및 행동",
            [
                "보통",
                "잠이 많아짐",
                "활동 감소",
                "활동 증가",
                "예민/공격적",
                "숨는 시간이 늘어남",
                "야옹거림 증가",
            ],
            default=["보통"],
        )

        symptoms = st.multiselect(
            "⚠️ 이상증세",
            [
                "구토",
                "기침",
                "호흡 이상",
                "절뚝거림",
                "눈/코 분비물",
                "가려움/과도 그루밍",
                "기타",
            ],
        )

        vomit_color = ""
        vomit_type = ""
        if "구토" in symptoms:
            st.markdown("#### 🤮 구토 상세 기록")
            vomit_color = st.selectbox(
                "구토 색",
                ["선택 안 함", "투명/거품", "노란색(담즙)", "갈색/사료", "붉은색/분홍색", "기타"],
            )
            vomit_type = st.selectbox(
                "구토 내용물",
                ["선택 안 함", "헤어볼", "사료 조각", "거품/액체", "이물 가능성", "기타"],
            )

        memo = st.text_area("📝 특이사항 메모", placeholder="환경 변화, 간식, 약 복용 등")

    if st.button("기록 저장"):
        rec = {
            "날짜": rec_date,
            "식사량": meal,
            "음수량": water,
            "배변": poop,
            "행동": ", ".join(activity) if activity else "",
            "이상증세": ", ".join(symptoms) if symptoms else "",
            "구토 색": vomit_color,
            "구토 내용": vomit_type,
            "메모": memo,
        }
        add_record(rec)
        st.success("기록이 저장되었습니다.")

    st.markdown("---")
    st.subheader("📚 최근 기록")

    df = get_records_df()
    if df.empty:
        st.info("아직 기록이 없습니다.")
    else:
        st.dataframe(df.tail(10), use_container_width=True)


# ======================================
# 2. AI 진단
# ======================================
def page_ai_diagnosis():
    st.title("📊 AI 진단")

    df = get_records_df()
    if df.empty:
        st.info("먼저 ‘건강 기록’에 최소 1개 이상의 기록을 남겨 주세요.")
        return

    recent = df.tail(7)
    warnings = []
    tips = []

    # 식사량
    low_meal = recent["식사량"].isin(["거의 안 먹음", "적게"]).sum()
    if low_meal >= 2:
        warnings.append("최근 며칠 간 식사량이 줄어든 날이 여러 번 있습니다.")
        tips.append("식욕 저하는 다양한 질환의 초기가 될 수 있으니 24시간 이상 지속 시 병원 상담을 권장합니다.")

    # 음수량
    low_water = recent["음수량"].isin(["거의 안 마심", "적게"]).sum()
    if low_water >= 2:
        warnings.append("물 섭취가 부족한 날이 반복되고 있습니다.")
        tips.append("요로·신장 문제 예방을 위해 물그릇/정수기 점검과 습식 사료 활용을 고려해 보세요.")

    # 배변
    bad_poop = recent["배변"].isin(["설사", "혈변", "안 봄"]).sum()
    if bad_poop >= 2:
        warnings.append("배변 상태 이상(설사/혈변/배변 없음)이 여러 번 기록되었습니다.")
        tips.append("3일 이상 지속되면 변 상태 사진과 함께 병원 진료를 받는 것이 안전합니다.")

    # 행동
    if "행동" in recent.columns:
        low_act = recent["행동"].str.contains("활동 감소|잠이 많아짐|숨는 시간이 늘어남", na=False).sum()
        if low_act >= 2:
            warnings.append("무기력하거나 숨어 지내는 패턴이 반복되고 있습니다.")
            tips.append("활동 감소 + 식욕 저하가 함께 보이면 더 주의가 필요합니다.")

    # 구토
    if "이상증세" in recent.columns:
        vomit_days = recent["이상증세"].str.contains("구토", na=False).sum()
        if vomit_days >= 2:
            warnings.append("일주일 안에 ‘구토’가 여러 번 기록되었습니다.")
            tips.append("헤어볼, 사료, 장 문제 등 원인이 다양하니 토한 내용물과 횟수를 기록해 두면 도움이 됩니다.")

    if "구토 색" in recent.columns:
        blood_like = recent["구토 색"].str.contains("붉은색|분홍", na=False).sum()
        if blood_like >= 1:
            warnings.append("붉은색·분홍색 구토가 기록되었습니다. 혈성 구토 가능성이 있어 즉시 병원 진료가 필요할 수 있습니다.")

    if not warnings:
        st.success("최근 기록에서 뚜렷한 위험 신호는 크게 보이지 않습니다.")
        st.write("그래도 작은 변화가 쌓여 이상으로 이어질 수 있으니 꾸준히 기록해 주세요.")
    else:
        st.subheader("⚠️ 주의가 필요한 변화")
        for w in warnings:
            st.warning("- " + w)

    if tips:
        st.subheader("💡 참고하면 좋은 팁")
        for t in tips:
            st.write("- " + t)

    with st.expander("최근 7개 기록 보기"):
        st.dataframe(recent, use_container_width=True)


# ======================================
# 3. 집사 가이드
# ======================================
def page_guide():
    st.title("📚 집사 가이드")

    tabs = st.tabs(
        [
            "초보 집사 기본 가이드",
            "약 먹이기",
            "격리·적응",
            "목욕",
            "발톱 관리",
            "노령묘 관리",
            "중성화 이후",
            "다이어트/체중 관리",
            "대표 질병 징후",
        ]
    )

    with tabs[0]:
        st.write("- 숨을 수 있는 안전한 공간을 먼저 마련해 주세요.")
        st.write("- 밥·물·화장실 위치를 자주 바꾸지 않는 것이 좋습니다.")
        st.write("- 화장실과 밥그릇은 서로 너무 가깝지 않게 배치해 주세요.")
        st.write("- 갑작스러운 소음·손님 방문·이사 등은 큰 스트레스를 줄 수 있습니다.")

    with tabs[1]:
        st.subheader("💊 약 먹이기")
        st.write("- 가능하면 약 먹이기 보조 간식(필 포켓 등)을 활용해 주세요.")
        st.write("- 알약은 혀 뒤쪽에 두고 입을 닫은 뒤 목을 살짝 쓰다듬으며 삼키는지 확인합니다.")
        st.write("- 가루약은 좋아하는 습식에 아주 소량 섞어 반응을 보며 양을 조절합니다.")

    with tabs[2]:
        st.subheader("🚪 격리·적응")
        st.write("- 새 고양이를 들일 때는 최소 며칠간 방을 나누어 냄새와 소리에 먼저 적응시킵니다.")
        st.write("- 문틈으로 냄새만 공유하고, 짧은 시간씩 대면을 시도하며 점차 늘려갑니다.")

    with tabs[3]:
        st.subheader("🛁 목욕")
        st.write("- 필요할 때만 짧게 하고, 미끄럽지 않은 환경에서 진행해 주세요.")
        st.write("- 고양이 전용 샴푸를 사용하고, 충분히 말리지 않으면 감기·피부 문제가 생길 수 있습니다.")

    with tabs[4]:
        st.subheader("💅 발톱 관리")
        st.write("- 처음에는 한두 발가락만, 간식과 함께 짧게 연습해 보세요.")
        st.write("- 분홍색 혈관 부분을 피해서 끝의 뾰족한 부분만 조금씩 자르는 것이 안전합니다.")

    with tabs[5]:
        st.subheader("🐾 노령묘 관리")
        st.write("- 먹는 양·배변·점프 능력·활동량 등의 작은 변화를 자주 확인해 주세요.")
        st.write("- 관절·신장·갑상선 질환이 늘어나는 시기라 정기 검진이 중요합니다.")

    with tabs[6]:
        st.subheader("✂️ 중성화 수술 이후")
        st.write("- 수술 부위를 핥지 못하도록 넥카라를 착용합니다.")
        st.write("- 상처 부위가 붉게 붓거나 분비물이 보이면 바로 병원에 문의하세요.")
        st.write("- 중성화 이후에는 대사량이 줄어 살이 찌기 쉬우므로 사료 양을 조절해 주세요.")

    with tabs[7]:
        st.subheader("⚖️ 다이어트 / 체중 관리")
        st.write("- 무작정 양을 줄이기보다는 저칼로리·다이어트용 사료로 천천히 전환하는 것이 좋습니다.")
        st.write("- 하루 급여량을 2~3회로 나누어 주면 폭식과 구토를 줄이는 데 도움이 됩니다.")

    with tabs[8]:
        st.subheader("🩺 대표 질병 징후")
        st.write("- 방광염/요로계: 화장실을 자주 들락거리거나 소변 양이 줄고 혈뇨가 보일 수 있습니다.")
        st.write("- 장 문제: 지속적인 설사·구토·식욕 저하·체중 감소 등이 동반됩니다.")
        st.write("- 구강 문제: 입 냄새, 침 흘림, 딱딱한 사료를 씹기 어려워하는 모습이 보일 수 있습니다.")


# ======================================
# 4. 응급상황 AI
# ======================================
def page_ai_emergency():
    st.title("🚨 응급상황 AI")

    mode = st.selectbox(
        "상황 종류를 선택해 주세요.",
        ["선택하세요", "건강 관련 응급", "심폐소생술 개념", "화재/지진 등 재난 상황", "고양이 실종/가출"],
    )

    if mode == "건강 관련 응급":
        st.subheader("🩺 건강 관련 응급상황")
        sym = st.selectbox(
            "주 증상을 선택해 주세요.",
            ["선택하세요", "반복 구토", "지속 설사/혈변", "호흡 곤란", "갑작스러운 무기력", "외상/출혈"],
        )
        if st.button("응급 가이드 보기"):
            if sym == "반복 구토":
                st.write("- 사료와 물을 잠시 치우고, 구토 횟수·내용물을 기록해 주세요.")
                st.write("- 하루 이상 반복되면 24시 동물병원 문의를 권장합니다.")
            elif sym == "지속 설사/혈변":
                st.write("- 사람용 지사제는 사용하지 마세요.")
                st.write("- 변의 색·모양·횟수를 기록하고 사진을 남겨 두면 진료에 도움이 됩니다.")
            elif sym == "호흡 곤란":
                st.error("입을 벌리고 헐떡이거나 혀·잇몸이 파랗게 보이면 **매우 위급한 상황**입니다. 즉시 응급 병원으로 이동해야 합니다.")
            elif sym == "갑작스러운 무기력":
                st.write("- 체온(너무 뜨겁거나 차갑지 않은지), 호흡 수, 잇몸 색을 확인해 주세요.")
                st.write("- 먹지도, 움직이지도 않으면 바로 병원 상담이 필요합니다.")
            elif sym == "외상/출혈":
                st.write("- 깨끗한 거즈나 천으로 상처 부위를 부드럽게 압박해 지혈을 시도합니다.")
                st.write("- 큰 출혈·절뚝거림이 있으면 즉시 병원으로 이동해야 합니다.")

    elif mode == "심폐소생술 개념":
        st.subheader("❤️ 반려동물 심폐소생술 (원리 소개)")
        st.write("- 의식과 호흡, 맥박이 있는지 먼저 확인합니다.")
        st.write("- 호흡과 맥박이 모두 없을 때에만 심폐소생술을 고려해야 합니다.")
        st.write("- 작은 고양이는 한 손 혹은 두 손가락으로 가슴을 압박하며 분당 100~120회 정도의 속도로 시행합니다.")
        st.info("실제 상황에서는 24시 동물병원과 통화하며 안내를 받는 것이 가장 안전합니다.")

    elif mode == "화재/지진 등 재난 상황":
        st.subheader("🔥 화재/지진 등 재난 상황 시 대처")
        st.write("- 이동장을 항상 눈에 띄는 곳에 두고, 고양이가 평소에 들어가 익숙해지도록 해 주세요.")
        st.write("- 화재 시에는 고양이를 찾느라 너무 오래 머무르기보다, 가까운 곳에 있는 개체부터 이동장에 넣어 빠르게 대피합니다.")
        st.write("- 지진 시에는 창문, 떨어질 물건 근처에서 멀어져 고양이와 함께 낮은 자세를 유지합니다.")

    elif mode == "고양이 실종/가출":
        st.subheader("🔍 고양이 실종/가출 시 대처")
        st.write("- 실종 직후, 집 주변 50m 이내를 조용히 돌아보며 익숙한 이름으로 불러 주세요.")
        st.write("- 차 밑, 계단 아래, 화단 등 숨기 좋은 곳을 중심으로 살펴봅니다.")
        st.write("- 집 근처에 사용하던 담요·모래·밥그릇 등을 놓아 냄새로 돌아올 수 있게 합니다.")
        st.write("- 동네 커뮤니티, SNS, 전단을 활용해 위치·시간·특징을 공유하면 도움이 됩니다.")


# ======================================
# 5. 음식 사전
# ======================================
def page_food_dict():
    st.title("🍙 음식 사전")

    food_db = st.session_state.food_db

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("사람 음식 이름을 입력해 주세요. (예: 양파, 사과, 초콜릿 등)", key="food_query")
    with col2:
        search_clicked = st.button("검색")

    st.markdown("<br>", unsafe_allow_html=True)

    if search_clicked:
        name = (st.session_state.food_query or "").strip()
        if not name:
            st.warning("먼저 음식 이름을 입력해 주세요.")
        elif name in food_db:
            info = food_db[name]
            if info["가능"] == "불가":
                st.error(f"❌ {name} : 고양이에게 **절대 급여하면 안 되는 음식**입니다.")
            else:
                st.success(f"⭕ {name} : {info['가능']}")
            st.write("⚠️ 주의사항:")
            st.write("- " + info["주의"])
        else:
            st.warning(f"'{name}' 에 대한 데이터가 없습니다.")
            st.write("반드시 수의사나 신뢰할 수 있는 자료를 통해 다시 한 번 확인해 주세요.")

    with st.expander("📃 현재 등록된 음식 목록 보기"):
        df_food = pd.DataFrame(
            [
                {"음식": k, "급여 가능/조건": v["가능"], "주의사항": v["주의"]}
                for k, v in food_db.items()
            ]
        )
        st.dataframe(df_food, use_container_width=True)


# ======================================
# 6. 마켓
# ======================================
def page_market():
    st.title("🛍️ 묘멘트 마켓")

    df = get_records_df()
    if df.empty:
        st.info("최근 건강 기록이 없어 기본 추천만 보여드립니다.")
        state = "정보 부족"
    else:
        last = df.iloc[-1]
        state = "전반적으로 양호"
        if last["배변"] in ["설사", "혈변"]:
            state = "장 건강 민감"
        elif last["음수량"] in ["거의 안 마심", "적게"]:
            state = "수분 섭취 부족"
        elif last["식사량"] in ["거의 안 먹음", "적게"]:
            state = "식욕 저하 가능"

    st.subheader(f"현재 상태 (간단 추정): {state}")

    st.markdown("---")
    st.subheader("추천 사료/간식 타입")

    if state == "장 건강 민감":
        st.write("- 소화가 잘 되는 저자극 사료")
        st.write("- 유산균이 포함된 사료/간식")
        st.write("- 갑작스러운 사료 변경은 피하고 서서히 바꾸기")
    elif state == "수분 섭취 부족":
        st.write("- 수분 함량이 높은 습식 사료")
        st.write("- 물 섭취를 유도하는 국물·츄르 형태 간식")
        st.write("- 자동 급수기(분수형) 사용도 도움이 될 수 있습니다.")
    elif state == "식욕 저하 가능":
        st.write("- 향이 강한 습식 사료와 츄르를 소량씩 자주 급여")
        st.write("- 식사 환경(소음, 스트레스 요인 등)을 점검해 보세요.")
    else:
        st.write("- 연령·중성화 여부에 맞춘 균형형 사료")
        st.write("- 비만 방지를 위해 칼로리 과다한 간식은 피하기")

    st.info("실제 서비스에서는 쇼핑몰과 연동해 구체적인 상품까지 추천하도록 확장할 수 있습니다.")


# ======================================
# 라우팅
# ======================================
menu = st.sidebar.radio(
    "메뉴",
    ["홈", "건강 기록", "AI 진단", "집사 가이드", "응급상황 AI", "음식 사전", "마켓"],
)

if menu == "홈":
    try:
        st.image("banner.png", use_column_width=True)
    except Exception:
        st.title("🐱 묘멘트")
        st.write("배너 이미지를 불러올 수 없어요. `banner.png` 파일 위치를 확인해 주세요.")
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
