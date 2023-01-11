import genanki
import pandas as pd


def make_model(model_id):
    model = genanki.Model(
        model_id,
        'Simple Model with Media',
        fields=[
            {'name': 'English'},
            {'name': 'Russian'},
            #{'name': 'Audio'},  # ADD THIS
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{English}}',  # AND THIS
                'afmt': '{{FrontSide}}<hr id="answer">{{Russian}}',
            },
        ])
    return model

def make_deck(deck_id):
    deck = genanki.Deck(
        deck_id,
        'openrussian.org data automatically converted')
    return deck

def make_first_row_specific_length(row, length):
    diff = length - len(row)
    for i in range(diff):
        row = row.append(str(i))
    return row

def convert_list_of_lists_to_html(list_table):
    output_string = "<table>"
    for row in list_table:
        output_string += "<tr>"
        for element in row:
            output_string += "<td>" + str(element) + "</td>"
        output_string += "</tr>"
    output_string += "</table>"
    return(output_string)

def get_note_from_data(word, overview_info, translations, examples, tables, model):
    print(word)
    print(overview_info)
    translation_string = ""
    example_string = ""
    table_string = ""
    overview_string = ""

    for ov in overview_info:
        overview_string += "<br>" + str(ov)

    for transl in translations:
        translation_string += "<br>" + str(transl)

    for ex in examples:
        example_string += "<br>" + str(ex) + "<br>"

    for table in tables:
        table_string += "<br>" + convert_list_of_lists_to_html(table)

    #note_a is english to russian, note_b vice versa
    note_a = genanki.Note(
        model=model,
        fields=[translation_string, word + overview_string + example_string + table_string]
    )

    note_b = genanki.Note(
        model=model,
        fields=[word, translation_string + example_string]
    )

    return note_a, note_b

def create_test_deck(model, deck):
    df1 = pd.DataFrame(columns=["Test1", "Test2", "Test3"])
    df1.loc[len(df1)] = ['ви́деть', 25, 'бу́дешь ви́деть']

    df2 = pd.DataFrame(columns=["Test1", "Test2", "Test3"])
    df2.loc[len(df2)] = ['ви́жу', 13, 'он/она́/оно́ ви́дит']

    test_note_1 = genanki.Note(
        model=model,
        fields=['ви́деть', df1.to_html()])

    test_note_2 = genanki.Note(
        model=model,
        fields=['ви́де', df2.to_html()])

    deck.add_note(test_note_1)
    deck.add_note(test_note_2)

    genanki.Package(deck).write_to_file('test.apkg')