import streamlit as st
import random
import os
import re

# 웹사이트의 탭 이름과 화면을 넓게 쓰도록 기본 설정을 해줍니다.
st.set_page_config(page_title="랜덤 자리 배치", layout="wide")

# 각 줄에 몇 쌍이 앉을지 기억하는 변수를 새로 만들었습니다. 
if "row_pairs" not in st.session_state:
    st.session_state.row_pairs = [4, 4, 3]

# 설정된 짝꿍 수에 곱하기 2를 해서 총 몇 명인지 계산합니다.
total_seats = sum(st.session_state.row_pairs) * 2

# 프로그램이 다시 실행되어도 데이터가 날아가지 않도록 세션 상태에 저장해둡니다.
if "seats" not in st.session_state or len(st.session_state.seats) != total_seats:
    st.session_state.seats = ["(빈자리)"] * total_seats

# 아직 자리를 배정받지 못한 남은 사람들의 명단을 저장할 공간입니다.
if "remaining_names" not in st.session_state:
    st.session_state.remaining_names = []

# 가장 마지막에 뽑힌 사람의 자리 번호를 기억해서 애니메이션 효과를 줄 때 사용합니다.
if "last_picked_idx" not in st.session_state:
    st.session_state.last_picked_idx = -1

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
/* 교탁(가운데 위쪽)에서 시작해서 자리로 이동하는 애니메이션 (검정 계열 박스) */
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

# * 변경사항: 이름 앞에 붙어있는 숫자 기호들을 모두 지운 뒤, 1번부터 차례대로 깔끔하게 번호를 다시 붙여주는 함수입니다.
def format_names_with_numbers(text):
    # 빈 줄을 제외하고 글자들을 가져옵니다.
    lines = [line for line in text.split('\n') if line.strip()]
    # 정규표현식을 사용해 맨 앞의 숫자, 점, 공백 등을 모두 제거하여 순수 이름만 남깁니다.
    cleaned_lines = [re.sub(r'^\d+[\.\)\]\s]+', '', line.strip()) for line in lines]
    # 1번부터 차례대로 번호를 예쁘게 붙여줍니다.
    numbered_lines = [f"{i+1}. {name}" for i, name in enumerate(cleaned_lines)]
    return '\n'.join(numbered_lines)

# * 변경사항: 텍스트 입력창에서 글자를 고치고 바깥을 클릭했을 때 자동으로 번호를 다시 정렬해주는 기능입니다.
def on_text_area_change():
    if "names_textarea" in st.session_state:
        st.session_state["names_textarea"] = format_names_with_numbers(st.session_state["names_textarea"])

def load_students_file():
    if os.path.exists("students.txt"):
        with open("students.txt", "r", encoding="utf-8") as f:
            # * 변경사항: 파일에서 글자를 불러올 때도 자동으로 번호를 붙이도록 수정했습니다.
            st.session_state["names_textarea"] = format_names_with_numbers(f.read())
    else:
        st.sidebar.error("같은 폴더에 students.txt 파일이 없습니다.")

def load_example_file():
    if os.path.exists("example.txt"):
        with open("example.txt", "r", encoding="utf-8") as f:
            # * 변경사항: 파일에서 글자를 불러올 때도 자동으로 번호를 붙이도록 수정했습니다.
            st.session_state["names_textarea"] = format_names_with_numbers(f.read())
    else:
        st.sidebar.error("같은 폴더에 example.txt 파일이 없습니다.")

def shuffle_names():
    if "names_textarea" in st.session_state:
        raw_text = st.session_state["names_textarea"]
        lines = [line for line in raw_text.split('\n') if line.strip()]
        
        # * 변경사항: 순서를 섞기 전에 먼저 번호를 떼어냅니다.
        cleaned_lines = [re.sub(r'^\d+[\.\)\]\s]+', '', line.strip()) for line in lines]
        
        # 순서를 마구 섞어줍니다.
        random.shuffle(cleaned_lines)
        
        # * 변경사항: 순서가 섞인 상태로 다시 1번부터 번호를 새로 붙여줍니다.
        numbered_lines = [f"{i+1}. {name}" for i, name in enumerate(cleaned_lines)]
        st.session_state["names_textarea"] = '\n'.join(numbered_lines)

# * 변경사항: 화면 왼쪽에 다른 탭으로 넘어갈 수 있는 메뉴 버튼을 새로 만들었습니다.
st.sidebar.title("메뉴 선택")
menu = st.sidebar.radio("원하시는 작업을 선택해주세요.", ["자리 배치 프로그램", "명단 랜덤 뽑기"])

st.sidebar.write("---")

# 화면 왼쪽에 있는 명단 입력 메뉴를 만듭니다. (이 부분은 어떤 탭에 있든 항상 유지됩니다)
st.sidebar.title("이름 명단 입력")
st.sidebar.write(f"총 {total_seats}석의 자리가 준비되어 있습니다. 이름은 한 줄에 하나씩 적어주세요.")

st.sidebar.button("명단 불러오기 (students.txt)", on_click=load_students_file)
st.sidebar.button("명단 불러오기 (example.txt)", on_click=load_example_file)
st.sidebar.button("랜덤으로 섞기", on_click=shuffle_names)

# * 변경사항: 텍스트 박스에 on_change를 넣어서, 내용을 고친 뒤 마우스로 다른 곳을 클릭하면 자동으로 번호가 매겨집니다.
names_input = st.sidebar.text_area("명단", height=400, key="names_textarea", on_change=on_text_area_change)

# * 변경사항: 자리 배치나 랜덤 뽑기를 할 때는 화면의 1. 2. 등의 숫자가 보이지 않도록 숫자를 제거한 이름만 골라냅니다.
raw_lines = [name.strip() for name in names_input.split('\n') if name.strip()]
current_names = [re.sub(r'^\d+[\.\)\]\s]+', '', name) for name in raw_lines]

# 현재 입력된 인원과 우리가 설정한 총 자릿수를 비교해서 보여줍니다.
if len(current_names) == total_seats:
    st.sidebar.success(f"현재 입력된 인원: {len(current_names)}명 / 총 자릿수: {total_seats}석 (딱 맞습니다!)")
elif len(current_names) < total_seats:
    st.sidebar.info(f"현재 입력된 인원: {len(current_names)}명 / 총 자릿수: {total_seats}석 (빈자리가 남게 됩니다.)")
else:
    st.sidebar.warning(f"현재 입력된 인원: {len(current_names)}명 / 총 자릿수: {total_seats}석 (자리가 부족합니다!)")

# 명단 등록 및 초기화 버튼을 누르면 작동하는 부분입니다.
if st.sidebar.button("명단 등록 및 초기화"):
    if len(current_names) <= total_seats:
        # 번호가 지워진 순수 이름만 프로그램 안에 저장합니다.
        st.session_state.remaining_names = current_names.copy()
        st.session_state.seats = ["(빈자리)"] * total_seats
        st.session_state.last_picked_idx = -1
        st.sidebar.success(f"총 {len(current_names)}명 등록되었습니다.")
    else:
        st.sidebar.error(f"자릿수({total_seats}석)보다 많은 인원({len(current_names)}명)이 입력되었습니다. 자리를 늘리거나 인원을 줄여주세요.")

# * 변경사항: 왼쪽 메뉴에서 선택한 탭에 따라 중앙 화면의 모습을 다르게 보여주도록 나누었습니다.

if menu == "자리 배치 프로그램":
    # ------------------ 자리 배치 프로그램 탭 ------------------
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
        if st.button("1명 랜덤 배치하기"):
            if st.session_state.remaining_names:
                empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(빈자리)"]
                if empty_seat_indices:
                    person_index = random.randint(0, len(st.session_state.remaining_names) - 1)
                    person = st.session_state.remaining_names.pop(person_index)
                    seat_index = random.choice(empty_seat_indices)
                    st.session_state.seats[seat_index] = person
                    st.session_state.last_picked_idx = seat_index
            else:
                st.warning("모든 인원이 자리에 배치되었습니다.")
                st.session_state.last_picked_idx = -1

    st.write("---")

    def draw_row(start_idx, pair_count):
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
                seat1_class = "animated-seat" if st.session_state.last_picked_idx == seat1_idx else "normal-seat"
                seat2_class = "animated-seat" if st.session_state.last_picked_idx == seat2_idx else "normal-seat"
                inner_cols[0].markdown(f"<div class='{seat1_class}'>{st.session_state.seats[seat1_idx]}</div>", unsafe_allow_html=True)
                inner_cols[1].markdown(f"<div class='{seat2_class}'>{st.session_state.seats[seat2_idx]}</div>", unsafe_allow_html=True)

    start_idx = 0
    for i, pair_count in enumerate(st.session_state.row_pairs):
        st.subheader(str(i + 1))
        draw_row(start_idx, pair_count)
        start_idx += pair_count * 2

elif menu == "명단 랜덤 뽑기":
    # ------------------ 명단 랜덤 뽑기 탭 ------------------
    st.title("명단 랜덤 뽑기")
    st.write("등록된 명단에서 자리에 배치되지 않고 남은 인원 중, 원하시는 인원수만큼 무작위로 추첨합니다.")
    
    st.write("---")
    
    # 뽑을 인원을 설정할 수 있는 숫자 입력창입니다.
    max_draw = len(st.session_state.remaining_names) if len(st.session_state.remaining_names) > 0 else 1
    draw_count = st.number_input("뽑을 인원", min_value=1, max_value=max_draw, value=1, step=1)
    
    if st.button("랜덤으로 뽑기"):
        if st.session_state.remaining_names:
            if draw_count <= len(st.session_state.remaining_names):
                # 파이썬의 sample 기능을 사용해서 중복 없이 선택한 인원만큼 사람을 뽑습니다.
                picked_people = random.sample(st.session_state.remaining_names, draw_count)
                st.success(f"당첨된 인원: {', '.join(picked_people)}")
            else:
                st.warning("현재 명단에 남은 인원보다 많이 뽑을 수 없습니다.")
        else:
            st.warning("명단에 남은 인원이 없습니다. 왼쪽 사이드바에서 명단을 등록해주세요.")
