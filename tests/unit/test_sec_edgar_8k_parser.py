from src.data_providers.sec_edgar import SECEdgarClient

# Layout taken from a real 8-K: headings on their own lines, cross references inline.
FILING_TEXT = """UNITED STATES
FORM 8-K
Check the appropriate box below ... Rule 425 under the Securities Act (17 CFR 230.425)

Item 1.01. Entry into a Material Definitive Agreement.

On November 9, 2026, the Company entered into Amendment No. 1 to its Credit Agreement
with its lenders, increasing the facility.

  Item 2.03.      Creation of a Direct Financial Obligation or an Obligation.

The disclosure set forth in Item 1.01 of this Current Report on Form 8-K is hereby
incorporated into this Item 2.03 by reference.

Item 9.01 Financial Statements and Exhibits.

(d) Exhibits.
  10.1   Amendment No. 1 to Credit and Guaranty Agreement

SIGNATURE

Pursuant to the requirements of the Securities Exchange Act of 1934, the registrant
has duly caused this report to be signed.
"""


def _client() -> SECEdgarClient:
    return SECEdgarClient.__new__(SECEdgarClient)


def test_parses_every_item_section_with_its_own_content():
    items, ids = _client()._extract_8k_data(FILING_TEXT)

    assert ids == ["1.01", "2.03", "9.01"]
    by_id = {i["item_id"]: i for i in items}
    assert "Amendment No. 1 to its Credit Agreement" in by_id["1.01"]["content"]
    assert by_id["1.01"]["title"] == "Entry into a Material Definitive Agreement"
    assert by_id["1.01"]["display_name"] == "Material Definitive Agreement"
    assert "incorporated into this Item 2.03" in by_id["2.03"]["content"]


def test_inline_cross_references_are_not_headings():
    items, _ = _client()._extract_8k_data(FILING_TEXT)

    assert len(items) == 3


def test_signature_block_is_not_part_of_the_last_item():
    items, _ = _client()._extract_8k_data(FILING_TEXT)

    last = items[-1]["content"]
    assert "Exhibits" in last
    assert "duly caused" not in last


def test_text_without_items_returns_nothing():
    assert _client()._extract_8k_data("Just a cover page, no items.") == ([], [])
