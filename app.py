import streamlit as st
import random
import os

# 페이지 기본 설정
st.set_page_config(page_title="랜덤 자리 배치", layout="wide")

# 세션 상태 초기화
if "seats" not in st.session_state:
    st.session_state.seats = ["(빈자리)"] * 22
if "remaining_names" not in st.session_state:
    st.session_state.remaining_names = []
# 방금 뽑힌 사람의 자리 인덱스를 기억하기 위한 변수
if "last_picked_idx" not in st.session_state:
    st.session_state.last_picked_idx = -1

# 가운데 정렬 및 이동 애니메이션을 위한 CSS 스타일 주입
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
/* 명단 박스(왼쪽)에서 시작해서 자리로 이동하는 애니메이션 */
@keyframes flyAndLand {
    0% {
        transform: translate(-30vw, -20vh);
        opacity: 0;
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
    }
    40% {
        transform: translate(-15vw, -10vh) scale(1.5);
        opacity: 1;
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
    }
    80% {
        transform: translate(0, 0) scale(1.1);
        background-color: #4a90e2;
        color: white;
        border-radius: 8px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.2);
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

# 학생 명단 파일을 불러오는 함수
def load_students_file():
    if os.path.exists("students.txt"):
        with open("students.txt", "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = f.read()
    else:
        st.sidebar.error("같은 폴더에 students.txt 파일이 없습니다.")

def load_students_file_2():
    if os.path.exists("example.txt"):
        with open("example.txt", "r", encoding="utf-8") as f:
            st.session_state["names_textarea"] = f.read()
    else:
        st.sidebar.error("같은 폴더에 example.txt 파일이 없습니다.")

# 왼쪽 사이드바 구성
st.sidebar.title("이름 명단 입력")
st.sidebar.write("총 22명의 이름을 줄바꿈으로 구분해서 입력해주세요.")
st.sidebar.button("명단 불러오기 (students.txt)", on_click=load_students_file)
st.sidebar.button("명단 불러오기 (example.txt)", on_click=load_students_file_2)


names_input = st.sidebar.text_area("명단", height=400, key="names_textarea")
current_names = [name.strip() for name in names_input.split('\n') if name.strip()]
st.sidebar.write(f"현재 입력된 인원: {len(current_names)}명")

# 등록 버튼
if st.sidebar.button("명단 등록 및 초기화"):
    if len(current_names) == 22:
        st.session_state.remaining_names = current_names.copy()
        st.session_state.seats = ["(빈자리)"] * 22
        st.session_state.last_picked_idx = -1
        st.sidebar.success("22명의 명단이 성공적으로 등록되었습니다.")
    else:
        st.sidebar.error(f"현재 {len(current_names)}명이 입력되었습니다. 정확히 22명을 입력해야 합니다.")

# 메인 화면 구성
st.title("랜덤 자리 배치")

# 한 명씩 자리를 배치하는 버튼
if st.button("1명 랜덤 배치하기"):
    if st.session_state.remaining_names:
        empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(빈자리)"]
        
        if empty_seat_indices:
            person_index = random.randint(0, len(st.session_state.remaining_names) - 1)
            person = st.session_state.remaining_names.pop(person_index)
            
            seat_index = random.choice(empty_seat_indices)
            st.session_state.seats[seat_index] = person
            
            # 방금 배치된 자리 인덱스를 저장하여 애니메이션을 트리거합니다.
            st.session_state.last_picked_idx = seat_index
    else:
        st.warning("모든 인원이 자리에 배치되었습니다.")
        st.session_state.last_picked_idx = -1

st.write("---")

# 짝(2명)을 테두리로 묶고 짝 사이를 띄우는 화면 출력 함수
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
            
            # 방금 뽑힌 자리인지 확인하여 클래스를 다르게 적용합니다.
            seat1_class = "animated-seat" if st.session_state.last_picked_idx == seat1_idx else "normal-seat"
            seat2_class = "animated-seat" if st.session_state.last_picked_idx == seat2_idx else "normal-seat"
            
            # HTML을 사용하여 텍스트 가운데 정렬 및 애니메이션 클래스를 적용합니다.
            inner_cols[0].markdown(f"<div class='{seat1_class}'>{st.session_state.seats[seat1_idx]}</div>", unsafe_allow_html=True)
            inner_cols[1].markdown(f"<div class='{seat2_class}'>{st.session_state.seats[seat2_idx]}</div>", unsafe_allow_html=True)

# 1행 출력 (6명, 3쌍)
st.subheader("1행")
draw_row(0, 3)

# 2행 출력 (8명, 4쌍)
st.subheader("2행")
draw_row(6, 4)

# 3행 출력 (8명, 4쌍)
st.subheader("3행")
draw_row(14, 4)
