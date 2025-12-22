def get_k_factor(rating):
    if rating < 1300:
        return 24
    return 32

def calculate_elo(player_a_rating, player_b_rating, result_a):
    """
    Calculates the new ELO ratings for two players.
    
    Args:
        player_a_rating (int): Current rating of Player A
        player_b_rating (int): Current rating of Player B
        result_a (float): Result for Player A (1.0 = win, 0.5 = draw, 0.0 = loss)
        
    Returns:
        tuple: (new_rating_a, new_rating_b)
    """
    # 1. Determine K-factors
    k_a = get_k_factor(player_a_rating)
    k_b = get_k_factor(player_b_rating)
    
    # 2. Calculate Expected Scores
    # Ea = 1 / (1 + 10 ^ ((Rb - Ra) / 400))
    expected_a = 1 / (1 + 10 ** ((player_b_rating - player_a_rating) / 400))
    expected_b = 1 - expected_a # Zero-sum game
    
    # 3. Calculate New Ratings
    # R' = R + K * (S - E)
    result_b = 1.0 - result_a
    
    new_rating_a = player_a_rating + k_a * (result_a - expected_a)
    new_rating_b = player_b_rating + k_b * (result_b - expected_b)
    
    return round(new_rating_a), round(new_rating_b)
