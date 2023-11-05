from otree.api import *
from django.core.validators import MinValueValidator, MaxValueValidator


doc = """
Mini ultimatum game that takes 3 players.
Player 1 is given Ksh200 and is asked to send som to player 2.
player 2 waits to recieve money from player 1
player 3 waits for player 1 to make an offer to player 2, \
he sees the amount before player 2. 
Depending on how he feels about the amount, player 3 can punish or not punish player 1.
If player 3 punishes player 1, both player 1 and 2 do not get any money.
If player 3 does not punish player 1, player 1 gets his amount - amount sent to player 2\
and player 2 gets the amount sent to him by player 1.
"""


class C(BaseConstants):
    """Constants for mini_ultimatum_game."""
    NAME_IN_URL = 'mini_ultimatum_game'
    PLAYERS_PER_GROUP = 3
    # Chose to have the game run just once
    NUM_ROUNDS = 1
    ENDOWMENT = 200
    MIN_OFFER = 0
    MAX_OFFER = ENDOWMENT


class Subsession(BaseSubsession):
    """Defines subsession for mini_ultimatum_game."""
    pass


class Group(BaseGroup):
    """Defines methods related to the group of players."""
    def decision_made(self):
        """Returns True if all players have made a decision."""
        # check if all players have made a decision
        return all([p.decision in ['Punish', 'Not Punish'] for p in self.get_players()])


class Player(BasePlayer):
    """Defines player roles and actions."""
    # define player roles and actions

    # player 1 sends amount to player 2
    sent_amount = models.CurrencyField(
        min=C.MIN_OFFER, max=C.MAX_OFFER,
        doc="How much do you want to send to player 2?",
        verbose_name='Ksh'
    )

    # player 2 waits to receive amount from player 1
    received_amount = models.CurrencyField(
        doc="Amount received from player 1"
    )

    # player 3 decides whether player 1's offer is fair or not
    decision = models.StringField(
        choices=['Punish', 'Not Punish'],
        doc="If you choose to punish, both player1 and player 2 will not get any money."
    )
    payout = models.CurrencyField(
        doc="Players' payout"
    )

    # exit survey questions
    # Define the survey questions
    capital_city = models.StringField(
        choices=['Kisumu', 'Nairobi', 'Mombasa'],
        label='Q1. What is the capital city of Kenya?'
    )
    math_question = models.IntegerField(
        label='Q2. What is 14 + 15?',
        # Define a range of acceptable answers for the math question
        min=20,
        max=35,
        # try to confine acceptable answer within a range
        validators=[MinValueValidator(29), MaxValueValidator(29)]
    )
    population_question = models.IntegerField(
        label='Q3. What is the population of Kenya?'
    )


# PAGES
class introduction(Page):
    """Gives instructions for the mini_ultimatum_game."""""
    pass


class SendAmount(Page):
    """Page 1: Player 1 sends amount to player 2."""
    form_model = 'player'
    form_fields = ['sent_amount']

    def vars_for_template(self):
        """Returns the currency for the game."""
        # attempt to change the currency to Ksh
        return {
            'currency': 'Ksh',
        }

    def is_displayed(self):
        """Display the page to player 1 only."""
        return self.id_in_group == 1


class Verdict(Page):
    """Page 2: Player 3 decides whether player 1's offer is fair or not."""""
    form_model = 'player'
    form_fields = ['decision']

    def is_displayed(self):
        """Display the page to player 3 only."""
        return self.id_in_group == 3

    def vars_for_template(self):
        """Returns the amount sent by player 1."""
        player1 = self.group.get_player_by_id(1)
        player2 = self.group.get_player_by_id(2)
        return {
            'sent_amount': player1.sent_amount,
            'player1': player1,
            'player2': player2
        }


class Payout(Page):
    """Page 3: Player 1 and 2 see their payout."""
    def is_displayed(self):
        """Display the page to player 1 and 2 only."""
        return self.id_in_group != 3

    def vars_for_template(self):
        """Returns the payout for each player."""
        player1 = self.group.get_player_by_id(1)
        player2 = self.group.get_player_by_id(2)
        player3 = self.group.get_player_by_id(3)
        if player3.decision == 'Punish':
            player1.payout = 0
            player2.payout = 0
            player3.payout = 0
        else:
            player1.payout = C.ENDOWMENT - player1.sent_amount
            player2.payout = player1.sent_amount
            player3.payout = 0
        return {
            'player1': player1,
            'player2': player2,
            'player3': player3
        }


class SendAmountWait(WaitPage):
    """Wait page between page 1 and 2."""
    def is_displayed(self):
        """Display the wait page to player 2 and 3 only."""
        # let player 1 send an amount
        return self.id_in_group != 1


class DecisionWait(WaitPage):
    """Wait page between page 2 and 3."""
    def is_displayed(self):
        """Display the wait page to player 1 and 2 only."""
        # let player 3 make a decision
        return self.id_in_group != 3


class ExitSurvey(Page):
    """ Exit survey"""
    # Although implemented, the exit survey does not work as instructed
    # the survey accepts any answer given even for the math question despite saveguards
    # The survey page is displayed after the game though.
    form_model = 'player'
    form_fields = ['capital_city', 'math_question', 'population_question']

    @staticmethod
    def is_displayed(player):
        """Display the exit survey on the last round only."""
        return player.round_number == C.NUM_ROUNDS

    
page_sequence = [introduction, SendAmount,
                 SendAmountWait, Verdict, DecisionWait, Payout, ExitSurvey]
