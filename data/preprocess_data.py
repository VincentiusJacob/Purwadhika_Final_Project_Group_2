import pandas as pd
import json
import sqlite3
import re
import os

INPUT_FILE = 'jobs.jsonl' 
DB_NAME = 'jobs_database.db'      

def clean_salary_advanced(salary_text):

    """
    Fungsi:
    Membersihkan format gaji yang kotor.
    - Mengubah "Rp 10.000.000" jadi integer.
    - Menangani "None", "World Class Benefits", dll jadi 0.
    - Memisahkan range jadi min_salary dan max_salary.
    """

    if pd.isna(salary_text) or str(salary_text).lower() == "none":
        return 0, 0
    
    # Lowercase & hapus karakter yang tidak diperlukan
    text = str(salary_text).lower().replace('.', '').replace(',', '')
    
    # Cek kehadiran angka dalam teks
    if not any(char.isdigit() for char in text):
        return 0, 0
    

    multiplier = 1
    if 'juta' in text or 'jt' in text:
        multiplier = 1_000_000
    
    # Cari semua angka dalam teks
    numbers = re.findall(r'\d+', text)
    
    # Filter angka 
    # Hapus angka yang terlalu kecil (misal angka tahun 2025 atau tanggal)
    # Asumsi: Gaji bulanan minimal 500.000
    valid_numbers = []
    for n in numbers:
        val = int(n) * multiplier
        if val > 500000: 
            valid_numbers.append(val)
    
    if not valid_numbers:
        return 0, 0
    
    if len(valid_numbers) == 1:
        return valid_numbers[0], valid_numbers[0]
    else:
        return min(valid_numbers), max(valid_numbers)



def extract_work_style(location_text):

    """
    Fungsi:
    Mendeteksi Work Style dari kolom location.
    Contoh: "Jakarta (Hibrid)" -> "Hybrid"
    Contoh: "Jakarta (Jarak jauh)" -> "Remote"
    """

    text = str(location_text).lower()
    if 'jarak jauh' in text or 'remote' in text:
        return 'Remote'
    elif 'hibrid' in text or 'hybrid' in text:
        return 'Hybrid'
    else:
        return 'On-site' 


def clean_location_name(location_text):

    """
    Fungsi:
    Membersihkan nama kota dari keterangan tambahan.
    Contoh: "Jakarta Selatan\n(Hibrid)" -> "Jakarta Selatan"
    """

    text = str(location_text).split('\n')[0]
    return text.strip()


def main():
    
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} tidak ditemukan!")
        return

    try:
        df = pd.read_json(INPUT_FILE, lines=True)
        print(f"Berhasil load {len(df)} baris data.")
    except ValueError as e:
        print(f"Format JSON invalid. Detail: {e}")
        return


    # Standarisasi kolom Salary
    salary_cleaned = df['salary'].apply(clean_salary_advanced)
    df['min_salary'] = [x[0] for x in salary_cleaned]
    df['max_salary'] = [x[1] for x in salary_cleaned]
    
    # Ekstrak Work Style (Remote/Hybrid)
    df['work_style'] = df['location'].apply(extract_work_style)
    
    # Standarisasi lokasi kerjaNe
    df['clean_location'] = df['location'].apply(clean_location_name)

    # Handle Missing Values
    df['company_name'] = df['company_name'].fillna('Unknown Company')
    df['job_title'] = df['job_title'].fillna('Unknown Title')
    df['work_type'] = df['work_type'].fillna('Full time')


    conn = sqlite3.connect(DB_NAME)
    
    sql_columns = [
        'job_title', 
        'company_name', 
        'clean_location', 
        'work_style',     
        'work_type', 
        'min_salary', 
        'max_salary',
        'job_description' 
    ]
    
    df[sql_columns].to_sql('jobs', conn, if_exists='replace', index=False)
    conn.close()
    print("Database SQL berhasil dibuat!")

if __name__ == "__main__":
    main()