import re
import os
import shutil

rxDiacritics = re.compile('[ӧёӱҥ]')
rxDiacriticsYo = re.compile('ё')
rxDiaPartsStem = re.compile('( stem:)( *[^\r\n]+)')
rxDiaPartsFlex = re.compile('(-flex:)( *[^\r\n]+)')
rxStemVariants = re.compile('[^ |/]+')
rxFlexVariants = re.compile('[^ /]+')
dictDiacritics = {
    'ҥ': 'н',
    'ӧ': 'о',
    'ё': 'е',
    'ӱ': 'у'
}


def collect_lemmata(dirName):
    lemmata = ''
    lexrules = ''
    for fname in os.listdir(dirName):
        if fname.endswith('.txt') and fname.startswith('mhr_lexemes_'):
            f = open(os.path.join(dirName, fname), 'r', encoding='utf-8-sig')
            lemmata += f.read() + '\n'
            f.close()
        elif fname.endswith('.txt') and fname.startswith('mhr_lexrules_'):
            f = open(os.path.join(dirName, fname), 'r', encoding='utf-8-sig')
            lexrules += f.read() + '\n'
            f.close()
    lemmataSet = set(re.findall('-lexeme\n(?: [^\r\n]*\n)+', lemmata, flags=re.DOTALL))
    lemmata = '\n'.join(sorted(list(lemmataSet)))
    return lemmata, lexrules


def add_diacriticless(morph):
    """
    Add a diacriticless variant to a stem or an inflection
    """
    morph = morph.group(0)
    if rxDiacritics.search(morph) is None:
        return morph
    return morph + '//' + rxDiacritics.sub(lambda m: dictDiacritics[m.group(0)], morph)


def add_diacriticless_yo(morph):
    """
    Add a yo-less variant to a stem or an inflection
    """
    morph = morph.group(0)
    if rxDiacriticsYo.search(morph) is None:
        return morph
    return morph + '//' + rxDiacriticsYo.sub(lambda m: dictDiacritics[m.group(0)], morph)


def process_diacritics_stem(line):
    """
    Remove diacritics from one line that contains stems.
    """
    morphCorrected = rxStemVariants.sub(add_diacriticless, line.group(2))
    return line.group(1) + morphCorrected


def process_diacritics_stem_yo(line):
    """
    Remove yo diacritics from one line that contains stems.
    """
    morphCorrected = rxStemVariants.sub(add_diacriticless_yo, line.group(2))
    return line.group(1) + morphCorrected


def process_diacritics_flex(line):
    """
    Remove diacritics from one line that contains inflextions.
    """
    morphCorrected = rxFlexVariants.sub(add_diacriticless, line.group(2))
    return line.group(1) + morphCorrected


def russify(text):
    """
    Add diacriticless variants for stems and inflections.
    """
    text = rxDiaPartsStem.sub(process_diacritics_stem, text)
    text = rxDiaPartsFlex.sub(process_diacritics_flex, text)
    return text


def russify_yo(text):
    """
    Add yo-less variants for stems.
    """
    text = rxDiaPartsStem.sub(process_diacritics_stem_yo, text)
    return text


def prepare_files():
    """
    Put all the lemmata to lexemes.txt. Put all the lexical
    rules to lexical_rules.txt. Create separate versions of
    relevant files for diacriticless texts.
    Put all grammar files to ../uniparser_meadow_mari/data_strict/
    (original version) or ../uniparser_meadow_mari/data_nodiacritics/
    (diacriticless version).
    """
    lemmata, lexrules = collect_lemmata('.')
    fOutLemmata = open('uniparser_meadow_mari/data_strict/lexemes.txt', 'w', encoding='utf-8')
    fOutLemmata.write(russify_yo(lemmata))
    fOutLemmata.close()
    fOutLemmataRus = open('uniparser_meadow_mari/data_nodiacritics/lexemes.txt', 'w', encoding='utf-8')
    fOutLemmataRus.write(russify(lemmata))
    fOutLemmataRus.close()
    fInParadigms = open('paradigms.txt', 'r', encoding='utf-8-sig')
    paradigms = fInParadigms.read()
    fInParadigms.close()
    fOutParadigms = open('uniparser_meadow_mari/data_strict/paradigms.txt', 'w', encoding='utf-8')
    fOutParadigms.write(paradigms)
    fOutParadigms.close()
    fOutParadigmsRus = open('uniparser_meadow_mari/data_nodiacritics/paradigms.txt', 'w', encoding='utf-8')
    fOutParadigmsRus.write(russify(paradigms))
    fOutParadigmsRus.close()
    fOutLexrules = open('uniparser_meadow_mari/data_strict/lex_rules.txt', 'w', encoding='utf-8')
    fOutLexrules.write(lexrules)
    fOutLexrules.close()
    fOutLexrules = open('uniparser_meadow_mari/data_nodiacritics/lex_rules.txt', 'w', encoding='utf-8')
    fOutLexrules.write(lexrules)
    fOutLexrules.close()
    shutil.copy2('bad_analyses.txt', 'uniparser_meadow_mari/data_strict/')
    shutil.copy2('bad_analyses.txt', 'uniparser_meadow_mari/data_nodiacritics/')
    shutil.copy2('meadow_mari_disambiguation.cg3', 'uniparser_meadow_mari/data_strict/')
    shutil.copy2('meadow_mari_disambiguation.cg3', 'uniparser_meadow_mari/data_nodiacritics/')


def parse_wordlists():
    """
    Analyze wordlists/wordlist.csv.
    """
    from uniparser_meadow_mari import MeadowMariAnalyzer
    a = MeadowMariAnalyzer(mode='strict')
    a.analyze_wordlist(freqListFile='wordlists/wordlist_main.csv',
                       parsedFile='wordlists/wordlist_analyzed.txt',
                       unparsedFile='wordlists/wordlist_unanalyzed.txt',
                       verbose=True)


if __name__ == '__main__':
    prepare_files()
    # parse_wordlists()
    from uniparser_meadow_mari import MeadowMariAnalyzer
    a = MeadowMariAnalyzer(mode='strict')
    res = a.analyze_words(['Петя', 'грипп', 'ден', 'черланен', '.'], disambiguate=True)
    print(res)
    res = a.analyze_words(['Пу', 'комыля', 'вӱдыш', 'пурен', 'каен', '.'], disambiguate=True)
    print(res)
    res = a.analyze_words(['Петя', 'кӱым', 'шуэн', '/', 'кудалтен', '.'], disambiguate=True)
    print(res)
    res = a.analyze_words(['Петя', 'полка', 'гыч', 'книгам', 'нале', '.'], disambiguate=True)
    print(res)
    res = a.analyze_words(['Петя', 'пырдыжым', 'тӱкыш', '.'], disambiguate=True)
    print(res)
    res = a.analyze_words(['Петя', 'Машам', 'шӱдыш', '.'], disambiguate=True)
    print(res)

