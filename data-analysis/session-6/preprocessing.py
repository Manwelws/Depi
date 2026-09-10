import pandas as pd

def read_data_file(path):
    """
    Reads a data file (csv) from the specified path and returns a pandas DataFrame.

    Parameters:
    path (str): The file path to the data file.

    Returns:
    pd.DataFrame: A DataFrame containing the data from the file.
    """
    try:
        data = pd.read_csv(path)
        return data
    except Exception as e:
        print(f"Error reading the data file: {e}")
        return None

def drop_unnecessary_features(df, cols_to_drop):
    """
    Drops specified columns from the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame from which to drop columns.
    cols_to_drop (list): A list of column names to drop.

    Returns:
    pd.DataFrame: A DataFrame with the specified columns dropped.
    """
    try:
        df_dropped = df.drop(columns=cols_to_drop)
        return df_dropped
    except KeyError as e:
        print(f"Error dropping columns: {e}")
        return df

def check_data_type(df):
    """
    Checks the data types of each column in the DataFrame and returns a transposed DataFrame
    with column name, data type, and number of unique values.

    Parameters:
    df (pd.DataFrame): The DataFrame to check.

    Returns:
    pd.DataFrame: A transposed DataFrame with index as column names and columns: 
                  'DataType', 'UniqueValues'
    """

    
    info = {
        'DataType': df.dtypes,
        'UniqueValues': df.nunique()
    }
    info_df = pd.DataFrame(info)
    return info_df.T