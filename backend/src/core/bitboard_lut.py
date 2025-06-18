ROW_LEFT_TABLE = {}
ROW_SCORE_TABLE = {}

def unpack_row(row_val: int):
    return [
        (row_val >> 12) & 0xF,
        (row_val >> 8) & 0xF,
        (row_val >> 4) & 0xF,
        row_val & 0xF
    ]

def pack_row(c0: int, c1: int, c2: int, c3: int) -> int:
    return ((c0 & 0xF) << 12) | ((c1 & 0xF) << 8) | ((c2 & 0xF) << 4) | (c3 & 0xF)
