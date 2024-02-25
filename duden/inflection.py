"""
Module containing classes and functions related to word inflection.

The most important are the grammatical category enums like Case, Gender,
and the Inflector class.
"""
from enum import Enum

from .page.grammar import GrammarPage

# key names of Inflector raw data dict
NOUN = "Deklination"
ADJ_STRONG = "Starke Beugung (ohne Artikel)"
ADJ_WEAK = "Schwache Beugung (mit Artikel)"
ADJ_MIXED = "Gemischte Beugung (mit ein, kein, Possessivpronomen u. a.)"
ADJ_COMPARE = "Steigerungsformen"
VERB_INDICATIVE = "Indikativ"
VERB_SUBJUNCTIVE_I = "Konjunktiv I"
VERB_SUBJUNCTIVE_II = "Konjunktiv II"
VERB_IMPERATIVE = "Imperativ"
VERB_INFINITIVE_FORMS = "Infinite Formen"


class Number(Enum):
    """Grammatical number"""

    SINGULAR = "Singular"
    PLURAL = "Plural"


class Case(Enum):
    """Grammatical case"""

    NOMINATIVE = "Nominativ"
    GENITIVE = "Genitiv"
    DATIVE = "Dativ"
    ACCUSATIVE = "Akkusativ"


class Gender(Enum):
    """Grammatical gender"""

    MASCULINE = "Maskulinum"
    FEMININE = "Femininum"
    NEUTER = "Neutrum"


class Degree(Enum):
    """Grammatical degree (for adjective comparison)"""

    POSITIVE = "Positiv"
    COMPARATIVE = "Komparativ"
    SUPERLATIVE = "Superlativ"


# TODO: reduce to three categories
class Person(Enum):
    """Grammatical person"""

    FIRST_SINGULAR = "ich"
    SECOND_SINGULAR = "du"
    THIRD_SINGULAR = "er/sie/es"
    FIRST_PLURAL = "wir"
    SECOND_PLURAL = "ihr"
    THIRD_PLURAL = "sie"


class Mood(Enum):
    """Grammatical mood"""

    INDICATIVE = VERB_INDICATIVE
    SUBJUNCTIVE_I = VERB_SUBJUNCTIVE_I
    SUBJUNCTIVE_II = VERB_SUBJUNCTIVE_II


class Tense(Enum):
    """Grammatical tense"""

    PRESENT = "Präsens"
    PAST = "Präteritum"
    PERFECT = "Perfekt"
    PAST_PERFECT = "Plusquamperfekt"
    FUTURE = "Futur I"
    FUTURE_PERFECT = "Futur II"


# TODO: rely only on number
class ImperativePerson(Enum):
    """Grammatical person (only for imperative forms of verbs)"""

    PERSON_2_SINGULAR = "2. Person Singular [du]"
    PERSON_2_PLURAL = "2. Person Plural [ihr]"


class InfinitiveForm(Enum):
    """Infinitive form of verb"""

    INFINITIVE_WITH_ZU = "Infinitiv mit zu"
    PARTICIPLE_I = "Partizip I"
    PARTICIPLE_II = "Partizip II"


class KeyChainError(KeyError):
    """Variant of KeyError which stores previously accessed keys of a nested dict"""

    def __init__(self, key, previous_keys):
        super().__init__(key)
        self.key = key
        self.previous_keys = previous_keys


class Enumdict:
    """
    A dict wrapper with these properties

    * Enums behave as their raw values when used as keys (d["Singular"] == d[Number.SINGULAR])
    * Nested inner dicts are also Enumdicts and store the key path they were accessed with
    """

    def __init__(self, source, key_prefix=None):
        self.source = source
        self.key_prefix = key_prefix or []  # used for error messages

    def __getitem__(self, key):
        real_key = key.value if isinstance(key, Enum) else key
        try:
            value = self.source[real_key]
        except KeyError:
            raise KeyChainError(real_key, self.key_prefix) from None
        new_prefix = self.key_prefix + [real_key]
        return (
            Enumdict(value, key_prefix=new_prefix) if isinstance(value, dict) else value
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.source)})"


class Inflector:
    """
    Provides methods for word inflection

    Example:

        > r = requests.get("https://www.duden.de/deklination/substantive/Hase")
        > soup = bs4.BeautifulSoup(r.text)
        > inf = Inflector(soup)
        > inf.noun_decline(Number.SINGULAR, Case.NOMINATIVE)
        'der Hase'
    """

    def __init__(self, soup):
        """
        Construct Inflector object

        Args:
            soup (BeautifulSoup): parsed grammar page
        """
        self.page = GrammarPage(soup)
        self.data = {
            key: conditional_transform(key, value)
            for key, value in self.page.table_data.items()
        }
        self.enumraw = Enumdict(self.data)

    def __repr__(self):
        if not self.data:
            example = "Empty"
        else:
            example = self.data
            while isinstance(example, dict):
                example = list(example.values())[0]
            example = repr(example) + ", ..."
        return f"({self.__class__.__name__}: {example})"

    def inflect(self, *key_chain):
        """Fetch data from nested dict in self.enumraw by providing a list of keys to apply"""
        inner = self.enumraw
        try:
            for key in key_chain:
                inner = inner[key]
        except KeyChainError as err:
            keys_str = ".".join(repr(key) for key in (err.previous_keys + [err.key]))
            other_choices = ", ".join(repr(key) for key in inner.source.keys())
            err_msg = _("Cannot inflect. Missing data for: {} . Did you mean {}?")
            raise ValueError(err_msg.format(keys_str, other_choices)) from None
        return inner

    # nouns
    def noun_decline(self, number, case):
        """
        number: "Singular" or "Plural"
        case: "Nominativ", "Genitiv", "Dativ", "Akkusativ"
        """
        return self.inflect(NOUN, number, case)

    # adjectives
    def adjective_decline_strong(self, gender, case):
        """Strong adjective inflection"""
        return self.inflect(ADJ_STRONG, gender, case)

    def adjective_decline_weak(self, gender, case):
        """Weak adjective inflection"""
        return self.inflect(ADJ_WEAK, gender, case)

    def adjective_decline_mixed(self, gender, case):
        """Mixed adjective inflection"""
        return self.inflect(ADJ_MIXED, gender, case)

    def adjective_compare(self, degree):
        """Adjective comparative"""
        return self.inflect(ADJ_COMPARE, degree)

    # verbs
    def verb_conjugate(self, mood, tense, person):
        """Verb conjugation"""
        return self.inflect(mood, tense, person)

    def verb_imperative(self, person):
        """Verb imperative form"""
        return self.inflect(VERB_IMPERATIVE, person)

    def verb_infinitive_forms(self, form):
        """Verb infinitive form"""
        return self.inflect(VERB_INFINITIVE_FORMS, form)


def legend_left_transform(structure):
    """Transform data for tables where legend on the left"""
    return dict(zip(*structure[0]))


def legend_top_transform(structure):
    """Transform data for tables where legend at the top"""
    return dict(s[0] for s in structure)


def hidden_title_transform(structure):
    """Transform data for most verb and noun tables"""
    resmap = {}
    for legend, content in structure:
        name = content[0]
        mapping = dict(zip(legend[1:], content[1:]))
        resmap[name] = mapping
    return resmap


def square_transform(structure):
    """Transform data for most adjective tables"""
    _, *left_legend = structure[0][0]
    res = {}
    for _, column in structure:
        top_key, *values = column
        res[top_key] = dict(zip(left_legend, values))
    return res


def conditional_transform(key, structure):
    """Transform grammar table data conditionally based on table title"""
    transformation = table_transformations[key]
    return transformation(structure)


# how individual top-level section table_data must be transformed
table_transformations = {
    # noun
    NOUN: hidden_title_transform,
    # verb
    VERB_INDICATIVE: hidden_title_transform,
    VERB_SUBJUNCTIVE_I: hidden_title_transform,
    VERB_SUBJUNCTIVE_II: hidden_title_transform,
    VERB_IMPERATIVE: legend_left_transform,
    VERB_INFINITIVE_FORMS: legend_top_transform,
    # adjective sections
    ADJ_COMPARE: legend_top_transform,
    ADJ_STRONG: square_transform,
    ADJ_WEAK: square_transform,
    ADJ_MIXED: square_transform,
}
