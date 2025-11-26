import streamlit as st
import base64
import os
import pandas as pd
from datetime import date
import requests
from geopy.geocoders import Nominatim  # OSM 주소 → 좌표

# ======================================
# 0. 기본 설정
# ======================================
st.set_page_config(page_title="묘멘트", page_icon="♧", layout="wide")

# ======================================
# 1. 폰트 + 전역 스타일 (원래 쓰던 버전 유지)
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

/* 전체 배경 */
body, .main, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.block-container {{
    background-color: #FEF7EB !important;
}}

/* 사이드바 */
[data-testid="stSidebar"] {{
    background-color: #F3E8DD !important;
}}

/* 텍스트 색상 */
h1, h2, h3, h4, h5 {{
    color: #4A332D !important;
}}
p, span, label {{
    color: #4A332D !important;
}}

/* 버튼 */
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

/* 입력창 */
input, textarea {{
    background-color: #FEF7EB !important;
    color: #4A332D !important;
    border-radius: 8px !important;
}}
div[data-baseweb="select"] > div {{
    background-color: #FEF7EB !important;
    border-radius: 8px !important;
}}

/* 라디오/체크박스 */
input[type="radio"], input[type="checkbox"] {{
    accent-color: #E6B59D !important;
}}

/* 스크롤 바 */
::-webkit-scrollbar-thumb {{
    background-color: #E6B59D !important;
    border-radius: 10px;
}}

/* keyboard_double_arrow_right 아이콘/버튼 제거 */
svg[data-testid="stActionButtonIcon"] {{
    display: none !important;
}}
button[kind="header"] {{
    display: none !important;
}}

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
# 4. AI 진단 (이전 버전 그대로)
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
        tips.append("수분 섭취를 높이기 위해 자동 급수기, 습식 사료 등을 고려해 보세요.")

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
# 5. OSM 기반 동물병원 검색
# ======================================
def search_animal_hospitals_osm(region: str):
    region = (region or "").strip()
    if not region:
        st.warning("먼저 주소나 동네 이름을 입력해 주세요.")
        return None, None

    geolocator = Nominatim(user_agent="myoment_app")
    try:
        loc = geolocator.geocode(region)
    except Exception:
        st.error("주소 검색 중 오류가 발생했습니다.")
        return None, None

    if loc is None:
        st.warning("해당 주소를 찾을 수 없습니다. (예: 서울 강남구, 부산 해운대구)")
        return None, None

    lat, lon = loc.latitude, loc.longitude

    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    (
      node["amenity"="veterinary"](around:3000,{lat},{lon});
    );
    out;
    """
    try:
        res = requests.get(overpass_url, params={"data": query}, timeout=25)
    except Exception:
        st.error("동물병원 정보를 가져오는 중 오류가 발생했습니다.")
        return None, None

    if res.status_code != 200:
        st.error("동물병원 정보를 가져오는 중 오류가 발생했습니다.")
        return None, None

    data = res.json()
    elements = data.get("elements", [])
    if not elements:
        st.info("주변 3km 이내에 등록된 동물병원을 찾지 못했습니다.")
        return None, None

    map_rows = []
    table_rows = []
    for el in elements:
        if el.get("type") != "node":
            continue
        tags = el.get("tags", {})
        name = tags.get("name", "이름 미상 동물병원")
        addr = tags.get("addr:full") or tags.get("addr:road") or tags.get("addr:street") or ""
        phone = tags.get("phone", "")

        plat = el["lat"]
        plon = el["lon"]

        map_rows.append({"lat": plat, "lon": plon})
        table_rows.append({"이름": name, "주소": addr, "전화": phone})

    map_df = pd.DataFrame(map_rows)
    table_df = pd.DataFrame(table_rows)

    return map_df, table_df


def page_ai_emergency():
    st.title("† 응급상황 AI")

    st.subheader("♧ 근처 동물병원 찾기 (OpenStreetMap)")
    region = st.text_input("주소 입력 (예: 서울 강남구)")
    if st.button("검색"):
        map_df, table_df = search_animal_hospitals_osm(region)
        if map_df is not None:
            st.map(map_df)
            if table_df is not None:
                st.dataframe(table_df, use_container_width=True)

    st.markdown("---")
    mode = st.selectbox(
        "상황 선택",
        ["선택", "건강 응급", "심폐소생술", "화재/지진", "고양이 실종"],
    )

    if mode == "건강 응급":
        st.write("- 반복 구토: 사료/물 잠시 치우고 횟수·내용 기록")
        st.write("- 설사/혈변: 사람용 지사제 사용 금지, 변 상태 기록 후 병원 문의")
        st.write("- 호흡 곤란: 입 벌리고 헐떡이거나 혀·잇몸이 파랗게 보이면 즉시 응급 병원 이동")
    elif mode == "심폐소생술":
        st.write("- 의식 확인 → 호흡·맥박 없을 때에만 흉부 압박을 고려")
        st.write("- 작은 고양이는 한 손/두 손가락으로 분당 100~120회 정도로 가슴 압박")
    elif mode == "화재/지진":
        st.write("- 이동장을 항상 눈에 띄는 곳에 두고, 평소에 들어가 쉬는 습관을 들이기")
        st.write("- 화재 시에는 가장 가까운 고양이부터 이동장에 넣고 빠르게 대피")
        st.write("- 지진 시에는 떨어질 물건·창문에서 멀리 떨어져 낮은 자세 유지")
    elif mode == "고양이 실종":
        st.write("- 실종 직후 집 주변 50m를 조용히 돌며 숨기 좋은 곳(차 밑, 계단 아래 등) 위주로 탐색")
        st.write("- 사용하던 담요·모래·밥그릇을 집 근처에 두어 냄새로 돌아오게 유도")
        st.write("- 동네 커뮤니티, SNS, 전단을 활용해 위치·시간·특징 공유")


# ======================================
# 6. 집사 가이드 (내용 채운 버전)
# ======================================
def page_guide():
    st.title("£ 집사 가이드")

    tabs = st.tabs(
        [
            "기본 가이드",
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

    # 1) 기본 가이드
    with tabs[0]:
        st.subheader("초보 집사를 위한 기본 가이드")
        lines = [
            "처음 함께 살게 되면, 숨을 수 있는 안전한 공간과 조용한 환경을 먼저 만들어 주세요.",
            "밥·물·화장실 위치는 자주 바꾸지 않는 것이 좋습니다.",
            "화장실, 물, 밥그릇은 서로 너무 가깝지 않게 배치하는 것이 안정감에 도움이 됩니다.",
            "갑작스러운 환경 변화(이사, 공사 소음, 새 가족)는 스트레스를 주어 행동 변화로 나타날 수 있어요.",
            "처음 며칠은 억지로 안고 놀기보다, 스스로 다가올 때까지 기다려 주세요.",
        ]
        for l in lines:
            st.write("- " + l)

    # 2) 약 먹이기
    with tabs[1]:
        st.subheader("약 먹이기")
        lines = [
            "가능하면 고양이 전용 처방약, 약 먹이기 보조 간식(필 포켓 등)을 활용하세요.",
            "알약은 혀 뒤편에 두고 입을 닫은 뒤 목을 살짝 쓰다듬으며 삼키는지 확인합니다.",
            "가루약은 좋아하는 습식/간식에 극소량 섞어 반응을 본 뒤 점점 양을 늘려 주세요.",
            "약 먹이기 직후 작은 간식을 주어 약 먹는 경험을 긍정적으로 연결해 주면 좋습니다.",
        ]
        for l in lines:
            st.write("- " + l)

    # 3) 격리·적응
    with tabs[2]:
        st.subheader("격리·적응")
        lines = [
            "새 고양이를 들일 때는 최소 며칠간 방을 나누어 냄새와 소리에 먼저 적응시킵니다.",
            "문을 사이에 두고 냄새만 공유하는 기간을 가진 뒤, 짧은 시간씩 대면 시간을 늘려갑니다.",
            "기존 고양이와 새로운 고양이 모두에게 ‘자신만의 안전한 공간’을 마련해 주세요.",
            "처음 대면할 때는 간식을 활용해 서로를 좋은 경험과 연결시켜 주세요.",
        ]
        for l in lines:
            st.write("- " + l)

    # 4) 목욕
    with tabs[3]:
        st.subheader("목욕")
        lines = [
            "필요한 경우(오염, 피부 문제 등)에만 짧게 하고, 미끄럽지 않은 환경에서 진행합니다.",
            "고양이 전용 샴푸를 사용하고, 물과 거품이 눈·귀에 들어가지 않도록 주의합니다.",
            "샤워기 물줄기는 약하게, 소음이 크게 나지 않도록 조절해 주세요.",
            "목욕 후에는 수건+드라이어를 이용해 충분히 말려주지 않으면 감기·피부 문제가 생길 수 있습니다.",
        ]
        for l in lines:
            st.write("- " + l)

    # 5) 발톱 관리
    with tabs[4]:
        st.subheader("발톱 관리")
        lines = [
            "처음에는 한 발가락씩 아주 짧게만 자르며 간식과 칭찬을 함께 주세요.",
            "발을 만지는 것 자체에 익숙해지도록 평소에도 가볍게 터치하며 칭찬해 주세요.",
            "혈관이 있는 분홍 부분을 피해서 끝의 뾰족한 부분만 조금씩 잘라 주세요.",
            "한 번에 모든 발톱을 다 자르려 하기보다 여러 번 나눠서 하는 것이 좋습니다.",
        ]
        for l in lines:
            st.write("- " + l)

    # 6) 노령묘 관리
    with tabs[5]:
        st.subheader("노령묘 관리")
        lines = [
            "먹는 양, 배변, 움직임, 점프 능력 등 작은 변화를 자주 확인해 주세요.",
            "관절 통증, 신장·갑상선 질환 등이 늘어나는 시기라 정기 검진이 중요합니다.",
            "높은 곳 대신 낮은 곳에도 쉴 수 있는 공간을 마련하고, 점프를 줄일 수 있도록 발판을 두면 도움이 됩니다.",
            "놀이 시간은 자주, 하지만 너무 격하지 않게 진행해 주세요.",
        ]
        for l in lines:
            st.write("- " + l)

    # 7) 중성화 이후
    with tabs[6]:
        st.subheader("중성화 수술 이후")
        lines = [
            "수술 부위를 핥거나 뜯지 못하도록 넥카라를 착용합니다.",
            "수술 부위가 붉게 붓거나 지속적인 출혈·분비물이 보이면 병원에 즉시 문의하세요.",
            "1~2일 정도 활동량과 식사량이 줄 수 있지만 오래 지속되면 반드시 상담이 필요합니다.",
            "중성화 이후에는 대사량이 줄어 살이 찌기 쉬우므로 사료 양과 운동량을 함께 조절해야 합니다.",
        ]
        for l in lines:
            st.write("- " + l)

    # 8) 다이어트/체중 관리
    with tabs[7]:
        st.subheader("다이어트 / 체중 관리")
        lines = [
            "무작정 양만 줄이기보다는 저칼로리/다이어트용 사료로 천천히 전환하는 것이 좋습니다.",
            "하루 급여량을 2~3회로 나누어 주면 폭식과 구토를 줄이는 데 도움이 됩니다.",
            "간식은 하루 총 칼로리의 10% 이내로 유지하고, 사냥놀이로 활동량을 늘려 주세요.",
            "급격한 체중 감소는 지방간 등 심각한 문제를 유발할 수 있으니 천천히 감량하는 것이 중요합니다.",
        ]
        for l in lines:
            st.write("- " + l)

    # 9) 대표 질병 징후
    with tabs[8]:
        st.subheader("대표 질병 징후")
        lines = [
            "방광염/요로계: 화장실을 자주 들락거리거나 소변 양이 줄고 혈뇨가 보일 수 있습니다.",
            "장 문제: 지속적인 설사·구토·식욕 저하·체중 감소 등이 동반될 수 있습니다.",
            "구강 문제: 침 흘림, 입 냄새, 딱딱한 사료를 씹기 어려워함, 한쪽으로만 씹는 모습이 보일 수 있습니다.",
            "호흡기 문제: 기침, 헐떡임, 쉬는 상태에서 호흡수가 빠른 경우 등을 주의 깊게 관찰해 주세요.",
        ]
        for l in lines:
            st.write("- " + l)


# ======================================
# 7. 음식 사전
# ======================================
def page_food_dict():
    st.title("¢ 음식 사전")

    col1, col2 = st.columns([3, 1])
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
    st.write("- 상태에 맞는 사료/간식 타입을 간단히 보여주는 프로토타입입니다.")


# ======================================
# 9. 라우팅
# ======================================
menu = st.sidebar.radio(
    "메뉴",
    ["홈", "건강 기록", "AI 진단", "집사 가이드", "응급상황 AI", "음식 사전", "마켓"],
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
