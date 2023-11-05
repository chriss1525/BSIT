from otree.api import *


class Constants(BaseConstants):
    name_in_url = 'exit_survey'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    capital_city = models.StringField(
        choices=['Kisumu', 'Nairobi', 'Mombasa'],
        label='Q1. What is the capital city of Kenya?'
    )
    math_answer = models.IntegerField(
        label='Q2. What is 14 + 15?',
        # Define a range of acceptable answers
        min=29,
        max=29
    )
    population_answer = models.IntegerField(
        label='Q3. What is the population of Kenya?'
    )


class ExitSurvey(Page):
    form_model = Player
    form_fields = ['capital_city', 'math_answer', 'population_answer']

    def before_next_page(self):
        # Define rounds so that the questions are only displayed if the previous question was answered correctly
        if self.round_number == 1:
            if self.participant.capital_city == 'Nairobi':
                self.participant.vars['question1_correct'] = True
            else:
                self.participant.vars['question1_correct'] = False
        elif self.round_number == 2:
            if self.participant.math_answer == 29:
                self.participant.vars['question2_correct'] = True
            else:
                self.participant.vars['question2_correct'] = False
        elif self.round_number == 3:
            if self.participant.population_answer == '50000000':
                self.participant.vars['question3_correct'] = True
            else:
                self.participant.vars['question3_correct'] = False

    def is_displayed(self):
        # check if answers to previous questions are correct
        if self.round_number == 1:
            return True
        elif self.round_number == 2:
            return self.participant.vars.get('question1_correct', False)
        elif self.round_number == 3:
            return self.participant.vars.get('question2_correct', False)

    def vars_for_template(self):
        return {
            'question1_correct': self.participant.vars.get('question1_correct', None),
            'question2_correct': self.participant.vars.get('question2_correct', None),
        }


page_sequence = [ExitSurvey]
