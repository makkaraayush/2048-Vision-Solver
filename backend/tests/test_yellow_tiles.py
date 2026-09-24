def test_yellow_ambiguity():
    c128 = (237, 207, 114)
    c256 = (237, 204, 97)
    delta_e = sum(abs(a - b) for a, b in zip(c128, c256))
    assert delta_e < 25
