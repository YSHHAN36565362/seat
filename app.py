{\rtf1\ansi\ansicpg949\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 HelveticaNeue;}
{\colortbl;\red255\green255\blue255;\red23\green23\blue26;\red255\green255\blue255;\red0\green0\blue0;
}
{\*\expandedcolortbl;;\cssrgb\c11765\c11765\c13725;\cssrgb\c100000\c100000\c100000;\cssrgb\c0\c0\c0;
}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs28 \cf2 \cb3 \expnd0\expndtw0\kerning0
import streamlit as st\
import random\
\
# \uc0\u54168 \u51060 \u51648  \u44592 \u48376  \u49444 \u51221 \
st.set_page_config(page_title="\uc0\u47004 \u45924  \u51088 \u47532  \u48176 \u52824 ", layout="wide")\
\
# \uc0\u49464 \u49496  \u49345 \u53468  \u52488 \u44592 \u54868 : \u45936 \u51060 \u53552 \u47484  \u50976 \u51648 \u54616 \u44592  \u50948 \u54644  \u54596 \u50836 \u54633 \u45768 \u45796 .\
if "seats" not in st.session_state:\
    st.session_state.seats = ["(\uc0\u48712 \u51088 \u47532 )"] * 22\
if "remaining_names" not in st.session_state:\
    st.session_state.remaining_names = []\
\
# \uc0\u50812 \u51901  \u49324 \u51060 \u46300 \u48148  \u44396 \u49457 \
st.sidebar.title("\uc0\u51060 \u47492  \u47749 \u45800  \u51077 \u47141 ")\
st.sidebar.write("\uc0\u52509  22\u47749 \u51032  \u51060 \u47492 \u51012  \u51460 \u48148 \u45000 \u51004 \u47196  \u44396 \u48516 \u54644 \u49436  \u51077 \u47141 \u54644 \u51452 \u49464 \u50836 .")\
names_input = st.sidebar.text_area("\uc0\u47749 \u45800 ", height=400)\
\
if st.sidebar.button("\uc0\u47749 \u45800  \u46321 \u47197  \u48143  \u52488 \u44592 \u54868 "):\
    # \uc0\u51460 \u48148 \u45000 \u51012  \u44592 \u51456 \u51004 \u47196  \u51060 \u47492 \u51012  \u45208 \u45572 \u44256  \u44277 \u48177 \u51012  \u51228 \u44144 \u54633 \u45768 \u45796 .\
    names = [name.strip() for name in names_input.split('\\n') if name.strip()]\
    \
    if len(names) == 22:\
        st.session_state.remaining_names = names\
        st.session_state.seats = ["(\uc0\u48712 \u51088 \u47532 )"] * 22\
        st.sidebar.success("22\uc0\u47749 \u51032  \u47749 \u45800 \u51060  \u49457 \u44277 \u51201 \u51004 \u47196  \u46321 \u47197 \u46104 \u50632 \u49845 \u45768 \u45796 .")\
    else:\
        st.sidebar.error(f"\uc0\u54788 \u51116  \{len(names)\}\u47749 \u51060  \u51077 \u47141 \u46104 \u50632 \u49845 \u45768 \u45796 . \u51221 \u54869 \u55176  22\u47749 \u51012  \u51077 \u47141 \u54644 \u50556  \u54633 \u45768 \u45796 .")\
\
# \uc0\u47700 \u51064  \u54868 \u47732  \u44396 \u49457 \
st.title("\uc0\u47004 \u45924  \u51088 \u47532  \u48176 \u52824  \u54532 \u47196 \u44536 \u47016 ")\
\
# \uc0\u54620  \u47749 \u50473  \u51088 \u47532 \u47484  \u48176 \u52824 \u54616 \u45716  \u48260 \u53948 \
if st.button("1\uc0\u47749  \u47004 \u45924  \u48176 \u52824 \u54616 \u44592 "):\
    if st.session_state.remaining_names:\
        # \uc0\u54788 \u51116  \u48712 \u51088 \u47532 \u51032  \u51064 \u45937 \u49828  \u48264 \u54840 \u47484  \u47784 \u46160  \u52286 \u49845 \u45768 \u45796 .\
        empty_seat_indices = [i for i, seat in enumerate(st.session_state.seats) if seat == "(\uc0\u48712 \u51088 \u47532 )"]\
        \
        if empty_seat_indices:\
            # \uc0\u45224 \u51008  \u49324 \u46988  \u51473 \u50640 \u49436  \u47924 \u51089 \u50948 \u47196  1\u47749 \u51012  \u48977 \u49845 \u45768 \u45796 .\
            person_index = random.randint(0, len(st.session_state.remaining_names) - 1)\
            person = st.session_state.remaining_names.pop(person_index)\
            \
            # \uc0\u45224 \u51008  \u48712 \u51088 \u47532  \u51473 \u50640 \u49436  \u47924 \u51089 \u50948 \u47196  1\u44060 \u47484  \u48977 \u49845 \u45768 \u45796 .\
            seat_index = random.choice(empty_seat_indices)\
            \
            # \uc0\u54644 \u45817  \u51088 \u47532 \u50640  \u48977 \u55180  \u49324 \u46988 \u51032  \u51060 \u47492 \u51012  \u45347 \u49845 \u45768 \u45796 .\
            st.session_state.seats[seat_index] = person\
    else:\
        st.warning("\uc0\u47784 \u46304  \u51064 \u50896 \u51060  \u51088 \u47532 \u50640  \u48176 \u52824 \u46104 \u50632 \u49845 \u45768 \u45796 .")\
\
st.write("---")\
\
# 1\uc0\u54665  \u52636 \u47141  (6\u47749 , 2\u47749 \u50473  \u51677 \u51648 \u50612 \u49436  \u48372 \u50668 \u51469 \u45768 \u45796 )\
st.subheader("1\uc0\u54665 ")\
cols1 = st.columns(6)\
for i in range(6):\
    cols1[i].write(st.session_state.seats[i])\
\
# 2\uc0\u54665  \u52636 \u47141  (8\u47749 )\
st.subheader("2\uc0\u54665 ")\
cols2 = st.columns(8)\
for i in range(8):\
    cols2[i].write(st.session_state.seats[6 + i])\
\
# 3\uc0\u54665  \u52636 \u47141  (8\u47749 )\
st.subheader("3\uc0\u54665 ")\
cols3 = st.columns(8)\
for i in range(8):\
    cols3[i].write(st.session_state.seats[14 + i])}