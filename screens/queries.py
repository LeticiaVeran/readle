"""Screen with the three queries of item 6 of the report (item 7c).

The SQL comes from sql/queries.sql, so the application runs exactly the same
queries shown in the report. Each result is shown in two ways: as a table and
as a bar chart. On the screen, the column names of the result are written in
plain Portuguese (genero -> Gênero), but the SQL stays the same.
"""
import os

import streamlit as st

import database
import ui

# Text shown for each query (in the same order as in sql/queries.sql) and the
# columns used in the chart.
QUERY_INFO = [
    {
        "tab": "Consulta 1",
        "title": "Avaliação média por gênero literário",
        "goal": "Para cada gênero, quantas avaliações seus livros receberam e a nota média "
                "dessas avaliações. Tabelas: GENERO, CLASSIFICA e AVALIACAO_RESENHA. "
                "Agregação: COUNT e AVG.",
        "column_names": {"genero": "Gênero", "total_avaliacoes": "Avaliações", "nota_media": "Nota média"},
        "category_column": "Gênero",
        "value_column": "Nota média",
        "value_label": "Nota média (1 a 5)",
    },
    {
        "tab": "Consulta 2",
        "title": "Ranking de leitores por páginas lidas",
        "goal": "Para cada usuário, quantos livros ele concluiu (status Lido) e o total de "
                "páginas desses livros. Tabelas: USUARIO, ITEM_ESTANTE e LIVRO. "
                "Agregação: COUNT e SUM.",
        "column_names": {"leitor": "Leitor", "livros_lidos": "Livros lidos", "paginas_lidas": "Páginas lidas"},
        "category_column": "Leitor",
        "value_column": "Páginas lidas",
        "value_label": "Páginas lidas",
    },
    {
        "tab": "Consulta 3",
        "title": "Engajamento dos grupos de leitura",
        "goal": "Para cada grupo, o livro discutido, o total de mensagens visíveis e quantos "
                "membros diferentes publicaram. Tabelas: GRUPO_LEITURA, LIVRO, ETAPA_LEITURA e "
                "MENSAGEM. Agregação: COUNT e COUNT(DISTINCT).",
        "column_names": {"grupo": "Grupo", "livro": "Livro", "mensagens": "Mensagens",
                         "membros_que_publicaram": "Membros que publicaram"},
        "category_column": "Grupo",
        "value_column": "Mensagens",
        "value_label": "Mensagens visíveis",
    },
]


def load_queries():
    """Reads sql/queries.sql and returns the SELECT statements, in order.
    Lines starting with -- are comments and are skipped; each statement ends with ';'."""
    path = os.path.join(database.SQL_FOLDER, "queries.sql")
    sql_file = open(path, encoding="utf-8")
    content = sql_file.read()
    sql_file.close()
    statements = []
    current_lines = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped == "" or stripped.startswith("--"):
            continue
        current_lines.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current_lines))
            current_lines = []
    return statements


def show():
    ui.page_title("Consultas do relatório")
    statements = load_queries()
    # One tab for each query
    tab_names = []
    for info in QUERY_INFO:
        tab_names.append(info["tab"])
    tabs = st.tabs(tab_names)
    position = 0
    for info in QUERY_INFO:
        with tabs[position]:
            show_query(info, statements[position])
        position = position + 1


def show_query(info, sql):
    st.subheader(info["title"])
    st.write(info["goal"])
    with st.expander("Ver o SQL da consulta"):
        st.code(sql, language="sql")

    table = database.fetch_table(sql)
    # Readable column names on the screen (the SQL keeps the original names)
    table = table.rename(columns=info["column_names"])

    st.markdown("**Resultado em tabela**")
    st.dataframe(table, hide_index=True)

    st.markdown("**Resultado em gráfico**")
    # PostgreSQL returns averages as exact decimals (Decimal); the chart needs plain
    # numbers (float), so the column is converted.
    value_column = info["value_column"]
    table[value_column] = table[value_column].astype(float)
    # With horizontal=True the bars lie down: the categories go on the vertical axis
    # and the values on the horizontal one. The labels still follow x (category) and y (value).
    st.bar_chart(
        table,
        x=info["category_column"],
        y=value_column,
        x_label="",
        y_label=info["value_label"],
        horizontal=True,
        sort=False,  # keeps the order that came from the ORDER BY of the query
    )
