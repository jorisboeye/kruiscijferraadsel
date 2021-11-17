from kruiscijferraadsel import CrossNumber


def test_add_sections(words):
    cn = CrossNumber(words=words)
    cn.add_section(indexes=("FB", "FC", "FD", "FE", "FF"), horizontal=True)
    cn.add_section(indexes=("AB", "BB", "CB", "DB", "EB", "FB"), horizontal=False)
    assert len(cn.sections) == 2


def test_connect(words):
    cn = CrossNumber(words=words)
    cn.add_section(indexes=("FB", "FC", "FD", "FE", "FF"), horizontal=True)
    cn.add_section(indexes=("AB", "BB", "CB", "DB", "EB", "FB"), horizontal=False)
    cn.connect()
    cn.connect()
    assert len(cn.intersections) == 1
