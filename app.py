import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="묘멘트", page_icon="🐱", layout="wide")

# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "records" not in st.session_state:
    # 건강 기록 리스트
    st.session_state.records = []  # 각 요소가 dict

if "food_db" not in st.session_state:
    # 음식 사전 간단 DB (예시)
    st.session_state.food_db = {
        "닭가슴살": {"가능": "소량 삶아서, 간·양념 없이 가능", "주의": "염분·양념, 훈제 제품은 피하기"},
        "참치캔": {"가능": "고양이 전용 참치는 가끔 소량 가능", "주의": "사람용 참치캔은 염분·기름 때문에 비추천"},
        "우유": {"가능": "고양이 전용 락토프리 우유만 소량 가능", "주의": "일반 우유는 설사 유발 가능"},
        "양파": {"가능": "불가", "주의": "적혈구 파괴 → 빈혈 유발, 절대 금지"},
        "마늘": {"가능": "불가", "주의": "양파와 비슷하게 독성, 아주 소량도 금지"},
        "포도": {"가능": "불가", "주의": "신장 손상 가능성, 원인 불명이라 완전 금지"},
        "초콜릿": {"가능": "불가", "주의": "카카오 성분 독성, 소량도 위험"},
        "사과": {"가능": "과육은 극소량 간식으로 가능", "주의": "씨·심은 제거해야 함"},
    }


# -----------------------------
# 유틸 함수
# -----------------------------
def add_record(rec: dict):
    st.session_state.records.append(rec)


def get_records_df():
    if not st.session_state.records:
        return pd.DataFrame()
    return pd.DataFrame(st.session_state.records)


# -----------------------------
# 페이지 1. 건강 기록
# -----------------------------
def page_health_log():
    st.title("📒 건강 기록")

    st.write("버튼/선택 위주로 **간단하게** 오늘 상태를 기록하는 화면이에요.")

    col1, col2 = st.columns(2)

    with col1:
        rec_date = st.date_input("기록 날짜", value=date.today())
        meal = st.radio("🍽 식사량", ["거의 안 먹음", "평소보다 적게", "평소와 비슷", "평소보다 많이"], index=2)
        water = st.radio("💧 음수량", ["거의 안 마심", "평소보다 적게", "평소와 비슷", "평소보다 많이"], index=2)
        poop = st.radio("💩 배변 상태", ["정상", "단단함", "무름/설사", "혈변/검은 변", "안 봄"], index=0)

    with col2:
        activity = st.radio(
            "🏃 활동 및 행동",
            ["평소와 비슷", "잠이 많아짐", "활동이 줄어듦", "예민/공격적", "숨는 시간이 많음"],
            index=0,
        )
        symptoms = st.multiselect(
            "⚠️ 이상 증세",
            ["구토", "기침/헐떡임", "기침 없음", "다리를 절음", "눈/코 분비물", "가려움/과도한 그루밍", "기타"],
        )
        memo = st.text_area("📝 특이사항 메모 (선택)", placeholder="평소와 달랐던 점, 먹은 간식, 환경 변화 등")

    if st.button("기록 저장"):
        rec = {
            "날짜": rec_date,
            "식사량": meal,
            "음수량": water,
            "배변": poop,
            "행동": activity,
            "이상증세": ", ".join(symptoms) if symptoms else "",
            "메모": memo,
        }
        add_record(rec)
        st.success("기록이 저장되었습니다.")

    st.markdown("---")
    st.subheader("📚 최근 기록 목록")

    df = get_records_df()
    if df.empty:
        st.info("아직 기록이 없습니다.")
    else:
        st.dataframe(df.tail(10), use_container_width=True)


# -----------------------------
# 페이지 2. AI 진단 (간단 룰 기반)
# -----------------------------
def page_ai_diagnosis():
    st.title("📊 AI 진단 (프로토타입)")

    df = get_records_df()
    if df.empty:
        st.info("진단을 위해 최소 1개 이상의 기록이 필요합니다.")
        return

    st.write("최근 기록을 바탕으로 **식욕·음수량·배변·행동 변화**를 간단하게 분석한 결과예요.")

    # 최근 7개 기록 기준
    recent = df.tail(7)

    warnings = []
    notes = []

    # 식사량 분석
    low_meal_days = (recent["식사량"].isin(["거의 안 먹음", "평소보다 적게"])).sum()
    if low_meal_days >= 2:
        warnings.append("최근 며칠간 식사량이 평소보다 적게 기록된 날이 여러 번 있어요.")
        notes.append("24시간 이상 거의 먹지 않으면 병원 상담을 권장해요.")

    # 음수량 분석
    low_water_days = (recent["음수량"].isin(["거의 안 마심", "평소보다 적게"])).sum()
    if low_water_days >= 2:
        warnings.append("물 섭취가 적게 기록된 날이 반복되고 있어요.")
        notes.append("방광염·요로계 문제의 초기 신호일 수 있으니 주의 깊게 관찰하세요.")

    # 배변 분석
    bad_poop_days = (recent["배변"].isin(["무름/설사", "혈변/검은 변", "안 봄"])).sum()
    if bad_poop_days >= 2:
        warnings.append("배변 상태가 ‘설사/혈변/안 봄’으로 기록된 날이 많아요.")
        notes.append("3일 이상 지속되면 변 사진을 가져가 병원 진료를 받는 것이 좋아요.")

    # 행동 분석
    low_activity_days = (recent["행동"].isin(["잠이 많아짐", "활동이 줄어듦", "숨는 시간이 많음"])).sum()
    if low_activity_days >= 2:
        warnings.append("무기력하거나 숨어 지내는 날이 여러 번 기록됐어요.")
        notes.append("무기력 + 식욕 감소가 같이 있으면 더 위험 신호일 수 있어요.")

    # 이상 증세 카운트
    if "이상증세" in recent.columns:
        vomit_days = recent["이상증세"].str.contains("구토", na=False).sum()
        if vomit_days >= 2:
            warnings.append("일주일 안에 ‘구토’가 여러 번 기록됐어요.")
            notes.append("헤어볼, 사료, 장 문제 등 원인이 다양하니 영상·사진을 남겨 두면 도움이 돼요.")

    if not warnings:
        st.success("최근 기록에서 뚜렷한 위험 신호는 크게 보이지 않습니다.")
        st.write("그래도 **작은 변화가 쌓여서 이상으로 이어질 수 있으니** 꾸준히 기록해 주세요.")
    else:
        st.subheader("⚠️ 주의가 필요한 변화")
        for w in warnings:
            st.warning(w)

    if notes:
        st.subheader("💡 참고하면 좋은 팁")
        for n in notes:
            st.write("- " + n)

    st.markdown("---")
    with st.expander("최근 7개 기록 다시 보기"):
        st.dataframe(recent, use_container_width=True)


# -----------------------------
# 페이지 3. 집사 가이드
# -----------------------------
def page_guide():
    st.title("📚 집사 가이드")

    st.write("고양이 집사가 자주 궁금해하는 내용을 모아둔 **지식 아카이브**입니다.")

    sections = {
        "응급처치 기본": [
            "호흡 곤란, 반복 구토, 혈변/혈뇨, 경련 등의 증상이 보이면 지체하지 말고 병원으로 이동하세요.",
            "응급 상황에서는 ‘사람 약’이나 인터넷 민간요법을 시도하지 말고, 상태를 기록(영상/사진)하는 것이 도움됩니다.",
        ],
        "약 먹이기": [
            "가능하면 고양이 전용 처방약, 약 먹이기 보조 간식(필 포켓 등)을 활용하세요.",
            "알약은 목 깊숙이 넣기보다는 혀 뒤편에 두고, 고개를 살짝 숙인 상태에서 삼키는지 확인합니다.",
            "가루약은 평소 좋아하는 습식/간식에 극소량 섞어 반응을 본 뒤 양을 조정합니다.",
        ],
        "모래 관리": [
            "하루 1~2회는 반드시 배변 상태를 확인하고, 배변 패턴이 갑자기 바뀌지 않았는지 살핍니다.",
            "화장실 수는 ‘고양이 수 + 1개’가 이상적이며, 조용하고 접근이 쉬운 곳에 두는 것이 좋습니다.",
        ],
        "사료 선택": [
            "연령, 체중, 중성화 여부, 질환(비만, 비뇨기계 등)에 맞는 사료를 선택해야 합니다.",
            "갑작스러운 사료 변경은 설사를 유발할 수 있으므로 1~2주에 걸쳐 서서히 바꾸는 것이 좋습니다.",
        ],
        "격리/적응": [
            "새 고양이를 들일 때는 최소 며칠간 방을 나누어 냄새와 소리에 먼저 적응시키고, 점진적으로 대면합니다.",
        ],
        "목욕": [
            "필요한 경우에만 짧게, 미끄럽지 않은 환경에서 하고, 반드시 고양이 전용 샴푸를 사용합니다.",
        ],
        "대표 질병 징후": [
            "방광염/요로계: 화장실을 자주 들락날락, 소변 양 적음, 혈뇨, 배 만질 때 통증 호소.",
            "장 문제: 장기간 설사, 토, 식욕 저하, 체중 감소.",
        ],
        "헤어볼 관리": [
            "장모종은 정기적인 빗질과 헤어볼 케어 간식/사료를 활용하면 도움이 됩니다.",
        ],
        "사냥놀이 팁": [
            "레이저 포인터만 지속적으로 사용하면 좌절감을 줄 수 있으므로, 실제 잡을 수 있는 장난감도 함께 사용하세요.",
        ],
    }

    for title, lines in sections.items():
        with st.expander(title):
            for line in lines:
                st.write("- " + line)


# -----------------------------
# 페이지 4. AI 응급처치
# -----------------------------
def page_ai_emergency():
    st.title("🚑 AI 응급처치 (프로토타입)")

    st.write("현재 상태를 선택하면 **기본 응급조치 가이드**를 보여줍니다. (실제 진료를 대체하지 않습니다.)")

    main_symptom = st.selectbox(
        "주요 증상",
        ["선택하세요", "반복 구토", "설사/혈변", "호흡 곤란", "갑작스러운 무기력", "외상/출혈", "기타"],
    )
    duration = st.selectbox(
        "증상이 지속된 시간",
        ["선택하세요", "1시간 이내", "수 시간 정도", "하루 이상", "3일 이상"],
    )
    region = st.text_input("거주 동네(동/구) (예: 강남구, ○○동) - 병원 안내 예시용", "")

    if st.button("응급 조치 가이드 보기"):
        if main_symptom == "선택하세요":
            st.warning("먼저 주요 증상을 선택해 주세요.")
            return

        # 간단 룰 기반 안내
        if main_symptom == "반복 구토":
            st.subheader("📌 예상 가능 질환·상황 (예시)")
            st.write("- 헤어볼, 급격한 사료 변경, 이물 섭취, 위장 장애 등")
            st.subheader("🩺 기본 응급조치")
            st.write("- 사료와 물을 잠시 치우고, 구토 횟수와 시간 간격을 기록합니다.")
            st.write("- 토한 내용물(사료, 이물, 거품 등)을 사진으로 남겨 두면 진료에 도움이 됩니다.")
            if duration in ["하루 이상", "3일 이상"]:
                st.error("하루 이상 구토가 지속되면 지체 없이 병원 진료가 필요합니다.")

        elif main_symptom == "설사/혈변":
            st.subheader("📌 예상 가능 질환·상황 (예시)")
            st.write("- 급격한 사료 변경, 장염, 기생충, 알레르기 등")
            st.subheader("🩺 기본 응급조치")
            st.write("- 사람용 지사제는 절대 사용하지 말고, 수분 공급 상태를 관찰하세요.")
            st.write("- 변의 색, 형태, 횟수를 기록하고 사진을 남겨 두는 것이 좋습니다.")
            if "혈" in main_symptom or duration in ["하루 이상", "3일 이상"]:
                st.error("혈변이 보이거나 설사가 오래 지속되면 병원 진료를 권장합니다.")

        elif main_symptom == "호흡 곤란":
            st.subheader("📌 매우 위급한 상황일 수 있습니다.")
            st.write("- 혀·잇몸이 파랗게 보이거나, 입을 벌리고 심하게 호흡하는 경우 즉시 병원 이동이 필요합니다.")
            st.subheader("🩺 기본 응급조치")
            st.write("- 이동 중에도 고양이를 과하게 자극하지 말고, 편안한 자세를 유지시켜 주세요.")
            st.error("호흡 곤란은 지체 없이 24시간 응급 동물병원을 찾아야 하는 상황입니다.")

        elif main_symptom == "갑작스러운 무기력":
            st.subheader("📌 예상 가능 질환·상황 (예시)")
            st.write("- 고열, 통증, 심혈관/호흡기 문제, 중독 등")
            st.subheader("🩺 기본 응급조치")
            st.write("- 체온이 너무 뜨겁거나 차갑지 않은지, 잇몸 색이 창백하지 않은지 확인하세요.")
            st.write("- 먹지 않고, 움직이려 하지 않고, 숨소리가 이상하면 즉시 병원 권장입니다.")

        elif main_symptom == "외상/출혈":
            st.subheader("📌 기본 응급조치")
            st.write("- 거즈나 깨끗한 천으로 출혈 부위를 부드럽게 압박해 지혈을 시도합니다.")
            st.write("- 상처 부위를 핥지 못하도록 하고, 필요 시 넥카라를 사용합니다.")
            st.error("큰 출혈, 절뚝거림, 통증 반응이 있으면 바로 병원으로 이동하세요.")

        else:
            st.write("증상이 애매하거나 여러 개일 경우, 사진·영상 기록을 남기고 가능한 빨리 병원과 상담하는 것이 가장 안전합니다.")

        if region.strip():
            st.markdown("---")
            st.subheader("📍 근처 동물병원 (예시)")
            st.write(f"- {region} 24시 동물의료센터 (예시)")
            st.write(f"- {region} 동물병원 (예시)")
            st.info("실제 서비스에서는 지도 API와 연동해 현재 위치 기준 병원을 보여줄 수 있습니다.")


# -----------------------------
# 페이지 5. 음식 사전
# -----------------------------
def page_food_dict():
    st.title("🍙 음식 사전")

    food_db = st.session_state.food_db

    query = st.text_input("사람 음식 이름을 입력하세요 (예: 양파, 사과, 초콜릿)")
    if st.button("검색"):
        q = query.strip()
        if not q:
            st.warning("먼저 음식 이름을 입력해 주세요.")
        elif q in food_db:
            info = food_db[q]
            if info["가능"] == "불가":
                st.error(f"❌ {q} : 고양이에게 **절대 급여하면 안 되는 음식**입니다.")
            else:
                st.success(f"⭕ {q} : '{info['가능']}'")
            st.write("ℹ️ 주의사항:")
            st.write("- " + info["주의"])
        else:
            st.warning(f"'{q}' 에 대한 데이터가 없습니다.")
            st.write("반드시 **수의사나 신뢰 가능한 자료**를 통해 안전 여부를 확인하세요.")

    with st.expander("예시로 등록된 음식 목록 보기"):
        st.write(list(food_db.keys()))


# -----------------------------
# 페이지 6. 마켓 (간단 추천)
# -----------------------------
def page_market():
    st.title("🛍️ 묘멘트 마켓 (프로토타입)")

    df = get_records_df()
    st.write("최근 건강 기록을 바탕으로 **사료/간식 타입을 간단히 추천**하는 예시 화면이에요.")

    if df.empty:
        st.info("먼저 ‘건강 기록’에서 몇 가지 기록을 남기면 더 맞는 추천이 가능합니다.")
        base_state = "정보 부족"
    else:
        last = df.iloc[-1]
        base_state = "전반적 양호"

        if last["배변"] in ["무름/설사", "혈변/검은 변"]:
            base_state = "민감한 장"
        elif last["음수량"] in ["거의 안 마심", "평소보다 적게"]:
            base_state = "수분 섭취 부족"
        elif last["식사량"] in ["거의 안 먹음", "평소보다 적게"]:
            base_state = "식욕 저하"

    st.subheader("현재 상태 요약 (단순 추정)")
    st.write(f"- 상태: **{base_state}**")

    st.subheader("추천 사료/간식 타입 (예시)")
    if base_state == "민감한 장":
        st.write("- 💡 장 건강용 저자극 사료")
        st.write("- 💡 소화가 잘 되는 습식 위주의 식단")
        st.write("- 💡 유산균/장 건강 보조 간식")
    elif base_state == "수분 섭취 부족":
        st.write("- 💡 수분 함량이 높은 습식 사료")
        st.write("- 💡 물 섭취를 유도하는 국물 간식")
        st.write("- 💡 정수기형 급수기 사용 권장")
    elif base_state == "식욕 저하":
        st.write("- 💡 향이 강한 습식/츄르 기반 보조")
        st.write("- 💡 소량씩 자주 급여 가능한 사료")
    else:
        st.write("- 💡 연령/중성화 상태에 맞춘 균형형 사료")
        st.write("- 💡 칼로리 과다하지 않은 간식 위주")

    st.info("실제 서비스에서는 쇼핑몰/브랜드 정보와 연동해 구체적인 상품까지 추천할 수 있습니다.")


# -----------------------------
# 라우팅
# -----------------------------
menu = st.sidebar.radio(
    "메뉴",
    ["홈", "건강 기록", "AI 진단", "집사 가이드", "AI 응급처치", "음식 사전", "마켓"],
)

if menu == "홈":
    st.title("🐱 묘멘트")
    st.write("고양이의 일상 건강을 기록하고, 작은 변화를 감지해 주는 집사용 케어 웹앱입니다.")
    st.write("- 왼쪽 사이드바에서 기능을 선택해 보세요.")
elif menu == "건강 기록":
    page_health_log()
elif menu == "AI 진단":
    page_ai_diagnosis()
elif menu == "집사 가이드":
    page_guide()
elif menu == "AI 응급처치":
    page_ai_emergency()
elif menu == "음식 사전":
    page_food_dict()
elif menu == "마켓":
    page_market()
