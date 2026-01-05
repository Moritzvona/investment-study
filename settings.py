from os import environ

SESSION_CONFIGS = [
    dict(
        name='investment_experiment',
        display_name='Investment Portfolio Study',
        app_sequence=['investment_experiment'],
        num_demo_participants=100,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc='',
)

ROOMS = [
    dict(
        name='study',
        display_name='Investment Study',
    ),
]

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD', 'admin')

DEMO_PAGE_INTRO_HTML = ''
SECRET_KEY = '1234567890'
