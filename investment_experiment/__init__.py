from otree.api import *

doc = """
Investment experiment examining how prior outcomes affect risk-taking behavior.
"""

class C(BaseConstants):
    NAME_IN_URL = 'investment'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    INITIAL_ENDOWMENT = 100
    SAFE_RETURN = 0.03  # 3% for government bond
    RISKY_GAIN = 0.29   # +29% gain scenario
    RISKY_LOSS = -0.15  # -15% loss scenario

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    # Round 1 investment
    risk1_share = models.IntegerField(
        min=0, max=100,
        label="Percentage to invest in Tech Stock (Asset B)"
    )
    
    # Round 1 outcome (randomly assigned)
    r1_outcome_is_gain = models.BooleanField()
    r1_safe_eur = models.FloatField()
    r1_risky_eur = models.FloatField()
    outcome_r1 = models.FloatField()
    performance_r1 = models.FloatField()
    
    # Beliefs and attitudes (measured between rounds)
    wta_sell = models.FloatField(
        min=0, max=200,
        label="Minimum selling price for portfolio (€)"
    )
    belief_stock_prob = models.IntegerField(
        min=0, max=100,
        label="Probability of positive return (%)"
    )
    luck_vs_skill = models.IntegerField(
        min=1, max=7,
        label="Luck (1) vs Skill (7)"
    )
    
    # Round 2 investment
    risk2_share = models.IntegerField(
        min=0, max=100,
        label="Percentage to invest in Tech Stock (Asset B)"
    )
    
    # Round 2 outcome
    r2_outcome_is_gain = models.BooleanField()
    r2_safe_eur = models.FloatField()
    r2_risky_eur = models.FloatField()
    outcome_r2 = models.FloatField()
    performance_r2 = models.FloatField()
    
    # Computed variables
    delta_risk = models.IntegerField()  # risk2 - risk1
    paper_gain = models.BooleanField()  # same as r1_outcome_is_gain
    
    # Demographics
    age = models.IntegerField(min=18, max=100, label="Age")
    gender = models.StringField(
        choices=['male', 'female', 'other', 'prefer not to say'],
        label="Gender"
    )
    education = models.StringField(
        choices=['high_school', 'bachelor', 'master', 'phd', 'other'],
        label="Highest education level"
    )
    field_of_study = models.StringField(
        label="Field of study (if applicable)",
        blank=True
    )
    risk_attitude = models.IntegerField(
        min=1, max=10,
        label="Risk attitude (1=very risk-averse, 10=very risk-seeking)"
    )
    investment_experience = models.StringField(
        choices=['none', 'little', 'moderate', 'extensive'],
        label="Investment experience"
    )
    decision_reasoning = models.LongStringField(
        label="What influenced your Round 2 decision?",
        blank=True
    )

# PAGES
class Welcome(Page):
    pass

class Round1Investment(Page):
    form_model = 'player'
    form_fields = ['risk1_share']

class Round1Feedback(Page):
    @staticmethod
    def before_next_page(player, timeout_happened):
        import random
        
        # Randomly assign gain or loss
        player.r1_outcome_is_gain = random.choice([True, False])
        player.paper_gain = player.r1_outcome_is_gain
        
        # Calculate Round 1 outcome
        safe_amount = C.INITIAL_ENDOWMENT * (100 - player.risk1_share) / 100
        risky_amount = C.INITIAL_ENDOWMENT * player.risk1_share / 100
        
        player.r1_safe_eur = round(safe_amount * (1 + C.SAFE_RETURN), 2)
        
        if player.r1_outcome_is_gain:
            player.r1_risky_eur = round(risky_amount * (1 + C.RISKY_GAIN), 2)
        else:
            player.r1_risky_eur = round(risky_amount * (1 + C.RISKY_LOSS), 2)
        
        player.outcome_r1 = round(player.r1_safe_eur + player.r1_risky_eur, 2)
        player.performance_r1 = round((player.outcome_r1 - C.INITIAL_ENDOWMENT) / C.INITIAL_ENDOWMENT, 4)
    
    @staticmethod
    def vars_for_template(player):
        safe_amount = C.INITIAL_ENDOWMENT * (100 - player.risk1_share) / 100
        risky_amount = C.INITIAL_ENDOWMENT * player.risk1_share / 100
        
        # Pre-calculate for display (actual values set in before_next_page)
        import random
        is_gain = random.choice([True, False])
        
        safe_return = round(safe_amount * (1 + C.SAFE_RETURN), 2)
        if is_gain:
            risky_return = round(risky_amount * (1 + C.RISKY_GAIN), 2)
            return_percent = "+29%"
        else:
            risky_return = round(risky_amount * (1 + C.RISKY_LOSS), 2)
            return_percent = "-15%"
        
        outcome = round(safe_return + risky_return, 2)
        performance = round((outcome - C.INITIAL_ENDOWMENT) / C.INITIAL_ENDOWMENT * 100, 2)
        
        # Store for use
        player.r1_outcome_is_gain = is_gain
        player.paper_gain = is_gain
        player.r1_safe_eur = safe_return
        player.r1_risky_eur = risky_return
        player.outcome_r1 = outcome
        player.performance_r1 = round((outcome - C.INITIAL_ENDOWMENT) / C.INITIAL_ENDOWMENT, 4)
        
        return dict(
            safe_amount=int(safe_amount),
            risky_amount=int(risky_amount),
            safe_return=safe_return,
            risky_return=risky_return,
            outcome=outcome,
            is_gain=is_gain,
            return_percent=return_percent,
            performance_percent=performance
        )

class Beliefs(Page):
    form_model = 'player'
    form_fields = ['wta_sell', 'belief_stock_prob', 'luck_vs_skill']
    
    @staticmethod
    def vars_for_template(player):
        return dict(current_portfolio=player.outcome_r1)

class Round2Investment(Page):
    form_model = 'player'
    form_fields = ['risk2_share']
    
    @staticmethod
    def vars_for_template(player):
        current = player.outcome_r1
        r1_perf = round(player.performance_r1 * 100, 2)
        return dict(
            current_portfolio=current,
            r1_gain=player.r1_outcome_is_gain,
            r1_performance=r1_perf,
            safe_default=round(current * 0.5, 2),
            risky_default=round(current * 0.5, 2)
        )

class Round2Feedback(Page):
    @staticmethod
    def before_next_page(player, timeout_happened):
        import random
        
        # Randomly assign gain or loss for round 2
        player.r2_outcome_is_gain = random.choice([True, False])
        
        # Calculate Round 2 outcome based on Round 1 outcome
        current_portfolio = player.outcome_r1
        safe_amount = current_portfolio * (100 - player.risk2_share) / 100
        risky_amount = current_portfolio * player.risk2_share / 100
        
        player.r2_safe_eur = round(safe_amount * (1 + C.SAFE_RETURN), 2)
        
        if player.r2_outcome_is_gain:
            player.r2_risky_eur = round(risky_amount * (1 + C.RISKY_GAIN), 2)
        else:
            player.r2_risky_eur = round(risky_amount * (1 + C.RISKY_LOSS), 2)
        
        player.outcome_r2 = round(player.r2_safe_eur + player.r2_risky_eur, 2)
        player.performance_r2 = round((player.outcome_r2 - current_portfolio) / current_portfolio, 4)
        
        # Calculate delta risk
        player.delta_risk = player.risk2_share - player.risk1_share
    
    @staticmethod
    def vars_for_template(player):
        current_portfolio = player.outcome_r1
        safe_amount = current_portfolio * (100 - player.risk2_share) / 100
        risky_amount = current_portfolio * player.risk2_share / 100
        
        import random
        is_gain = random.choice([True, False])
        
        safe_return = round(safe_amount * (1 + C.SAFE_RETURN), 2)
        if is_gain:
            risky_return = round(risky_amount * (1 + C.RISKY_GAIN), 2)
        else:
            risky_return = round(risky_amount * (1 + C.RISKY_LOSS), 2)
        
        outcome = round(safe_return + risky_return, 2)
        total_return = round(outcome - C.INITIAL_ENDOWMENT, 2)
        total_return_percent = round((outcome - C.INITIAL_ENDOWMENT) / C.INITIAL_ENDOWMENT * 100, 1)
        
        # Store values
        player.r2_outcome_is_gain = is_gain
        player.r2_safe_eur = safe_return
        player.r2_risky_eur = risky_return
        player.outcome_r2 = outcome
        player.performance_r2 = round((outcome - current_portfolio) / current_portfolio, 4)
        player.delta_risk = player.risk2_share - player.risk1_share
        
        return dict(
            is_gain=is_gain,
            r1_outcome=player.outcome_r1,
            outcome=outcome,
            total_return=total_return,
            total_return_percent=total_return_percent
        )

class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'education', 'field_of_study', 
                   'risk_attitude', 'investment_experience', 'decision_reasoning']

class Results(Page):
    @staticmethod
    def vars_for_template(player):
        total_return = round(player.outcome_r2 - C.INITIAL_ENDOWMENT, 2)
        total_return_percent = round((player.outcome_r2 - C.INITIAL_ENDOWMENT) / C.INITIAL_ENDOWMENT * 100, 1)
        return dict(
            initial=C.INITIAL_ENDOWMENT,
            r1_outcome=player.outcome_r1,
            final_outcome=player.outcome_r2,
            total_return=total_return,
            total_return_percent=total_return_percent,
            r1_gain=player.r1_outcome_is_gain,
            r2_gain=player.r2_outcome_is_gain
        )

page_sequence = [
    Welcome,
    Round1Investment,
    Round1Feedback,
    Beliefs,
    Round2Investment,
    Round2Feedback,
    Demographics,
    Results
]
