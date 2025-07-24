import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import numpy as np

st.title("2025년 7월 등급별 인원 분포 비교 시각화")

uploaded_file = st.file_uploader("등급 분포표 PDF 업로드", type="pdf")

def extract_table_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        data = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for i in range(1, len(table), 3):  # 과목별 3줄씩: 구분 / 학교 / 전국
                    if i+2 >= len(table):
                        continue
                    subject_row = table[i]
                    school_row = table[i+1]
                    national_row = table[i+2]

                    subject = subject_row[0]
                    try:
                        school_percents = [float(school_row[j].replace('%','').strip()) for j in range(2, 19, 2)]
                        national_percents = [float(national_row[j].replace('%','').strip()) for j in range(2, 19, 2)]
                    except:
                        continue

                    data.append({
                        '과목': subject,
                        '구분': '학교',
                        **{f'{i}등급': val for i, val in enumerate(school_percents, start=1)}
                    })
                    data.append({
                        '과목': subject,
                        '구분': '전국',
                        **{f'{i}등급': val for i, val in enumerate(national_percents, start=1)}
                    })
        df = pd.DataFrame(data)
    return df

if uploaded_file is not None:
    df = extract_table_from_pdf(uploaded_file)

    st.subheader("CSV 데이터 미리보기")
    st.dataframe(df)

    csv_data = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(label="CSV 다운로드", data=csv_data, file_name='등급별_학교_전국_비교.csv', mime='text/csv')

    st.subheader("과목별 등급 비율 비교 히스토그램")

    subjects = df['과목'].unique()
    selected_subjects = st.multiselect("과목 선택", subjects, default=list(subjects)[:3])

    for subject in selected_subjects:
        df_sub = df[df['과목'] == subject].set_index('구분')
        labels = [f'{i}등급' for i in range(1, 10)]
        x = np.arange(len(labels))  # 등급 수
        width = 0.35

        fig, ax = plt.subplots()
        school_vals = df_sub.loc['학교'][labels]
        national_vals = df_sub.loc['전국'][labels]

        ax.bar(x - width/2, school_vals, width, label='학교')
        ax.bar(x + width/2, national_vals, width, label='전국')

        ax.set_ylabel('비율 (%)')
        ax.set_title(f'{subject} - 등급별 인원 비율 비교')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        st.pyplot(fig)
