from models import MenuItem

def test_menu_item_repr():
    item = MenuItem(
        name="Pizza",
        description="Delicious pizza",
        price=25.50,
        available=True
    )

    result = repr(item)
    assert "Pizza" in result
    assert "25.5" in result
    assert "True" in result