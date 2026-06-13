STAGES = [
"""\
  +---+
  |   |
      |
      |
      |
      |
=========""",
"""\
  +---+
  |   |
  O   |
      |
      |
      |
=========""",
"""\
  +---+
  |   |
  O   |
  |   |
      |
      |
=========""",
"""\
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========""",
"""\
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========""",
"""\
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========""",
"""\
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========""",
]

MAX_WRONG = {'easy': 8, 'medium': 7, 'hard': 6, 'nightmare': 5}
EVIL_MODE = {'easy': False, 'medium': False, 'hard': True, 'nightmare': True}

FALLBACK = {
    'easy': [
        ('BANJO',  'Music'),       ('BLITZ',  'Events'),      ('BRAVE',  'Traits'),
        ('CRISP',  'Adjectives'),  ('CRYPT',  'Places'),      ('DWARF',  'Fantasy'),
        ('FJORD',  'Geography'),   ('FLAME',  'Elements'),    ('FLUTE',  'Music'),
        ('GLYPH',  'Typography'),  ('JEWEL',  'Gems'),        ('KNEEL',  'Actions'),
        ('LYMPH',  'Biology'),     ('OCEAN',  'Nature'),      ('PLUMB',  'Building'),
        ('QUEEN',  'Royalty'),     ('QUIRK',  'Traits'),      ('TRYST',  'Events'),
        ('WALTZ',  'Dance'),       ('WITCH',  'Supernatural'),
    ],
    'medium': [
        ('ALCHEMY',   'Science'),      ('BIZARRE',   'Adjectives'),  ('BLOTCH',  'Marks'),
        ('CRYPTIC',   'Adjectives'),   ('DYNASTY',   'History'),     ('ECLIPSE', 'Astronomy'),
        ('FLUMMOX',   'Actions'),      ('GLITCH',    'Technology'),  ('HIJACK',  'Actions'),
        ('JIGSAW',    'Puzzles'),      ('JUKEBOX',   'Items'),       ('KERFUFFLE','Events'),
        ('LABYRINTH', 'Places'),       ('MISCHIEF',  'Traits'),      ('NOXIOUS', 'Adjectives'),
        ('PHANTOM',   'Supernatural'), ('QUARTZ',    'Minerals'),    ('RANSACK', 'Actions'),
        ('SERPENT',   'Animals'),      ('SPHINX',    'Mythology'),   ('TYCOON',  'People'),
        ('UNKEMPT',   'Adjectives'),   ('VERDICT',   'Law'),         ('VORTEX',  'Physics'),
        ('WAMPUM',    'History'),      ('WHIMSY',    'Qualities'),   ('ZEALOUS', 'Traits'),
        ('ZEPHYR',    'Weather'),
    ],
    'hard': [
        ('ABSQUATULATE',   'Actions'),    ('BORBORYGMUS',    'Medical'),
        ('CALLIPYGIAN',    'Adjectives'), ('DEFENESTRATE',   'Actions'),
        ('DISCOMBOBULATE', 'Actions'),    ('FLABBERGASTED',  'Emotions'),
        ('FLIBBERTIGIBBET','People'),     ('GOBBLEDYGOOK',   'Language'),
        ('GOBSMACKED',     'Emotions'),   ('HORNSWOGGLE',    'Actions'),
        ('HULLABALOO',     'Sounds'),     ('IMBROGLIO',      'Events'),
        ('JACKANAPES',     'People'),     ('LOLLYGAG',       'Actions'),
        ('MELLIFLUOUS',    'Adjectives'), ('MOLLYCODDLE',    'Actions'),
        ('NEFARIOUS',      'Adjectives'), ('OBSTREPEROUS',   'Adjectives'),
        ('ONOMATOPOEIA',   'Language'),   ('PERSNICKETY',    'Adjectives'),
        ('QUIZZICAL',      'Adjectives'), ('RAGAMUFFIN',     'People'),
        ('SKULLDUGGERY',   'Actions'),    ('SYCOPHANT',      'People'),
        ('TARADIDDLE',     'Language'),   ('TRUCULENT',      'Adjectives'),
        ('VEXILLOLOGY',    'Sciences'),   ('WHIPPERSNAPPER', 'People'),
        ('WIDDERSHINS',    'Directions'), ('ZYMURGY',        'Sciences'),
    ],
    'nightmare': [
        # ── Vowel-starved / consonant clusters ───────────────────────────────
        ('CRWTH',        'Music'),         ('GLYPH',        'Typography'),
        ('LYMPH',        'Biology'),       ('MYRRH',        'Substances'),
        ('NYMPH',        'Mythology'),     ('PSYCH',        'Actions'),
        ('PYGMY',        'Anthropology'),  ('RHYTHMS',      'Music'),
        ('SYLPH',        'Mythology'),     ('SYZYGY',       'Astronomy'),
        ('TRYST',        'Events'),        ('WYRM',         'Fantasy'),
        ('CRYPT',        'Architecture'),  ('FLYBY',        'Aviation'),
        ('GYPSUM',       'Minerals'),      ('KNURL',        'Engineering'),
        ('NYMPHS',       'Mythology'),     ('SCYTHE',       'Tools'),
        ('SYLPHS',       'Mythology'),     ('TRYSTS',       'Events'),
        ('WHELK',        'Marine'),        ('XYLYL',        'Chemistry'),
        ('WALTZ',        'Dance'),         ('GLITZ',        'Entertainment'),
        ('BORAX',        'Chemistry'),     ('TOPAZ',        'Minerals'),
        # ── 6-letter unusual clusters ─────────────────────────────────────────
        ('BROUHAHA',     'Events'),        ('BULWARK',      'Architecture'),
        ('CZAR',         'Titles'),        ('FJORD',        'Geography'),
        ('GEWGAW',       'Objects'),       ('GNARLY',       'Adjectives'),
        ('KNAVE',        'People'),        ('KVETCH',       'Actions'),
        ('PHLEGM',       'Biology'),       ('PIZZAZZ',      'Qualities'),
        ('WRAITH',       'Supernatural'),  ('XANTHIC',      'Adjectives'),
        ('COCCYX',       'Anatomy'),       ('SPHINX',       'Mythology'),
        ('ZEPHYR',       'Meteorology'),   ('SPHYNX',       'Breed'),
        ('ZENITH',       'Astronomy'),     ('PHYLLO',       'Cooking'),
        ('PSYCHE',       'Psychology'),    ('WYVERN',       'Fantasy'),
        ('GNEISS',       'Geology'),       ('SCHISM',       'Religion'),
        ('FROWZY',       'Adjectives'),    ('SCRIMP',       'Finance'),
        ('FLUXED',       'Physics'),       ('THRONG',       'People'),
        ('PHYLUM',       'Biology'),       ('CRYPTS',       'Architecture'),
        ('KLUDGE',       'Computing'),     ('SCHLEP',       'Actions'),
        ('KLUTZY',       'Adjectives'),    ('SPLOTCH',      'Patterns'),
        ('SQUELCH',      'Sounds'),        ('BLOTCH',       'Patterns'),
        # ── 7-letter ──────────────────────────────────────────────────────────
        ('COXSWAIN',     'Nautical'),      ('GYPSY',        'People'),
        ('KNICKKNACK',   'Objects'),       ('SCHNOZZLE',    'Anatomy'),
        ('ZEITGEIST',    'Philosophy'),    ('CZARINA',      'Titles'),
        ('EPITAPH',      'Writing'),       ('GRYPHON',      'Fantasy'),
        ('NYMPHAL',      'Entomology'),    ('ZYMURGY',      'Biochemistry'),
        ('TWELFTH',      'Numbers'),       ('SYMPTOM',      'Medicine'),
        ('GLYCINE',      'Biochemistry'),  ('THYSELF',      'Archaic'),
        ('SCHLOCK',      'Adjectives'),    ('SCHMALTZ',     'Cooking'),
        ('WRATHFUL',     'Emotions'),      ('SQUELCHY',     'Adjectives'),
        ('CRYPTIDS',     'Cryptozoology'), ('ZYMOSIS',      'Biology'),
        ('RHYTHMIC',     'Music'),         ('CHTHONIC',     'Mythology'),
        ('PSYCHICS',     'Supernatural'),  ('GRAPHIC',      'Art'),
        ('WYVERNS',      'Fantasy'),       ('KVETCHY',      'Adjectives'),
        ('SPLOTCHY',     'Adjectives'),    ('FLUXION',      'Mathematics'),
        # ── 8-letter ──────────────────────────────────────────────────────────
        ('VUVUZELA',     'Music'),         ('RAZZMATAZZ',   'Entertainment'),
        ('QUIXOTIC',     'Philosophy'),    ('JUXTAPOSE',    'Actions'),
        ('BROUGHAM',     'Transport'),     ('GLYCOGEN',     'Biochemistry'),
        ('KNAPSACK',     'Equipment'),     ('MNEMONIC',     'Linguistics'),
        ('PARADIGM',     'Philosophy'),    ('SYNDROME',     'Medicine'),
        ('MYTHICAL',     'Adjectives'),    ('LABYRINTH',    'Architecture'),
        ('CAPYBARA',     'Zoology'),       ('CATECHISM',    'Religion'),
        ('SCHNAPPS',     'Beverages'),     ('VEXILLUM',     'Heraldry'),
        ('SQUELCHED',    'Sounds'),        ('LYNCHPIN',     'Engineering'),
        ('GLYCEROL',     'Chemistry'),     ('SYLVATIC',     'Ecology'),
        ('PHTHISIS',     'Medicine'),      ('CHTHONIAN',    'Mythology'),
        ('SYZYGIES',     'Astronomy'),     ('COXSWAINS',    'Nautical'),
        # ── 9-letter ──────────────────────────────────────────────────────────
        ('CHRYSALIS',    'Entomology'),    ('GYMNASIUM',    'Architecture'),
        ('LYMPHATIC',    'Anatomy'),       ('PNEUMONIA',    'Medicine'),
        ('SYNAGOGUE',    'Architecture'),  ('XYLOPHONE',    'Music'),
        ('SCHMALTZIER',  'Cooking'),
        # ── 10+ letters ───────────────────────────────────────────────────────
        ('ARCHIPELAGO',  'Geography'),     ('TRYPTOPHAN',   'Biochemistry'),
        ('ZYMOTIC',      'Medicine'),      ('DIPHTHERIA',   'Medicine'),
        ('ONOMATOPOEIA', 'Linguistics'),   ('PHYSIOGNOMY',  'Science'),
        ('SCHIZOTYPAL',  'Psychology'),    ('LYMPHOCYTIC',  'Biology'),
    ],
}

# Training corpus for the character n-gram model.
# Separate from the game word list so that rare words (SYZYGY, CRWTH) surface
# as high-perplexity rather than appearing "expected" to the model.
COMMON_EN = [
    'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
    'OUR','OUT','DAY','GET','HAS','HIM','HIS','HOW','MAN','NEW','NOW','OLD',
    'SEE','TWO','WAY','WHO','BOY','DID','ITS','LET','PUT','SAY','SHE','TOO',
    'USE','RUN','THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','KNOW',
    'WANT','BEEN','GOOD','MUCH','SOME','TIME','VERY','WHEN','COME','HERE',
    'JUST','LIKE','LONG','MAKE','MANY','MORE','ONLY','OVER','SUCH','TAKE',
    'THAN','THEM','WELL','WERE','WHAT','LOOK','ALSO','BACK','CALL','CAME',
    'EACH','EVEN','GIVE','HAND','HIGH','KEEP','LAST','LEFT','LIFE','LIVE',
    'LOVE','MADE','MOVE','MUST','NAME','NEXT','PART','PLAY','SAME','SHOW',
    'SIDE','TELL','THEN','THINK','THREE','PLACE','RIGHT','SMALL','FOUND',
    'STILL','WORLD','NEVER','EVERY','THOSE','HOUSE','AFTER','GREAT','WHERE',
    'WHILE','POINT','WATER','AGAIN','LARGE','OFTEN','LIGHT','NIGHT','MIGHT',
    'UNTIL','YOUNG','COULD','WOULD','THEIR','THESE','OTHER','ABOUT','ALONG',
    'AMONG','BRING','BUILT','CARRY','CAUSE','CLOSE','COVER','CROSS','DRAWN',
    'DRIVE','EARLY','EARTH','EIGHT','ENTER','EQUAL','EXIST','EXTRA','FINAL',
    'FIRST','FORCE','FRONT','GOING','HANDS','HAPPY','HEARD','HEART','HEAVY',
    'HORSE','HUMAN','KNOWN','LATER','LAYER','LEARN','LEAST','LEVEL','LOCAL',
    'LOWER','LUCKY','MAJOR','MEANS','METAL','MODEL','MONEY','MONTH','MOUTH',
    'MUSIC','NORTH','NOVEL','ORDER','OUTER','PAINT','PAPER','PARTY','PEACE',
    'PHASE','PIECE','PILOT','PLAIN','PLANE','PLANT','PLATE','POWER','PRESS',
    'PRICE','PRIDE','PRIME','PRINT','PRIOR','PROOF','PROUD','PROVE','QUICK',
    'QUIET','QUITE','RADIO','RANGE','REACH','READY','REPLY','RIVER','ROUND',
    'ROUTE','ROYAL','RURAL','SCALE','SCENE','SCORE','SENSE','SEVEN','SHAKE',
    'SHALL','SHAPE','SHARE','SHARP','SHEET','SHIFT','SHIRT','SHORT','SIGHT',
    'SINCE','SIXTH','SIXTY','SKILL','SLEEP','SLICE','SLIDE','SLOPE','SMART',
    'SMILE','SMOKE','SOLID','SOLVE','SORRY','SOUTH','SPACE','SPARE','SPEED',
    'SPEND','SPLIT','SPOKE','SPORT','SPRAY','STAGE','START','STATE','STORE',
    'STORM','STORY','STRIP','SUGAR','SWEET','SWING','TABLE','TAKEN','TASTE',
    'TEACH','THROW','TIRED','TITLE','TODAY','TOTAL','TOUCH','TOUGH','TOWER',
    'TRACK','TRADE','TRAIL','TRAIN','TREAT','TRIAL','TRIED','TRUCK','TRULY',
    'TRUST','TRUTH','TWICE','UNDER','UNION','UNITE','UPSET','USAGE','USUAL',
    'VALUE','VIDEO','VISIT','VITAL','VOICE','VOTER','WASTE','WATCH','WEIGH',
    'WHOLE','WHOSE','WIDER','WOMAN','WOMEN','WORDS','WORKS','WORSE','WORTH',
    'WRITE','WROTE','YEARS','YIELD','CLEAR','FIELD','NEVER','THINK','SPEAK',
    'STONE','GREEN','BREAD','BLOOD','BREAK','BROWN','BUILT','CHAIR','CHART',
    'CHECK','CHIEF','CHILD','CLAIM','CLASS','CLEAN','CLOUD','COLOR','COUNT',
    'COURT','COVER','CRASH','CREAM','CRIME','CROWD','CROWN','CRUEL','CURVE',
    'CYCLE','DANCE','DEATH','DELAY','DEPTH','DEVIL','DIARY','DIGIT','DIRTY',
    'DOUBT','DROWN','DRUGS','DRUMS','DYING','ELITE','EMAIL','EMPTY','ERROR',
    'EVENT','EXACT','EVERY','FIFTY','FIGHT','FILED','FILLED','FLAME',
    'FLASH','FLOAT','FLOOD','FLOOR','FLOUR','FLUID','FOCUS','FORTY','FOUND',
    'FRANK','FRESH','FRUIT','FULLY','FUNNY','GIANT','GIVEN','GLASS','GLOBE',
    'GRACE','GRADE','GRAIN','GRAND','GRANT','GRAPH','GRASP','GRASS','GRAVE',
]
