# import csv
import pandas as pd
import sqlite3
import numpy as np
import locale 

def csv_types(file):
    # Read the CSV file into a Pandas DataFrame
    df = pd.read_csv(file)
    # df = df.dropna(subset=[str(df.columns[0])])
    df = df.rename(columns=lambda x: x.strip())

    # Set the locale to the appropriate format for your input CSV
    locale.setlocale(locale.LC_ALL, "en_CA.UTF-8")

    def convert_to_float(x):
        if x != np.nan:
            x = str(x).strip()
            x = locale.atof(x.replace('$', ''))
        return x

    for col in df.columns:
        should_convert = False
        column_as_list = df[col].tolist()
        df[col] = df[col].replace(' -   ', np.nan)
        df[col] = df[col].replace(' $-   ', np.nan)
        df[col] = df[col].replace(' ', np.nan)
        df[col] = df[col].replace('', np.nan)
        df[col] = df[col].replace('#DIV/0!', np.nan)

        for item in column_as_list:
            if '$' in str(item):
                should_convert = True

        if should_convert == True:
            df[col] = df[col].apply(lambda x: convert_to_float(x))

            try:
                df[col] = df[col].astype(int)
            except:
                df[col] = df[col].astype(float)


    # Get the names and data types of each column in the DataFrame
    column_names = df.columns
    column_types = df.dtypes
    
    return df

    
    # # Map Pandas data types to SQLite data types
    # sql_types = {
    #     'int64': 'INTEGER',
    #     'float64': 'REAL',
    #     'object': 'TEXT',
    #     'bool': 'BOOLEAN',
    #     'datetime64': 'DATETIME',
    # }


    # # Create a list of column definitions in SQLite syntax
    # columns = []
    # formatted_names = []
    # for i in range(len(column_names)):
    #     name = column_names[i].strip()
    #     name = name.replace(' $', "")
    #     name = name.replace(' ', "_")
    #     name = name.replace('/', "")
    #     name = name.replace('(', "")
    #     name = name.replace(')', "")
        
        
    #     formatted_names.append(name)
    #     dtype = column_types[i].name
    #     sql_type = sql_types.get(dtype, 'TEXT')
    #     columns.append(f"{name} {sql_type}")


    # # Create a SQL table definition
    # table_definition = ", ".join(columns)

    # # Connect to an SQLite database
    # conn = sqlite3.connect(f"{file.name.split('.')[0]}.db")

    # # Create a table in the database
    # cursor = conn.cursor()
    # drop_table_query = "DROP TABLE IF EXISTS data;"
    # cursor.execute(drop_table_query)
    
    # print(table_definition)
    # create_table_query = f"CREATE TABLE data ({table_definition})"
    
    # print(create_table_query)
    
    # cursor.execute(create_table_query)

    # # Get the number of columns in the first row of the CSV file
    # num_columns = len(df.columns)

    # # Output the string "(?, ?, ..., ?)" with the appropriate number of placeholders
    # placeholders = "(" + "?, " * (num_columns - 1) + "?)"
    
    # insert_query = """
    # INSERT INTO data (
    # {columns}
    # ) VALUES {placeholders}
    # """
    
    # # Open the CSV file and iterate over its rows
    # for _, row in df.iterrows():
    #     if not pd.isnull(row[0]):
    #         cursor.execute(insert_query.format(columns=",\n".join(formatted_names), placeholders=placeholders), row)

    # conn.commit()
    # conn.close()
    