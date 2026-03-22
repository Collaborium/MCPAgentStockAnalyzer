import pandas as pd
import sqlite3
from typing import List

def query_bhavdata(file_paths: List[str], sql_query: str) -> str:
    """
    Load local BhavData CSV files into a temporary SQLite database and execute a SQL query.
    The table name will always be 'bhavdata'.
    Example query: 'SELECT SYMBOL, CLOSE, TOTTRDQTY FROM bhavdata ORDER BY TOTTRDQTY DESC LIMIT 5'
    """
    if not file_paths:
        return "Error: No file paths provided."

    conn = sqlite3.connect(":memory:")
    
    try:
        tables_loaded = 0
        for path in file_paths:
            try:
                # Read CSV
                df = pd.read_csv(path)
                
                # Strip spaces from column names to make SQL querying easier
                df.columns = df.columns.str.strip()
                
                # Append to single table 'bhavdata'
                df.to_sql("bhavdata", conn, if_exists="append", index=False)
                tables_loaded += 1
            except Exception as e:
                return f"Error loading file at {path}: {str(e)}"
                
        if tables_loaded == 0:
            return "No valid files were loaded."
            
        # Execute the user's SQL query
        try:
            result_df = pd.read_sql_query(sql_query, conn)
            
            # Limit returned rows strictly to avoid exceeding LLM context memory
            if len(result_df) > 100:
                result_df = result_df.head(100)
                csv_data = result_df.to_csv(index=False)
                return csv_data + "\n(Note: Output was truncated to first 100 rows to prevent context overflow.)"
                
            return result_df.to_csv(index=False)
            
        except sqlite3.OperationalError as e:
            # helpful debug information to ensure LLM writes valid SQL
            try:
                schema_df = pd.read_sql_query("PRAGMA table_info(bhavdata)", conn)
                columns = ", ".join(schema_df["name"].tolist())
                return f"SQL Error: {str(e)}\n\nAvailable columns in 'bhavdata' table: {columns}"
            except Exception:
                return f"SQL Error: {str(e)}"
        except Exception as e:
            return f"Error executing query: {str(e)}"
            
    finally:
        conn.close()
