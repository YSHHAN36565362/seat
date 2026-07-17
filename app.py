import streamlit as st
import random
import os

# 웹사이트의 탭 이름과 화면을 넓게 쓰도록 기본 설정을 해줍니다.
st.set_page_config(page_title="랜덤 자리 배치", layout="wide")

# * 변경사항: 각 줄에 몇 쌍이 앉을지 기억하는 변수를 새로 만들었습니다. 
# 기본값으로 1행 4쌍, 2행 4쌍, 3행 3쌍을 설정합니다.
if "row_pairs" not in st.session_state:
    st.session_state.row_pairs = [4, 4, 3]

# * 변경사항: 설정된 짝꿍 수에 곱하기 2를 해서 총 몇 명인지 계산합니다.
total_seats = sum(st.session_state.row_pairs) * 2

# 프로그램이 다시 실행되어도 데이터가 날아가지 않도록 세션 상태에 저장해둡니다.
# * 변경사항: 22라는 숫자 대신, 계산된 total_seats 변수를 사용하여 빈자리를 만듭니다.
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

# 컴퓨터에 저장된 students.txt 파일 안의 글자를 읽어와서 입력창에 넣어주는 함수입니다.
def load_students_file():
    if os.path.exists("students.txt"):
        with open("students.txt", "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = f.read()
    else:
        st.sidebar.error("같은 폴더에 students.txt 파일이 없습니다.")

# 컴퓨터에 저장된 example.txt 파일 안의 글자를 읽어와서 입력창에 넣어주는 함수입니다.
def load_example_file():
    if os.path.exists("example.txt"):
        with open("example.txt", "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = f.read()
    else:
        st.sidebar.error("같은 폴더에 example.txt 파일이 없습니다.")

# 현재 텍스트 입력창에 있는 사람들의 이름을 무작위 순서로 뒤섞어주는 함수입니다.
def shuffle_names():
    if "names_textarea" in st.session_state:
        current_text = st.session_state["names_textarea"]
        # 빈 줄은 빼고 이름만 모아서 리스트로 만듭니다.
        names_list = [name.strip() for name in current_text.split('\n') if name.strip()]
        # 파이썬의 random 기능을 사용해 순서를 마구 섞어줍니다.
        random.shuffle(names_list)
        # 섞인 이름들을 다시 줄바꿈으로 연결해서 입력창에 넣어줍니다.
        st.session_state["names_textarea"] = '\n'.join(names_list)

# 화면 왼쪽에 있는 사이드바 메뉴를 만듭니다.
st.sidebar.title("이름 명단 입력")
# * 변경사항: 22명이라고 고정된 글자 대신, 계산된 total_seats 변수를 보여줍니다.
st.sidebar.write(f"총 {total_seats}명의 이름을 줄바꿈으로 구분해서 입력해주세요.")

# 사이드바에 명단 불러오기 버튼과 랜덤 섞기 버튼을 배치합니다.
st.sidebar.button("명단 불러오기 (students.txt)", on_click=load_students_file)
st.sidebar.button("명단 불러오기 (example.txt)", on_click=load_example_file)
st.sidebar.button("랜덤으로 섞기", on_click=shuffle_names)

# 이름을 직접 입력할 수도 있는 텍스트 박스입니다.
names_input = st.sidebar.text_area("명단", height=400, key="names_textarea")

# 입력창에 써진 이름이 총 몇 명인지 계산해서 화면에 보여줍니다.
current_names = [name.strip() for name in names_input.split('\n') if name.strip()]
st.sidebar.write(f"현재 입력된 인원: {len(current_names)}명")

# 명단 등록 및 초기화 버튼을 누르면 작동하는 부분입니다.
if st.sidebar.button("명단 등록 및 초기화"):
    # * 변경사항: 입력된 인원이 현재 설정된 총 자리수와 맞는지 확인합니다.
    if len(current_names) == total_seats:
        st.session_state.remaining_names = current_names.copy()
        st.session_state.seats = ["(빈자리)"] * total_seats
        st.session_state.last_picked_idx = -1
        st.sidebar.success(f"{total_seats}명의 명단이 성공적으로 등록되었습니다.")
    else:
        st.sidebar.error(f"현재 {len(current_names)}명이 입력되었습니다. 정확히 {total_seats}명을 입력해야 합니다.")

# * 변경사항: 메인 화면의 윗부분을 화면 비율 7대 3으로 나누어 제목과 설정 창을 분리합니다.
title_col, config_col = st.columns([7, 3])

with title_col:
    # 가운데 큰 화면의 메인 제목입니다.
    st.title("랜덤 자리 배치 프로그램")

with config_col:
    # * 변경사항: 화면 오른쪽 위에 클릭하면 아래로 펼쳐지는 설정 창을 만듭니다.
    with st.expander("자리 배치 설정 (클릭)"):
        st.write("각 줄에 몇 쌍(2명=1쌍)이 앉을지 수정할 수 있습니다.")
        
        # 몇 줄로 자리를 만들지 숫자를 입력받습니다.
        temp_rows = st.number_input("총 행(가로줄) 개수", min_value=1, max_value=10, value=len(st.session_state.row_pairs))
        
        temp_pairs = []
        # 위에서 입력한 줄의 수만큼 반복해서 각 줄의 짝꿍 수를 입력받습니다.
        for i in range(temp_rows):
            # 기존에 설정된 값이 있으면 가져오고, 새로 생긴 줄이면 기본으로 4쌍을 채워줍니다.
            default_val = st.session_state.row_pairs[i] if i < len(st.session_state.row_pairs) else 4
            val = st.number_input(f"{i+1}행 짝꿍 수", min_value=1, max_value=10, value=default_val)
            temp_pairs.append(val)
            
        # 설정 적용 버튼을 눌렀을 때 실행되는 과정입니다.
        if st.button("설정 적용 및 초기화"):
            # 새롭게 설정한 각 줄의 짝꿍 수 정보를 저장합니다.
            st.session_state.row_pairs = temp_pairs
            
            # 자리 설정이 바뀌었으므로 모든 기록을 지우고 화면을 완전히 새로고침합니다.
            new_total = sum(temp_pairs) * 2
            st.session_state.seats = ["(빈자리)"] * new_total
            st.session_state.remaining_names = []
            st.session_state.last_picked_idx = -1
            st.rerun()

# 교실 앞쪽의 모습을 꾸미기 위해 화면을 4개의 열로 나눕니다.
front_cols = st.columns([1, 2, 1, 1.5])

# 두 번째 열에는 칠판 이미지를 넣습니다.
with front_cols[1]:
    st.markdown("<div style='text-align: center;'><img src='https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi4I4zFnoGWku6HlvRHMoq5lU_eTEQR51_U0Uc1aDC9yom6QiLmTHPwulXQcQ0-FbCR_OFSLLwX-qdM29tW-1nnom99XsEPOvdLezDdZXE27Qqj2Y4TMC2JbL1e7njxi5UX1iNyA9b93M8C/w1200-h630-p-k-no-nu/school_class_woman_aseru.png' style='width: 50%;'><br><span style='color: gray; font-size: 14px;'>칠판</span></div>", unsafe_allow_html=True)

# 세 번째 열에는 TV 이미지를 넣습니다.
with front_cols[2]:
    st.markdown("<div style='text-align: center;'><img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ_DZA5M8KH80YmEcHxZxumZnYGPyDQNcD0fkFQe3Q39zmtrho&s' style='width: 50%;'><br><span style='color: gray; font-size: 14px;'>TV</span></div>", unsafe_allow_html=True)

# 네 번째 열에는 1명씩 배치하는 동작 버튼을 넣습니다.
with front_cols[3]:
    st.write("")
    st.write("")
    # 버튼이 눌렸을 때 실행되는 과정입니다.
    if st.button("1명 랜덤 배치하기"):
        # 남은 사람이 있는지 확인합니다.
        if st.session_state.remaining_names:
            # 22개의 자리 중에서 현재 (빈자리)라고 적힌 곳의 번호만 찾아냅니다.
            empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(빈자리)"]
            
            # 빈자리가 남아있다면 배치를 시작합니다.
            if empty_seat_indices:
                # 1. 남은 사람 명단에서 아무나 1명을 뽑아냅니다.
                person_index = random.randint(0, len(st.session_state.remaining_names) - 1)
                person = st.session_state.remaining_names.pop(person_index)
                
                # 2. 남은 빈자리 중에서 아무 곳이나 1곳을 선택합니다.
                seat_index = random.choice(empty_seat_indices)
                
                # 3. 선택된 빈자리에 뽑힌 사람의 이름을 넣습니다.
                st.session_state.seats[seat_index] = person
                
                # 애니메이션을 재생하기 위해 방금 들어간 자리 번호를 기억시킵니다.
                st.session_state.last_picked_idx = seat_index
        else:
            # 남은 사람이 없으면 경고 메시지를 띄웁니다.
            st.warning("모든 인원이 자리에 배치되었습니다.")
            st.session_state.last_picked_idx = -1

# 구분선을 하나 그어줍니다.
st.write("---")

# 지정된 짝꿍 수만큼 테두리를 그리고 자리를 배치하는 함수입니다.
def draw_row(start_idx, pair_count):
    # 짝꿍들 사이에 빈 공간을 주기 위해 열의 너비 비율을 정해줍니다.
    col_ratios = []
    for i in range(pair_count):
        col_ratios.append(2)
        if i < pair_count - 1:
            col_ratios.append(0.5)
            
    # 정해진 비율대로 화면을 나눕니다.
    cols = st.columns(col_ratios)
    
    # 짝꿍의 개수만큼 반복해서 자리를 화면에 표시합니다.
    for i in range(pair_count):
        # 빈 공간을 건너뛰고 짝꿍이 들어갈 실제 열을 찾습니다.
        target_col = cols[i * 2]
        
        # 사각형 테두리를 만들어줍니다.
        with target_col.container(border=True):
            # 테두리 안에 2명의 자리를 만듭니다.
            inner_cols = st.columns(2)
            seat1_idx = start_idx + i * 2
            seat2_idx = start_idx + i * 2 + 1
            
            # 방금 배치된 사람인지 확인해서 애니메이션 효과를 줍니다.
            seat1_class = "animated-seat" if st.session_state.last_picked_idx == seat1_idx else "normal-seat"
            seat2_class = "animated-seat" if st.session_state.last_picked_idx == seat2_idx else "normal-seat"
            
            # 각각의 자리에 이름을 출력합니다.
            inner_cols[0].markdown(f"<div class='{seat1_class}'>{st.session_state.seats[seat1_idx]}</div>", unsafe_allow_html=True)
            inner_cols[1].markdown(f"<div class='{seat2_class}'>{st.session_state.seats[seat2_idx]}</div>", unsafe_allow_html=True)

# * 변경사항: 1행, 2행을 고정해서 쓰지 않고, 설정된 줄 수에 맞춰서 자동으로 그려주도록 수정했습니다.
start_idx = 0
for i, pair_count in enumerate(st.session_state.row_pairs):
    # 각 줄의 번호를 출력합니다.
    st.subheader(str(i + 1))
    # 설정에 저장된 짝꿍 수만큼 자리를 그립니다.
    draw_row(start_idx, pair_count)
    # 다음 줄을 그릴 때는 방금 그린 자리 수만큼 번호를 건너뛰어 계산합니다. (1쌍당 2명)
    start_idx += pair_count * 2
