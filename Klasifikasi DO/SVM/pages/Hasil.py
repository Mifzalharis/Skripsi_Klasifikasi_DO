import streamlit as st
import mysql.connector
import pandas as pd
import joblib
import altair as alt

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="svm_do"
)
cursor = conn.cursor()

# Load the trained model
pipeline = joblib.load('svm_model.pkl')

# Function to fetch combined data from mahasiswa and klasifikasi tables
def fetch_combined_data(search_query=""):
    sql = '''
        SELECT m.nama, m.prodi, m.nim, m.jenjang, m.ip, m.ipk, m.jumlah_cuti, m.jumlah_semester, m.jumlah_kehadiran, k.status
        FROM mahasiswa m
        JOIN klasifikasi k ON m.id = k.mahasiswa_id
    '''
    if search_query:
        sql += " WHERE m.nama LIKE %s OR m.nim LIKE %s"
        val = ('%' + search_query + '%', '%' + search_query + '%')
        cursor.execute(sql, val)
    else:
        cursor.execute(sql)
    
    result = cursor.fetchall()
    columns = ['Nama', 'Prodi', 'NIM', 'Jenjang', 'IP', 'IPK', 'Jumlah Cuti', 'Jumlah Semester', 'Jumlah Kehadiran', 'Status']
    return pd.DataFrame(result, columns=columns)

# Function to fetch data from mahasiswa and klasifikasi tables based on status
def fetch_data_by_status(status):
    sql = '''
        SELECT m.nama, m.prodi, m.nim, m.jenjang, m.ip, m.ipk, m.jumlah_cuti, m.jumlah_semester, m.jumlah_kehadiran, k.status
        FROM mahasiswa m
        JOIN klasifikasi k ON m.id = k.mahasiswa_id
        WHERE k.status = %s
    '''
    val = (status,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    columns = ['Nama', 'Prodi', 'NIM', 'Jenjang', 'IP', 'IPK', 'Jumlah Cuti', 'Jumlah Semester', 'Jumlah Kehadiran', 'Status']
    return pd.DataFrame(result, columns=columns)

# Function to fetch report data for visualization
def fetch_report_data():
    sql = '''
        SELECT m.prodi, k.status, COUNT(*) as count
        FROM mahasiswa m
        JOIN klasifikasi k ON m.id = k.mahasiswa_id
        GROUP BY m.prodi, k.status
    '''
    cursor.execute(sql)
    rows = cursor.fetchall()
    report_df = pd.DataFrame(rows, columns=['Prodi', 'Status', 'Count'])
    report_df['Count'] = report_df['Count'].astype(int)
    
    # Pivot table for reporting
    pivot_df = report_df.pivot(index='Prodi', columns='Status', values='Count').fillna(0).reset_index()
    return pivot_df

# Function to get the prodi with the highest and lowest DO counts
def get_prodi_summary(report_df):
    if report_df.empty:
        return None, None
    
    # Find the prodi with highest and lowest DO counts
    if 'DO' not in report_df.columns:
        return None, None
    
    max_do_prodi = report_df.loc[report_df['DO'].idxmax()] if not report_df['DO'].empty else None
    min_do_prodi = report_df.loc[report_df['DO'].idxmin()] if not report_df['DO'].empty else None
    
    return max_do_prodi, min_do_prodi

# Function to delete all data from both klasifikasi and mahasiswa tables
def delete_all_data():
    # Delete all records from klasifikasi table
    cursor.execute('DELETE FROM klasifikasi')
    # Delete all records from mahasiswa table
    cursor.execute('DELETE FROM mahasiswa')
    conn.commit()

# Main function to display the combined interface
def main():
    st.title('Dashboard Data Mahasiswa dan Klasifikasi')

    # Define the tabs
    tab1, tab2, tab3 = st.tabs(["Pencarian Data Mahasiswa", "Data Berdasarkan Status", "Klasifikasi dan Laporan"])

    # Tab 1: Pencarian Data Mahasiswa
    with tab1:
        st.subheader('Pencarian Data Mahasiswa')
        search_query = st.text_input("Cari Mahasiswa berdasarkan Nama atau NIM:")
        data = fetch_combined_data(search_query)

        if not data.empty:
            st.write(data)
        else:
            st.write("Tidak ada data yang ditemukan untuk pencarian tersebut.")

    # Tab 2: Data Berdasarkan Status
    with tab2:
        st.subheader('Data Mahasiswa Berdasarkan Status Klasifikasi')
        status_option = st.selectbox("Pilih Status Klasifikasi:", ["Semua", "DO", "Tidak DO"])

        if status_option != "Semua":
            data_status = fetch_data_by_status(status_option)
            if not data_status.empty:
                st.write(f"Data Mahasiswa dengan Status {status_option}:")
                st.write(data_status)
            else:
                st.write(f"Tidak ada data mahasiswa dengan status {status_option}.")
        else:
            data_do = fetch_data_by_status("DO")
            data_tidak_do = fetch_data_by_status("Tidak DO")

            st.write("Data Mahasiswa dengan Status DO:")
            if not data_do.empty:
                st.write(data_do)
            else:
                st.write("Tidak ada data mahasiswa dengan status DO.")

            st.write("Data Mahasiswa dengan Status Tidak DO:")
            if not data_tidak_do.empty:
                st.write(data_tidak_do)
            else:
                st.write("Tidak ada data mahasiswa dengan status Tidak DO.")

    # Tab 3: Klasifikasi dan Laporan
    with tab3:
        st.subheader('Visualisasi Data')
        report_df = fetch_report_data()
        
        if not report_df.empty:
            report_df.columns = ['Prodi', 'Tidak DO', 'DO']
            
            # Show the report table
            st.dataframe(report_df)
            
            # Visualization
            status_counts = report_df.melt(id_vars=["Prodi"], var_name="Status", value_name="Count")
            chart = alt.Chart(status_counts).mark_bar().encode(
                x='Prodi',
                y='Count',
                color='Status',
                tooltip=['Prodi', 'Status', 'Count']
            ).properties(
                width=600,
                height=400
            )
            st.altair_chart(chart, use_container_width=True)

            # Get summary
            max_do_prodi, min_do_prodi = get_prodi_summary(report_df)
            
            if max_do_prodi is not None:
                st.write(f"Program studi dengan jumlah DO paling banyak adalah {max_do_prodi['Prodi']} dengan {max_do_prodi['DO']} DO.")
            else:
                st.write("Tidak ada data DO untuk menentukan program studi dengan jumlah DO paling banyak.")
            
            if min_do_prodi is not None:
                st.write(f"Program studi dengan jumlah DO paling sedikit adalah {min_do_prodi['Prodi']} dengan {min_do_prodi['DO']} DO.")
            else:
                st.write("Tidak ada data DO untuk menentukan program studi dengan jumlah DO paling sedikit.")
        else:
            st.write("Data kosong atau tidak ada data untuk laporan.")

        # Add button to delete all records at the bottom of the report section
        if st.button('Delete All Records'):
            delete_all_data()
            st.success("All records have been deleted")
            st.experimental_rerun()

if __name__ == '__main__':
    main()
