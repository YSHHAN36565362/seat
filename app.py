import streamlit as st
import random
import os
import re

# =========================================================================
# 1. 페이지 기본 설정
# =========================================================================
# 브라우저 탭 제목과 화면을 넓게 쓰도록 설정합니다.
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
# 예: 기둥에 가려진 자리, 고장 난 의자 등 - 모든 사람에게 공통으로 적용됩니다.
if "disabled_seats" not in st.session_state:
    st.session_state.disabled_seats = set()

# [핵심] 특정 사람이 앉을 수 없는 자리를 저장하는 딕셔너리입니다.
# 형태: {"홍길동": {2, 5, 9}, "김철수": {0, 1}} -> 홍길동은 2,5,9번 자리에 못 앉음
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
# -------------------------------------------------------------------------
# 이 함수들은 "텍스트 문자열을 다루는 일"만 담당합니다.
# =========================================================================

def format_names_with_numbers(text: str) -> str:
    # 빈 줄은 걸러내고, 줄 앞의 "1. " 같은 기존 번호를 지운 뒤 새로 번호를 붙입니다.
    lines = [line for line in text.split('\n') if line.strip()]
    cleaned_lines = [re.sub(r'^\d+[\.\)\]\s]+', '', line.strip()) for line in lines]
    numbered_lines = [f"{i + 1}. {name}" for i, name in enumerate(cleaned_lines)]
    return '\n'.join(numbered_lines)


def parse_names_from_raw_text(raw_text: str) -> list:
    # 텍스트를 줄 단위로 나누고, 앞의 번호(1. 2. 등)를 제거해서 순수 이름 리스트만 반환합니다.
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    names = [re.sub(r'^\d+[\.\)\]\s]+', '', line) for line in lines]
    return names


def on_text_area_change():
    # 사용자가 이름 입력창을 수정하고 다른 곳을 클릭하면 자동으로 번호를 다시 매깁니다.
    if "names_textarea" in st.session_state:
        st.session_state["names_textarea"] = format_names_with_numbers(st.session_state["names_textarea"])


def load_names_from_txt_file(file_name: str):
    # 지정한 txt 파일을 읽어서 이름 입력창에 넣어줍니다. 파일이 없으면 오류 메시지를 보여줍니다.
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = format_names_with_numbers(f.read())
    else:
        st.sidebar.error(f"같은 폴더에 {file_name} 파일이 없습니다.")


def shuffle_names_in_textarea():
    # 입력창에 있는 이름들의 순서만 무작위로 섞습니다. (자리 배치가 아니라 명단 순서 섞기 용도)
    if "names_textarea" in st.session_state:
        raw_text = st.session_state["names_textarea"]
        names = parse_names_from_raw_text(raw_text)
        random.shuffle(names)
        numbered_lines = [f"{i + 1}. {name}" for i, name in enumerate(names)]
        st.session_state["names_textarea"] = '\n'.join(numbered_lines)


# =========================================================================
# 4. [단일 책임] 자리(좌석) 구조 관련 함수들
# -------------------------------------------------------------------------
# 이 함수들은 "자리 번호와 자리 배치 구조를 계산하는 일"만 담당합니다.
# =========================================================================

def get_all_seat_ids(row_pairs: list) -> list:
    # row_pairs = [4, 4, 3] 이면 총 자리 번호 0번부터 (합계*2 - 1)번까지 리스트를 만듭니다.
    total = sum(row_pairs) * 2
    return list(range(total))


def get_active_seat_ids(all_seat_ids: list, disabled_seats: set) -> list:
    # 물리적으로 비활성화(고장/사용불가) 처리된 자리를 제외한, 실제로 사용 가능한 자리 목록입니다.
    return [seat_id for seat_id in all_seat_ids if seat_id not in disabled_seats]


# =========================================================================
# 5. [단일 책임] 제약 조건(블랙리스트) 계산 함수
# -------------------------------------------------------------------------
# 이 함수는 "이 사람이 앉을 수 있는 자리가 몇 개인지 계산하는 일"만 담당합니다.
# =========================================================================

def get_assignable_seats_for_person(
    person_name: str,
    currently_empty_seats: list,
    forbidden_seats_map: dict
) -> list:
    # 이 사람의 개인 금지 자리 목록을 가져옵니다. 없으면 빈 집합을 사용합니다.
    person_forbidden = forbidden_seats_map.get(person_name, set())
    # "현재 비어있는 자리" 중에서, "이 사람이 금지된 자리"가 아닌 자리만 남깁니다.
    return [seat_id for seat_id in currently_empty_seats if seat_id not in person_forbidden]


# =========================================================================
# 6. [단일 책임] 랜덤 배치 실행 함수 (핵심 비즈니스 로직)
# -------------------------------------------------------------------------
# 이 함수는 오직 "누구를 어느 자리에 앉힐지 계산하는 일"만 담당하고,
# 화면을 그리거나 파일을 읽는 등의 다른 일은 절대 하지 않습니다. (단일 책임 원칙)
# =========================================================================

def run_single_random_assignment(
    people_names: list,
    all_seat_ids: list,
    disabled_seats: set,
    forbidden_seats_map: dict
):
    # 물리적으로 막힌 자리를 뺀, 실제로 앉을 수 있는 전체 빈 자리 목록을 만듭니다.
    empty_seats = set(get_active_seat_ids(all_seat_ids, disabled_seats))

    # 최종 결과를 담을 딕셔너리입니다. {자리번호: 이름}
    seat_to_name = {}
    # 자리가 부족해서 끝내 배치 못 한 사람 이름을 담을 리스트입니다.
    failed_names = []

    # ---------------------------------------------------------------
    # MRV(최소 잔여값) 휴리스틱: 앉을 수 있는 자리가 적은 사람일수록
    # 먼저 배치해야 나중에 "자리가 없어서 못 앉는" 상황을 줄일 수 있습니다.
    # ---------------------------------------------------------------
    people_with_seat_counts = []
    for name in people_names:
        assignable = get_assignable_seats_for_person(name, list(empty_seats), forbidden_seats_map)
        people_with_seat_counts.append((name, len(assignable)))

    # 앉을 수 있는 자리 수가 적은 사람부터 처리하도록 정렬합니다.
    people_with_seat_counts.sort(key=lambda pair: pair[1])
    sorted_people = [pair[0] for pair in people_with_seat_counts]

    # 정렬된 순서대로 한 명씩 랜덤 자리를 배정합니다.
    for name in sorted_people:
        # 현재 남아있는 빈 자리 중에서, 이 사람이 앉을 수 있는 자리만 골라냅니다.
        candidate_seats = get_assignable_seats_for_person(name, list(empty_seats), forbidden_seats_map)

        if candidate_seats:
            # 후보 자리 중 하나를 무작위로 뽑아서 배정합니다.
            chosen_seat = random.choice(candidate_seats)
            seat_to_name[chosen_seat] = name
            empty_seats.remove(chosen_seat)
        else:
            # 앉을 수 있는 자리가 하나도 없으면 실패 목록에 넣습니다.
            failed_names.append(name)

    return seat_to_name, failed_names


# =========================================================================
# 7. [단일 책임] 화면(UI)을 그리는 함수들
# -------------------------------------------------------------------------
# 이 함수들은 "화면에 무엇을 보여줄지"만 담당하고, 데이터를 계산하지 않습니다.
# =========================================================================

def render_name_input_sidebar():
    # 사이드바 상단에 이름 명단을 입력받는 UI를 그립니다.
    st.sidebar.title("이름 명단 입력")
    st.sidebar.write(f"총 {total_seats}석 중 물리적으로 비활성화된 자리를 제외하고 배치됩니다.")

    st.sidebar.button("불러오기 (students.txt)", on_click=load_names_from_txt_file, args=("students.txt",))
    st.sidebar.button("불러오기 (example.txt)", on_click=load_names_from_txt_file, args=("example.txt",))
    st.sidebar.button("명단 순서 랜덤 섞기", on_click=shuffle_names_in_textarea)

    st.sidebar.text_area("명단 (한 줄에 한 명씩)", height=280, key="names_textarea", on_change=on_text_area_change)


def render_seat_board(seat_to_name: dict, disabled_seats: set, row_pairs: list):
    # 강의실 모양 그대로 자리 배치 결과를 화면에 그립니다.
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
                            # 물리적으로 사용 불가능한 자리는 회색으로 표시합니다.
                            st.markdown(
                                f"<div style='text-align:center; color:#aaa; padding:15px 0;'>사용불가</div>",
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

# 왼쪽 메뉴에서 화면 전환용 탭을 고릅니다.
menu = st.sidebar.radio("작업 선택", ["자리 배치 실행", "자리 구조/비활성 자리 설정", "인원별 금지 자리 설정"])

st.title("랜덤 자리 배치 프로그램 (블랙리스트 방식)")

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
    st.write("행(가로줄) 개수와 각 행의 짝꿍 수를 정하고, 물리적으로 아무도 앉을 수 없는 자리를 지정합니다.")

    temp_rows = st.number_input("총 행(가로줄) 개수", min_value=1, max_value=10, value=len(st.session_state.row_pairs))
    temp_pairs = []
    for i in range(temp_rows):
        default_val = st.session_state.row_pairs[i] if i < len(st.session_state.row_pairs) else 4
        val = st.number_input(f"{i + 1}행 짝꿍 수", min_value=1, max_value=10, value=default_val, key=f"row_input_{i}")
        temp_pairs.append(val)

    if st.button("자리 구조 적용 (초기화됩니다)"):
        st.session_state.row_pairs = temp_pairs
        new_total = sum(temp_pairs) * 2
        st.session_state.seats = ["(빈자리)"] * new_total
        st.session_state.disabled_seats = set()
        st.session_state.forbidden_seats_map = {}
        st.session_state.last_assignment_result = {}
        st.session_state.last_failed_names = []
        st.rerun()

    st.write("---")
    st.write("물리적으로 사용할 수 없는 자리 번호를 모두 선택하세요. (예: 기둥에 가려진 자리)")

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
    render_seat_board({}, st.session_state.disabled_seats, st.session_state.row_pairs)

else:
    st.write("특정 인원이 앉을 수 없는 자리를 지정합니다. (블랙리스트 방식: 여기서 선택한 자리에는 절대 앉지 않습니다)")

    if not current_names:
        st.info("먼저 사이드바에서 명단을 입력해주세요.")
    else:
        unique_names = sorted(set(current_names))
        target_name = st.selectbox("금지 자리를 설정할 사람", unique_names, key="forbidden_target_select")

        # 이미 물리적으로 비활성화된 자리는 애초에 선택 대상에서 뺍니다. (중복 관리 방지)
        available_for_selection = [s for s in all_seat_ids if s not in st.session_state.disabled_seats]
        seat_label_map = {s: f"{s + 1}번" for s in available_for_selection}

        current_forbidden = list(st.session_state.forbidden_seats_map.get(target_name, set()))

        # ---------------------------------------------------------------
        # [요청 기능] "모두 선택" 버튼: 이 사람이 모든 자리에 앉지 못하도록
        # 한 번에 전체 자리를 금지 목록에 넣을 수 있게 해주는 편의 기능입니다.
        # ---------------------------------------------------------------
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
