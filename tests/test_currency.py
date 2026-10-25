import sqlite3

import pytest

from cogs import currency


@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE currency(user_id text, user_name text, bonus text, money int)")
    yield conn
    conn.close()


def _add(conn, user_id, money, bonus="0"):
    conn.execute(
        "insert into currency values (?, ?, ?, ?)", (user_id, f"name{user_id}", bonus, money)
    )
    conn.commit()


def test_claim_bonus_new_user(conn):
    assert currency.claim_bonus(conn, "1", "a") == currency.BONUS_VALUE
    assert currency.claim_bonus(conn, "1", "a") is None
    assert currency.get_money(conn, "1") == currency.BONUS_VALUE


def test_claim_bonus_existing_user_without_bonus(conn):
    _add(conn, "1", 100)
    assert currency.claim_bonus(conn, "1", "a") == 100 + currency.BONUS_VALUE
    assert currency.claim_bonus(conn, "1", "a") is None


def test_transfer_moves_money_and_registers_receiver(conn):
    _add(conn, "1", 500)
    assert currency.transfer(conn, "1", "2", "b", 200)
    assert currency.get_money(conn, "1") == 300
    assert currency.get_money(conn, "2") == 200
    assert conn.execute("select bonus from currency where user_id = '2'").fetchone() == ("0",)

    assert currency.transfer(conn, "1", "2", "b", 300)
    assert currency.get_money(conn, "1") == 0
    assert currency.get_money(conn, "2") == 500


def test_transfer_insufficient_funds_changes_nothing(conn):
    _add(conn, "1", 100)
    assert not currency.transfer(conn, "1", "2", "b", 101)
    assert currency.get_money(conn, "1") == 100
    assert currency.get_money(conn, "2") is None


def test_transfer_from_unregistered_sender_fails(conn):
    assert not currency.transfer(conn, "1", "2", "b", 1)
    assert currency.get_money(conn, "2") is None


def test_set_money_and_top_users(conn):
    currency.set_money(conn, "1", "a", "1", 10)
    currency.set_money(conn, "2", "b", "0", 30)
    currency.set_money(conn, "1", "a", "0", 20)
    assert currency.top_users(conn) == [("2", 30), ("1", 20)]
