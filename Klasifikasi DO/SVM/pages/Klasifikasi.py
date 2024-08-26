import streamlit as st
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import mysql.connector

# Load the SVM model
pipeline = joblib.load('svm_model.pkl')

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="svm_do"
)
cursor = conn.cursor()

# Function to check if the mahasiswa already exists in the database
def check_duplicate(nim):
    sql = "SELECT id FROM mahasiswa WHERE nim = %s"
    cursor.execute(sql, (nim,))
    result = cursor.fetchone()
    return result is not None  # Returns True if the record exists, False otherwise

# Function to insert data into the mahasiswa table
def insert_mahasiswa(nama, prodi, nim, jenjang, ip, ipk, jumlah_cuti, jumlah_semester, jumlah_kehadiran):
    sql = '''
        INSERT INTO mahasiswa (nama, prodi, nim, jenjang, ip, ipk, jumlah_cuti, jumlah_semester, jumlah_kehadiran)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    val = (nama, prodi, nim, jenjang, ip, ipk, jumlah_cuti, jumlah_semester, jumlah_kehadiran)
    cursor.execute(sql, val)
    conn.commit()
    return cursor.lastrowid  # Return the inserted student's ID

# Function to insert data into the klasifikasi table
def insert_klasifikasi(mahasiswa_id, status):
    sql = '''
        INSERT INTO klasifikasi (mahasiswa_id, status)
        VALUES (%s, %s)
    '''
    val = (mahasiswa_id, status)
    cursor.execute(sql, val)
    conn.commit()

def main():
    st.title('Upload Data Mahasiswa')
    st.write("")

    # Allow user to upload a CSV file
    uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])

    if uploaded_file is not None:
        # Read the uploaded CSV file
        data = pd.read_csv(uploaded_file, sep=";")

        # Perform the necessary preprocessing similar to training
        data['Status'] = data['Status'].replace({'DO': 1, 'Tidak DO': 0})
        for column in ['IP', 'IPK', 'Jumlah Cuti', 'Jumlah Kehadiran']:
            data[column] = data[column].astype(str).str.replace(',', '.').astype(float)

        # Extract features
        X = data[['IP', 'IPK', 'Jumlah Cuti', 'Jumlah Kehadiran']]
        
        # Predict using the loaded model
        y_pred = pipeline.predict(X)

        # Show the classification results
        st.subheader('Data Hasil Klasifikasi:')
        data['Predicted Status'] = y_pred
        st.write(data)

        # Calculate and display accuracy
        st.subheader('Hasil Evaluasi:')
        y_true = data['Status']
        accuracy = accuracy_score(y_true, y_pred)
        st.write(f'Accuracy: {accuracy:.2f}')

        # Display confusion matrix
        st.subheader('Confusion Matrix:')
        cm = confusion_matrix(y_true, y_pred)
        st.write(cm)

        # Display classification report
        st.subheader('Classification Report:')
        report = classification_report(y_true, y_pred, zero_division=1)
        st.text(report)

        # Save the uploaded data into the mahasiswa and klasifikasi tables
        st.subheader('Menyimpan Data ke Database:')
        for i, row in data.iterrows():
            # Check for duplicate entry
            if check_duplicate(row['NIM']):
                st.warning(f"Data dengan NIM {row['NIM']} sudah ada di database dan tidak akan diupload.")
            else:
                # Insert data into mahasiswa table
                mahasiswa_id = insert_mahasiswa(
                    row['Nama'], 
                    row['Prodi'], 
                    row['NIM'], 
                    row['Jenjang'], 
                    row['IP'], 
                    row['IPK'], 
                    row['Jumlah Cuti'], 
                    row['Jumlah Semester'], 
                    row['Jumlah Kehadiran']
                )

                # Insert classification result into klasifikasi table
                status = 'DO' if row['Predicted Status'] == 1 else 'Tidak DO'
                insert_klasifikasi(mahasiswa_id, status)

        st.success("Proses upload selesai!")

if __name__ == '__main__':
    main()
