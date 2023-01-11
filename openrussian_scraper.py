import urllib.request
from html_table_parser.parser import HTMLTableParser
from anki_generator import *
import requests
from bs4 import BeautifulSoup

def url_get_contents(url):
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)
    return f.read()

def parse_website(url):
    xhtml = url_get_contents(url).decode('utf-8')
    p = HTMLTableParser()
    p.feed(xhtml)
    return p.tables #assuming that we only have the wordlist table here - seems to be the case

def get_all_word_urls_for_difficulty_link(base_url):
    last_suffix_value = 0
    all_links_for_cur_difficulty = []

    while True:
        cur_url = base_url
        if (last_suffix_value > 0):
            cur_url += "&start=" + str(last_suffix_value)
        last_suffix_value += 50

        try:
            rawdata = requests.get(cur_url)
            html = rawdata.content

            soup = BeautifulSoup(html, 'html.parser')
            links_on_site = soup.findAll('a')
            links_to_words = []

            for url in links_on_site:
                url = url['href']
                if (str(url).startswith("/ru/")):
                    links_to_words.append("https://en.openrussian.org" + url)

            if len(links_to_words) == 0:
                break
            else:
                all_links_for_cur_difficulty.extend(links_to_words)
        except:
            break

    print(len(all_links_for_cur_difficulty))
    return all_links_for_cur_difficulty

"""
Returns:
string word
list of strings overview_info
list of strings translations
list of strings examples
list of tables in list format tables
"""
def extract_data_for_verb_url(word_url):
    rawdata = requests.get(word_url)
    html = rawdata.content
    soup = BeautifulSoup(html, 'html.parser')
    #Find the important elements
    #The name of the word is always in the first h1 element
    word = soup.find('h1').text
    #print("WORD: " + str(word))

    #Get overview data (word type, specifically)
    overview = soup.find('div', {'class': 'overview'})
    #print("OVERVIEW: " + str(overview))

    overview_info = []
    for data in overview.findAll('p'):
        overview_info.append("<br>" + str(data.text))

    #now we want paragraphs of class t1 for translation and example for examples
    paragraphs = soup.findAll('p')
    translations = []
    examples = []
    for p in paragraphs:
        if p.has_attr('class'):
            if p['class'][0] == 'tl':  # Notice that I put [0], as para['class'] is a list.
                print("TRANSLATION: " + p.text)
                translations.append(p.text)
            elif p['class'][0] == 'example':
                print("EXAMPLE: " + p.text)
                examples.append(p.text)


    tables = parse_website(word_url)

    return word, overview_info, translations, examples, tables

if __name__ == '__main__':
    #Only verbs first
    a2_url_verbs = "https://en.openrussian.org/list/verbs?level=A2"
    list_of_word_urls = get_all_word_urls_for_difficulty_link(a2_url_verbs)#Remove this restriction after debugging

    all_words = []
    all_overviews = []
    all_examples = []
    all_translations = []
    all_examples = []
    all_tables = []

    for word_url in list_of_word_urls:
        word, overview_info, translations, examples, tables = extract_data_for_verb_url(word_url)
        all_words.append(word)
        all_overviews.append(overview_info)
        all_examples.append(examples)
        all_translations.append(translations)
        all_tables.append(tables)


    #Convert to Anki
    model_id = 1819827700  # both ids have been randomly generated
    deck_id = 1697752550

    model = make_model(model_id)
    deck = make_deck(deck_id)
    #create_test_deck(model, deck)

    for i in range(len(all_words)):
        note_a, note_b = get_note_from_data(all_words[i], all_overviews[i], all_translations[i], all_examples[i],
                                      all_tables[i], model)
        deck.add_note(note_a)
        deck.add_note(note_b)

    genanki.Package(deck).write_to_file('test.apkg')

