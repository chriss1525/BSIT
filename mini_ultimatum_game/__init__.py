from otree.api import *


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
    NAME_IN_URL = 'mini_ultimatum_game'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    ENDOWMENT = 200 # Ksh
    MIN_OFFER = 0
    MAX_OFFER = ENDOWMENT


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    def decision_made(self):
        return all([p.decision in ['Punish', 'Not Punish'] for p in self.get_players()])


class Player(BasePlayer):
    sent_amount = models.CurrencyField(
        min=C.MIN_OFFER, max=C.MAX_OFFER,
        doc="How much do you want to send to player 2?",
        verbose_name='Ksh'
    )

    received_amount = models.CurrencyField(
        doc="Amount received from player 1"
    )

    decision = models.StringField(
        choices=['Punish', 'Not Punish'],
        doc="If you choose to punish, both player1 and player 2 will not get any money."
    )
    payout = models.CurrencyField(
        doc="Players' payout"
    )


# PAGES
class introduction(Page):
    pass


class SendAmount(Page):
    form_model = 'player'
    form_fields = ['sent_amount']

    def vars_for_template(self):
        return {
            'currency': 'Ksh',
        }
    def is_displayed(self):
        return self.id_in_group == 1


class Verdict(Page):
    form_model = 'player'
    form_fields = ['decision']

    def is_displayed(self):
        return self.id_in_group == 3

    def vars_for_template(self):
        player1 = self.group.get_player_by_id(1)
        player2 = self.group.get_player_by_id(2)
        return {
            'sent_amount': player1.sent_amount,
            'player1': player1,
            'player2': player2
        }


class Payout(Page):
    def is_displayed(self):
        return self.id_in_group != 3

    def vars_for_template(self):
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
    def is_displayed(self):
        return self.id_in_group != 1
    pass

class DecisionWait(WaitPage):
    def is_displayed(self):
        return self.id_in_group != 3
    pass


class Results(Page):
    pass


page_sequence = [introduction, SendAmount, SendAmountWait , Verdict, DecisionWait, Payout]
