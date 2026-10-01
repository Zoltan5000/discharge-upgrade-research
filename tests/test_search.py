from app.search import to_match


def test_phrases_words_and_operators():
    assert to_match('"liberal consideration" PTSD OR TBI') == '"liberal consideration" "PTSD" OR "TBI"'
    assert to_match("urinal*") == '"urinal"*'


def test_odd_input_never_breaks_the_search():
    assert to_match("14-12c") == '"14 12c"'
    assert to_match('"unbalanced') == '"unbalanced"'
    assert to_match("OR NOT") == ""
    assert to_match("PTSD OR") == '"PTSD"'
