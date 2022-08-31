from django.shortcuts import render, get_object_or_404
import api.models


#called in django created signal for profile and update method in views when data contains ntrp update
def RankCalibration(ntrp_rating, user_id):
    if ntrp_rating == '2.5':
        teammate_ntrp = '2.5'
        teammate_rank= '#904d00'
        score = 0
    elif ntrp_rating == '3':
        teammate_ntrp = '3'
        teammate_rank= '#904d00'
        score = 75
    elif ntrp_rating == '3.5':
        teammate_ntrp = '3.5'
        teammate_rank= '#904d00'
        score = 150
    elif ntrp_rating == '4':
        teammate_ntrp = '4'
        teammate_rank= '#904d00'
        score = 225
    elif ntrp_rating == '4.5':
        teammate_ntrp = '4.5'
        teammate_rank= '#904d00'
        score = 300
    elif ntrp_rating == '5':
        teammate_ntrp = '5'
        teammate_rank= '#904d00'
        score = 375
    
    user_instance = get_object_or_404(api.models.User, id=user_id)
    api.models.RankUpdate.objects.create(tm_ntrp = teammate_ntrp, tm_rank = teammate_rank, tm_score = score, user = user_instance)

def determine_game_type(instance):
    match_type = instance.survey.game_session.match_type
    winner_session= api.models.SurveyResponse.objects.filter(survey__id=instance.survey.id, response="Winner")
    winner_session_count = api.models.SurveyResponse.objects.filter(survey__id=instance.survey.id, response="Winner").count()
    user_win_count = api.models.SurveyResponse.objects.filter(survey__id=instance.survey.id, response="Winner",about_user=instance.survey.respondent).count()
    user_latest_rank_update = api.models.RankUpdate.objects.filter(user = instance.survey.respondent).latest('tm_score')
    user_score = user_latest_rank_update.tm_score
    if match_type == "Doubles":
        if winner_session_count >= 2:
            if user_win_count > 0:
                game_session_guest = (instance.survey.game_session.guest).all()
                game_session_guest = game_session_guest.exclude(user=winner_session[0].survey.respondent)
                game_session_guest = game_session_guest.exclude(user=winner_session[1].survey.respondent)
                game_session_guest = game_session_guest.exclude(status="Pending")
                game_session_guest = game_session_guest.exclude(status="Wait Listed")
                game_session_guest = game_session_guest.exclude(status="Rejected")
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(user = game_session_guest[0].user).latest('tm_score')
                player1_score = player1_latest_rank_update.tm_score
                player2_latest_rank_update = api.models.RankUpdate.objects.filter(user = game_session_guest[1].user).latest('tm_score')
                player2_score = player2_latest_rank_update.tm_score
                player_avg_score = (player2_score + player1_score)/2
                RankCalculation(user_score, player_avg_score, "win")
            else:
                #lose
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(user = winner_session[0].survey.respondent).latest('tm_score')
                player1_score = player1_latest_rank_update.tm_score
                player2_latest_rank_update = api.models.RankUpdate.objects.filter(user = winner_session[1].survey.respondent).latest('tm_score')
                player2_score = player2_latest_rank_update.tm_score
                player_avg_score = (player2_score + player1_score)/2
                RankCalculation(user_score, player_avg_score, "loss")
    elif match_type == "Singles":
        if winner_session_count == 1:
            if user_win_count > 0:
                game_session_guest = (instance.survey.game_session.guest).all()
                game_session_guest = game_session_guest.exclude(user=winner_session[0].survey.respondent)
                game_session_guest = game_session_guest.exclude(status="Pending")
                game_session_guest = game_session_guest.exclude(status="Wait Listed")
                game_session_guest = game_session_guest.exclude(status="Rejected")
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(user = game_session_guest[0].user).latest('tm_score')
                player1_score = player1_latest_rank_update.tm_score
                RankCalculation(user_score, player1_score, "win")
                pass
            else:
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(user = winner_session[0].survey.respondent).latest('tm_score')
                player1_score = player1_latest_rank_update.tm_score
                RankCalculation(user_score, player1_score, "loss")


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
