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

# 학생 명단 파일을 불러오는 함수
def load_students_file():
    if os.path.exists("students.txt"):
        with open("students.txt", "r", encoding="utf-8") as f:
            # 텍스트 에어리어의 상태값(key)을 파일 내용으로 업데이트합니다.
            st.session_state["names_textarea"] = f.read()
    else:
        st.sidebar.error("같은 폴더에 students.txt 파일이 없습니다.")

# 왼쪽 사이드바 구성
st.sidebar.title("이름 명단 입력")
st.sidebar.write("총 22명의 이름을 줄바꿈으로 구분해서 입력해주세요.")

# 불러오기 버튼 추가
st.sidebar.button("명단 불러오기 (students.txt)", on_click=load_students_file)

# 명단 입력창 (key를 지정하여 상태를 관리합니다)
names_input = st.sidebar.text_area("명단", height=400, key="names_textarea")

# 현재 입력된 이름이 몇 줄인지(몇 명인지) 계산하여 표시
current_names = [name.strip() for name in names_input.split('\n') if name.strip()]
st.sidebar.write(f"현재 입력된 인원: {len(current_names)}명")

# 등록 버튼
if st.sidebar.button("명단 등록 및 초기화"):
    if len(current_names) == 22:
        st.session_state.remaining_names = current_names.copy()
        st.session_state.seats = ["(빈자리)"] * 22
        st.sidebar.success("22명의 명단이 성공적으로 등록되었습니다.")
    else:
        st.sidebar.error(f"현재 {len(current_names)}명이 입력되었습니다. 정확히 22명을 입력해야 합니다.")

# 메인 화면 구성
st.title("랜덤 자리 배치 프로그램")

# 한 명씩 자리를 배치하는 버튼
if st.button("1명 랜덤 배치하기"):
    if st.session_state.remaining_names:
        empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(빈자리)"]
        
        if empty_seat_indices:
            person_index = random.randint(0, len(st.session_state.remaining_names) - 1)
            person = st.session_state.remaining_names.pop(person_index)
            
            seat_index = random.choice(empty_seat_indices)
            st.session_state.seats[seat_index] = person
    else:
        st.warning("모든 인원이 자리에 배치되었습니다.")

st.write("---")

# 짝(2명)을 테두리로 묶고 짝 사이를 띄우는 화면 출력 함수
def draw_row(start_idx, pair_count):
    # 짝 사이의 빈 공간을 만들기 위해 열(컬럼) 비율을 설정합니다.
    # 예: 짝이 들어갈 공간 2, 빈 공간 0.5
    col_ratios = []
    for i in range(pair_count):
        col_ratios.append(2)
        if i < pair_count - 1:
            col_ratios.append(0.5)
            
    cols = st.columns(col_ratios)
    
    for i in range(pair_count):
        # 짝이 들어갈 열의 인덱스는 0, 2, 4 순서입니다.
        target_col = cols[i * 2]
        
        # 테두리가 있는 컨테이너를 생성하여 짝꿍임을 표시합니다.
        with target_col.container(border=True):
            inner_cols = st.columns(2)
            seat1_idx = start_idx + i * 2
            seat2_idx = start_idx + i * 2 + 1
            inner_cols[0].write(st.session_state.seats[seat1_idx])
            inner_cols[1].write(st.session_state.seats[seat2_idx])

# 1행 출력 (6명, 3쌍)
st.subheader("1행")
draw_row(0, 3)

# 2행 출력 (8명, 4쌍)
st.subheader("2행")
draw_row(6, 4)

# 3행 출력 (8명, 4쌍)
st.subheader("3행")
draw_row(14, 4)
