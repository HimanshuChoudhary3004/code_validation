import pandas as pd

def load_input_data(mode):
    """
    Loads the appropriate input CSV based on the active mode.
    """
    if mode == 'code_generation':
        return pd.read_csv('input/code_generation.csv').to_dict(orient='records')
    elif mode == 'code_enhancement':
        return pd.read_csv('input/code_enhancement.csv').to_dict(orient='records')
    else:
        raise ValueError(f"Unsupported mode: {mode}")
