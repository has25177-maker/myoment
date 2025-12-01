import streamlit as st
import base64
import os
import pandas as pd
from datetime import date
import requests

# ======================================
# 1. 폰트 + 전역 스타일
# ======================================
def load_font_base64(font_path):
    with open(font_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


FONT_PATH = os.path.join(os.path.dirname(__file__), "Ownglyph_PDH-Rg.woff2")
font_base64 = load_font_base64(FONT_PATH)

CUSTOM_STYLE = f"""
<style>

@font-face {{
    font-family: 'MyoFont';
    src: url(data:font/woff2;base64,{font_base64}) format('woff2');
    font-weight: normal;
    font-style: normal;
}}

html, body, [class^="st-"], [class*=" st-"], div, span, label, p, h1, h2, h3, h4, h5, h6 {{
    font-family: 'MyoFont', sans-serif !important;
}}

input, textarea, select {{
    font-family: 'MyoFont', sans-serif !important;
}}

button, .stButton > button {{
    font-family: 'MyoFont', sans-serif !important;
}}

body, .main, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.block-container {{
    background-color: #FEF7EB !important;
}}

[data-testid="stSidebar"] {{
    background-color: #F3E8DD !important;
}}

h1, h2, h3, h4, h5 {{
    color: #4A332D !important;
}}
p, span, label {{
    color: #4A332D !important;
}}

.stButton > button {{
    background-color: #E6B59D !important;
    color: #4A332D !important;
    border-radius: 10px;
    border: none;
    padding: 0.5rem 1.2rem;
}}
.stButton > button:hover {{
    background-color: #d8c4b6 !important;
}}

input, textarea {{
    background-color: #FEF7EB !important;
    color: #4A332D !important;
    border-radius: 8px !important;
}}

div[data-baseweb="select"] > div {{
    background-color: #FEF7EB !important;
    border-radius: 8px !important;
}}

input[type="radio"], input[type="checkbox"] {{
    accent-color: #E6B59D !important;
}}

::-webkit-scrollbar-thumb {{
    background-color: #E6B59D !important;
    border-radius: 10px;
}}

button svg,
[data-testid="baseButton-headerNoPadding"] svg,
[data-testid="stSidebarContent"] svg,
.css-1647f2h svg,
.css-1cpxbza svg,
.css-1r6r8x4 svg {
    display: none !important;
}

</style>
"""

st.markdown(CUSTOM_STYLE, unsafe_allow_html=True)

# ======================================
# 2. 세션 상태 초기화
# ======================================
if "records" not in st.session_state:
    st.session_state.records = []

if "food_db" not in st.session_state:
    st.session_state.food_db = {
        "닭가슴살": {"가능": "소량 삶아서 가능", "주의": "양념·소금 없이 주세요."},
        "소고기": {"가능": "잘 익혀 소량 가능", "주의": "양념된 형태는 금지."},
        "돼지고기": {"가능": "충분히 익힌 살코기만", "주의": "기름 많은 부분 X"},
        "연어": {"가능": "익힌 연어만 가능", "주의": "생연어·훈제 연어 금지"},
        "사과": {"가능": "씨 제거 후 과육만", "주의": "씨 독성 주의"},
        "초콜릿": {"가능": "불가", "주의": "카카오 독성"},
        "양파": {"가능": "불가", "주의": "적혈구 파괴 유발"},
        "포도": {"가능": "불가", "주의": "신장 손상 위험"},
    }


# ======================================
# 유틸
# ======================================
def add_record(rec: dict):
    st.session_state.records.append(rec)

def get_records_df():
    if not st.session_state.records:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.records)


# ======================================
# 3. 건강 기록 페이지
# ======================================
def page_health_log():
    st.title("♧ 건강 기록")

    col1, col2 = st.columns(2)

    with col1:
        rec_date = st.date_input("기록 날짜", value=date.today())

        meal = st.radio("식사량", ["거의 안 먹음", "적게", "보통", "많이"], index=2)
        water = st.radio("음수량", ["거의 안 마심", "적게", "보통", "많이"], index=2)
        poop = st.radio("배변 상태", ["정상", "단단함", "설사", "혈변", "안 봄"], index=0)

    with col2:
        activity = st.multiselect(
            "활동 및 행동",
            ["보통", "잠이 많아짐", "활동 감소", "활동 증가", "예민/공격적", "숨는 시간이 늘어남"],
            default=["보통"],
        )

        symptoms = st.multiselect(
            "이상증세",
            ["구토", "기침", "호흡 이상", "절뚝거림", "눈/코 분비물", "가려움", "기타"],
        )

        vomit_color = ""
        vomit_type = ""
        if "구토" in symptoms:
            st.markdown("#### ♤ 구토 상세 기록")
            vomit_color = st.selectbox(
                "구토 색",
                ["선택 안 함", "투명/거품", "노란색(담즙)", "갈색/사료", "붉은색/분홍색", "기타"],
            )
            vomit_type = st.selectbox(
                "구토 내용물",
                ["선택 안 함", "헤어볼", "사료 조각", "거품/액체", "이물질 가능", "기타"],
            )

        memo = st.text_area("메모", placeholder="환경 변화, 약 복용, 간식 등")

    if st.button("기록 저장"):
        rec = {
            "날짜": rec_date,
            "식사량": meal,
            "음수량": water,
            "배변": poop,
            "행동": ", ".join(activity),
            "이상증세": ", ".join(symptoms),
            "구토 색": vomit_color,
            "구토 내용": vomit_type,
            "메모": memo,
        }
        add_record(rec)
        st.success("기록이 저장되었습니다!")

    st.markdown("---")
    st.subheader("최근 기록")
    df = get_records_df()
    if df.empty:
        st.info("아직 기록이 없습니다.")
    else:
        st.dataframe(df.tail(10), use_container_width=True)


# ======================================
# 4. AI 진단
# ======================================
def page_ai_diagnosis():
    st.title("♤ AI 진단")

    df = get_records_df()
    if df.empty:
        st.info("먼저 건강 기록을 입력해 주세요.")
        return

    recent = df.tail(7)
    warnings = []
    tips = []

    # 식사량 저하
    if recent["식사량"].isin(["거의 안 먹음", "적게"]).sum() >= 2:
        warnings.append("식사량이 줄어든 날이 여러 번 있었어요.")
        tips.append("24시간 이상 지속되면 병원 상담이 필요합니다.")

    # 음수량 부족
    if recent["음수량"].isin(["거의 안 마심", "적게"]).sum() >= 2:
        warnings.append("음수량이 부족한 날이 반복되고 있어요.")
        tips.append("수분 섭취를 높이기 위해 자동 급수기 등을 고려해 보세요.")

    # 배변 이상
    if recent["배변"].isin(["설사", "혈변", "안 봄"]).sum() >= 2:
        warnings.append("배변 이상이 반복되고 있어요.")
        tips.append("사진 기록 후 병원 상담을 권장합니다.")

    # 구토
    if recent["이상증세"].str.contains("구토", na=False).sum() >= 2:
        warnings.append("구토가 여러 번 기록되었습니다.")
        tips.append("헤어볼 · 사료 문제 등 다양한 원인이 있을 수 있습니다.")

    if not warnings:
        st.success("최근 기록에서는 큰 위험 신호가 보이지 않습니다.")
    else:
        st.subheader("주의가 필요한 변화")
        for w in warnings:
            st.warning("- " + w)

    if tips:
        st.subheader("참고 팁")
        for t in tips:
            st.write("- " + t)

# ======================================
# 응급상황 AI – OpenStreetMap 기반 병원 검색 (folium 없이)
# ======================================
def page_ai_emergency():
    st.title("† 응급상황 AI")

    # ----------------------------
    # 1) 응급 상황별 가이드 (먼저 표시)
    # ----------------------------
    st.subheader("⚠️ 응급 상황별 가이드")

    mode = st.selectbox(
        "상황 선택",
        ["선택", "건강 응급", "심폐소생술", "화재/지진", "고양이 실종"]
    )

    if mode == "건강 응급":
        st.write("- 반복 구토: 사료/물 잠시 치우고 기록")
        st.write("- 호흡 곤란: 즉시 병원 이동")
        st.write("- 의식 저하: 바로 응급 진료")

    elif mode == "심폐소생술":
        st.write("- 의식 확인 → 호흡·맥박 없으면 즉시 엄지 손가락과 네 손가락으로 흉부 압박")
        st.write("- 100~120회/분 속도, 1/3 흉곽 깊이")
        st.write("- 30회 압박 후 2회 인공호흡 반복")

    elif mode == "화재/지진":
        st.write("- 이동장 바로 사용하도록 평소 훈련")
        st.write("- 큰 소리·진동 → 숨을 수 있는 공간 확보")
        st.write("- 화재 연기 흡입 시 즉시 병원 이동")

    elif mode == "고양이 실종":
        st.write("- 50m 반경 조용히 탐색")
        st.write("- 집 주변 숨기 좋은 공간 집중 확인")
        st.write("- 낯선 사람이 찾지 말고 집사가 직접 탐색")
        st.write("- 먹이/모래/담요 이용해 유도 가능")

    st.markdown("---")

    # ----------------------------
    # 2) 근처 병원 지도 (아래 표시)
    # ----------------------------
    st.subheader("📍 근처 동물병원 찾기")
    page_osm_map()


import requests
import pandas as pd

# 1) 주소를 좌표로 변환
def geocode_address(address: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }
    res = requests.get(url, params=params, headers={"User-Agent": "myoment-app"})
    data = res.json()

    if not data:
        return None, None

    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    return lat, lon


# 2) Overpass API로 근처 동물병원 검색
def search_pet_hospitals(lat, lon, radius=3000):
    query = f"""
    [out:json][timeout:20];
    (
      node["amenity"="veterinary"](around:{radius},{lat},{lon});
      way["amenity"="veterinary"](around:{radius},{lat},{lon});
      relation["amenity"="veterinary"](around:{radius},{lat},{lon});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"
    res = requests.post(url, data={"data": query})
    data = res.json()

    results = []
    for e in data["elements"]:
        if "lat" in e and "lon" in e:
            results.append({
                "이름": e["tags"].get("name", "이름 없음"),
                "lat": float(e["lat"]),
                "lon": float(e["lon"]),
            })

    return pd.DataFrame(results)


# 3) Streamlit 페이지
def page_osm_map():
    st.title("📍 근처 동물병원 찾기 (OpenStreetMap)")

    address = st.text_input("주소 입력 (예: 서울 강남구)")

    if st.button("검색"):
        if not address:
            st.warning("주소를 입력해 주세요.")
            return

        lat, lon = geocode_address(address)

        if lat is None:
            st.error("주소를 찾을 수 없습니다.")
            return

        # 병원 검색
        df = search_pet_hospitals(lat, lon)

        if df.empty:
            st.info("반경 3km 내 동물병원이 없습니다.")
            return

        # 지도 표시
        st.map(df[["lat", "lon"]])

        # 표 표시
        st.subheader("📋 병원 목록")
        st.dataframe(df, use_container_width=True)


# ======================================
# 6. 집사 가이드
# ======================================
def page_guide():
    st.title("£ 집사 가이드")
    tabs = st.tabs([
        "기본", "약 먹이기", "격리", "목욕", "발톱 관리", "노령묘",
        "중성화 이후", "다이어트", "대표 질병"
    ])

    with tabs[0]:
        st.write("- 안전한 숨숨 집 제공")
        st.write("- 밥/물/화장실 위치는 자주 바꾸지 않기")
        st.write("- 스트레스 요인(소음/손님) 최소화")

    with tabs[1]:
        st.write("- 알약은 혀 뒤쪽에 두고 턱을 살짝 받쳐 삼키도록 유도")
        st.write("- 필 포켓 같은 보조 간식 사용 추천")
        st.write("- 가루약은 습식+아주 소량부터 섞기")

    with tabs[2]:
        st.write("- 새로운 고양이 도입 시 최소 며칠 생활 공간 분리")
        st.write("- 문틈 냄새 공유 → 짧은 대면 → 점진적 적응")

    with tabs[3]:
        st.write("- 미끄럽지 않은 욕조 매트 사용")
        st.write("- 고양이 전용 샴푸 사용, 물 온도는 미지근하게")
        st.write("- 완전히 말려주지 않으면 감기 위험")

    with tabs[4]:
        st.write("- 처음엔 한두 발가락만 가볍게 연습")
        st.write("- 분홍색 혈관 부분 피해서 투명 끝만 자르기")

    with tabs[5]:
        st.write("- 활동량/식사량/점프력 감소는 초기 징후일 수 있음")
        st.write("- 정기 검진 추천(6개월~1년)")

    with tabs[6]:
        st.write("- 넥카라 착용 유지")
        st.write("- 수술 부위 붉음/부종/분비물 → 병원 상담")
        st.write("- 중성화 후 살찌기 쉬워 사료 조절 필요")

    with tabs[7]:
        st.write("- 저칼로리/다이어트 사료 활용")
        st.write("- 하루 2~3회 소분 급여")
        st.write("- 갑작스러운 사료 변경 금지")

    with tabs[8]:
        st.write("- 방광염: 화장실을 자주 들락날락/혈뇨 가능")
        st.write("- 장 문제: 설사·구토·체중 감소")
        st.write("- 구강 문제: 침 흘림, 입 냄새, 사료 씹기 어려움")


# ======================================
# 7. 음식 사전
# ======================================
def page_food_dict():
    st.title("¢ 음식 사전")

    col1, col2 = st.columns([3,1])
    with col1:
        query = st.text_input("음식 이름 입력", key="food_query")
    with col2:
        search = st.button("검색")

    if search:
        name = query.strip()
        if not name:
            st.warning("음식 이름을 입력하세요.")
        elif name in st.session_state.food_db:
            info = st.session_state.food_db[name]
            if info["가능"] == "불가":
                st.error(f"❌ {name} : 절대 금지")
            else:
                st.success(f"⭕ {name} : {info['가능']}")
            st.write("- " + info["주의"])
        else:
            st.warning("등록되지 않은 음식입니다.")

    with st.expander("전체 목록"):
        fdf = pd.DataFrame(
            [
                {"음식": k, "급여": v["가능"], "주의": v["주의"]}
                for k, v in st.session_state.food_db.items()
            ]
        )
        st.dataframe(fdf, use_container_width=True)


# ======================================
# 8. 마켓
# ======================================
def page_market():
    st.title("♤ 묘멘트 마켓")

    df = get_records_df()
    if df.empty:
        st.info("기록이 없어 기본 추천만 보여줍니다.")
        state = "정보 부족"
    else:
        last = df.iloc[-1]
        if last["배변"] in ["설사", "혈변"]:
            state = "장 건강 민감"
        elif last["음수량"] in ["거의 안 마심", "적게"]:
            state = "수분 부족"
        elif last["식사량"] in ["거의 안 먹음", "적게"]:
            state = "식욕 저하"
        else:
            state = "전반적으로 양호"

    st.subheader(f"현재 상태: {state}")
    st.write("- 맞춤형 사료 추천")
        # -----------------------------------------------------------
    # 상태별 추천 사료 리스트 (간단 예시)
    # -----------------------------------------------------------
    recommendations = {
        "장 건강 민감": [
            "✨ 로얄캐닌 센서티브 Digestion",
            "✨ 퓨리나 프로플랜 센서티브",
            "✨ ANF 인도어 솔루션 장 건강"
        ],
        "수분 부족": [
            "💧 북어국물 동결건조 토핑",
            "💧 뉴트리플랜 수분파우치",
            "💧 캣잇 플로우 동결건조 수분토핑"
        ],
        "식욕 저하": [
            "🍽️ 챠오 츄르(보조용)",
            "🍽️ 인스팅트 오리지날 캔",
            "🍽️ K9 내추럴 치킨&램 캔"
        ],
        "전반적으로 양호": [
            "🌿 오리젠 오리지날",
            "🌿 아카나 그라스랜드",
            "🌿 몬지 인도어 어덜트"
        ],
        "정보 부족": [
            "✔️ 몬지 데일리 캣",
            "✔️ 뉴트리소스 캣푸드",
            "✔️ 퓨리나 원 인도어"
        ]
    }

    st.markdown("### 추천 사료")

    for item in recommendations[state]:
        st.write(f"- {item}")



# ======================================
# 9. 라우팅
# ======================================
menu = st.sidebar.radio(
    "메뉴",
    ["홈", "건강 기록", "AI 진단", "집사 가이드", "응급상황 AI", "음식 사전", "마켓"]
)

if menu == "홈":
    try:
        st.image("banner.png", use_column_width=True)
    except:
        st.title("♧ 묘멘트")
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

