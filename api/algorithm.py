from django.shortcuts import render, get_object_or_404
import api.models


#called in django created signal for profile and update method in views when data contains ntrp update
def rank_calibration(ntrp_rating, user_id):
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
    api.models.RankUpdate.objects.create(
        tm_ntrp = teammate_ntrp,
        tm_rank = teammate_rank,
        tm_score = score,
        user = user_instance)

def determine_game_type(instance):
    match_type = instance.survey.game_session.match_type
    winner_session = api.models.SurveyResponse.objects.filter(
        survey__id=instance.survey.id, response="Winner")
    winner_session_count = api.models.SurveyResponse.objects.filter(
        survey__id=instance.survey.id, response="Winner").count()
    user_win_count = api.models.SurveyResponse.objects.filter(
        survey__id=instance.survey.id, 
        response="Winner",
        about_user=instance.survey.respondent).count()
    user_latest_rank_update = api.models.RankUpdate.objects.filter(
        user=instance.survey.respondent).latest('created_at')
    user_score = user_latest_rank_update.tm_score

    if match_type == "Doubles":
        if winner_session_count >= 2:
            if user_win_count > 0:
                game_session_guest = (instance.survey.game_session.guest).all()
                game_session_guest = game_session_guest.exclude(
                    user=winner_session[0].survey.respondent)
                game_session_guest = game_session_guest.exclude(
                    user=winner_session[1].survey.respondent)
                game_session_guest = game_session_guest.exclude(status="Pending")
                game_session_guest = game_session_guest.exclude(status="Wait Listed")
                game_session_guest = game_session_guest.exclude(status="Rejected")
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(
                    user=game_session_guest[0].user).latest('created_at')
                player1_score = player1_latest_rank_update.tm_score
                player2_latest_rank_update = api.models.RankUpdate.objects.filter(
                    user=game_session_guest[1].user).latest('created_at')
                player2_score = player2_latest_rank_update.tm_score
                player_avg_score = (player2_score + player1_score)/2
                RankCalculation(user_score, player_avg_score, "win", instance)
            else:
                # Loss
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(
                    user=winner_session[0].survey.respondent).latest('created_at')
                player1_score = player1_latest_rank_update.tm_score
                player2_latest_rank_update = api.models.RankUpdate.objects.filter(
                    user=winner_session[1].survey.respondent).latest('created_at')
                player2_score = player2_latest_rank_update.tm_score
                player_avg_score = (player2_score + player1_score)/2
                RankCalculation(user_score, player_avg_score, "loss", instance)
    elif match_type == "Singles":
        if winner_session_count == 1:
            if user_win_count > 0:
                game_session_guest = (instance.survey.game_session.guest).all()
                game_session_guest = game_session_guest.exclude(
                    user=winner_session[0].survey.respondent)
                game_session_guest = game_session_guest.exclude(status="Pending")
                game_session_guest = game_session_guest.exclude(status="Wait Listed")
                game_session_guest = game_session_guest.exclude(status="Rejected")
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(
                    user=game_session_guest[0].user).latest('created_at')
                player1_score = player1_latest_rank_update.tm_score
                RankCalculation(user_score, player1_score, "win", instance)
                pass
            else:
                player1_latest_rank_update = api.models.RankUpdate.objects.filter(
                    user=winner_session[0].survey.respondent).latest('created_at')
                player1_score = player1_latest_rank_update.tm_score
                RankCalculation(user_score, player1_score, "loss", instance)


def RankCalculation(user_score, opponent_score, win_loss, instance):

    if win_loss == "win":
        if abs(user_score - opponent_score) <= 25:
            user_score += 8
        elif user_score - opponent_score >= 25 and user_score - opponent_score <= 125:
            user_score += 6
        elif opponent_score - user_score >= 25 and opponent_score - user_score <= 125:
            user_score += 10
        elif user_score - opponent_score > 125:
            user_score += 4
        elif opponent_score - user_score > 125:
            user_score += 13
    elif win_loss == "loss":
        if abs(user_score - opponent_score) <= 25:
            user_score -= 8
        elif user_score - opponent_score >= 25 and user_score - opponent_score <= 125:
            user_score -= 10
        elif opponent_score - user_score >= 25 and opponent_score - user_score <= 125:
            user_score -= 6
        elif user_score - opponent_score > 125:
            user_score -= 13
        elif opponent_score - user_score > 125:
            user_score -= 4
    
    if user_score > 450:
        user_score = 450
    if user_score < 0:
        user_score = 0
    
    ScoreToRankConverter(user_score, instance)

def ScoreToRankConverter(user_score, instance):
    
    if user_score <= 25:
        #rank = "TwoFiveBronze"
        teammate_ntrp = '2.5'
        teammate_rank= '#904d00'
    elif user_score <= 50:
        #rank = "TwoFiveSilver"
        teammate_ntrp = '2.5'
        teammate_rank= '#a9a9a9'
    elif user_score <= 75:
        #rank = "TwoFiveGold"
        teammate_ntrp = '5'
        teammate_rank= '#daa520'
    elif user_score <= 100:
        #rank = "ThreeBronze"
        teammate_ntrp = '3'
        teammate_rank= '#904d00'
    elif user_score <= 125:
        #rank = "ThreeSilver"
        teammate_ntrp = '3'
        teammate_rank= '#a9a9a9'
    elif user_score <= 150:
        #rank = "ThreeGold"
        teammate_ntrp = '5'
        teammate_rank= '#daa520'
    elif user_score <= 175:
        #rank = "ThreeFiveBronze"
        teammate_ntrp = '3.5'
        teammate_rank= '#904d00'
    elif user_score <= 200:
        rank = "ThreeFiveSilver"
        teammate_ntrp = '3.5'
        teammate_rank= '#a9a9a9'
    elif user_score <= 225:
        #rank = "ThreeFiveGold"
        teammate_ntrp = '5'
        teammate_rank= '#daa520'
    elif user_score <= 250:
        #rank = "FourBronze"
        teammate_ntrp = '4'
        teammate_rank= '#904d00'
    elif user_score <= 275:
        #rank = "FourSilver"
        teammate_ntrp = '4'
        teammate_rank= '#a9a9a9'
    elif user_score <= 300:
        #rank = "FourGold"
        teammate_ntrp = '4'
        teammate_rank= '#daa520'
    elif user_score <= 325:
        #rank = "FourFiveBronze"
        teammate_ntrp = '4.5'
        teammate_rank= '#904d00'
    elif user_score <= 350:
        #rank = "FourFiveSilver"
        teammate_ntrp = '4.5'
        teammate_rank= '#a9a9a9'
    elif user_score <= 375:
        #rank = "FourFiveGold"
        teammate_ntrp = '4.5'
        teammate_rank= '#daa520'
    elif user_score <= 400:
        #rank = "FiveBronze"
        teammate_ntrp = '5'
        teammate_rank= '#904d00'
    elif user_score <= 425:
        #rank = "FiveSilver"
        teammate_ntrp = '5'
        teammate_rank= '#a9a9a9'
    elif user_score <= 450:
        #rank = "FiveGold"
        teammate_ntrp = '5'
        teammate_rank= '#daa520'
    
    api.models.RankUpdate.objects.create(
        tm_ntrp = teammate_ntrp,
        tm_rank = teammate_rank,
        tm_score = user_score,
        user = instance.survey.respondent)
