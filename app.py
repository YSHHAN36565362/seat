import streamlit as st
import random
import os
import re

# 웹사이트의 탭 이름과 화면을 넓게 쓰도록 기본 설정을 해줍니다.
st.set_page_config(page_title="랜덤 자리 배치", layout="wide")

# 각 줄에 몇 쌍이 앉을지 기억하는 변수입니다.
if "row_pairs" not in st.session_state:
    st.session_state.row_pairs = [4, 4, 3]

total_seats = sum(st.session_state.row_pairs) * 2

if "seats" not in st.session_state or len(st.session_state.seats) != total_seats:
    st.session_state.seats = ["(빈자리)"] * total_seats

if "remaining_names" not in st.session_state:
    st.session_state.remaining_names = []

if "uid_counter" not in st.session_state:
    st.session_state.uid_counter = 0

if "last_picked_idx" not in st.session_state:
    st.session_state.last_picked_idx = -1

# {이름: [자리인덱스, ...]} 형태로 저장되는 좌석 제약 조건입니다.
if "seat_constraints" not in st.session_state:
    st.session_state.seat_constraints = {}

# 시각적인 디자인과 움직이는 애니메이션 효과를 위해 CSS 스타일 코드를 주입합니다.
st.markdown("""
<style>
.normal-seat {
    text-align: center;
    font-size: 16px;
    padding: 15px 0;
}
.animated-seat {
    text-align: center;
    font-size: 16px;
    padding: 15px 0;
    animation: flyAndLand 2s ease-in-out forwards;
}
.seat-number {
    text-align: center;
    font-size: 11px;
    color: #888;
    margin-top: -6px;
}
.seat-tag-mine {
    text-align: center;
    font-size: 11px;
    color: #1a7f37;
    font-weight: bold;
}
.seat-tag-other {
    text-align: center;
    font-size: 11px;
    color: #c62828;
}
@keyframes flyAndLand {
    0% {
        transform: translate(0, -40vh);
        opacity: 0;
        background-color: #2b2b2b;
        color: white;
        border-radius: 8px;
    }
    40% {
        transform: translate(0, -20vh) scale(1.5);
        opacity: 1;
        background-color: #2b2b2b;
        color: white;
        border-radius: 8px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.5);
    }
    80% {
        transform: translate(0, 0) scale(1.1);
        background-color: #2b2b2b;
        color: white;
        border-radius: 8px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.3);
    }
    100% {
        transform: translate(0, 0) scale(1);
        background-color: transparent;
        color: inherit;
        box-shadow: none;
    }
}
</style>
""", unsafe_allow_html=True)

def format_names_with_numbers(text):
    lines = [line for line in text.split('\n') if line.strip()]
    cleaned_lines = [re.sub(r'^\d+[\.\)\]\s]+', '', line.strip()) for line in lines]
    numbered_lines = [f"{i+1}. {name}" for i, name in enumerate(cleaned_lines)]
    return '\n'.join(numbered_lines)

def on_text_area_change():
    if "names_textarea" in st.session_state:
        st.session_state["names_textarea"] = format_names_with_numbers(st.session_state["names_textarea"])

def load_students_file():
    if os.path.exists("students.txt"):
        with open("students.txt", "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = format_names_with_numbers(f.read())
    else:
        st.sidebar.error("같은 폴더에 students.txt 파일이 없습니다.")

def load_example_file():
    if os.path.exists("example.txt"):
        with open("example.txt", "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = format_names_with_numbers(f.read())
    else:
        st.sidebar.error("같은 폴더에 example.txt 파일이 없습니다.")

def shuffle_names():
    if "names_textarea" in st.session_state:
        raw_text = st.session_state["names_textarea"]
        lines = [line for line in raw_text.split('\n') if line.strip()]
        cleaned_lines = [re.sub(r'^\d+[\.\)\]\s]+', '', line.strip()) for line in lines]
        random.shuffle(cleaned_lines)
        numbered_lines = [f"{i+1}. {name}" for i, name in enumerate(cleaned_lines)]
        st.session_state["names_textarea"] = '\n'.join(numbered_lines)

# 제약 조건이 있는 사람을 먼저, 빈 후보 자리 중 랜덤 하나에 배치하고
# 나머지 자유 인원을 남은 빈자리에 랜덤 배치하는 핵심 알고리즘입니다.
def assign_people(people_to_place, empty_seat_indices):
    available = set(empty_seat_indices)
    assignments = []
    unplaced = []

    constrained = [p for p in people_to_place if p[1] in st.session_state.seat_constraints]
    free = [p for p in people_to_place if p[1] not in st.session_state.seat_constraints]

    # 후보 자리가 적은 사람을 먼저 배치해야 충돌이 줄어듭니다.
    constrained.sort(
        key=lambda p: len([s for s in st.session_state.seat_constraints[p[1]] if s in available])
    )

    random.shuffle(free)

    for uid, name in constrained:
        candidate_seats = [s for s in st.session_state.seat_constraints[name] if s in available]
        if candidate_seats:
            chosen_seat = random.choice(candidate_seats)
            available.remove(chosen_seat)
            assignments.append((uid, name, chosen_seat))
        else:
            unplaced.append((uid, name))

    remaining_seats = list(available)
    random.shuffle(remaining_seats)

    for (uid, name), seat_idx in zip(free, remaining_seats):
        assignments.append((uid, name, seat_idx))

    if len(free) > len(remaining_seats):
        unplaced.extend(free[len(remaining_seats):])

    return assignments, unplaced

# 좌석 배치도를 화면에 그려주는 공용 함수입니다.
# mode="view" 이면 배정된 사람 이름만 보여주고,
# mode="edit" 이면 자리마다 체크박스를 넣어 제약 조건 편집에 사용합니다.
def draw_seat_grid(mode="view", target_name=None):
    start_idx = 0
    for row_i, pair_count in enumerate(st.session_state.row_pairs):
        st.markdown(f"**{row_i + 1}행**")
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
                seat1_idx = start_idx + i * 2
                seat2_idx = start_idx + i * 2 + 1

                for local_idx, seat_idx in [(0, seat1_idx), (1, seat2_idx)]:
                    with inner_cols[local_idx]:
                        if mode == "view":
                            seat_class = "animated-seat" if st.session_state.last_picked_idx == seat_idx else "normal-seat"
                            st.markdown(f"<div class='{seat_class}'>{st.session_state.seats[seat_idx]}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='seat-number'>#{seat_idx + 1}</div>", unsafe_allow_html=True)
                        else:
                            occupant = st.session_state.seats[seat_idx]
                            key = f"cst_{target_name}_{seat_idx}"
                            if key not in st.session_state:
                                existing = st.session_state.seat_constraints.get(target_name, [])
                                st.session_state[key] = seat_idx in existing

                            st.checkbox(f"{seat_idx + 1}번", key=key)

                            other_owner = None
                            for owner_name, seat_list in st.session_state.seat_constraints.items():
                                if owner_name != target_name and seat_idx in seat_list:
                                    other_owner = owner_name
                                    break

                            if other_owner:
                                st.markdown(f"<div class='seat-tag-other'>{other_owner} 지정됨</div>", unsafe_allow_html=True)
                            elif occupant != "(빈자리)":
                                st.markdown(f"<div class='seat-number'>{occupant} 배정됨</div>", unsafe_allow_html=True)

        start_idx += pair_count * 2

# 화면 왼쪽 메뉴입니다.
st.sidebar.title("메뉴 선택")
menu = st.sidebar.radio("원하시는 작업을 선택해주세요.", ["자리 배치 프로그램", "명단 랜덤 뽑기", "좌석 제약 조건 관리"])

st.sidebar.write("---")

st.sidebar.title("이름 명단 입력")
st.sidebar.write(f"총 {total_seats}석의 자리가 준비되어 있습니다. 이름은 한 줄에 하나씩 적어주세요.")

st.sidebar.button("명단 불러오기 (students.txt)", on_click=load_students_file)
st.sidebar.button("명단 불러오기 (example.txt)", on_click=load_example_file)
st.sidebar.button("랜덤으로 섞기", on_click=shuffle_names)

names_input = st.sidebar.text_area("명단", height=300, key="names_textarea", on_change=on_text_area_change)

raw_lines = [name.strip() for name in names_input.split('\n') if name.strip()]
current_names = [re.sub(r'^\d+[\.\)\]\s]+', '', name) for name in raw_lines]

if len(current_names) == total_seats:
    st.sidebar.success(f"현재 입력된 인원: {len(current_names)}명 / 총 자릿수: {total_seats}석")
elif len(current_names) < total_seats:
    st.sidebar.info(f"현재 입력된 인원: {len(current_names)}명 / 총 자릿수: {total_seats}석 (빈자리)")
else:
    st.sidebar.warning(f"현재 입력된 인원: {len(current_names)}명 / 총 자릿수: {total_seats}석 (자리가 부족합니다)")

if st.sidebar.button("명단 등록 및 초기화"):
    if len(current_names) <= total_seats:
        st.session_state.remaining_names = []
        for name in current_names:
            st.session_state.uid_counter += 1
            st.session_state.remaining_names.append((st.session_state.uid_counter, name))
        st.session_state.seats = ["(빈자리)"] * total_seats
        st.session_state.last_picked_idx = -1
        st.sidebar.success(f"총 {len(current_names)}명 등록되었습니다.")
    else:
        st.sidebar.error(f"자릿수({total_seats}석)보다 많은 인원({len(current_names)}명)이 입력되었습니다. 자리를 늘리거나 인원을 줄여주세요.")

if menu == "자리 배치 프로그램":
    title_col, config_col = st.columns([7, 3])

    with title_col:
        st.title("랜덤 자리 배치 프로그램")

    with config_col:
        with st.expander("자리 배치 설정 (클릭)"):
            st.write("각 줄에 몇 쌍(2명=1쌍)이 앉을지 수정할 수 있습니다.")
            temp_rows = st.number_input("총 행(가로줄) 개수", min_value=1, max_value=10, value=len(st.session_state.row_pairs))
            temp_pairs = []
            for i in range(temp_rows):
                default_val = st.session_state.row_pairs[i] if i < len(st.session_state.row_pairs) else 4
                val = st.number_input(f"{i+1}행 짝꿍 수", min_value=1, max_value=10, value=default_val)
                temp_pairs.append(val)

            if st.button("설정 적용 및 초기화"):
                st.session_state.row_pairs = temp_pairs
                new_total = sum(temp_pairs) * 2
                st.session_state.seats = ["(빈자리)"] * new_total
                st.session_state.remaining_names = []
                st.session_state.last_picked_idx = -1
                st.rerun()

    front_cols = st.columns([1, 2, 1, 1.5])

    with front_cols[1]:
        st.markdown("<div style='text-align: center;'><img src='https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi4I4zFnoGWku6HlvRHMoq5lU_eTEQR51_U0Uc1aDC9yom6QiLmTHPwulXQcQ0-FbCR_OFSLLwX-qdM29tW-1nnom99XsEPOvdLezDdZXE27Qqj2Y4TMC2JbL1e7njxi5UX1iNyA9b93M8C/w1200-h630-p-k-no-nu/school_class_woman_aseru.png' style='width: 50%;'><br><span style='color: gray; font-size: 14px;'>칠판</span></div>", unsafe_allow_html=True)

    with front_cols[2]:
        st.markdown("<div style='text-align: center;'><img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ_DZA5M8KH80YmEcHxZxumZnYGPyDQNcD0fkFQe3Q39zmtrho&s' style='width: 50%;'><br><span style='color: gray; font-size: 14px;'>TV</span></div>", unsafe_allow_html=True)

    with front_cols[3]:
        st.write("")
        st.write("")
        btn_cols = st.columns(2)

        with btn_cols[0]:
            if st.button("1명 랜덤 배치"):
                if st.session_state.remaining_names:
                    empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(빈자리)"]
                    if empty_seat_indices:
                        person = random.choice(st.session_state.remaining_names)
                        assignments, unplaced = assign_people([person], empty_seat_indices)
                        if assignments:
                            uid, name, seat_idx = assignments[0]
                            st.session_state.seats[seat_idx] = name
                            st.session_state.remaining_names.remove(person)
                            st.session_state.last_picked_idx = seat_idx
                        else:
                            st.warning(f"'{person[1]}'님의 지정 좌석이 모두 차 있어 배치할 수 없습니다.")
                    else:
                        st.warning("빈자리가 없습니다.")
                else:
                    st.warning("모든 인원이 자리에 배치되었습니다.")
                    st.session_state.last_picked_idx = -1

        with btn_cols[1]:
            if st.button("모두 랜덤 배치"):
                if st.session_state.remaining_names:
                    empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(빈자리)"]
                    if empty_seat_indices:
                        assignments, unplaced = assign_people(st.session_state.remaining_names, empty_seat_indices)
                        for uid, name, seat_idx in assignments:
                            st.session_state.seats[seat_idx] = name
                        placed_uids = {a[0] for a in assignments}
                        st.session_state.remaining_names = [p for p in st.session_state.remaining_names if p[0] not in placed_uids]
                        if assignments:
                            st.session_state.last_picked_idx = assignments[-1][2]
                        if unplaced:
                            names_str = ", ".join([p[1] for p in unplaced])
                            st.warning(f"지정 좌석이 모두 차서 배치 못 한 인원: {names_str}")
                    else:
                        st.warning("빈자리가 없습니다.")
                else:
                    st.warning("모든 인원이 자리에 배치되었습니다.")
                    st.session_state.last_picked_idx = -1

    st.write("---")
    draw_seat_grid(mode="view")

elif menu == "명단 랜덤 뽑기":
    st.title("명단 랜덤 뽑기")
    st.write("등록된 명단에서 자리에 배치되지 않고 남은 인원 중, 원하시는 인원수만큼 무작위로 추첨합니다.")
    st.write("---")

    max_draw = len(st.session_state.remaining_names) if len(st.session_state.remaining_names) > 0 else 1
    draw_count = st.number_input("뽑을 인원", min_value=1, max_value=max_draw, value=1, step=1)

    if st.button("랜덤으로 뽑기"):
        if st.session_state.remaining_names:
            if draw_count <= len(st.session_state.remaining_names):
                picked_people = random.sample(st.session_state.remaining_names, draw_count)
                names_str = ", ".join([p[1] for p in picked_people])
                st.success(f"당첨된 인원: {names_str}")
            else:
                st.warning("현재 명단에 남은 인원보다 많이 뽑을 수 없습니다.")
        else:
            st.warning("명단에 남은 인원이 없습니다. 왼쪽 사이드바에서 명단을 등록해주세요.")

else:
    # ------------------ 좌석 제약 조건 관리 탭 ------------------
    st.title("좌석 제약 조건 관리")
    st.write("아래 실제 좌석 배치도에서 체크박스로 후보 자리를 선택하면, 그 사람은 선택된 자리 중 하나에만 랜덤 배치됩니다.")
    st.write("---")

    unique_names = sorted(set([name for _, name in st.session_state.remaining_names])) if st.session_state.remaining_names else sorted(set(current_names))

    if not unique_names:
        st.info("먼저 사이드바에서 명단을 입력하고 등록해주세요.")
    else:
        target_name = st.selectbox("조건을 설정할 사람", unique_names)

        st.write(f"**'{target_name}'** 님이 앉을 수 있는 자리를 체크하세요. (여러 개 선택 가능, 그중 하나에 랜덤 배치됨)")
        st.write("")

        # 실제 배치도와 동일한 모양으로 체크박스 그리드를 그립니다.
        draw_seat_grid(mode="edit", target_name=target_name)

        st.write("---")
        save_col, clear_col = st.columns(2)

        with save_col:
            if st.button("조건 저장"):
                chosen_seats = [
                    seat_idx for seat_idx in range(total_seats)
                    if st.session_state.get(f"cst_{target_name}_{seat_idx}", False)
                ]
                if chosen_seats:
                    st.session_state.seat_constraints[target_name] = chosen_seats
                    seat_display = ", ".join([str(s + 1) for s in chosen_seats])
                    st.success(f"'{target_name}'님은 이제 {seat_display}번 자리 중 하나에만 배치됩니다.")
                else:
                    st.warning("자리를 1개 이상 선택해주세요.")

        with clear_col:
            if st.button(f"'{target_name}' 조건 삭제"):
                if target_name in st.session_state.seat_constraints:
                    del st.session_state.seat_constraints[target_name]
                for seat_idx in range(total_seats):
                    key = f"cst_{target_name}_{seat_idx}"
                    if key in st.session_state:
                        st.session_state[key] = False
                st.success(f"'{target_name}'님의 조건이 삭제되었습니다.")
                st.rerun()

        st.write("---")
        st.subheader("현재 등록된 조건 목록")
        if st.session_state.seat_constraints:
            for name, seats in st.session_state.seat_constraints.items():
                seat_display = ", ".join([str(s + 1) for s in seats])
                st.write(f"- **{name}**: {seat_display}번 자리 중 하나")
        else:
            st.write("등록된 조건이 없습니다.")
