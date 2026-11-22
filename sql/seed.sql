/* =====================================================================
   READLE - Seed data (PostgreSQL)
   Run after schema.sql, on a database whose tables are empty.

   Ids are written explicitly to make the file easier to read (every
   reference has a comment saying what it points to). At the end the id
   sequences are moved forward with setval, so rows inserted later by the
   application keep counting from there.

   All dates are relative to the day the script runs (CURRENT_DATE - n),
   so deadlines, locked stages and deadline notices always make sense
   no matter when the database is created.

   The data follows the business rules of the report (Quadro 1). Cases
   included on purpose to demonstrate the application:
   - an author (Conceição Evaristo) and a genre (Poesia) with no books: they can be deleted;
   - the book Rápido e Devagar is on no shelf and in no group: it can be deleted;
   - one closed group, three active groups and one waiting for members;
   - members invited, requesting and removed; hidden messages;
   - future stages that are still locked (RN12) and stages whose deadline
     is in the next 7 days with members who have not finished them yet
     (the 'Gerar avisos de prazo' button creates notices for them).
   ISBNs are fictitious, with valid format and check digit.
   Password of every test user: readle123 (stored as a SHA-256 hash).
   ===================================================================== */

-- Genres
INSERT INTO GENERO (id_genero, nome) VALUES
    (1, 'Romance'),
    (2, 'Fantasia'),
    (3, 'Ficção científica'),
    (4, 'Suspense'),
    (5, 'Clássico'),
    (6, 'Não ficção'),
    (7, 'Distopia'),
    (8, 'Literatura brasileira'),
    (9, 'Poesia');

-- Authors
INSERT INTO AUTOR (id_autor, nome) VALUES
    (1, 'Machado de Assis'),
    (2, 'Aluísio Azevedo'),
    (3, 'Graciliano Ramos'),
    (4, 'Clarice Lispector'),
    (5, 'Jorge Amado'),
    (6, 'J. R. R. Tolkien'),
    (7, 'J. K. Rowling'),
    (8, 'Patrick Rothfuss'),
    (9, 'Frank Herbert'),
    (10, 'Isaac Asimov'),
    (11, 'George Orwell'),
    (12, 'Aldous Huxley'),
    (13, 'Ray Bradbury'),
    (14, 'Margaret Atwood'),
    (15, 'Gillian Flynn'),
    (16, 'Thomas Harris'),
    (17, 'Agatha Christie'),
    (18, 'Jane Austen'),
    (19, 'Colleen Hoover'),
    (20, 'Yuval Noah Harari'),
    (21, 'Charles Duhigg'),
    (22, 'Daniel Kahneman'),
    (23, 'Itamar Vieira Junior'),
    (24, 'Terry Pratchett'),
    (25, 'Neil Gaiman'),
    (26, 'Paulo Coelho'),
    (27, 'Conceição Evaristo');

-- Books
INSERT INTO LIVRO (id_livro, titulo, isbn, ano_publicacao, numero_paginas, sinopse, url_capa) VALUES
    (1, 'Dom Casmurro', '9788535000016', 1899, 256, 'Bentinho revisita a própria vida e o ciúme que sente de Capitu, deixando ao leitor a dúvida sobre a traição.', NULL),
    (2, 'Memórias Póstumas de Brás Cubas', '9788535000023', 1881, 240, 'Um defunto narra a própria vida com ironia, expondo a vaidade da elite carioca do século XIX.', NULL),
    (3, 'O Cortiço', '9788535000030', 1890, 304, 'A vida coletiva de um cortiço no Rio de Janeiro mostra como o ambiente molda as pessoas.', NULL),
    (4, 'Vidas Secas', '9788535000047', 1938, 176, 'Uma família de retirantes atravessa o sertão fugindo da seca e da miséria.', NULL),
    (5, 'A Hora da Estrela', '9788535000054', 1977, 88, 'Um narrador tenta contar a história de Macabéa, nordestina pobre e solitária no Rio de Janeiro.', NULL),
    (6, 'Capitães da Areia', '9788535000061', 1937, 280, 'Um grupo de meninos de rua sobrevive em Salvador entre pequenos furtos e laços de amizade.', NULL),
    (7, 'O Senhor dos Anéis: A Sociedade do Anel', '9788535000078', 1954, 576, 'Frodo recebe um anel perigoso e parte com companheiros para impedir que ele volte ao seu criador.', NULL),
    (8, 'O Hobbit', '9788535000085', 1937, 336, 'Bilbo é arrastado para uma aventura com anões em busca de um tesouro guardado por um dragão.', NULL),
    (9, 'Harry Potter e a Pedra Filosofal', '9788535000092', 1997, 264, 'Um menino descobre que é bruxo e começa seus estudos em uma escola de magia.', NULL),
    (10, 'O Nome do Vento', '9788535000108', 2007, 656, 'Kvothe conta a própria história, da infância numa trupe itinerante aos anos na universidade de magia.', NULL),
    (11, 'Duna', '9788535000115', 1965, 680, 'Num planeta desértico disputado por sua especiaria, um jovem herdeiro enfrenta intrigas políticas.', NULL),
    (12, 'Fundação', '9788535000122', 1951, 320, 'Um matemático prevê a queda de um império galáctico e cria um plano para encurtar a era de barbárie.', NULL),
    (13, 'Eu, Robô', '9788535000139', 1950, 320, 'Contos sobre robôs regidos pelas Três Leis da Robótica e os dilemas que elas produzem.', NULL),
    (14, '1984', '9788535000146', 1949, 416, 'Winston vive sob um regime que vigia tudo e reescreve a história, e começa a questioná-lo.', NULL),
    (15, 'A Revolução dos Bichos', '9788535000153', 1945, 152, 'Animais tomam uma fazenda para viver em igualdade, até que os novos líderes repetem os antigos abusos.', NULL),
    (16, 'Admirável Mundo Novo', '9788535000160', 1932, 312, 'Uma sociedade controla nascimentos e emoções em nome da estabilidade e do consumo.', NULL),
    (17, 'Fahrenheit 451', '9788535000177', 1953, 216, 'Um bombeiro encarregado de queimar livros passa a duvidar do próprio trabalho.', NULL),
    (18, 'O Conto da Aia', '9788535000184', 1985, 368, 'Num regime teocrático, mulheres férteis são obrigadas a servir às famílias da elite.', NULL),
    (19, 'Garota Exemplar', '9788535000191', 2012, 448, 'O desaparecimento de uma esposa transforma o marido no principal suspeito.', NULL),
    (20, 'O Silêncio dos Inocentes', '9788535000207', 1988, 368, 'Uma agente do FBI busca a ajuda de um psiquiatra preso para capturar um assassino.', NULL),
    (21, 'Assassinato no Expresso do Oriente', '9788535000214', 1934, 240, 'Hercule Poirot investiga um crime cometido num trem parado pela neve.', NULL),
    (22, 'E Não Sobrou Nenhum', '9788535000221', 1939, 272, 'Dez desconhecidos são reunidos numa ilha e começam a morrer um a um.', NULL),
    (23, 'Orgulho e Preconceito', '9788535000238', 1813, 424, 'Elizabeth Bennet e o Sr. Darcy precisam superar primeiras impressões e diferenças sociais.', NULL),
    (24, 'É Assim que Acaba', '9788535000245', 2016, 368, 'Lily se apaixona por um neurocirurgião e precisa enfrentar um relacionamento difícil.', NULL),
    (25, 'Sapiens: Uma Breve História da Humanidade', '9788535000252', 2011, 464, 'Um panorama da história humana, da revolução cognitiva à era da ciência.', NULL),
    (26, 'O Poder do Hábito', '9788535000269', 2012, 408, 'Explica como os hábitos se formam e como podem ser modificados.', NULL),
    (27, 'Rápido e Devagar', '9788535000276', 2011, 608, 'Descreve os dois modos de pensamento que orientam nossos julgamentos e decisões.', NULL),
    (28, 'Torto Arado', '9788535000283', 2019, 264, 'Duas irmãs do sertão baiano têm a vida marcada por um acidente na infância e pela luta pela terra.', NULL),
    (29, 'Belas Maldições', '9788535000290', 1990, 400, 'Um anjo e um demônio se unem para adiar o fim do mundo, onde se acostumaram a viver.', NULL),
    (30, 'O Alquimista', '9788535000306', 1988, 208, 'Um pastor andaluz viaja até o Egito atrás de um tesouro que viu em sonho.', NULL);

-- Book authors (ESCREVE)
INSERT INTO ESCREVE (FK_AUTOR_id_autor, FK_LIVRO_id_livro) VALUES
    (1, 1),  -- Machado de Assis / Dom Casmurro
    (1, 2),  -- Machado de Assis / Memórias Póstumas de Brás Cubas
    (2, 3),  -- Aluísio Azevedo / O Cortiço
    (3, 4),  -- Graciliano Ramos / Vidas Secas
    (4, 5),  -- Clarice Lispector / A Hora da Estrela
    (5, 6),  -- Jorge Amado / Capitães da Areia
    (6, 7),  -- J. R. R. Tolkien / O Senhor dos Anéis: A Sociedade do Anel
    (6, 8),  -- J. R. R. Tolkien / O Hobbit
    (7, 9),  -- J. K. Rowling / Harry Potter e a Pedra Filosofal
    (8, 10),  -- Patrick Rothfuss / O Nome do Vento
    (9, 11),  -- Frank Herbert / Duna
    (10, 12),  -- Isaac Asimov / Fundação
    (10, 13),  -- Isaac Asimov / Eu, Robô
    (11, 14),  -- George Orwell / 1984
    (11, 15),  -- George Orwell / A Revolução dos Bichos
    (12, 16),  -- Aldous Huxley / Admirável Mundo Novo
    (13, 17),  -- Ray Bradbury / Fahrenheit 451
    (14, 18),  -- Margaret Atwood / O Conto da Aia
    (15, 19),  -- Gillian Flynn / Garota Exemplar
    (16, 20),  -- Thomas Harris / O Silêncio dos Inocentes
    (17, 21),  -- Agatha Christie / Assassinato no Expresso do Oriente
    (17, 22),  -- Agatha Christie / E Não Sobrou Nenhum
    (18, 23),  -- Jane Austen / Orgulho e Preconceito
    (19, 24),  -- Colleen Hoover / É Assim que Acaba
    (20, 25),  -- Yuval Noah Harari / Sapiens: Uma Breve História da Humanidade
    (21, 26),  -- Charles Duhigg / O Poder do Hábito
    (22, 27),  -- Daniel Kahneman / Rápido e Devagar
    (23, 28),  -- Itamar Vieira Junior / Torto Arado
    (24, 29),  -- Terry Pratchett / Belas Maldições
    (25, 29),  -- Neil Gaiman / Belas Maldições
    (26, 30);  -- Paulo Coelho / O Alquimista

-- Book genres (CLASSIFICA)
INSERT INTO CLASSIFICA (FK_GENERO_id_genero, FK_LIVRO_id_livro) VALUES
    (5, 1),  -- Clássico / Dom Casmurro
    (8, 1),  -- Literatura brasileira / Dom Casmurro
    (1, 1),  -- Romance / Dom Casmurro
    (5, 2),  -- Clássico / Memórias Póstumas de Brás Cubas
    (8, 2),  -- Literatura brasileira / Memórias Póstumas de Brás Cubas
    (5, 3),  -- Clássico / O Cortiço
    (8, 3),  -- Literatura brasileira / O Cortiço
    (8, 4),  -- Literatura brasileira / Vidas Secas
    (5, 4),  -- Clássico / Vidas Secas
    (8, 5),  -- Literatura brasileira / A Hora da Estrela
    (8, 6),  -- Literatura brasileira / Capitães da Areia
    (1, 6),  -- Romance / Capitães da Areia
    (2, 7),  -- Fantasia / O Senhor dos Anéis: A Sociedade do Anel
    (2, 8),  -- Fantasia / O Hobbit
    (2, 9),  -- Fantasia / Harry Potter e a Pedra Filosofal
    (2, 10),  -- Fantasia / O Nome do Vento
    (3, 11),  -- Ficção científica / Duna
    (3, 12),  -- Ficção científica / Fundação
    (3, 13),  -- Ficção científica / Eu, Robô
    (7, 14),  -- Distopia / 1984
    (3, 14),  -- Ficção científica / 1984
    (5, 14),  -- Clássico / 1984
    (7, 15),  -- Distopia / A Revolução dos Bichos
    (5, 15),  -- Clássico / A Revolução dos Bichos
    (7, 16),  -- Distopia / Admirável Mundo Novo
    (3, 16),  -- Ficção científica / Admirável Mundo Novo
    (7, 17),  -- Distopia / Fahrenheit 451
    (3, 17),  -- Ficção científica / Fahrenheit 451
    (7, 18),  -- Distopia / O Conto da Aia
    (4, 19),  -- Suspense / Garota Exemplar
    (4, 20),  -- Suspense / O Silêncio dos Inocentes
    (4, 21),  -- Suspense / Assassinato no Expresso do Oriente
    (5, 21),  -- Clássico / Assassinato no Expresso do Oriente
    (4, 22),  -- Suspense / E Não Sobrou Nenhum
    (1, 23),  -- Romance / Orgulho e Preconceito
    (5, 23),  -- Clássico / Orgulho e Preconceito
    (1, 24),  -- Romance / É Assim que Acaba
    (6, 25),  -- Não ficção / Sapiens: Uma Breve História da Humanidade
    (6, 26),  -- Não ficção / O Poder do Hábito
    (6, 27),  -- Não ficção / Rápido e Devagar
    (8, 28),  -- Literatura brasileira / Torto Arado
    (1, 28),  -- Romance / Torto Arado
    (2, 29),  -- Fantasia / Belas Maldições
    (8, 30);  -- Literatura brasileira / O Alquimista

-- Users
INSERT INTO USUARIO (id_usuario, nome_usuario, email, senha_hash, data_cadastro, nome) VALUES
    (1, 'ana.souza', 'ana.souza@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 584, 'Ana Souza'),
    (2, 'bruno.lima', 'bruno.lima@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 565, 'Bruno Lima'),
    (3, 'carla.mendes', 'carla.mendes@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 517, 'Carla Mendes'),
    (4, 'diego.rocha', 'diego.rocha@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 495, 'Diego Rocha'),
    (5, 'eduarda.alves', 'eduarda.alves@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 468, 'Eduarda Alves'),
    (6, 'felipe.costa', 'felipe.costa@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 426, 'Felipe Costa'),
    (7, 'gabi.nunes', 'gabi.nunes@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 381, 'Gabriela Nunes'),
    (8, 'henrique.dias', 'henrique.dias@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 326, 'Henrique Dias'),
    (9, 'isa.martins', 'isa.martins@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 277, 'Isabela Martins'),
    (10, 'joao.pereira', 'joao.pereira@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 224, 'João Pereira'),
    (11, 'larissa.gomes', 'larissa.gomes@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 119, 'Larissa Gomes'),
    (12, 'mateus.ribeiro', 'mateus.ribeiro@exemplo.com', '8dd87f414e7d61bfad9c0d64dc06877386fee3c2b447e40ed98f8014320a7a1f', CURRENT_DATE - 19, 'Mateus Ribeiro');

-- Bookshelves (ITEM_ESTANTE)
INSERT INTO ITEM_ESTANTE (id_item, status_leitura, data_inclusao, data_inicio, data_conclusao, FK_LIVRO_id_livro, FK_USUARIO_id_usuario) VALUES
    (1, 'Lido', CURRENT_DATE - 568, CURRENT_DATE - 551, CURRENT_DATE - 536, 8, 1),  -- Ana Souza / O Hobbit
    (2, 'Abandonado', CURRENT_DATE - 567, CURRENT_DATE - 553, NULL, 26, 1),  -- Ana Souza / O Poder do Hábito
    (3, 'Lido', CURRENT_DATE - 508, CURRENT_DATE - 480, CURRENT_DATE - 470, 9, 1),  -- Ana Souza / Harry Potter e a Pedra Filosofal
    (4, 'Quero Ler', CURRENT_DATE - 474, NULL, NULL, 18, 1),  -- Ana Souza / O Conto da Aia
    (5, 'Lido', CURRENT_DATE - 452, CURRENT_DATE - 423, CURRENT_DATE - 387, 10, 1),  -- Ana Souza / O Nome do Vento
    (6, 'Lido', CURRENT_DATE - 378, CURRENT_DATE - 352, CURRENT_DATE - 322, 11, 1),  -- Ana Souza / Duna
    (7, 'Lido', CURRENT_DATE - 313, CURRENT_DATE - 288, CURRENT_DATE - 276, 16, 1),  -- Ana Souza / Admirável Mundo Novo
    (8, 'Lido', CURRENT_DATE - 251, CURRENT_DATE - 231, CURRENT_DATE - 186, 1, 1),  -- Ana Souza / Dom Casmurro
    (9, 'Lido', CURRENT_DATE - 240, CURRENT_DATE - 225, CURRENT_DATE - 209, 23, 1),  -- Ana Souza / Orgulho e Preconceito
    (10, 'Lido', CURRENT_DATE - 186, CURRENT_DATE - 166, CURRENT_DATE - 141, 25, 1),  -- Ana Souza / Sapiens: Uma Breve História da Humanidade
    (11, 'Lido', CURRENT_DATE - 114, CURRENT_DATE - 104, CURRENT_DATE - 82, 29, 1),  -- Ana Souza / Belas Maldições
    (12, 'Quero Ler', CURRENT_DATE - 114, NULL, NULL, 28, 1),  -- Ana Souza / Torto Arado
    (13, 'Lendo', CURRENT_DATE - 59, CURRENT_DATE - 55, NULL, 7, 1),  -- Ana Souza / O Senhor dos Anéis: A Sociedade do Anel
    (14, 'Lido', CURRENT_DATE - 527, CURRENT_DATE - 516, CURRENT_DATE - 507, 2, 2),  -- Bruno Lima / Memórias Póstumas de Brás Cubas
    (15, 'Lido', CURRENT_DATE - 447, CURRENT_DATE - 438, CURRENT_DATE - 424, 12, 2),  -- Bruno Lima / Fundação
    (16, 'Lido', CURRENT_DATE - 380, CURRENT_DATE - 354, CURRENT_DATE - 340, 13, 2),  -- Bruno Lima / Eu, Robô
    (17, 'Lido', CURRENT_DATE - 288, CURRENT_DATE - 271, CURRENT_DATE - 263, 17, 2),  -- Bruno Lima / Fahrenheit 451
    (18, 'Quero Ler', CURRENT_DATE - 261, NULL, NULL, 20, 2),  -- Bruno Lima / O Silêncio dos Inocentes
    (19, 'Quero Ler', CURRENT_DATE - 256, NULL, NULL, 11, 2),  -- Bruno Lima / Duna
    (20, 'Lido', CURRENT_DATE - 235, CURRENT_DATE - 230, CURRENT_DATE - 180, 1, 2),  -- Bruno Lima / Dom Casmurro
    (21, 'Lido', CURRENT_DATE - 205, CURRENT_DATE - 194, CURRENT_DATE - 185, 21, 2),  -- Bruno Lima / Assassinato no Expresso do Oriente
    (22, 'Lido', CURRENT_DATE - 129, CURRENT_DATE - 111, CURRENT_DATE - 101, 22, 2),  -- Bruno Lima / E Não Sobrou Nenhum
    (23, 'Abandonado', CURRENT_DATE - 80, CURRENT_DATE - 77, NULL, 24, 2),  -- Bruno Lima / É Assim que Acaba
    (24, 'Lendo', CURRENT_DATE - 38, CURRENT_DATE - 37, NULL, 14, 2),  -- Bruno Lima / 1984
    (25, 'Lido', CURRENT_DATE - 496, CURRENT_DATE - 468, CURRENT_DATE - 460, 15, 3),  -- Carla Mendes / A Revolução dos Bichos
    (26, 'Lido', CURRENT_DATE - 392, CURRENT_DATE - 377, CURRENT_DATE - 363, 16, 3),  -- Carla Mendes / Admirável Mundo Novo
    (27, 'Lido', CURRENT_DATE - 299, CURRENT_DATE - 286, CURRENT_DATE - 266, 18, 3),  -- Carla Mendes / O Conto da Aia
    (28, 'Lido', CURRENT_DATE - 234, CURRENT_DATE - 231, CURRENT_DATE - 184, 1, 3),  -- Carla Mendes / Dom Casmurro
    (29, 'Lido', CURRENT_DATE - 222, CURRENT_DATE - 194, CURRENT_DATE - 181, 3, 3),  -- Carla Mendes / O Cortiço
    (30, 'Lido', CURRENT_DATE - 128, CURRENT_DATE - 111, CURRENT_DATE - 92, 23, 3),  -- Carla Mendes / Orgulho e Preconceito
    (31, 'Quero Ler', CURRENT_DATE - 123, NULL, NULL, 19, 3),  -- Carla Mendes / Garota Exemplar
    (32, 'Quero Ler', CURRENT_DATE - 97, NULL, NULL, 10, 3),  -- Carla Mendes / O Nome do Vento
    (33, 'Lendo', CURRENT_DATE - 65, CURRENT_DATE - 37, NULL, 14, 3),  -- Carla Mendes / 1984
    (34, 'Quero Ler', CURRENT_DATE - 473, NULL, NULL, 11, 4),  -- Diego Rocha / Duna
    (35, 'Lido', CURRENT_DATE - 464, CURRENT_DATE - 434, CURRENT_DATE - 418, 20, 4),  -- Diego Rocha / O Silêncio dos Inocentes
    (36, 'Lido', CURRENT_DATE - 354, CURRENT_DATE - 326, CURRENT_DATE - 314, 22, 4),  -- Diego Rocha / E Não Sobrou Nenhum
    (37, 'Lido', CURRENT_DATE - 251, CURRENT_DATE - 221, CURRENT_DATE - 212, 21, 4),  -- Diego Rocha / Assassinato no Expresso do Oriente
    (38, 'Lido', CURRENT_DATE - 233, CURRENT_DATE - 228, CURRENT_DATE - 181, 1, 4),  -- Diego Rocha / Dom Casmurro
    (39, 'Lido', CURRENT_DATE - 129, CURRENT_DATE - 112, CURRENT_DATE - 97, 26, 4),  -- Diego Rocha / O Poder do Hábito
    (40, 'Quero Ler', CURRENT_DATE - 73, NULL, NULL, 25, 4),  -- Diego Rocha / Sapiens: Uma Breve História da Humanidade
    (41, 'Abandonado', CURRENT_DATE - 17, CURRENT_DATE - 17, NULL, 19, 4),  -- Diego Rocha / Garota Exemplar
    (42, 'Lido', CURRENT_DATE - 441, CURRENT_DATE - 414, CURRENT_DATE - 410, 5, 5),  -- Eduarda Alves / A Hora da Estrela
    (43, 'Quero Ler', CURRENT_DATE - 341, NULL, NULL, 30, 5),  -- Eduarda Alves / O Alquimista
    (44, 'Lido', CURRENT_DATE - 333, CURRENT_DATE - 316, CURRENT_DATE - 310, 4, 5),  -- Eduarda Alves / Vidas Secas
    (45, 'Lido', CURRENT_DATE - 234, CURRENT_DATE - 214, CURRENT_DATE - 204, 28, 5),  -- Eduarda Alves / Torto Arado
    (46, 'Lido', CURRENT_DATE - 232, CURRENT_DATE - 229, CURRENT_DATE - 178, 1, 5),  -- Eduarda Alves / Dom Casmurro
    (47, 'Quero Ler', CURRENT_DATE - 212, NULL, NULL, 9, 5),  -- Eduarda Alves / Harry Potter e a Pedra Filosofal
    (48, 'Lido', CURRENT_DATE - 113, CURRENT_DATE - 108, CURRENT_DATE - 92, 24, 5),  -- Eduarda Alves / É Assim que Acaba
    (49, 'Lendo', CURRENT_DATE - 38, CURRENT_DATE - 35, NULL, 14, 5),  -- Eduarda Alves / 1984
    (50, 'Lido', CURRENT_DATE - 402, CURRENT_DATE - 379, CURRENT_DATE - 367, 8, 6),  -- Felipe Costa / O Hobbit
    (51, 'Lido', CURRENT_DATE - 298, CURRENT_DATE - 282, CURRENT_DATE - 272, 9, 6),  -- Felipe Costa / Harry Potter e a Pedra Filosofal
    (52, 'Lido', CURRENT_DATE - 207, CURRENT_DATE - 189, CURRENT_DATE - 171, 29, 6),  -- Felipe Costa / Belas Maldições
    (53, 'Quero Ler', CURRENT_DATE - 136, NULL, NULL, 11, 6),  -- Felipe Costa / Duna
    (54, 'Lido', CURRENT_DATE - 110, CURRENT_DATE - 100, CURRENT_DATE - 75, 10, 6),  -- Felipe Costa / O Nome do Vento
    (55, 'Lendo', CURRENT_DATE - 81, CURRENT_DATE - 55, NULL, 7, 6),  -- Felipe Costa / O Senhor dos Anéis: A Sociedade do Anel
    (56, 'Quero Ler', CURRENT_DATE - 355, NULL, NULL, 23, 7),  -- Gabriela Nunes / Orgulho e Preconceito
    (57, 'Lido', CURRENT_DATE - 335, CURRENT_DATE - 319, CURRENT_DATE - 309, 22, 7),  -- Gabriela Nunes / E Não Sobrou Nenhum
    (58, 'Lido', CURRENT_DATE - 220, CURRENT_DATE - 213, CURRENT_DATE - 197, 20, 7),  -- Gabriela Nunes / O Silêncio dos Inocentes
    (59, 'Lido', CURRENT_DATE - 108, CURRENT_DATE - 107, CURRENT_DATE - 91, 24, 7),  -- Gabriela Nunes / É Assim que Acaba
    (60, 'Lendo', CURRENT_DATE - 59, CURRENT_DATE - 54, NULL, 7, 7),  -- Gabriela Nunes / O Senhor dos Anéis: A Sociedade do Anel
    (61, 'Lendo', CURRENT_DATE - 29, CURRENT_DATE - 17, NULL, 19, 7),  -- Gabriela Nunes / Garota Exemplar
    (62, 'Lido', CURRENT_DATE - 318, CURRENT_DATE - 289, CURRENT_DATE - 263, 11, 8),  -- Henrique Dias / Duna
    (63, 'Lido', CURRENT_DATE - 246, CURRENT_DATE - 216, CURRENT_DATE - 204, 12, 8),  -- Henrique Dias / Fundação
    (64, 'Lido', CURRENT_DATE - 178, CURRENT_DATE - 148, CURRENT_DATE - 139, 17, 8),  -- Henrique Dias / Fahrenheit 451
    (65, 'Lido', CURRENT_DATE - 106, CURRENT_DATE - 83, CURRENT_DATE - 62, 25, 8),  -- Henrique Dias / Sapiens: Uma Breve História da Humanidade
    (66, 'Quero Ler', CURRENT_DATE - 68, NULL, NULL, 13, 8),  -- Henrique Dias / Eu, Robô
    (67, 'Lendo', CURRENT_DATE - 58, CURRENT_DATE - 54, NULL, 7, 8),  -- Henrique Dias / O Senhor dos Anéis: A Sociedade do Anel
    (68, 'Lendo', CURRENT_DATE - 17, CURRENT_DATE - 16, NULL, 19, 8),  -- Henrique Dias / Garota Exemplar
    (69, 'Lido', CURRENT_DATE - 256, CURRENT_DATE - 231, CURRENT_DATE - 221, 9, 9),  -- Isabela Martins / Harry Potter e a Pedra Filosofal
    (70, 'Lido', CURRENT_DATE - 173, CURRENT_DATE - 155, CURRENT_DATE - 146, 30, 9),  -- Isabela Martins / O Alquimista
    (71, 'Lido', CURRENT_DATE - 97, CURRENT_DATE - 86, CURRENT_DATE - 68, 26, 9),  -- Isabela Martins / O Poder do Hábito
    (72, 'Lendo', CURRENT_DATE - 56, CURRENT_DATE - 52, NULL, 7, 9),  -- Isabela Martins / O Senhor dos Anéis: A Sociedade do Anel
    (73, 'Quero Ler', CURRENT_DATE - 33, NULL, NULL, 8, 9),  -- Isabela Martins / O Hobbit
    (74, 'Quero Ler', CURRENT_DATE - 3, NULL, NULL, 12, 9),  -- Isabela Martins / Fundação
    (75, 'Lido', CURRENT_DATE - 201, CURRENT_DATE - 178, CURRENT_DATE - 172, 15, 10),  -- João Pereira / A Revolução dos Bichos
    (76, 'Quero Ler', CURRENT_DATE - 168, NULL, NULL, 2, 10),  -- João Pereira / Memórias Póstumas de Brás Cubas
    (77, 'Lido', CURRENT_DATE - 96, CURRENT_DATE - 81, CURRENT_DATE - 69, 6, 10),  -- João Pereira / Capitães da Areia
    (78, 'Lendo', CURRENT_DATE - 55, CURRENT_DATE - 53, NULL, 7, 10),  -- João Pereira / O Senhor dos Anéis: A Sociedade do Anel
    (79, 'Lendo', CURRENT_DATE - 36, CURRENT_DATE - 34, NULL, 14, 10),  -- João Pereira / 1984
    (80, 'Lido', CURRENT_DATE - 87, CURRENT_DATE - 71, CURRENT_DATE - 57, 24, 11),  -- Larissa Gomes / É Assim que Acaba
    (81, 'Quero Ler', CURRENT_DATE - 7, NULL, NULL, 7, 11),  -- Larissa Gomes / O Senhor dos Anéis: A Sociedade do Anel
    (82, 'Quero Ler', CURRENT_DATE - 14, NULL, NULL, 12, 12),  -- Mateus Ribeiro / Fundação
    (83, 'Lendo', CURRENT_DATE - 14, CURRENT_DATE - 11, NULL, 13, 12),  -- Mateus Ribeiro / Eu, Robô
    (84, 'Quero Ler', CURRENT_DATE - 3, NULL, NULL, 7, 12);  -- Mateus Ribeiro / O Senhor dos Anéis: A Sociedade do Anel

-- Reviews (only for books marked Lido on the reviewer shelf, RN04)
INSERT INTO AVALIACAO_RESENHA (id_avaliacao, nota, texto_resenha, data_publicacao, FK_LIVRO_id_livro, FK_USUARIO_id_usuario) VALUES
    (1, 5, 'Reli depois de anos e continua uma delícia. Bilbo reclamando de tudo e indo mesmo assim é o melhor do livro.', CURRENT_DATE - 534, 8, 1),  -- Ana Souza / O Hobbit
    (2, 4, 'Leitura rápida e gostosa. O começo com os Dursley demora, mas depois de Hogwarts não larguei.', CURRENT_DATE - 469, 9, 1),  -- Ana Souza / Harry Potter e a Pedra Filosofal
    (3, 5, 'Kvothe contando a própria história é um jeito lindo de narrar. A parte da universidade é a minha favorita.', CURRENT_DATE - 387, 10, 1),  -- Ana Souza / O Nome do Vento
    (4, 4, NULL, CURRENT_DATE - 276, 16, 1),  -- Ana Souza / Admirável Mundo Novo
    (5, 5, 'Cheguei ao fim sem saber em quem acreditar, e acho que é essa a graça. Machado brinca com o leitor o tempo todo.', CURRENT_DATE - 182, 1, 1),  -- Ana Souza / Dom Casmurro
    (6, 4, 'Os diálogos da Elizabeth são ótimos. Achei o meio um pouco lento, cheio de bailes e visitas.', CURRENT_DATE - 208, 23, 1),  -- Ana Souza / Orgulho e Preconceito
    (7, 5, 'Ri alto várias vezes. Crowley e Aziraphale juntos funcionam demais.', CURRENT_DATE - 80, 29, 1),  -- Ana Souza / Belas Maldições
    (8, 4, NULL, CURRENT_DATE - 502, 2, 2),  -- Bruno Lima / Memórias Póstumas de Brás Cubas
    (9, 4, 'As ideias são enormes e a leitura é leve. Senti falta de personagens que durassem mais de um capítulo.', CURRENT_DATE - 422, 12, 2),  -- Bruno Lima / Fundação
    (10, 4, 'Curto e direto. Os bombeiros queimando livros ficaram na minha cabeça por dias.', CURRENT_DATE - 259, 17, 2),  -- Bruno Lima / Fahrenheit 451
    (11, 3, 'Entendo por que é clássico, mas o Bentinho me irritou do começo ao fim.', CURRENT_DATE - 175, 1, 2),  -- Bruno Lima / Dom Casmurro
    (12, 3, NULL, CURRENT_DATE - 180, 21, 2),  -- Bruno Lima / Assassinato no Expresso do Oriente
    (13, 5, 'Dá para ler numa tarde e passar a semana pensando. Os mandamentos mudando na parede são geniais.', CURRENT_DATE - 456, 15, 3),  -- Carla Mendes / A Revolução dos Bichos
    (14, 4, 'Mais assustador do que eu esperava, justamente porque todo mundo ali parece feliz.', CURRENT_DATE - 359, 16, 3),  -- Carla Mendes / Admirável Mundo Novo
    (15, 5, 'Pesado, mas necessário. A voz da Offred é contida e por isso dói mais.', CURRENT_DATE - 263, 18, 3),  -- Carla Mendes / O Conto da Aia
    (16, 4, NULL, CURRENT_DATE - 179, 1, 3),  -- Carla Mendes / Dom Casmurro
    (17, 4, 'O cortiço é o personagem principal. Algumas descrições envelheceram mal, mas é um retrato forte da época.', CURRENT_DATE - 179, 3, 3),  -- Carla Mendes / O Cortiço
    (18, 5, 'Terceira vez que leio e ainda rio com a senhora Bennet.', CURRENT_DATE - 89, 23, 3),  -- Carla Mendes / Orgulho e Preconceito
    (19, 3, 'Os capítulos com o Lecter são ótimos; o resto da investigação me pareceu comum.', CURRENT_DATE - 415, 20, 4),  -- Diego Rocha / O Silêncio dos Inocentes
    (20, 4, NULL, CURRENT_DATE - 212, 21, 4),  -- Diego Rocha / Assassinato no Expresso do Oriente
    (21, 5, 'Li para o clube e virou um dos meus preferidos. Capitu merecia um livro só dela.', CURRENT_DATE - 181, 1, 4),  -- Diego Rocha / Dom Casmurro
    (22, 3, 'Tem bons exemplos, mas repete a mesma ideia muitas vezes.', CURRENT_DATE - 92, 26, 4),  -- Diego Rocha / O Poder do Hábito
    (23, 3, 'Bonito e muito triste. Os capítulos soltos me deixaram meio perdida no começo.', CURRENT_DATE - 310, 4, 5),  -- Eduarda Alves / Vidas Secas
    (24, 4, NULL, CURRENT_DATE - 200, 28, 5),  -- Eduarda Alves / Torto Arado
    (25, 3, 'Gostei mais das conversas do clube do que do livro em si.', CURRENT_DATE - 176, 1, 5),  -- Eduarda Alves / Dom Casmurro
    (26, 5, 'Foi o livro que me fez gostar de fantasia. O jogo de adivinhas com o Gollum é perfeito.', CURRENT_DATE - 364, 8, 6),  -- Felipe Costa / O Hobbit
    (27, 5, 'Li em dois dias. Já comecei o segundo.', CURRENT_DATE - 271, 9, 6),  -- Felipe Costa / Harry Potter e a Pedra Filosofal
    (28, 4, NULL, CURRENT_DATE - 167, 29, 6),  -- Felipe Costa / Belas Maldições
    (29, 3, 'A ideia é ótima, mas adivinhei o culpado antes da metade.', CURRENT_DATE - 306, 22, 7),  -- Gabriela Nunes / E Não Sobrou Nenhum
    (30, 3, 'Esperava mais tensão. O filme me assustou mais do que o livro.', CURRENT_DATE - 196, 20, 7),  -- Gabriela Nunes / O Silêncio dos Inocentes
    (31, 3, 'Tema importante, mas o romance do começo demorou para me convencer.', CURRENT_DATE - 91, 24, 7),  -- Gabriela Nunes / É Assim que Acaba
    (32, 4, 'A psico-história é uma das ideias mais legais que já li. O texto é seco, mas funciona.', CURRENT_DATE - 199, 12, 8),  -- Henrique Dias / Fundação
    (33, 4, 'Escrito em 1953 e parece falar das telas de hoje.', CURRENT_DATE - 133, 17, 8),  -- Henrique Dias / Fahrenheit 451
    (34, 3, 'Interessante, mas o autor afirma muita coisa com mais certeza do que eu gostaria.', CURRENT_DATE - 59, 25, 8),  -- Henrique Dias / Sapiens: Uma Breve História da Humanidade
    (35, 4, NULL, CURRENT_DATE - 143, 30, 9),  -- Isabela Martins / O Alquimista
    (36, 2, 'Parece um artigo longo esticado até virar livro. Parei duas vezes antes de terminar.', CURRENT_DATE - 67, 26, 9),  -- Isabela Martins / O Poder do Hábito
    (37, 4, 'Simples na superfície e cheio de camadas. Ótimo para ler em grupo.', CURRENT_DATE - 171, 15, 10),  -- João Pereira / A Revolução dos Bichos
    (38, 3, 'Me emocionou em algumas partes, mas a escrita é bem básica.', CURRENT_DATE - 52, 24, 11);  -- Larissa Gomes / É Assim que Acaba

-- Reading groups (FK_USUARIO_id_usuario = organizer)
INSERT INTO GRUPO_LEITURA (id_grupo, nome, descricao, privacidade, data_criacao, situacao, FK_LIVRO_id_livro, FK_USUARIO_id_usuario) VALUES
    (1, 'Clube dos Clássicos', 'Leitura conjunta de clássicos da literatura brasileira, começando por Dom Casmurro.', 'Público', CURRENT_DATE - 236, 'Encerrado', 1, 1),  -- Dom Casmurro / organizer: Ana Souza
    (2, 'Expedição Terra-média', 'Primeira parte de O Senhor dos Anéis, lida em quatro etapas.', 'Público', CURRENT_DATE - 60, 'Ativo', 7, 6),  -- O Senhor dos Anéis: A Sociedade do Anel / organizer: Felipe Costa
    (3, 'Distopias em Debate', 'Grupo fechado para discutir 1984 e suas relações com o mundo atual.', 'Privado', CURRENT_DATE - 39, 'Ativo', 14, 3),  -- 1984 / organizer: Carla Mendes
    (4, 'Suspense de Sexta', 'Leitura de suspense com conversas às sextas-feiras.', 'Público', CURRENT_DATE - 18, 'Ativo', 19, 7),  -- Garota Exemplar / organizer: Gabriela Nunes
    (5, 'Fundação para Iniciantes', 'Para quem nunca leu Asimov e quer começar pela série Fundação.', 'Público', CURRENT_DATE - 4, 'Aguardando membros', 12, 12);  -- Fundação / organizer: Mateus Ribeiro

-- Group members (the organizer is also an active member, RN06)
INSERT INTO MEMBRO_GRUPO (id_membro, funcao, status_participacao, data_entrada, FK_USUARIO_id_usuario, FK_GRUPO_LEITURA_id_grupo) VALUES
    (1, 'Moderador', 'Ativo', CURRENT_DATE - 236, 1, 1),  -- Ana Souza / Clube dos Clássicos
    (2, 'Membro', 'Ativo', CURRENT_DATE - 235, 2, 1),  -- Bruno Lima / Clube dos Clássicos
    (3, 'Membro', 'Ativo', CURRENT_DATE - 234, 3, 1),  -- Carla Mendes / Clube dos Clássicos
    (4, 'Membro', 'Ativo', CURRENT_DATE - 233, 4, 1),  -- Diego Rocha / Clube dos Clássicos
    (5, 'Moderador', 'Ativo', CURRENT_DATE - 232, 5, 1),  -- Eduarda Alves / Clube dos Clássicos
    (6, 'Moderador', 'Ativo', CURRENT_DATE - 60, 6, 2),  -- Felipe Costa / Expedição Terra-média
    (7, 'Membro', 'Ativo', CURRENT_DATE - 59, 1, 2),  -- Ana Souza / Expedição Terra-média
    (8, 'Membro', 'Ativo', CURRENT_DATE - 59, 7, 2),  -- Gabriela Nunes / Expedição Terra-média
    (9, 'Moderador', 'Ativo', CURRENT_DATE - 58, 8, 2),  -- Henrique Dias / Expedição Terra-média
    (10, 'Membro', 'Ativo', CURRENT_DATE - 56, 9, 2),  -- Isabela Martins / Expedição Terra-média
    (11, 'Membro', 'Ativo', CURRENT_DATE - 55, 10, 2),  -- João Pereira / Expedição Terra-média
    (12, 'Membro', 'Convidado', CURRENT_DATE - 7, 11, 2),  -- Larissa Gomes / Expedição Terra-média
    (13, 'Membro', 'Solicitado', CURRENT_DATE - 3, 12, 2),  -- Mateus Ribeiro / Expedição Terra-média
    (14, 'Moderador', 'Ativo', CURRENT_DATE - 39, 3, 3),  -- Carla Mendes / Distopias em Debate
    (15, 'Moderador', 'Ativo', CURRENT_DATE - 38, 2, 3),  -- Bruno Lima / Distopias em Debate
    (16, 'Membro', 'Ativo', CURRENT_DATE - 38, 5, 3),  -- Eduarda Alves / Distopias em Debate
    (17, 'Membro', 'Ativo', CURRENT_DATE - 36, 10, 3),  -- João Pereira / Distopias em Debate
    (18, 'Moderador', 'Ativo', CURRENT_DATE - 18, 7, 4),  -- Gabriela Nunes / Suspense de Sexta
    (19, 'Membro', 'Ativo', CURRENT_DATE - 17, 8, 4),  -- Henrique Dias / Suspense de Sexta
    (20, 'Membro', 'Removido', CURRENT_DATE - 17, 4, 4),  -- Diego Rocha / Suspense de Sexta
    (21, 'Moderador', 'Ativo', CURRENT_DATE - 4, 12, 5),  -- Mateus Ribeiro / Fundação para Iniciantes
    (22, 'Membro', 'Convidado', CURRENT_DATE - 3, 9, 5);  -- Isabela Martins / Fundação para Iniciantes

-- Reading stages
INSERT INTO ETAPA_LEITURA (id_etapa, titulo, ordem, descricao, data_limite, FK_GRUPO_LEITURA_id_grupo) VALUES
    (1, 'Capítulos 1 a 40', 1, 'Apresentação de Bentinho, José Dias e a infância com Capitu.', CURRENT_DATE - 213, 1),  -- Clube dos Clássicos
    (2, 'Capítulos 41 a 90', 2, 'O seminário e a juventude do casal.', CURRENT_DATE - 197, 1),  -- Clube dos Clássicos
    (3, 'Capítulos 91 a 148', 3, 'Casamento, Escobar e o desfecho.', CURRENT_DATE - 177, 1),  -- Clube dos Clássicos
    (4, 'Livro I, capítulos 1 a 6', 1, 'Do aniversário de Bilbo até a saída do Condado.', CURRENT_DATE - 34, 2),  -- Expedição Terra-média
    (5, 'Livro I, capítulos 7 a 12', 2, 'A viagem até Valfenda.', CURRENT_DATE - 14, 2),  -- Expedição Terra-média
    (6, 'Livro II, capítulos 1 a 5', 3, 'O Conselho de Elrond e a travessia de Moria.', CURRENT_DATE + 5, 2),  -- Expedição Terra-média
    (7, 'Livro II, capítulos 6 a 10', 4, 'Lothlórien e a separação da Sociedade.', CURRENT_DATE + 32, 2),  -- Expedição Terra-média
    (8, 'Parte 1', 1, 'O cotidiano de Winston sob vigilância do Partido.', CURRENT_DATE - 19, 3),  -- Distopias em Debate
    (9, 'Parte 2', 2, 'Julia e a tentativa de resistência.', CURRENT_DATE + 6, 3),  -- Distopias em Debate
    (10, 'Parte 3 e apêndice', 3, 'O Ministério do Amor e os princípios da Novafala.', CURRENT_DATE + 32, 3),  -- Distopias em Debate
    (11, 'Parte 1', 1, 'O desaparecimento de Amy e o diário.', CURRENT_DATE + 12, 4),  -- Suspense de Sexta
    (12, 'Partes 2 e 3', 2, 'As revelações e o desfecho.', CURRENT_DATE + 42, 4),  -- Suspense de Sexta
    (13, 'Os psico-historiadores e Os enciclopedistas', 1, 'Hari Seldon e a criação da Fundação.', CURRENT_DATE + 22, 5),  -- Fundação para Iniciantes
    (14, 'Os prefeitos e Os comerciantes', 2, 'A Fundação diante dos reinos vizinhos.', CURRENT_DATE + 42, 5),  -- Fundação para Iniciantes
    (15, 'Os príncipes mercadores', 3, 'O comércio como instrumento de poder.', CURRENT_DATE + 62, 5);  -- Fundação para Iniciantes

-- Stage progress (member and stage of the same group, RN11)
INSERT INTO PROGRESSO_ETAPA (id_progresso, concluida, data_confirmacao, FK_ETAPA_LEITURA_id_etapa, FK_MEMBRO_GRUPO_id_membro) VALUES
    (1, TRUE, CURRENT_DATE - 218, 1, 1),  -- Ana Souza / Clube dos Clássicos, stage 1
    (2, TRUE, CURRENT_DATE - 203, 2, 1),  -- Ana Souza / Clube dos Clássicos, stage 2
    (3, TRUE, CURRENT_DATE - 186, 3, 1),  -- Ana Souza / Clube dos Clássicos, stage 3
    (4, TRUE, CURRENT_DATE - 216, 1, 2),  -- Bruno Lima / Clube dos Clássicos, stage 1
    (5, TRUE, CURRENT_DATE - 200, 2, 2),  -- Bruno Lima / Clube dos Clássicos, stage 2
    (6, TRUE, CURRENT_DATE - 180, 3, 2),  -- Bruno Lima / Clube dos Clássicos, stage 3
    (7, TRUE, CURRENT_DATE - 217, 1, 3),  -- Carla Mendes / Clube dos Clássicos, stage 1
    (8, TRUE, CURRENT_DATE - 199, 2, 3),  -- Carla Mendes / Clube dos Clássicos, stage 2
    (9, TRUE, CURRENT_DATE - 184, 3, 3),  -- Carla Mendes / Clube dos Clássicos, stage 3
    (10, TRUE, CURRENT_DATE - 214, 1, 4),  -- Diego Rocha / Clube dos Clássicos, stage 1
    (11, TRUE, CURRENT_DATE - 198, 2, 4),  -- Diego Rocha / Clube dos Clássicos, stage 2
    (12, TRUE, CURRENT_DATE - 181, 3, 4),  -- Diego Rocha / Clube dos Clássicos, stage 3
    (13, TRUE, CURRENT_DATE - 215, 1, 5),  -- Eduarda Alves / Clube dos Clássicos, stage 1
    (14, TRUE, CURRENT_DATE - 201, 2, 5),  -- Eduarda Alves / Clube dos Clássicos, stage 2
    (15, TRUE, CURRENT_DATE - 178, 3, 5),  -- Eduarda Alves / Clube dos Clássicos, stage 3
    (16, TRUE, CURRENT_DATE - 39, 4, 6),  -- Felipe Costa / Expedição Terra-média, stage 4
    (17, TRUE, CURRENT_DATE - 40, 4, 7),  -- Ana Souza / Expedição Terra-média, stage 4
    (18, TRUE, CURRENT_DATE - 37, 4, 8),  -- Gabriela Nunes / Expedição Terra-média, stage 4
    (19, TRUE, CURRENT_DATE - 35, 4, 9),  -- Henrique Dias / Expedição Terra-média, stage 4
    (20, TRUE, CURRENT_DATE - 31, 4, 10),  -- Isabela Martins / Expedição Terra-média, stage 4
    (21, TRUE, CURRENT_DATE - 36, 4, 11),  -- João Pereira / Expedição Terra-média, stage 4
    (22, TRUE, CURRENT_DATE - 18, 5, 6),  -- Felipe Costa / Expedição Terra-média, stage 5
    (23, TRUE, CURRENT_DATE - 19, 5, 7),  -- Ana Souza / Expedição Terra-média, stage 5
    (24, TRUE, CURRENT_DATE - 15, 5, 9),  -- Henrique Dias / Expedição Terra-média, stage 5
    (25, TRUE, CURRENT_DATE - 11, 5, 8),  -- Gabriela Nunes / Expedição Terra-média, stage 5
    (26, FALSE, NULL, 5, 11),  -- João Pereira / Expedição Terra-média, stage 5
    (27, TRUE, CURRENT_DATE - 5, 6, 6),  -- Felipe Costa / Expedição Terra-média, stage 6
    (28, TRUE, CURRENT_DATE - 3, 6, 7),  -- Ana Souza / Expedição Terra-média, stage 6
    (29, FALSE, NULL, 6, 9),  -- Henrique Dias / Expedição Terra-média, stage 6
    (30, TRUE, CURRENT_DATE - 24, 8, 14),  -- Carla Mendes / Distopias em Debate, stage 8
    (31, TRUE, CURRENT_DATE - 22, 8, 15),  -- Bruno Lima / Distopias em Debate, stage 8
    (32, TRUE, CURRENT_DATE - 20, 8, 16),  -- Eduarda Alves / Distopias em Debate, stage 8
    (33, TRUE, CURRENT_DATE - 16, 8, 17),  -- João Pereira / Distopias em Debate, stage 8
    (34, TRUE, CURRENT_DATE - 4, 9, 14),  -- Carla Mendes / Distopias em Debate, stage 9
    (35, TRUE, CURRENT_DATE - 2, 9, 15),  -- Bruno Lima / Distopias em Debate, stage 9
    (36, FALSE, NULL, 9, 16),  -- Eduarda Alves / Distopias em Debate, stage 9
    (37, TRUE, CURRENT_DATE - 7, 11, 18),  -- Gabriela Nunes / Suspense de Sexta, stage 11
    (38, TRUE, CURRENT_DATE - 4, 11, 19),  -- Henrique Dias / Suspense de Sexta, stage 11
    (39, TRUE, CURRENT_DATE - 14, 11, 20);  -- Diego Rocha / Suspense de Sexta, stage 11

-- Messages (posted after finishing the stage or after its deadline, RN12)
INSERT INTO MENSAGEM (id_mensagem, conteudo, data_hora_publicacao, data_hora_edicao, situacao, FK_ETAPA_LEITURA_id_etapa, FK_MEMBRO_GRUPO_id_membro) VALUES
    (1, 'Comecei animada: o narrador avisa logo que quer atar as duas pontas da vida, gostei da proposta.', (CURRENT_DATE - 218 + TIME '20:10'), NULL, 'Visível', 1, 1),  -- Ana Souza / stage 1
    (2, 'O apelido Dom Casmurro surgir de um cochilo no trem é muito bom.', (CURRENT_DATE - 216 + TIME '21:30'), NULL, 'Visível', 1, 2),  -- Bruno Lima / stage 1
    (3, 'José Dias e seus superlativos são a melhor parte até agora.', (CURRENT_DATE - 215 + TIME '19:05'), NULL, 'Visível', 1, 3),  -- Carla Mendes / stage 1
    (4, 'Achei o começo lento, mas a escrita compensa.', (CURRENT_DATE - 214 + TIME '22:40'), NULL, 'Visível', 1, 4),  -- Diego Rocha / stage 1
    (5, 'Guardem a imagem dos olhos de ressaca, acho que ela vai voltar.', (CURRENT_DATE - 213 + TIME '09:15'), NULL, 'Visível', 1, 5),  -- Eduarda Alves / stage 1
    (6, 'O seminário rende capítulos curtos e cheios de ironia.', (CURRENT_DATE - 202 + TIME '18:20'), NULL, 'Visível', 2, 1),  -- Ana Souza / stage 2
    (7, 'A amizade com Escobar ganhou peso nesta parte.', (CURRENT_DATE - 200 + TIME '20:45'), NULL, 'Visível', 2, 2),  -- Bruno Lima / stage 2
    (8, 'Bentinho é um narrador em quem eu confio cada vez menos.', (CURRENT_DATE - 199 + TIME '10:30'), (CURRENT_DATE - 199 + TIME '11:02'), 'Visível', 2, 5),  -- Eduarda Alves / stage 2
    (9, 'As promessas da mãe dele explicam muita coisa.', (CURRENT_DATE - 198 + TIME '21:10'), NULL, 'Visível', 2, 3),  -- Carla Mendes / stage 2
    (10, 'Terminei. Continuo sem saber o que pensar sobre Capitu, e acho que é essa a graça.', (CURRENT_DATE - 185 + TIME '19:00'), NULL, 'Visível', 3, 1),  -- Ana Souza / stage 3
    (11, 'O capítulo do enterro é de uma crueldade elegante.', (CURRENT_DATE - 182 + TIME '20:35'), NULL, 'Visível', 3, 3),  -- Carla Mendes / stage 3
    (12, 'Vale reler o primeiro capítulo depois do último.', (CURRENT_DATE - 179 + TIME '22:05'), NULL, 'Visível', 3, 2),  -- Bruno Lima / stage 3
    (13, 'Fiquei do lado da Capitu do começo ao fim.', (CURRENT_DATE - 176 + TIME '17:50'), NULL, 'Visível', 3, 4),  -- Diego Rocha / stage 3
    (14, 'Ótima escolha para abrir o clube. Próximo clássico?', (CURRENT_DATE - 175 + TIME '09:40'), NULL, 'Visível', 3, 5),  -- Eduarda Alves / stage 3
    (15, 'A festa de aniversário do Bilbo é um começo muito acolhedor.', (CURRENT_DATE - 40 + TIME '21:00'), NULL, 'Visível', 4, 7),  -- Ana Souza / stage 4
    (16, 'Bem-vindos! Prestem atenção na conversa de Gandalf com Frodo sobre o anel.', (CURRENT_DATE - 39 + TIME '19:30'), NULL, 'Visível', 4, 6),  -- Felipe Costa / stage 4
    (17, 'Não esperava que a saída do Condado demorasse tanto, mas estou gostando.', (CURRENT_DATE - 37 + TIME '20:15'), NULL, 'Visível', 4, 8),  -- Gabriela Nunes / stage 4
    (18, 'Quem já viu o filme sabe o que acontece com Gandalf mais adiante…', (CURRENT_DATE - 36 + TIME '08:40'), NULL, 'Oculta', 4, 8),  -- Gabriela Nunes / stage 4
    (19, 'Os Cavaleiros Negros dão um clima de suspense que eu não lembrava.', (CURRENT_DATE - 36 + TIME '22:10'), NULL, 'Visível', 4, 11),  -- João Pereira / stage 4
    (20, 'Gosto como as canções aparecem no meio da história.', (CURRENT_DATE - 35 + TIME '18:55'), NULL, 'Visível', 4, 9),  -- Henrique Dias / stage 4
    (21, 'Prazo da etapa 1 encerrado. Obrigado por evitarem spoilers!', (CURRENT_DATE - 33 + TIME '20:00'), NULL, 'Visível', 4, 6),  -- Felipe Costa / stage 4
    (22, 'Sam já é meu personagem favorito.', (CURRENT_DATE - 33 + TIME '21:20'), NULL, 'Visível', 4, 7),  -- Ana Souza / stage 4
    (23, 'Cheguei atrasada, mas terminei a etapa. A Floresta Velha é assustadora!', (CURRENT_DATE - 31 + TIME '19:45'), NULL, 'Visível', 4, 10),  -- Isabela Martins / stage 4
    (24, 'Valfenda é o descanso que todo mundo precisava.', (CURRENT_DATE - 18 + TIME '20:30'), NULL, 'Visível', 5, 7),  -- Ana Souza / stage 5
    (25, 'O ataque no Topo do Vento foi o momento mais tenso até aqui.', (CURRENT_DATE - 18 + TIME '21:15'), NULL, 'Visível', 5, 6),  -- Felipe Costa / stage 5
    (26, 'Passolargo cresceu muito em poucos capítulos.', (CURRENT_DATE - 15 + TIME '18:00'), NULL, 'Visível', 5, 9),  -- Henrique Dias / stage 5
    (27, 'Ainda estou no capítulo 10, mas já li as conversas da etapa.', (CURRENT_DATE - 12 + TIME '22:30'), NULL, 'Visível', 5, 11),  -- João Pereira / stage 5
    (28, 'A travessia do vau com a cheia é linda de imaginar.', (CURRENT_DATE - 11 + TIME '19:10'), NULL, 'Visível', 5, 8),  -- Gabriela Nunes / stage 5
    (29, 'Quero um mapa da Terra-média na parede depois desse livro.', (CURRENT_DATE - 10 + TIME '20:40'), NULL, 'Visível', 5, 10),  -- Isabela Martins / stage 5
    (30, 'Próxima etapa: Conselho de Elrond. Preparem-se para um capítulo longo.', (CURRENT_DATE - 10 + TIME '21:05'), NULL, 'Visível', 5, 6),  -- Felipe Costa / stage 5
    (31, 'Frodo aguentou muito mais do que eu esperava.', (CURRENT_DATE - 9 + TIME '17:25'), NULL, 'Visível', 5, 9),  -- Henrique Dias / stage 5
    (32, 'O Conselho de Elrond explica muita coisa sobre o anel.', (CURRENT_DATE - 5 + TIME '20:50'), NULL, 'Visível', 6, 6),  -- Felipe Costa / stage 6
    (33, 'Moria é sufocante, no bom sentido.', (CURRENT_DATE - 3 + TIME '21:30'), (CURRENT_DATE - 3 + TIME '21:41'), 'Visível', 6, 7),  -- Ana Souza / stage 6
    (34, 'A ponte de Khazad-dûm… sem palavras.', (CURRENT_DATE - 2 + TIME '19:20'), NULL, 'Visível', 6, 6),  -- Felipe Costa / stage 6
    (35, 'Precisei de um tempo depois desse final de etapa.', (CURRENT_DATE - 1 + TIME '22:00'), NULL, 'Visível', 6, 7),  -- Ana Souza / stage 6
    (36, 'A teletela ligada o tempo todo é angustiante.', (CURRENT_DATE - 24 + TIME '20:00'), NULL, 'Visível', 8, 14),  -- Carla Mendes / stage 8
    (37, 'O trabalho de Winston reescrevendo jornais é a parte mais assustadora.', (CURRENT_DATE - 22 + TIME '21:40'), NULL, 'Visível', 8, 15),  -- Bruno Lima / stage 8
    (38, 'Os Dois Minutos de Ódio lembram muito algumas redes sociais.', (CURRENT_DATE - 20 + TIME '19:15'), NULL, 'Visível', 8, 16),  -- Eduarda Alves / stage 8
    (39, 'Boa comparação, Eduarda. Vamos levar isso para a próxima etapa.', (CURRENT_DATE - 17 + TIME '18:30'), NULL, 'Visível', 8, 14),  -- Carla Mendes / stage 8
    (40, 'Terminei a Parte 1. A Novafala é genial e perturbadora.', (CURRENT_DATE - 16 + TIME '22:20'), NULL, 'Visível', 8, 17),  -- João Pereira / stage 8
    (41, 'A relação com Julia muda completamente o ritmo do livro.', (CURRENT_DATE - 4 + TIME '20:10'), NULL, 'Visível', 9, 14),  -- Carla Mendes / stage 9
    (42, 'O quarto alugado parece seguro demais para ser verdade.', (CURRENT_DATE - 2 + TIME '21:00'), NULL, 'Visível', 9, 15),  -- Bruno Lima / stage 9
    (43, 'Quem terminar a Parte 2 antes do prazo, comenta aqui.', (CURRENT_DATE - 1 + TIME '19:35'), NULL, 'Visível', 9, 14),  -- Carla Mendes / stage 9
    (44, 'Já sei o final, quem quiser é só me chamar.', (CURRENT_DATE - 13 + TIME '23:10'), NULL, 'Oculta', 11, 20),  -- Diego Rocha / stage 11
    (45, 'O diário da Amy alternando com o Nick deixa tudo ambíguo.', (CURRENT_DATE - 7 + TIME '20:00'), NULL, 'Visível', 11, 18),  -- Gabriela Nunes / stage 11
    (46, 'Não confio em nenhum dos dois narradores.', (CURRENT_DATE - 4 + TIME '21:25'), NULL, 'Visível', 11, 19),  -- Henrique Dias / stage 11
    (47, 'Sexta que vem conversamos sobre o fim da Parte 1.', (CURRENT_DATE - 3 + TIME '19:50'), NULL, 'Visível', 11, 18);  -- Gabriela Nunes / stage 11

-- Notifications
INSERT INTO NOTIFICACAO (id_notificacao, tipo, texto, data_hora, lida, FK_USUARIO_id_usuario) VALUES
    (1, 'Grupo', 'O grupo Clube dos Clássicos foi encerrado. Obrigado por participar!', (CURRENT_DATE - 172 + TIME '10:00'), TRUE, 1),  -- Ana Souza
    (2, 'Grupo', 'O grupo Clube dos Clássicos foi encerrado. Obrigado por participar!', (CURRENT_DATE - 172 + TIME '10:00'), TRUE, 2),  -- Bruno Lima
    (3, 'Grupo', 'Você foi removido do grupo Suspense de Sexta.', (CURRENT_DATE - 12 + TIME '09:30'), TRUE, 4),  -- Diego Rocha
    (4, 'Convite', 'Felipe Costa convidou você para o grupo Expedição Terra-média.', (CURRENT_DATE - 7 + TIME '18:00'), FALSE, 11),  -- Larissa Gomes
    (5, 'Grupo', 'Mateus Ribeiro pediu para entrar no grupo Expedição Terra-média.', (CURRENT_DATE - 3 + TIME '14:20'), FALSE, 6),  -- Felipe Costa
    (6, 'Grupo', 'Seu pedido para entrar no grupo Expedição Terra-média aguarda aprovação.', (CURRENT_DATE - 3 + TIME '14:20'), TRUE, 12),  -- Mateus Ribeiro
    (7, 'Convite', 'Mateus Ribeiro convidou você para o grupo Fundação para Iniciantes.', (CURRENT_DATE - 3 + TIME '15:00'), FALSE, 9),  -- Isabela Martins
    (8, 'Mensagem', 'Nova mensagem de Ana Souza em Expedição Terra-média.', (CURRENT_DATE - 3 + TIME '21:30'), TRUE, 6),  -- Felipe Costa
    (9, 'Mensagem', 'Nova mensagem de Bruno Lima em Distopias em Debate.', (CURRENT_DATE - 2 + TIME '21:00'), TRUE, 3),  -- Carla Mendes
    (10, 'Mensagem', 'Nova mensagem de Felipe Costa em Expedição Terra-média.', (CURRENT_DATE - 2 + TIME '19:20'), FALSE, 1),  -- Ana Souza
    (11, 'Mensagem', 'Nova mensagem de Gabriela Nunes em Suspense de Sexta.', (CURRENT_DATE - 3 + TIME '19:50'), TRUE, 8);  -- Henrique Dias

-- Moves the id sequences forward so new rows continue after the loaded ids
SELECT setval(pg_get_serial_sequence('genero', 'id_genero'), (SELECT MAX(id_genero) FROM GENERO));
SELECT setval(pg_get_serial_sequence('autor', 'id_autor'), (SELECT MAX(id_autor) FROM AUTOR));
SELECT setval(pg_get_serial_sequence('livro', 'id_livro'), (SELECT MAX(id_livro) FROM LIVRO));
SELECT setval(pg_get_serial_sequence('usuario', 'id_usuario'), (SELECT MAX(id_usuario) FROM USUARIO));
SELECT setval(pg_get_serial_sequence('item_estante', 'id_item'), (SELECT MAX(id_item) FROM ITEM_ESTANTE));
SELECT setval(pg_get_serial_sequence('avaliacao_resenha', 'id_avaliacao'), (SELECT MAX(id_avaliacao) FROM AVALIACAO_RESENHA));
SELECT setval(pg_get_serial_sequence('grupo_leitura', 'id_grupo'), (SELECT MAX(id_grupo) FROM GRUPO_LEITURA));
SELECT setval(pg_get_serial_sequence('membro_grupo', 'id_membro'), (SELECT MAX(id_membro) FROM MEMBRO_GRUPO));
SELECT setval(pg_get_serial_sequence('etapa_leitura', 'id_etapa'), (SELECT MAX(id_etapa) FROM ETAPA_LEITURA));
SELECT setval(pg_get_serial_sequence('progresso_etapa', 'id_progresso'), (SELECT MAX(id_progresso) FROM PROGRESSO_ETAPA));
SELECT setval(pg_get_serial_sequence('mensagem', 'id_mensagem'), (SELECT MAX(id_mensagem) FROM MENSAGEM));
SELECT setval(pg_get_serial_sequence('notificacao', 'id_notificacao'), (SELECT MAX(id_notificacao) FROM NOTIFICACAO));
