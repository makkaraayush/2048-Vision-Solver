ROW_LEFT_TABLE = {}
ROW_SCORE_TABLE = {}

def unpack_row(row_val: int):
    return [
        (row_val >> 12) & 0xF,
        (row_val >> 8) & 0xF,
        (row_val >> 4) & 0xF,
        row_val & 0xF
    ]
