-- LIMPEZA DO BANCO (EXCLUSÃO DOS DADOS ANTIGOS)
TRUNCATE TABLE 
    expenses_expensesplit, 
    expenses_expense, 
    expenses_groupmembership, 
    expenses_group, 
    accounts_customuser 
RESTART IDENTITY CASCADE;


-- INSERÇÃO DE USUÁRIOS (1 Admin + 9 Usuários Comuns)
-- Senha do admin: 'admin' | Senha dos demais: 'user'
INSERT INTO accounts_customuser (
    password, last_login, is_superuser, username, first_name, last_name, 
    email, is_staff, is_active, date_joined, role, created_at
) VALUES 
-- Admin
('pbkdf2_sha256$1500000$wLvt6r2bOUj5SI3DPaFqEC$oksZlkFpw/c2/u/H0noRVXg/CVn5F3SxbHrx9ZxScuA=', NOW(), TRUE, 'admin', 'Administrador', 'Geral', 'admin@split.com', TRUE, TRUE, NOW() - INTERVAL '1 year', 'ADMIN', NOW() - INTERVAL '1 year'),

-- Usuários Comuns
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'gustavo', 'Gustavo', 'Ferreira', 'gustavo@ufla.br', FALSE, TRUE, NOW() - INTERVAL '6 months', 'USER', NOW() - INTERVAL '6 months'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'fabio', 'Fábio', 'Souza', 'fabio@ufla.br', FALSE, TRUE, NOW() - INTERVAL '5 months', 'USER', NOW() - INTERVAL '5 months'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'gabriel', 'Gabriel', 'Silva', 'gabriel@ufla.br', FALSE, TRUE, NOW() - INTERVAL '3 months', 'USER', NOW() - INTERVAL '3 months'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'matheus', 'Matheus', 'Santos', 'matheus@ufla.br', FALSE, TRUE, NOW() - INTERVAL '2 months', 'USER', NOW() - INTERVAL '2 months'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'luany', 'Luany', 'Souza', 'luany@gmail.com', FALSE, TRUE, NOW() - INTERVAL '1 month', 'USER', NOW() - INTERVAL '1 month'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'mariana', 'Mariana', 'Costa', 'mariana@gmail.com', FALSE, TRUE, NOW() - INTERVAL '5 days', 'USER', NOW() - INTERVAL '5 days'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'carlos', 'Carlos', 'Eduardo', 'carlos@gmail.com', FALSE, FALSE, NOW() - INTERVAL '4 months', 'USER', NOW() - INTERVAL '4 months'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'juliana', 'Juliana', 'Sousa', 'juliana@gmail.com', FALSE, FALSE, NOW() - INTERVAL '2 months', 'USER', NOW() - INTERVAL '2 months'),
('pbkdf2_sha256$1500000$MewKComkNprbOxjgA2xW65$JNTa8XCAOrCnjChQfwooLqc7lgMD0JdaN2RHJR/FAf0=', NOW(), FALSE, 'roberto', 'Roberto', 'Carlos', 'roberto@gmail.com', FALSE, TRUE, NOW(), 'USER', NOW());


-- Inserção de grupos
INSERT INTO expenses_group (name, description, invite_code, created_by_id, is_active, created_at) VALUES 
('Viagem de Férias RJ', 'Gastos com hotel, passeios e transporte na praia', 'RJ2026', 2, TRUE, NOW() - INTERVAL '10 months'),
('Churrasco de Domingo', 'Carnes, bebidas e acompanhamentos', 'CHURR10', 3, TRUE, NOW() - INTERVAL '8 months'),
('Aluguel República', 'Conta de luz, internet e aluguel da casa', 'REP777', 2, TRUE, NOW() - INTERVAL '6 months'),
('Projeto de Extensão UFLA', 'Materiais para apresentação e banner', 'UFLA12', 4, FALSE, NOW() - INTERVAL '5 months'), -- Inativo
('Supermercado Mensal', 'Compras grandes de mantimentos', 'MERC99', 5, TRUE, NOW() - INTERVAL '3 months'),
('Reforma da Cozinha', 'Pintura, pisos e reparos hidráulicos', 'REF202', 6, FALSE, NOW() - INTERVAL '2 months'), -- Inativo
('Festa de Aniversário', 'Bolo, salgadinhos e decoração', 'FESTA5', 2, TRUE, NOW() - INTERVAL '20 days'),
('Jogos Online (Steam)', 'Compra de bundles compartilhados', 'STEAM1', 3, TRUE, NOW() - INTERVAL '3 days'),
('Academia e Suplementos', 'Plano anual e isotônicos', 'FIT888', 4, TRUE, NOW() - INTERVAL '1 day'),
('Presente Amigo Secreto', 'Vaquinha para o final do ano', 'AMIGO9', 5, TRUE, NOW());


-- 4. Inserção de membros do grupo - GroupMembership
INSERT INTO expenses_groupmembership (user_id, group_id, is_group_admin, is_accepted, joined_at) VALUES 
(2, 1, TRUE, TRUE, NOW() - INTERVAL '10 months'),
(3, 1, FALSE, TRUE, NOW() - INTERVAL '10 months'),
(4, 1, FALSE, FALSE, NOW() - INTERVAL '9 months'),
(3, 2, TRUE, TRUE, NOW() - INTERVAL '8 months'),
(5, 2, FALSE, TRUE, NOW() - INTERVAL '8 months'),
(2, 3, TRUE, TRUE, NOW() - INTERVAL '6 months'),
(4, 3, FALSE, TRUE, NOW() - INTERVAL '6 months'),
(5, 3, FALSE, TRUE, NOW() - INTERVAL '6 months'),
(4, 4, TRUE, TRUE, NOW() - INTERVAL '5 months'),
(6, 4, FALSE, TRUE, NOW() - INTERVAL '5 months'),
(5, 5, TRUE, TRUE, NOW() - INTERVAL '3 months'),
(6, 5, FALSE, TRUE, NOW() - INTERVAL '3 months'),
(7, 5, FALSE, TRUE, NOW() - INTERVAL '3 months'),
(6, 6, TRUE, TRUE, NOW() - INTERVAL '2 months'),
(2, 6, FALSE, TRUE, NOW() - INTERVAL '2 months'),
(2, 7, TRUE, TRUE, NOW() - INTERVAL '20 days'),
(3, 7, FALSE, TRUE, NOW() - INTERVAL '20 days'),
(4, 7, FALSE, TRUE, NOW() - INTERVAL '20 days'),
(3, 8, TRUE, TRUE, NOW() - INTERVAL '3 days'),
(7, 8, FALSE, TRUE, NOW() - INTERVAL '3 days'),
(4, 9, TRUE, TRUE, NOW() - INTERVAL '1 day'),
(6, 9, FALSE, TRUE, NOW() - INTERVAL '1 day'),
(5, 10, TRUE, TRUE, NOW()),
(2, 10, FALSE, TRUE, NOW()),
(3, 10, FALSE, TRUE, NOW());


-- Inserção de Despesas
INSERT INTO expenses_expense (group_id, paid_by_id, created_by_id, title, description, amount, date, created_at) VALUES 
-- Grupo 1 (Viagem RJ)
(1, 2, 2, 'Hotel Copacabana', 'Diárias 4 noites', 1200.00, '2025-06-10', NOW() - INTERVAL '10 months'),
(1, 3, 3, 'Aluguel de Carro', 'Locação por 3 dias', 450.00, '2025-06-11', NOW() - INTERVAL '10 months'),
(1, 2, 2, 'Passeio de Barco', 'Ingressos pra ilha', 300.00, '2025-06-12', NOW() - INTERVAL '10 months'),

-- Grupo 2 (Churrasco)
(2, 3, 3, 'Carnes no Açougue', 'Picanha e linguiça', 250.00, '2025-08-15', NOW() - INTERVAL '8 months'),
(2, 5, 5, 'Bebidas e Gelo', 'Cervejas e refrigerantes', 180.00, '2025-08-15', NOW() - INTERVAL '8 months'),
(2, 3, 3, 'Carvão e Temperos', 'Suprimentos', 60.00, '2025-08-16', NOW() - INTERVAL '8 months'),

-- Grupo 3 (Aluguel)
(3, 2, 2, 'Aluguel Vencimento', 'Referente ao mês', 1500.00, '2025-10-01', NOW() - INTERVAL '6 months'),
(3, 4, 4, 'Conta de Internet', 'Fibra ótica 500mb', 120.00, '2025-10-05', NOW() - INTERVAL '6 months'),
(3, 5, 5, 'Conta de Luz CEMIG', 'Energia elétrica', 210.50, '2025-10-10', NOW() - INTERVAL '6 months'),

-- Grupo 4 (Projeto UFLA)
(4, 4, 4, 'Impressão de Banner', 'Gráfica universitária', 90.00, '2025-11-10', NOW() - INTERVAL '5 months'),
(4, 6, 6, 'Componentes Eletrônicos', 'Cabos e sensores', 145.00, '2025-11-12', NOW() - INTERVAL '5 months'),

-- Grupo 5 (Supermercado)
(5, 5, 5, 'Compras de Mês', 'Arroz, óleo, carnes, limpeza', 850.00, '2026-01-10', NOW() - INTERVAL '3 months'),
(5, 6, 6, 'Hortifrúti', 'Frutas e verduras da semana', 130.00, '2026-01-15', NOW() - INTERVAL '3 months'),
(5, 7, 7, 'Produtos de Limpeza', 'Desinfetante e sabão', 95.00, '2026-01-20', NOW() - INTERVAL '3 months'),

-- Grupo 6 (Reforma)
(6, 6, 6, 'Latas de Tinta', 'Tinta acrílica branca', 320.00, '2026-02-01', NOW() - INTERVAL '2 months'),
(6, 2, 2, 'Pisos Porcelanato', 'Caixas de piso', 600.00, '2026-02-05', NOW() - INTERVAL '2 months'),

-- Grupo 7 (Festa)
(7, 2, 2, 'Bolo Encomenda', 'Bolo recheado com morango', 160.00, '2026-04-10', NOW() - INTERVAL '20 days'),
(7, 3, 3, 'Salgados Diversos', '100 coxinhas e kibe', 120.00, '2026-04-11', NOW() - INTERVAL '20 days'),
(7, 4, 4, 'Decoração Balões', 'Painel temático', 80.00, '2026-04-12', NOW() - INTERVAL '20 days'),

-- Grupo 8 (Jogos)
(8, 3, 3, 'Pack Jogos Co-op', 'Promoção de fim de semana', 150.00, '2026-05-01', NOW() - INTERVAL '3 days'),
(8, 7, 7, 'DLC Expansão', 'Conteúdo extra', 75.00, '2026-05-02', NOW() - INTERVAL '3 days'),

-- Grupo 9 (Academia)
(9, 4, 4, 'Whey Protein', 'Suplemento proteico', 190.00, '2026-05-03', NOW() - INTERVAL '1 day'),
(9, 6, 6, 'Creatina', 'Pote 300g', 95.00, '2026-05-03', NOW() - INTERVAL '1 day'),

-- Grupo 10 (Amigo Secreto)
(10, 5, 5, 'Cartões Presente', 'Vales compras lojas parceiras', 250.00, '2026-05-04', NOW()),
(10, 2, 2, 'Embalagens de Presente', 'Papel e laços', 35.00, '2026-05-04', NOW()),
(10, 3, 3, 'Chocolates Finos', 'Caixas sortidas', 110.00, '2026-05-04', NOW()),
(10, 5, 5, 'Lanches Rápida', 'Pizzas para o sorteio', 140.00, '2026-05-04', NOW()),
(10, 2, 2, 'Taxa de Entrega', 'Frete rápido', 25.00, '2026-05-04', NOW()),
(10, 3, 3, 'Guardanapos e Descartáveis', 'Copos e pratos', 45.00, '2026-05-04', NOW()),
(10, 5, 5, 'Guloseimas Extras', 'Bombons variados', 55.00, '2026-05-04', NOW());


-- 6. Inserção das divisões de despesas - ExpenseSplit
INSERT INTO expenses_expensesplit (expense_id, user_id, amount_owed, is_paid) VALUES 
(1, 2, 600.00, TRUE), (1, 3, 600.00, TRUE),
(2, 2, 225.00, TRUE), (2, 3, 225.00, FALSE),
(3, 2, 150.00, TRUE), (3, 3, 150.00, TRUE),
(4, 3, 125.00, TRUE), (4, 5, 125.00, TRUE),
(5, 3, 90.00, TRUE), (5, 5, 90.00, FALSE),
(6, 3, 30.00, FALSE), (6, 5, 30.00, TRUE),
(7, 2, 750.00, TRUE), (7, 4, 750.00, FALSE),
(8, 4, 60.00, TRUE), (8, 5, 60.00, TRUE),
(9, 2, 70.17, TRUE), (9, 4, 70.17, TRUE), (9, 5, 70.16, FALSE),
(10, 4, 45.00, TRUE), (10, 6, 45.00, TRUE),
(11, 4, 72.50, TRUE), (11, 6, 72.50, FALSE),
(12, 5, 283.33, TRUE), (12, 6, 283.33, TRUE), (12, 7, 283.34, TRUE),
(13, 6, 65.00, TRUE), (13, 7, 65.00, FALSE),
(14, 7, 47.50, TRUE), (14, 5, 47.50, TRUE),
(15, 6, 160.00, TRUE), (15, 2, 160.00, TRUE),
(16, 2, 300.00, TRUE), (16, 6, 300.00, FALSE),
(17, 2, 80.00, TRUE), (17, 3, 80.00, TRUE),
(18, 3, 60.00, TRUE), (18, 4, 60.00, TRUE),
(19, 4, 40.00, TRUE), (19, 2, 40.00, FALSE),
(20, 3, 75.00, TRUE), (20, 7, 75.00, TRUE),
(21, 7, 37.50, TRUE), (21, 3, 37.50, FALSE),
(22, 4, 95.00, TRUE), (22, 6, 95.00, TRUE),
(23, 6, 47.50, TRUE), (23, 4, 47.50, TRUE),
(24, 5, 83.33, TRUE), (24, 2, 83.33, TRUE), (24, 3, 83.34, TRUE),
(25, 2, 17.50, TRUE), (25, 3, 17.50, FALSE),
(26, 3, 36.66, TRUE), (26, 5, 36.67, TRUE), (26, 2, 36.67, TRUE),
(27, 5, 46.66, TRUE), (27, 2, 46.67, FALSE), (27, 3, 46.67, TRUE),
(28, 2, 12.50, TRUE), (28, 5, 12.50, TRUE),
(29, 3, 15.00, TRUE), (29, 5, 15.00, FALSE), (29, 2, 15.00, TRUE),
(30, 5, 18.33, TRUE), (30, 2, 18.33, TRUE), (30, 3, 18.34, TRUE);