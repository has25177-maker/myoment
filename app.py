import streamlit as st
import base64
import os
import pandas as pd
from datetime import date
import requests

# ======================================
# 0. 설정
# ======================================
st.set_page_config(page_title="묘멘트", page_icon="♧", layout="wide")

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

/* UI 색상 */
body, .main, [data-testid="stAppViewContainer"],
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

/* sidebar toggler(→ keyboard_double_arrow_right) 숨기기 */
button[kind="header"] {{
    display: none !important;
}}

</style>
"""
st.markdown(CUSTOM_STYLE, unsafe_allow_html=True)

# ======================================
# 2. 세션 상태
# ======================================
if "records" not in st.session_state:
    st.session_state.records = []

if "food_db" not in st.session_state:
    st.session_state.food_db = {
        "닭가슴살": {"가능": "소량 삶아서 가능", "주의": "양념·소금 없이 주세요."},
        "소고기": {"가능": "잘 익힌 살코기 가능", "주의": "양념된 고기 금지"},
        "돼지고기": {"가능": "충분히 익힌 살코기만", "주의": "기름 많은 부위 금지"},
        "연어": {"가능": "익힌 연어만 가능", "주의": "생·훈제 연어 금지"},
        "사과": {"가능": "씨 제거 후 과육만", "주의": "씨 독성 주의"},
        "초콜릿": {"가능": "불가", "주의": "카카오 독성"},
        "양파": {"가능": "불가", "주의": "적혈구 파괴 위험"},
        "포도": {"가능": "불가", "주의": "신장 손상 위험"},
    }

def add_record(rec):
    st.session_state.records.append(rec)

def get_records_df():
    if not st.session_state.records:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.records)


# ======================================
# 3. 건강 기록
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
            vomit_color = st.selectbox("구토 색", ["선택 안 함", "투명", "노란색", "갈색", "붉은색", "기타"])
            vomit_type = st.selectbox("구토 내용물", ["선택 안 함", "헤어볼", "사료 조각", "액체/거품", "기타"])

        memo = st.text_area("메모", placeholder="환경 변화, 약 복용 등")

    if st.button("기록 저장"):
        add_record({
            "날짜": rec_date,
            "식사량": meal,
            "음수량": water,
            "배변": poop,
            "행동": ", ".join(activity),
            "이상증세": ", ".join(symptoms),
            "구토 색": vomit_color,
            "구토 내용": vomit_type,
            "메모": memo,
        })
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
    warnings, tips = [], []

    if recent["식사량"].isin(["거의 안 먹음", "적게"]).sum() >= 2:
        warnings.append("식사량이 줄어든 날이 반복되고 있어요.")
        tips.append("식욕 저하는 다양한 질환의 신호일 수 있습니다.")

    if recent["음수량"].isin(["거의 안 마심", "적게"]).sum() >= 2:
        warnings.append("음수량이 부족한 날이 있어요.")
        tips.append("습식 사료, 자동 급수기 등을 활용해 주세요.")

    if recent["배변"].isin(["설사", "혈변", "안 봄"]).sum() >= 2:
        warnings.append("배변 이상이 여러 번 나타났어요.")
        tips.append("3일 이상 지속되면 병원 상담이 필요합니다.")

    if recent["이상증세"].str.contains("구토", na=False).sum() >= 2:
        warnings.append("구토 기록이 여러 번 있습니다.")
        tips.append("헤어볼, 장 문제 등 다양한 원인이 있습니다.")

    if not warnings:
        st.success("최근 기록에서 큰 위험 신호는 보이지 않습니다.")
    else:
        st.subheader("주의가 필요한 변화")
        for w in warnings:
            st.warning("- " + w)

    if tips:
        st.subheader("참고 팁")
        for t in tips:
            st.write("- " + t)


# ======================================
# 5. 응급상황 + 오픈스트리트맵(Nominatim API)
# ======================================

def geocode_osm(address):
    """주소 → 위도/경도 (OSM API)"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    r = requests.get(url, params=params, headers={"User-Agent": "myoment-app"})
    data = r.json()
    if not data:
        return None, None
    return float(data[0]["lat"]), float(data[0]["lon"])

def search_hospitals_osm(lat, lon):
    """OSM Overpass API로 주변 동물병원 검색"""
    query = f"""
    [out:json];
    (
      node["amenity"="veterinary"](around:5000,{lat},{lon});
      way["amenity"="veterinary"](around:5000,{lat},{lon});
      relation["amenity"="veterinary"](around:5000,{lat},{lon});
    );
    out center;
    """
    url = "https://overpass-api.de/api/interpreter"
    r = requests.post(url, data=query)
    data = r.json()

    results_map = []
    results_table = []

    for el in data["elements"]:
        if "lat" in el:
            lat2, lon2 = el["lat"], el["lon"]
        else:
            lat2, lon2 = el["center"]["lat"], el["center"]["lon"]

        name = el["tags"].get("name", "동물병원")
        addr = el["tags"].get("addr:full", "")
        phone = el["tags"].get("phone", "")

        results_map.append({"lat": lat2, "lon": lon2})
        results_table.append({"이름": name, "주소": addr, "전화": phone})

    return pd.DataFrame(results_map), pd.DataFrame(results_table)

def page_ai_emergency():
    st.title("† 응급상황 AI")

    st.subheader("♧ 근처 동물병원 찾기")
    region = st.text_input("주소 입력 (예: 서울 강남구)")
    if st.button("검색"):
        lat, lon = geocode_osm(region)
        if lat is None:
            st.warning("주소를 찾을 수 없습니다.")
        else:
            mdf, tdf = search_hospitals_osm(lat, lon)
            st.map(mdf)
            st.dataframe(tdf, use_container_width=True)

    st.markdown("---")
    mode = st.selectbox("응급 종류",
                        ["선택", "반복 구토", "호흡 곤란", "출혈/상처", "실종/가출"])

    if mode == "반복 구토":
        st.write("- 사료/물 잠시 치우고 상태 확인")
        st.write("- 하루 이상 지속되면 병원 상담 권장")
    elif mode == "호흡 곤란":
        st.error("즉시 응급 병원 이동해야 하는 상황입니다.")
    elif mode == "출혈/상처":
        st.write("- 깨끗한 천으로 압박 지혈")
        st.write("- 지속 시 응급 진료 필요")
    elif mode == "실종/가출":
        st.write("- 집 주변 50m 먼저 탐색")
        st.write("- 차 밑/계단 아래 등 숨기 좋은 곳 중심으로 확인")


# ======================================
# 6. 집사 가이드
# ======================================
def page_guide():
    st.title("£ 집사 가이드")

    tabs = st.tabs([
        "기본 가이드", "약 먹이기", "격리·적응", "목욕", "발톱 관리",
        "노령묘 관리", "중성화 이후", "다이어트", "대표 질병 징후"
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
            [{"음식": k, "급여": v["가능"], "주의": v["주의"]} for k,v in st.session_state.food_db.items()]
        )
        st.dataframe(fdf, use_container_width=True)


# ======================================
# 8. 마켓
# ======================================
def page_market():
    st.title("♤ 묘멘트 마켓")

    df = get_records_df()
    if df.empty:
        st.info("기록이 없어 기본 추천만 보여드립니다.")
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
            state = "전반적 양호"

    st.subheader(f"현재 상태: {state}")
    st.write("- 맞춤형 사료·간식 추천 예시")


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
