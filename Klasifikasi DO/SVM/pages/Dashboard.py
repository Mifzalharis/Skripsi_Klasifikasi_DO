import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import joblib

# Load the trained model
pipeline = joblib.load('svm_model.pkl')

# Function to load and preprocess the dataset
# Function to load and preprocess the dataset
def load_dataset():
    data = pd.read_csv('data_DO.csv', sep=";")
    data['Status'] = data['Status'].replace({'DO': 1, 'Tidak DO': 0})
    data['IP'] = data['IP'].str.replace(',', '.').astype(float)
    data['IPK'] = data['IPK'].str.replace(',', '.').astype(float)
    data['Jumlah Cuti'] = data['Jumlah Cuti'].astype(float)
    data['Jumlah Semester'] = data['Jumlah Semester'].astype(float)
    data['Jumlah Kehadiran'] = data['Jumlah Kehadiran'].astype(float)
    return data


# Function to perform predictions
def perform_predictions(data):
    X = data[['IP', 'IPK', 'Jumlah Cuti','Jumlah Kehadiran']]
    y_true = data['Status']
    y_pred = pipeline.predict(X)
    return y_true, y_pred

# Function to display the confusion matrix
# Function to display the confusion matrix
def display_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(cm, annot=True, cmap='Blues', fmt='d', cbar=False,
                xticklabels=['Tidak DO', 'DO'], yticklabels=['Tidak DO', 'DO'], ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    st.pyplot(fig)

# Function to display the distribution chart
def display_status_distribution(data):
    status_counts = data['Status'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=status_counts.index, y=status_counts.values, ax=ax)
    ax.set_title('Distribution of Student Status')
    ax.set_xlabel('Status')
    ax.set_ylabel('Count')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Tidak DO', 'DO'])
    st.pyplot(fig)

# Function to display status distribution by program
def display_status_by_prodi(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x='Prodi', hue='Status', data=data, palette='Set2', ax=ax)
    ax.set_title('Distribution of Status by Program Study')
    ax.set_xlabel('Program Study')
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)


# Main function for the dashboard
def main():
    st.title('Dashboard Klasifikasi Status Mahasiswa')

    # Load and preprocess the dataset
    data = load_dataset()

    # Perform predictions
    y_true, y_pred = perform_predictions(data)

    # Display classification table
    st.subheader('Tabel Klasifikasi:')
    st.write(data)

    # Display confusion matrix
    st.subheader('Confusion Matrix:')
    display_confusion_matrix(y_true, y_pred)

    # Display status distribution chart
    st.subheader('Distribusi Status Mahasiswa:')
    display_status_distribution(data)

    # Display status distribution by program
    st.subheader('Distribusi Status Mahasiswa per Program Studi:')
    display_status_by_prodi(data)

if __name__ == '__main__':
    main()
