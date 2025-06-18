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

def init_tables():
    for r in range(65536):
        cells = unpack_row(r)
        non_zero = [c for c in cells if c != 0]
        merged = []
        score = 0
        skip = False
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                val = non_zero[i] + 1
                merged.append(val)
                score += (1 << val)
                skip = True
            else:
                merged.append(non_zero[i])
        while len(merged) < 4:
            merged.append(0)
        ROW_LEFT_TABLE[r] = pack_row(*merged)
        ROW_SCORE_TABLE[r] = score

init_tables()
