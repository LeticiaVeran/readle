"""
Screen pieces reused by every screen of Readle.

Small functions used everywhere: the page title, choosing the action (Consultar,
Inserir, Alterar or Excluir), choosing a record from a list, showing a table,
confirming a deletion and showing the success or error message.
The text the user sees is in Portuguese.
"""
import datetime

import pandas as pd
import streamlit as st

import database

ACTIONS = ["Consultar", "Inserir", "Alterar", "Excluir"]


def page_title(title, table_name=None):
    """Title of the page. Table screens also show, in small letters, the name of the table."""
    st.title(title)
    if table_name is not None:
        st.caption("Tabela " + table_name)


def choose_action(prefix):
    """Shows the Consultar / Inserir / Alterar / Excluir bar and returns the chosen action.
    required=True means one option is always selected (it starts on Consultar)."""
    action = st.segmented_control(
        "O que você quer fazer?",
        ACTIONS,
        default="Consultar",
        required=True,
        key=prefix + "_action",
        label_visibility="collapsed",
    )
    return action


def build_options(rows, default_id=None):
    """Receives rows shaped like (id, text) and builds the options of a select box.

    Returns two things:
    - a dictionary {text shown on screen: id of the record}
    - the position of the option that starts selected (the one of default_id, if any)
    """
    options = {}
    start_position = 0
    counter = 0
    for row in rows:
        record_id = row[0]
        shown_text = str(row[1]) + " (id " + str(record_id) + ")"
        options[shown_text] = record_id
        if record_id == default_id:
            start_position = counter
        counter = counter + 1
    return options, start_position


def choose_record(label, sql, params=None, key=None, default_id=None):
    """Shows a select box with the records returned by the SQL.

    The SQL must return two columns: the id and a text to show.
    default_id is the record that starts selected (a ready example).
    Returns the chosen id, or None when there are no records.
    """
    rows = database.fetch_all(sql, params)
    if len(rows) == 0:
        st.info("Não há registros disponíveis para: " + label)
        return None
    options, start_position = build_options(rows, default_id)
    texts = list(options.keys())
    chosen_text = st.selectbox(label, texts, index=start_position, key=key)
    return options[chosen_text]


def choose_many(label, sql, params=None, key=None, default_ids=None):
    """Like choose_record, but allows several choices. Returns the list of chosen ids.
    default_ids are the records that start selected."""
    rows = database.fetch_all(sql, params)
    options, start_position = build_options(rows)
    texts = list(options.keys())
    default_texts = []
    if default_ids is not None:
        for text in texts:
            if options[text] in default_ids:
                default_texts.append(text)
    chosen_texts = st.multiselect(label, texts, default=default_texts, key=key)
    chosen_ids = []
    for text in chosen_texts:
        chosen_ids.append(options[text])
    return chosen_ids


def choose_value(label, possible_values, current_value, key):
    """Select box with fixed values (for example, the reading statuses),
    starting at the current value."""
    position = 0
    if current_value in possible_values:
        position = possible_values.index(current_value)
    return st.selectbox(label, possible_values, index=position, key=key)


def delete_button(key, record_id):
    """Shows the confirmation box and the Excluir button.
    Returns True when the user confirmed and clicked."""
    confirmed = st.checkbox(
        "Confirmo que quero excluir este registro",
        key=key + "_confirm_" + str(record_id),
    )
    clicked = st.button("Excluir", key=key + "_button", disabled=not confirmed)
    return clicked


def save_notice(text):
    """Keeps a success message to show after the screen reloads."""
    st.session_state["notice"] = text


def show_saved_notice():
    """Shows (only once) the saved success message, if there is one."""
    if "notice" in st.session_state:
        st.success(st.session_state["notice"])
        del st.session_state["notice"]


def finish(error, success_text):
    """After writing to the database: if it worked, keeps the success message and
    reloads the screen (so the lists show the new data); if it failed, shows the error."""
    if error is None:
        save_notice(success_text)
        st.rerun()
    else:
        st.error(error)


def is_blank(text):
    """Returns True when the text is empty or only has spaces."""
    if text is None:
        return True
    return text.strip() == ""


def format_date(value):
    """Turns a date into text in the day/month/year format."""
    if value is None:
        return "-"
    return value.strftime("%d/%m/%Y")


def format_number(number):
    """Writes a whole number the Brazilian way, with a dot every three digits (3792 -> 3.792)."""
    text = "{:,}".format(number)   # gives "3,792"
    return text.replace(",", ".")


def stars(rating):
    """Rating from 1 to 5 drawn with stars: stars(4) -> "★★★★☆"."""
    return "★" * rating + "☆" * (5 - rating)


def count_text(number, singular, plural):
    """Number plus the right word: count_text(1, "livro", "livros") -> "1 livro"."""
    if number == 1:
        return "1 " + singular
    return format_number(number) + " " + plural


# ---------------------------------------------------------------- Tables

def cell_text(value):
    """Text shown in one cell of a table: dates as day/month/year, empty cells blank."""
    if value is None or pd.isna(value):
        return ""
    if isinstance(value, bool):
        if value:
            return "sim"
        return "não"
    if isinstance(value, datetime.datetime):
        return value.strftime("%d/%m/%Y %H:%M")
    if isinstance(value, datetime.date):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))   # 5.0 -> "5"
    return str(value)


def needs_text(column_values):
    """True when a column has empty cells, dates or yes/no values,
    which are shown better as text."""
    for value in column_values:
        if value is None or pd.isna(value):
            return True
        if isinstance(value, bool) or isinstance(value, datetime.date):
            return True
    return False


def show_table(table):
    """Shows a pandas table (DataFrame) on the screen.
    Columns with dates or empty cells are turned into text first, so the screen shows
    24/03/2026 instead of 2026-03-24 and a blank cell instead of the word None.
    Number columns stay numbers (they are aligned to the right)."""
    for column in table.columns:
        if needs_text(table[column]):
            texts = []
            for value in table[column]:
                texts.append(cell_text(value))
            table[column] = texts
    st.dataframe(table, hide_index=True)
