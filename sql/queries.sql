-- =====================================================================
-- READLE - Queries of item 6 of the report
-- Each query uses at least 3 tables, returns at least 2 columns and
-- uses at least one aggregate function. The application (screens/queries.py)
-- reads this file and runs these same three statements, in this order.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Query 1 - Average rating by literary genre
-- Goal: for each genre, how many reviews its books received and the
-- average rating of those reviews, to find the best rated genres.
-- Tables: GENERO, CLASSIFICA, AVALIACAO_RESENHA
-- Aggregates: COUNT and AVG
-- ---------------------------------------------------------------------
SELECT g.nome                       AS genero,
       COUNT(a.id_avaliacao)        AS total_avaliacoes,
       ROUND(AVG(a.nota), 2)        AS nota_media
FROM GENERO g
JOIN CLASSIFICA c        ON c.FK_GENERO_id_genero = g.id_genero
JOIN AVALIACAO_RESENHA a ON a.FK_LIVRO_id_livro   = c.FK_LIVRO_id_livro
GROUP BY g.nome
ORDER BY nota_media DESC, total_avaliacoes DESC;


-- ---------------------------------------------------------------------
-- Query 2 - Readers ranked by pages read
-- Goal: for each user, how many books they finished (status 'Lido' on
-- the shelf) and the total number of pages of those books.
-- Tables: USUARIO, ITEM_ESTANTE, LIVRO
-- Aggregates: COUNT and SUM
-- ---------------------------------------------------------------------
SELECT u.nome                       AS leitor,
       COUNT(ie.id_item)            AS livros_lidos,
       SUM(l.numero_paginas)        AS paginas_lidas
FROM USUARIO u
JOIN ITEM_ESTANTE ie ON ie.FK_USUARIO_id_usuario = u.id_usuario
JOIN LIVRO l         ON l.id_livro               = ie.FK_LIVRO_id_livro
WHERE ie.status_leitura = 'Lido'
GROUP BY u.id_usuario, u.nome
ORDER BY paginas_lidas DESC;


-- ---------------------------------------------------------------------
-- Query 3 - Reading group engagement
-- Goal: for each group, the book being discussed, the number of visible
-- messages posted in its stages and how many different members posted.
-- LEFT JOIN keeps the groups that have no messages yet (count zero).
-- Tables: GRUPO_LEITURA, LIVRO, ETAPA_LEITURA, MENSAGEM
-- Aggregates: COUNT and COUNT(DISTINCT)
-- ---------------------------------------------------------------------
SELECT g.nome                                   AS grupo,
       l.titulo                                 AS livro,
       COUNT(m.id_mensagem)                     AS mensagens,
       COUNT(DISTINCT m.FK_MEMBRO_GRUPO_id_membro) AS membros_que_publicaram
FROM GRUPO_LEITURA g
JOIN LIVRO l              ON l.id_livro = g.FK_LIVRO_id_livro
LEFT JOIN ETAPA_LEITURA e ON e.FK_GRUPO_LEITURA_id_grupo = g.id_grupo
LEFT JOIN MENSAGEM m      ON m.FK_ETAPA_LEITURA_id_etapa = e.id_etapa
                         AND m.situacao = 'Visível'
GROUP BY g.id_grupo, g.nome, l.titulo
ORDER BY mensagens DESC;
