# Gestão de Despesas Django

## Descrição do Projeto

A aplicação web de gestão de despesas compartilhadas foi desenvolvida com o objetivo de facilitar o controle financeiro entre grupos de pessoas, inspirando-se no modelo de funcionamento de ferramentas como o Splitwise, onde os usuários podem organizar despesas comuns, registrar pagamentos e visualizar saldos parciais de forma automatizada. O sistema centraliza a administração de contas coletivas em um ambiente seguro, permitindo que os participantes criem círculos de gastos, ingressem por meio de códigos de convite exclusivos e acompanhem detalhadamente quem pagou e quem deve em cada transação, promovendo a transparência e o equilíbrio financeiro nas divisões.

---
## Integrantes do Projeto

| INTEGRANTE | GITHUB |
| --- | --- |
| Gustavo Alessandro de Souza Sabino | [https://github.com/GUSTAVO-ALESSANDRO](https://github.com/GUSTAVO-ALESSANDRO) |
| INTEGRANTE 2 | [GitHub](https://www.google.com/search?q=https://github.com/link-integrante-2) |
| INTEGRANTE 3 | [GitHub](https://www.google.com/search?q=https://github.com/link-integrante-3) |

---

## Tecnologias Utilizadas

O projeto foi construído utilizando a linguagem Python em conjunto com o framework Django, que fornece a arquitetura MVT, o sistema robusto de autenticação, o mapeamento objeto-relacional e a modularidade necessária para separar a aplicação em componentes reutilizáveis, garantindo organização e escalabilidade ao código-fonte.

Para o armazenamento persistente dos dados, o sistema emprega o banco de dados relacional PostgreSQL, assegurando a integridade referencial por meio de chaves estrangeiras, restrições e transações seguras, enquanto a interface do usuário foi estilizada com o framework CSS Bootstrap, oferecendo uma experiência responsiva, moderna e compatível com temas claros e escuros.

O controle de versão e a colaboração da equipe foram gerenciados através do Git e do GitHub, utilizando branches específicas para organização do fluxo de trabalho, e o painel administrativo do Django foi customizado com temas avançados para atender aos requisitos visuais e de filtragem propostos.

---

## Instruções para Instalação

Para realizar a instalação do projeto em seu ambiente local, certifique-se de possuir o Python 3 e o PostgreSQL instalados na sua máquina, abra o terminal e siga os passos abaixo:

1. Clone o repositório oficial do projeto a partir do GitHub com o comando:

```bash
git clone https://github.com/GUSTAVO-ALESSANDRO/gestao-despesas-django.git

```
ou apenas instale o .zip desse repositório.

2. Acesse o diretório raiz do projeto clonado:

```bash
cd gestao-despesas-django

```

3. Crie e ative um ambiente virtual para isolar as dependências da aplicação:

```bash
python3 -m venv venv
source venv/bin/activate

```

4. Instale as dependências necessárias listadas no projeto:

```bash
pip install -r requirements.txt

```

5. Configure as credenciais de acesso ao banco de dados PostgreSQL no arquivo de configurações do Django e aplique as migrações para criar as tabelas:

```bash
python3 manage.py makemigrations
python3 manage.py migrate

```

---

## Instruções para Execução

Após concluir a instalação e configurar o banco de dados, execute o servidor de desenvolvimento local com o seguinte comando:

```bash
python3 manage.py runserver

```

Com o servidor em execução, abra o seu navegador de preferência e acesse o endereço `[http://127.0.0.1:8000/](http://127.0.0.1:8000/)` para interagir com a aplicação web.

---

## Principais Funcionalidades

* Autenticação completa de usuários com suporte a cadastro, login e logout de sessão seguros.
* Gestão de perfis e papéis distintos, contemplando administradores gerais do sistema e usuários comuns.
* Criação, consulta e gerenciamento de grupos de despesas com geração automática de códigos alfanuméricos de convite.
* Sistema de aprovação de novos membros por parte do administrador do grupo.
* Cadastro, edição e exclusão lógica de despesas, permitindo detalhar o valor total, o título, a descrição e o responsável pelo pagamento.
* Divisão automática e individualizada de despesas entre os participantes do grupo com controle de quitação por fatia.
* Painel administrativo customizado e restrito aos administradores gerais, contendo métricas e relatórios globais de usuários e grupos ativos ou desativados.

