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
    
    print(user_score)
    return user_score

def ScoreToRankConverter(user_score):
    
    if user_score <= 25:
        rank = "TwoFiveBronze"
    elif user_score <= 50:
        rank = "TwoFiveSilver"
    elif user_score <= 75:
        rank = "TwoFiveGold"
    elif user_score <= 100:
        rank = "ThreeBronze"
    elif user_score <= 125:
        rank = "ThreeSilver"
    elif user_score <= 150:
        rank = "ThreeGold"
    elif user_score <= 175:
        rank = "ThreeFiveBronze"
    elif user_score <= 200:
        rank = "ThreeFiveSilver"
    elif user_score <= 225:
        rank = "ThreeFiveGold"
    elif user_score <= 250:
        rank = "FourBronze"
    elif user_score <= 275:
        rank = "FourSilver"
    elif user_score <= 300:
        rank = "FourGold"
    elif user_score <= 325:
        rank = "FourFiveBronze"
    elif user_score <= 350:
        rank = "FourFiveSilver"
    elif user_score <= 375:
        rank = "FourFiveGold"
    elif user_score <= 400:
        rank = "FiveBronze"
    elif user_score <= 425:
        rank = "FiveSilver"
    elif user_score <= 450:
        rank = "FiveGold"
    
    print(rank)
    return rank
