ROW_LEFT_TABLE = {}
ROW_SCORE_TABLE = {}

def transpose_board(b: int) -> int:
    a1 = b & 0xF0F00F0FF0F00F0F
    a2 = b & 0x0000F0F00000F0F0
    a3 = b & 0x0F0F00000F0F0000
    a = a1 | (a2 << 12) | (a3 >> 12)
    b1 = a & 0xFF00FF0000FF00FF
    b2 = a & 0x00FF00FF00000000
    b3 = a & 0x00000000FF00FF00
    return b1 | (b2 >> 24) | (b3 << 24)
