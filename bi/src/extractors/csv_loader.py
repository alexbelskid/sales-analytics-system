import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

# Добавляем путь к корню, чтобы импорты работали корректно
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

def load_csv_to_supabase(file_path: str, table_name: str, db_url: str):
    """
    Загружает CSV файл в схему RAW в Supabase.
    """
    try:
        print(f"Reading file: {file_path}")
        df = pd.read_csv(file_path)
        
        # Добавляем технические поля
        df['_loaded_at'] = pd.Timestamp.now()
        df['_source_file'] = os.path.basename(file_path)
        
        print(f"Connecting to database...")
        engine = create_engine(db_url)
        
        # Создаем схему raw, если её нет
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
            conn.commit()
        
        print(f"Loading {len(df)} rows into raw.{table_name}...")
        df.to_sql(
            name=table_name,
            con=engine,
            schema='raw',
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        print("Success!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

if __name__ == "__main__":
    # Пример использования (замените на реальные данные или аргументы CLI)
    # DB_URL = os.getenv("SUPABASE_DB_URL")
    # load_csv_to_supabase("data.csv", "sales_upload", DB_URL)
    pass
