from kruiscijferraadsel import CrossNumber, NumberIntersection, NumberSection


def test_add_sections(options):
    cn = CrossNumber()
    cn.add_section("A8-h", 4)
    cn.add_section("B8-v", 4)
    assert len(cn.sections) == 2


def test_connect(words):
    cn = CrossNumber(words=words)
    s1 = NumberSection(origin="A8", options=cn.options[4], orientation="horizontal")
    s2 = NumberSection(origin="B8", options=cn.options[4], orientation="vertical")
    cn.add_section("A8-h", 4)
    cn.add_section("B8-v", 4)
    cn.connect("A8-h", "B8-v", 1, 0)
    expected = NumberIntersection(s1, s2, 1, 0)
    assert cn.intersections[0] == expected
