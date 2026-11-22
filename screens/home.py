"""Home screen: what is happening in the reading groups right now.

Shows the next deadlines of the groups and the latest reviews, read straight
from the database. The number of rows of each table is on the database screen.
"""
import streamlit as st

import database
import ui


def show():
    ui.page_title("Hoje no Readle")

    if not database.tables_created():
        st.info("O banco está vazio. Crie as tabelas em **Criar ou apagar o banco**.")
        return

    show_next_deadlines()
    show_latest_reviews()


def show_next_deadlines():
    """Stages of the groups that are still open, with the closest deadline first."""
    st.subheader("Próximos prazos dos grupos")
    table = database.fetch_table(
        """SELECT e.data_limite AS "Prazo", g.nome AS "Grupo", e.titulo AS "Etapa", l.titulo AS "Livro"
           FROM ETAPA_LEITURA e
           JOIN GRUPO_LEITURA g ON g.id_grupo = e.FK_GRUPO_LEITURA_id_grupo
           JOIN LIVRO l ON l.id_livro = g.FK_LIVRO_id_livro
           WHERE e.data_limite >= CURRENT_DATE AND g.situacao <> 'Encerrado'
           ORDER BY e.data_limite
           LIMIT 6"""
    )
    if len(table) == 0:
        st.caption("Nenhum grupo tem etapa com prazo daqui para frente.")
    else:
        ui.show_table(table)


def show_latest_reviews():
    """The four most recent reviews, with the stars and the text."""
    st.subheader("Avaliações mais recentes")
    rows = database.fetch_all(
        """SELECT l.titulo, a.nota, u.nome, a.data_publicacao, a.texto_resenha
           FROM AVALIACAO_RESENHA a
           JOIN LIVRO l ON l.id_livro = a.FK_LIVRO_id_livro
           JOIN USUARIO u ON u.id_usuario = a.FK_USUARIO_id_usuario
           ORDER BY a.data_publicacao DESC, a.id_avaliacao DESC
           LIMIT 4"""
    )
    if len(rows) == 0:
        st.caption("Ainda não há avaliações.")
    for row in rows:
        # In Streamlit's markdown, two spaces + \n break the line and :gray[...] writes in gray
        st.markdown("**" + row[0] + "**  " + ui.stars(row[1]) + "  \n"
                    + ":gray[" + row[2] + ", " + ui.format_date(row[3]) + "]")
        if row[4] is not None:
            st.write(row[4])
