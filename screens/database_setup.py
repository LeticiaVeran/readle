"""Screen that creates and drops the tables (item 7e).

- "Criar tabelas e carregar dados" runs sql/schema.sql and sql/seed.sql on an empty database.
- "Apagar todas as tabelas" runs sql/drop.sql.
"""
import streamlit as st

import database
import ui


def show():
    ui.page_title("Criar ou apagar o banco")
    existing = database.existing_tables()
    tables_exist = len(existing) > 0

    st.subheader("Criar as tabelas")
    st.write("Executa `sql/schema.sql` e depois `sql/seed.sql`.")
    if tables_exist:
        st.caption("As tabelas já existem.")
    if st.button("Criar tabelas e carregar dados", key="setup_create", type="primary", disabled=tables_exist):
        error = database.run_sql_files(["schema.sql", "seed.sql"])
        ui.finish(error, "Tabelas criadas e dados de exemplo carregados.")

    st.subheader("Apagar as tabelas")
    st.write("Executa `sql/drop.sql`.")
    confirmed = st.checkbox("Confirmo que quero apagar todas as tabelas", key="setup_drop_confirm",
                            disabled=not tables_exist)
    if st.button("Apagar todas as tabelas", key="setup_drop", disabled=not confirmed):
        error = database.run_sql_files(["drop.sql"])
        ui.finish(error, "Todas as tabelas foram apagadas.")

    show_status(existing)


def show_status(existing):
    """Shows how many tables exist and how many rows each one has."""
    st.subheader("Linhas por tabela")
    if len(existing) == 0:
        st.caption("Nenhuma tabela criada.")
        return
    names = []
    counts = []
    for table_name in database.TABLES:
        if table_name in existing:
            names.append(table_name.upper())
            counts.append(database.fetch_value("SELECT COUNT(*) FROM " + table_name))
    st.dataframe({"Tabela": names, "Linhas": counts}, hide_index=True)
