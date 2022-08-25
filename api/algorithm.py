def RankCalculation(user_score, oponent_score, win_loss):
    if win_loss == "win":
        if abs(user_score - oponent_score) <= 25:
            user_score += 8
        elif user_score - oponent_score >= 25 and user_score - oponent_score <= 125:
            user_score += 6
        elif oponent_score - user_score >= 25 and oponent_score - user_score <= 125:
            user_score += 10
        elif user_score - oponent_score > 125:
            user_score += 4
        elif oponent_score - user_score > 125:
            user_score += 13
    elif win_loss == "loss":
        if abs(user_score - oponent_score) <= 25:
            user_score -= 8
        elif user_score - oponent_score >= 25 and user_score - oponent_score <= 125:
            user_score -= 10
        elif oponent_score - user_score >= 25 and oponent_score - user_score <= 125:
            user_score -= 6
        elif user_score - oponent_score > 125:
            user_score -= 13
        elif oponent_score - user_score > 125:
            user_score -= 4
    
    if user_score > 450:
        user_score = 450
    if user_score < 0:
        user_score = 0

    return user_score