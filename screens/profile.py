"""Reader profile screen: puts together, in one place, what the report promises the user.

According to item 2 of the report, a user can see their shelf, reviews and groups,
and the shelf data shows the reading history and the other users who marked the
same book as 'Quero Ler'. This screen only reads data (it changes nothing);
changes are made in the screen of each table.
"""
import streamlit as st

import database
import ui


def show():
    ui.page_title("Perfil do leitor")
    user_id = ui.choose_record("Leitor", "SELECT id_usuario, nome FROM USUARIO ORDER BY nome", key="profile_user")
    if user_id is None:
        return

    name = show_account(user_id)
    show_numbers(user_id, name)
    show_history(user_id)
    show_current_shelf(user_id)
    show_readers_with_same_wish(user_id)
    show_reviews(user_id)
    show_groups(user_id)
    show_notifications(user_id)


def show_account(user_id):
    """Shows the name and the account data. Returns the reader's name."""
    data = database.fetch_one("SELECT nome, nome_usuario, email, data_cadastro FROM USUARIO WHERE id_usuario = %s",
                              (user_id,))
    st.header(data[0])
    st.caption("Usuário @" + data[1] + ", e-mail " + data[2] + ", no Readle desde " + ui.format_date(data[3]) + ".")
    return data[0]


def show_numbers(user_id, name):
    """Writes the reader's numbers in a sentence: books in each status, pages read and reviews."""
    counts = {"Lido": 0, "Lendo": 0, "Quero Ler": 0, "Abandonado": 0}
    rows = database.fetch_all(
        "SELECT status_leitura, COUNT(*) FROM ITEM_ESTANTE WHERE FK_USUARIO_id_usuario = %s GROUP BY status_leitura",
        (user_id,),
    )
    for row in rows:
        counts[row[0]] = row[1]
    pages = database.fetch_value(
        """SELECT COALESCE(SUM(l.numero_paginas), 0)
           FROM ITEM_ESTANTE i JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
           WHERE i.FK_USUARIO_id_usuario = %s AND i.status_leitura = 'Lido'""",
        (user_id,),
    )
    reviews = database.fetch_value("SELECT COUNT(*) FROM AVALIACAO_RESENHA WHERE FK_USUARIO_id_usuario = %s",
                                   (user_id,))
    first_name = name.split(" ")[0]
    sentence = (first_name + " leu " + ui.count_text(counts["Lido"], "livro", "livros")
                + " (" + ui.count_text(pages, "página", "páginas") + ") e escreveu "
                + ui.count_text(reviews, "avaliação", "avaliações") + ". "
                + "Está lendo " + str(counts["Lendo"]) + ", quer ler " + str(counts["Quero Ler"])
                + " e abandonou " + str(counts["Abandonado"]) + ".")
    st.write(sentence)


def show_history(user_id):
    st.subheader("Histórico de leitura")
    table = database.fetch_table(
        """SELECT l.titulo AS "Livro",
                  (SELECT STRING_AGG(a.nome, ', ') FROM ESCREVE e JOIN AUTOR a ON a.id_autor = e.FK_AUTOR_id_autor
                    WHERE e.FK_LIVRO_id_livro = l.id_livro) AS "Autores",
                  i.data_inicio AS "Início", i.data_conclusao AS "Conclusão",
                  av.nota AS "Nota"
           FROM ITEM_ESTANTE i
           JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
           LEFT JOIN AVALIACAO_RESENHA av ON av.FK_USUARIO_id_usuario = i.FK_USUARIO_id_usuario
                                         AND av.FK_LIVRO_id_livro = i.FK_LIVRO_id_livro
           WHERE i.FK_USUARIO_id_usuario = %s AND i.status_leitura = 'Lido'
           ORDER BY i.data_conclusao DESC""",
        (user_id,),
    )
    if len(table) == 0:
        st.caption("Nenhum livro lido ainda.")
    else:
        ui.show_table(table)


def show_current_shelf(user_id):
    st.subheader("Lendo, quero ler e abandonados")
    table = database.fetch_table(
        """SELECT i.status_leitura AS "Status", l.titulo AS "Livro",
                  i.data_inclusao AS "Incluído em", i.data_inicio AS "Início"
           FROM ITEM_ESTANTE i
           JOIN LIVRO l ON l.id_livro = i.FK_LIVRO_id_livro
           WHERE i.FK_USUARIO_id_usuario = %s AND i.status_leitura <> 'Lido'
           ORDER BY i.status_leitura, l.titulo""",
        (user_id,),
    )
    if len(table) == 0:
        st.caption("Nenhum livro nesses status.")
    else:
        ui.show_table(table)


def show_readers_with_same_wish(user_id):
    """For each 'Quero Ler' book of the reader, shows the other users who also want to read it."""
    st.subheader("Outros leitores que querem ler os mesmos livros")
    table = database.fetch_table(
        """SELECT l.titulo AS "Livro",
                  STRING_AGG(u.nome, ', ' ORDER BY u.nome) AS "Também querem ler"
           FROM ITEM_ESTANTE mine
           JOIN ITEM_ESTANTE other ON other.FK_LIVRO_id_livro = mine.FK_LIVRO_id_livro
                                  AND other.FK_USUARIO_id_usuario <> mine.FK_USUARIO_id_usuario
                                  AND other.status_leitura = 'Quero Ler'
           JOIN USUARIO u ON u.id_usuario = other.FK_USUARIO_id_usuario
           JOIN LIVRO l ON l.id_livro = mine.FK_LIVRO_id_livro
           WHERE mine.FK_USUARIO_id_usuario = %s AND mine.status_leitura = 'Quero Ler'
           GROUP BY l.titulo
           ORDER BY l.titulo""",
        (user_id,),
    )
    if len(table) == 0:
        st.caption("Nenhum outro leitor marcou os mesmos livros como Quero Ler.")
    else:
        ui.show_table(table)


def show_reviews(user_id):
    st.subheader("Avaliações e resenhas")
    rows = database.fetch_all(
        """SELECT l.titulo, a.nota, a.texto_resenha, a.data_publicacao
           FROM AVALIACAO_RESENHA a JOIN LIVRO l ON l.id_livro = a.FK_LIVRO_id_livro
           WHERE a.FK_USUARIO_id_usuario = %s
           ORDER BY a.data_publicacao DESC""",
        (user_id,),
    )
    if len(rows) == 0:
        st.caption("Nenhuma avaliação publicada.")
    for row in rows:
        # Two spaces + \n break the line; :gray[...] writes in gray
        st.markdown("**" + row[0] + "**  " + ui.stars(row[1]) + "  \n"
                    + ":gray[Publicada em " + ui.format_date(row[3]) + "]")
        if row[2] is not None:
            st.write(row[2])


def show_groups(user_id):
    st.subheader("Grupos de leitura")
    table = database.fetch_table(
        """SELECT g.nome AS "Grupo", l.titulo AS "Livro", g.situacao AS "Situação do grupo",
                  m.funcao AS "Função", m.status_participacao AS "Participação",
                  CASE WHEN g.FK_USUARIO_id_usuario = m.FK_USUARIO_id_usuario THEN 'sim' ELSE '' END AS "Organizador"
           FROM MEMBRO_GRUPO m
           JOIN GRUPO_LEITURA g ON g.id_grupo = m.FK_GRUPO_LEITURA_id_grupo
           JOIN LIVRO l ON l.id_livro = g.FK_LIVRO_id_livro
           WHERE m.FK_USUARIO_id_usuario = %s
           ORDER BY g.nome""",
        (user_id,),
    )
    if len(table) == 0:
        st.caption("Não participa de nenhum grupo.")
    else:
        ui.show_table(table)


def show_notifications(user_id):
    st.subheader("Notificações")
    table = database.fetch_table(
        """SELECT CASE WHEN lida THEN 'lida' ELSE 'nova' END AS "Situação", tipo AS "Tipo", texto AS "Texto",
                  data_hora AS "Data e hora"
           FROM NOTIFICACAO
           WHERE FK_USUARIO_id_usuario = %s
           ORDER BY lida, data_hora DESC""",
        (user_id,),
    )
    if len(table) == 0:
        st.caption("Nenhuma notificação.")
    else:
        ui.show_table(table)
