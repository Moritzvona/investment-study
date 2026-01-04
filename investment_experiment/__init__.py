from otree.api import *
import random

doc = """Investment Risk Experiment"""

class C(BaseConstants):
    NAME_IN_URL = 'investment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    INITIAL_ENDOWMENT = 100
    SAFE_RETURN = 1.03
    RISKY_RETURN_UP = 1.25
    RISKY_RETURN_DOWN = 0.85
    RISKY_PROB_UP = 0.5

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    risk1_share = models.IntegerField(min=0, max=100, initial=50)
    r1_outcome_is_gain = models.BooleanField()
    r1_safe_eur = models.FloatField()
    r1_risky_eur = models.FloatField()
    outcome_r1 = models.FloatField()
    performance_r1 = models.FloatField()
    wta_sell = models.FloatField(min=0, max=500)
    belief_stock_prob = models.IntegerField(min=0, max=100)
    luck_vs_skill = models.IntegerField(min=1, max=7)
    risk2_share = models.IntegerField(min=0, max=100, initial=50)
    r2_outcome_is_gain = models.BooleanField()
    r2_safe_eur = models.FloatField()
    r2_risky_eur = models.FloatField()
    outcome_r2 = models.FloatField()
    performance_r2 = models.FloatField()
    delta_risk = models.IntegerField()
    paper_gain = models.BooleanField()
    age = models.IntegerField(min=18, max=100)
    gender = models.StringField(choices=[['male','Male'],['female','Female'],['diverse','Diverse'],['no_answer','Prefer not to say']])
    education = models.StringField(choices=[['high_school','High School'],['bachelor','Bachelor'],['master','Master'],['phd','PhD'],['other','Other']])
    field_of_study = models.StringField(blank=True)
    risk_attitude = models.IntegerField(min=1, max=10)
    investment_experience = models.StringField(choices=[['none','No experience'],['little','Little (<1 year)'],['moderate','Moderate (1-3 years)'],['experienced','Significant (>3 years)']])
    decision_reasoning = models.LongStringField(blank=True)

class Welcome(Page):
    pass

class Round1Investment(Page):
    form_model = 'player'
    form_fields = ['risk1_share']
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # Calculate Round 1 outcome ONCE when leaving this page
        risky_pct = player.risk1_share / 100
        player.r1_risky_eur = round(C.INITIAL_ENDOWMENT * risky_pct, 2)
        player.r1_safe_eur = round(C.INITIAL_ENDOWMENT * (1 - risky_pct), 2)
        player.r1_outcome_is_gain = random.random() < C.RISKY_PROB_UP
        if player.r1_outcome_is_gain:
            risky_return = player.r1_risky_eur * C.RISKY_RETURN_UP
        else:
            risky_return = player.r1_risky_eur * C.RISKY_RETURN_DOWN
        safe_return = player.r1_safe_eur * C.SAFE_RETURN
        player.outcome_r1 = round(safe_return + risky_return, 2)
        player.performance_r1 = round((player.outcome_r1 - 100) / 100, 4)
        player.paper_gain = player.outcome_r1 > C.INITIAL_ENDOWMENT

class Round1Feedback(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            risky_amount=player.r1_risky_eur,
            safe_amount=player.r1_safe_eur,
            is_gain=player.r1_outcome_is_gain,
            outcome=player.outcome_r1,
            performance_percent=round(player.performance_r1 * 100, 1),
            return_percent="+25%" if player.r1_outcome_is_gain else "-15%",
            safe_return=round(player.r1_safe_eur * C.SAFE_RETURN, 2),
            risky_return=round(player.r1_risky_eur * (C.RISKY_RETURN_UP if player.r1_outcome_is_gain else C.RISKY_RETURN_DOWN), 2)
        )

class BeliefsAttitudes(Page):
    form_model = 'player'
    form_fields = ['wta_sell', 'belief_stock_prob', 'luck_vs_skill']
    
    @staticmethod
    def vars_for_template(player):
        return dict(
            current_portfolio=player.outcome_r1,
            is_gain=player.paper_gain,
            performance_percent=round(player.performance_r1 * 100, 1)
        )

class Round2Investment(Page):
    form_model = 'player'
    form_fields = ['risk2_share']
    
    @staticmethod
    def vars_for_template(player):
        return dict(
            current_portfolio=player.outcome_r1,
            is_gain=player.paper_gain
        )
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        # Calculate Round 2 outcome ONCE when leaving this page
        risky_pct = player.risk2_share / 100
        player.r2_risky_eur = round(player.outcome_r1 * risky_pct, 2)
        player.r2_safe_eur = round(player.outcome_r1 * (1 - risky_pct), 2)
        player.r2_outcome_is_gain = random.random() < C.RISKY_PROB_UP
        if player.r2_outcome_is_gain:
            risky_return = player.r2_risky_eur * C.RISKY_RETURN_UP
        else:
            risky_return = player.r2_risky_eur * C.RISKY_RETURN_DOWN
        safe_return = player.r2_safe_eur * C.SAFE_RETURN
        player.outcome_r2 = round(safe_return + risky_return, 2)
        player.performance_r2 = round((player.outcome_r2 - player.outcome_r1) / player.outcome_r1, 4)
        player.delta_risk = player.risk2_share - player.risk1_share

class Round2Feedback(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            r1_outcome=player.outcome_r1,
            risky_amount=player.r2_risky_eur,
            safe_amount=player.r2_safe_eur,
            is_gain=player.r2_outcome_is_gain,
            outcome=player.outcome_r2,
            performance_percent=round(player.performance_r2 * 100, 1),
            delta_risk=player.delta_risk,
            return_percent="+25%" if player.r2_outcome_is_gain else "-15%",
            safe_return=round(player.r2_safe_eur * C.SAFE_RETURN, 2),
            risky_return=round(player.r2_risky_eur * (C.RISKY_RETURN_UP if player.r2_outcome_is_gain else C.RISKY_RETURN_DOWN), 2),
            total_return=round(player.outcome_r2 - C.INITIAL_ENDOWMENT, 2),
            total_return_percent=round((player.outcome_r2 - C.INITIAL_ENDOWMENT) / C.INITIAL_ENDOWMENT * 100, 1)
        )

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'field_of_study', 'risk_attitude', 'investment_experience', 'decision_reasoning']

class Results(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            initial=C.INITIAL_ENDOWMENT,
            r1_outcome=player.outcome_r1,
            final_outcome=player.outcome_r2,
            total_return=round(player.outcome_r2 - C.INITIAL_ENDOWMENT, 2),
            total_return_percent=round((player.outcome_r2 - C.INITIAL_ENDOWMENT) / C.INITIAL_ENDOWMENT * 100, 1),
            r1_gain=player.paper_gain,
            r2_gain=player.r2_outcome_is_gain
        )

page_sequence = [Welcome, Round1Investment, Round1Feedback, BeliefsAttitudes, Round2Investment, Round2Feedback, Demographics, Results]
