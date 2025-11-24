def calculate_elo(player_a, player_b, result_a, k=32):
    """
    result_a: 1 = win, 0.5 = draw, 0 = lose
    """
    expected_a = 1 / (1 + 10 ** ((player_b - player_a) / 400))
    new_a = player_a + k * (result_a - expected_a)
    return round(new_a)
