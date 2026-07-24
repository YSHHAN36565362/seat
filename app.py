import streamlit as st
import random
import os
import re

# =========================================================================
# 1. 페이지 기본 설정
# =========================================================================
st.set_page_config(page_title="랜덤 자리 배치 (블랙리스트 버전)", layout="wide")


# =========================================================================
# 2. 세션 상태(session_state) 초기화
# -------------------------------------------------------------------------
# Streamlit은 버튼을 누를 때마다 파일 전체를 위에서 아래로 다시 실행합니다.
# 그래서 "다시 실행돼도 사라지면 안 되는 값"들은 st.session_state에 저장해야 합니다.
# =========================================================================

# 각 줄(행)에 몇 쌍(짝꿍)이 앉는지 저장하는 리스트입니다. 예: [4, 4, 3] = 1행 4쌍, 2행 4쌍, 3행 3쌍
if "row_pairs" not in st.session_state:
    st.session_state.row_pairs = [4, 4, 3]

# 총 자리 수는 쌍 수 * 2명 입니다.
total_seats = sum(st.session_state.row_pairs) * 2

# 자리 배열입니다. 처음엔 전부 "(빈자리)"로 채워둡니다.
if "seats" not in st.session_state or len(st.session_state.seats) != total_seats:
    st.session_state.seats = ["(빈자리)"] * total_seats

# [핵심] 물리적으로 아무도 앉을 수 없는 자리 번호들을 저장하는 집합(set)입니다.
if "disabled_seats" not in st.session_state:
    st.session_state.disabled_seats = set()

# [핵심] 특정 사람이 앉을 수 없는 자리를 저장하는 딕셔너리입니다.
# 형태: {"홍길동": {2, 5, 9}} -> 홍길동은 2,5,9번 자리에 못 앉음
if "forbidden_seats_map" not in st.session_state:
    st.session_state.forbidden_seats_map = {}

# 마지막으로 실행한 배치 결과(자리번호 -> 이름)를 저장합니다.
if "last_assignment_result" not in st.session_state:
    st.session_state.last_assignment_result = {}

# 배치에 실패한 사람들(자리가 전부 막혀서 못 앉은 사람)을 저장합니다.
if "last_failed_names" not in st.session_state:
    st.session_state.last_failed_names = []


# =========================================================================
# 3. [단일 책임] 이름 텍스트 처리 관련 함수들
# =========================================================================

def format_names_with_numbers(text: str) -> str:
    lines = [line for line in text.split('\n') if line.strip()]
    cleaned_lines = [re.sub(r'^\d+[\.\)\]\s]+', '', line.strip()) for line in lines]
    numbered_lines = [f"{i + 1}. {name}" for i, name in enumerate(cleaned_lines)]
    return '\n'.join(numbered_lines)


def parse_names_from_raw_text(raw_text: str) -> list:
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    names = [re.sub(r'^\d+[\.\)\]\s]+', '', line) for line in lines]
    return names


def on_text_area_change():
    if "names_textarea" in st.session_state:
        st.session_state["names_textarea"] = format_names_with_numbers(st.session_state["names_textarea"])


def load_names_from_txt_file(file_name: str):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = format_names_with_numbers(f.read())
    else:
        st.sidebar.error(f"같은 폴더에 {file_name} 파일이 없습니다.")


def shuffle_names_in_textarea():
    if "names_textarea" in st.session_state:
        raw_text = st.session_state["names_textarea"]
        names = parse_names_from_raw_text(raw_text)
        random.shuffle(names)
        numbered_lines = [f"{i + 1}. {name}" for i, name in enumerate(names)]
        st.session_state["names_textarea"] = '\n'.join(numbered_lines)


# =========================================================================
# 4. [단일 책임] 자리(좌석) 구조 관련 함수들
# =========================================================================

def get_all_seat_ids(row_pairs: list) -> list:
    total = sum(row_pairs) * 2
    return list(range(total))


def get_active_seat_ids(all_seat_ids: list, disabled_seats: set) -> list:
    # 물리적으로 비활성화된 자리를 제외한, 실제로 사용 가능한 자리 목록입니다.
    return [seat_id for seat_id in all_seat_ids if seat_id not in disabled_seats]


# =========================================================================
# 5. [단일 책임] 제약 조건(블랙리스트) 계산 함수
# =========================================================================

def get_assignable_seats_for_person(person_name: str, currently_empty_seats: list, forbidden_seats_map: dict) -> list:
    person_forbidden = forbidden_seats_map.get(person_name, set())
    return [seat_id for seat_id in currently_empty_seats if seat_id not in person_forbidden]


# =========================================================================
# 6. [단일 책임] 랜덤 배치 실행 함수 (핵심 비즈니스 로직)
# =========================================================================

def run_single_random_assignment(people_names: list, all_seat_ids: list, disabled_seats: set, forbidden_seats_map: dict):
    empty_seats = set(get_active_seat_ids(all_seat_ids, disabled_seats))
    seat_to_name = {}
    failed_names = []

    # MRV(최소 잔여값) 휴리스틱: 앉을 수 있는 자리가 적은 사람일수록 먼저 배치합니다.
    people_with_seat_counts = []
    for name in people_names:
        assignable = get_assignable_seats_for_person(name, list(empty_seats), forbidden_seats_map)
        people_with_seat_counts.append((name, len(assignable)))

    people_with_seat_counts.sort(key=lambda pair: pair[1])
    sorted_people = [pair[0] for pair in people_with_seat_counts]

    for name in sorted_people:
        candidate_seats = get_assignable_seats_for_person(name, list(empty_seats), forbidden_seats_map)
        if candidate_seats:
            chosen_seat = random.choice(candidate_seats)
            seat_to_name[chosen_seat] = name
            empty_seats.remove(chosen_seat)
        else:
            failed_names.append(name)

    return seat_to_name, failed_names


# =========================================================================
# 7. [단일 책임] 화면(UI)을 그리는 함수들
# =========================================================================

def render_name_input_sidebar():
    st.sidebar.title("이름 명단 입력")
    st.sidebar.write(f"총 {total_seats}석 중 물리적으로 비활성화된 자리를 제외하고 배치됩니다.")

    st.sidebar.button("불러오기 (students.txt)", on_click=load_names_from_txt_file, args=("students.txt",))
    st.sidebar.button("불러오기 (example.txt)", on_click=load_names_from_txt_file, args=("example.txt",))
    st.sidebar.button("명단 순서 랜덤 섞기", on_click=shuffle_names_in_textarea)

    st.sidebar.text_area("명단 (한 줄에 한 명씩)", height=280, key="names_textarea", on_change=on_text_area_change)


def render_front_illustration():
    # [기존 구조 유지] 칠판과 TV 이미지를 화면 상단에 그대로 보여주는 부분입니다.
    front_cols = st.columns([1, 2, 1, 1.5])

    with front_cols[1]:
        st.markdown(
            "<div style='text-align: center;'>"
            "<img src='https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi4I4zFnoGWku6HlvRHMoq5lU_eTEQR51_U0Uc1aDC9yom6QiLmTHPwulXQcQ0-FbCR_OFSLLwX-qdM29tW-1nnom99XsEPOvdLezDdZXE27Qqj2Y4TMC2JbL1e7njxi5UX1iNyA9b93M8C/w1200-h630-p-k-no-nu/school_class_woman_aseru.png' style='width: 50%;'>"
            "<br><span style='color: gray; font-size: 14px;'>칠판</span></div>",
            unsafe_allow_html=True
        )

    with front_cols[2]:
        st.markdown(
            "<div style='text-align: center;'>"
            "<img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ_DZA5M8KH80YmEcHxZxumZnYGPyDQNcD0fkFQe3Q39zmtrho&s' style='width: 50%;'>"
            "<br><span style='color: gray; font-size: 14px;'>TV</span></div>",
            unsafe_allow_html=True
        )

    return front_cols


def render_seat_board(seat_to_name: dict, disabled_seats: set, row_pairs: list, highlight_forbidden: set = None):
    """
    좌석 배치도를 그려주는 공용 함수입니다.
    - seat_to_name: 배치 결과를 보여줄 때 사용 (없으면 빈 딕셔너리 전달)
    - disabled_seats: 물리적으로 비활성화된 자리 (회색 '사용불가' 표시)
    - highlight_forbidden: 특정 인원의 금지 자리 설정 화면에서, 그 사람이 못 앉는 자리를 빨간색으로 강조 표시할 때 사용
    """
    if highlight_forbidden is None:
        highlight_forbidden = set()

    start_idx = 0
    for row_index, pair_count in enumerate(row_pairs):
        st.markdown(f"**{row_index + 1}행**")
        col_ratios = []
        for i in range(pair_count):
            col_ratios.append(2)
            if i < pair_count - 1:
                col_ratios.append(0.5)
        cols = st.columns(col_ratios)

        for i in range(pair_count):
            target_col = cols[i * 2]
            with target_col.container(border=True):
                inner_cols = st.columns(2)
                seat_ids = [start_idx + i * 2, start_idx + i * 2 + 1]

                for local_idx, seat_id in enumerate(seat_ids):
                    with inner_cols[local_idx]:
                        if seat_id in disabled_seats:
                            # 물리적으로 사용 불가능한 자리는 회색 배경으로 표시합니다.
                            st.markdown(
                                "<div style='text-align:center; color:#999; background-color:#eee; "
                                "padding:15px 0; border-radius:4px;'>사용불가</div>",
                                unsafe_allow_html=True
                            )
                        elif seat_id in highlight_forbidden:
                            # 지금 설정 중인 사람이 못 앉는 자리는 빨간색으로 강조합니다.
                            st.markdown(
                                "<div style='text-align:center; color:#c62828; background-color:#ffebee; "
                                "padding:15px 0; border-radius:4px;'>금지</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            occupant = seat_to_name.get(seat_id, "(빈자리)")
                            st.markdown(
                                f"<div style='text-align:center; padding:15px 0;'>{occupant}</div>",
                                unsafe_allow_html=True
                            )
                        st.markdown(
                            f"<div style='text-align:center; font-size:11px; color:#888;'>#{seat_id + 1}</div>",
                            unsafe_allow_html=True
                        )
        start_idx += pair_count * 2


# =========================================================================
# 8. 메인 화면 구성
# =========================================================================

render_name_input_sidebar()

names_input = st.session_state.get("names_textarea", "")
current_names = parse_names_from_raw_text(names_input)
all_seat_ids = get_all_seat_ids(st.session_state.row_pairs)

st.sidebar.write("---")
if len(current_names) <= total_seats:
    st.sidebar.success(f"입력된 인원: {len(current_names)}명 / 총 {total_seats}석")
else:
    st.sidebar.error(f"입력 인원({len(current_names)}명)이 총 자릿수({total_seats}석)보다 많습니다.")

menu = st.sidebar.radio("작업 선택", ["자리 배치 실행", "자리 구조/비활성 자리 설정", "인원별 금지 자리 설정"])

title_col, config_col = st.columns([7, 3])
with title_col:
    st.title("랜덤 자리 배치 프로그램 (블랙리스트 방식)")

with config_col:
    with st.expander("자리 배치 설정 (클릭)"):
        st.write("각 줄에 몇 쌍(2명=1쌍)이 앉을지 수정할 수 있습니다.")
        temp_rows = st.number_input("총 행(가로줄) 개수", min_value=1, max_value=10, value=len(st.session_state.row_pairs))
        temp_pairs = []
        for i in range(temp_rows):
            default_val = st.session_state.row_pairs[i] if i < len(st.session_state.row_pairs) else 4
            val = st.number_input(f"{i + 1}행 짝꿍 수", min_value=1, max_value=10, value=default_val, key=f"row_input_{i}")
            temp_pairs.append(val)

        if st.button("설정 적용 및 초기화"):
            st.session_state.row_pairs = temp_pairs
            new_total = sum(temp_pairs) * 2
            st.session_state.seats = ["(빈자리)"] * new_total
            st.session_state.disabled_seats = set()
            st.session_state.forbidden_seats_map = {}
            st.session_state.last_assignment_result = {}
            st.session_state.last_failed_names = []
            st.rerun()

# [기존 구조 유지] 칠판/TV 이미지는 항상 상단에 표시됩니다.
render_front_illustration()

st.write("---")

if menu == "자리 배치 실행":
    st.write("아래 버튼을 누르면 금지 자리와 비활성 자리를 모두 반영해서 단 한 번 무작위로 배치합니다.")

    if st.button("전체 랜덤 배치 실행", type="primary"):
        if len(current_names) == 0:
            st.warning("먼저 사이드바에서 이름 명단을 입력해주세요.")
        else:
            seat_to_name, failed_names = run_single_random_assignment(
                current_names,
                all_seat_ids,
                st.session_state.disabled_seats,
                st.session_state.forbidden_seats_map
            )
            st.session_state.last_assignment_result = seat_to_name
            st.session_state.last_failed_names = failed_names

            if failed_names:
                st.error(f"금지 자리 조건 때문에 배치 못 한 인원: {', '.join(failed_names)}")
            else:
                st.success("전원이 조건에 맞게 배치되었습니다!")

    st.write("---")
    render_seat_board(
        st.session_state.last_assignment_result,
        st.session_state.disabled_seats,
        st.session_state.row_pairs
    )

elif menu == "자리 구조/비활성 자리 설정":
    st.write("물리적으로 아무도 앉을 수 없는 자리를 지정합니다. 아래 배치도를 보면서 선택하세요.")

    seat_options = all_seat_ids
    seat_label_map = {s: f"{s + 1}번" for s in seat_options}

    chosen_disabled = st.multiselect(
        "비활성 처리할 자리",
        options=seat_options,
        default=list(st.session_state.disabled_seats),
        format_func=lambda s: seat_label_map[s],
        key="disabled_seat_selector"
    )

    if st.button("비활성 자리 저장"):
        st.session_state.disabled_seats = set(chosen_disabled)
        st.success(f"{len(chosen_disabled)}개의 자리가 사용 불가로 설정되었습니다.")
        st.rerun()

    st.write("---")
    st.write("현재 좌석 구조 (회색 '사용불가'가 지금 선택된 비활성 자리입니다)")
    # 저장 버튼을 누르기 전, 실시간으로 고르고 있는 자리도 바로 배치도에 반영해서 보여줍니다.
    render_seat_board({}, set(chosen_disabled), st.session_state.row_pairs)

else:
    st.write("특정 인원이 앉을 수 없는 자리를 지정합니다. (여기서 선택한 자리에는 절대 앉지 않습니다)")

    if not current_names:
        st.info("먼저 사이드바에서 명단을 입력해주세요.")
    else:
        unique_names = sorted(set(current_names))
        target_name = st.selectbox("금지 자리를 설정할 사람", unique_names, key="forbidden_target_select")

        # 이미 물리적으로 비활성화된 자리는 선택 대상에서 뺍니다. (중복 관리 방지)
        available_for_selection = [s for s in all_seat_ids if s not in st.session_state.disabled_seats]
        seat_label_map = {s: f"{s + 1}번" for s in available_for_selection}

        current_forbidden = list(st.session_state.forbidden_seats_map.get(target_name, set()))

        # [요청 기능] "모두 선택" 버튼: 이 사람이 모든 자리에 앉지 못하도록 한 번에 전체를 금지 처리합니다.
        def select_all_forbidden_for_target():
            st.session_state[f"forbidden_multiselect_{target_name}"] = list(available_for_selection)

        def clear_all_forbidden_for_target():
            st.session_state[f"forbidden_multiselect_{target_name}"] = []

        col_select_all, col_clear_all = st.columns(2)
        with col_select_all:
            st.button("이 사람 - 모든 자리 금지 선택", on_click=select_all_forbidden_for_target)
        with col_clear_all:
            st.button("이 사람 - 금지 선택 전체 해제", on_click=clear_all_forbidden_for_target)

        chosen_forbidden = st.multiselect(
            "이 사람이 앉을 수 없는 자리",
            options=available_for_selection,
            default=current_forbidden,
            format_func=lambda s: seat_label_map[s],
            key=f"forbidden_multiselect_{target_name}"
        )

        st.write("---")
        st.write(f"현재 좌석 구조 (빨간색 '금지'가 '{target_name}'님이 지금 선택 중인 금지 자리입니다)")
        # 저장 전에도 실시간으로 선택 중인 금지 자리를 배치도에 바로 반영해서 보여줍니다.
        render_seat_board(
            {},
            st.session_state.disabled_seats,
            st.session_state.row_pairs,
            highlight_forbidden=set(chosen_forbidden)
        )

        st.write("---")
        if st.button("금지 자리 저장"):
            st.session_state.forbidden_seats_map[target_name] = set(chosen_forbidden)
            st.success(f"'{target_name}'님은 이제 {len(chosen_forbidden)}개 자리에 앉을 수 없습니다.")
            st.rerun()

        if st.button(f"'{target_name}' 금지 조건 완전히 삭제"):
            if target_name in st.session_state.forbidden_seats_map:
                del st.session_state.forbidden_seats_map[target_name]
                st.success(f"'{target_name}'님의 금지 조건이 삭제되었습니다.")
            st.rerun()

        st.write("---")
        st.subheader("현재 등록된 금지 조건 목록")
        if st.session_state.forbidden_seats_map:
            for name, seats in st.session_state.forbidden_seats_map.items():
                if seats:
                    seat_display = ", ".join([str(s + 1) for s in sorted(seats)])
                    st.write(f"- **{name}**: {seat_display}번 자리 금지")
        else:
            st.write("등록된 금지 조건이 없습니다.")
