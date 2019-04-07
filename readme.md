# Movies API

## Descrição

Este projeto consiste em numa API REST de filmes. A API foi desenvolvida em Pythom com o framework Flask e banco de dados MongoDB. A API suporta operações CRUD de filmes além de registro e autorização de usuário, através de token JWT, e importação de filme através de integração com a API da [OMDb](http://www.omdbapi.com/).

## Tecnologias

* Python Python 3.5.2;
* pip 19.0.3;
* Flask 1.0.2;
* Mongo DB 4.0.7;

## Instalação local

Siga os passos:

1. Instalação das dependências Python através do comando abaixo:

* `pip install -r requirements.txt`

> Substituir `pip` por `pip3` quando o primeiro não estiver atrelado a versão 3 do Python.

2. Criar um banco `movies_api` no MongoDB (sem autentificação) e as collections `users` e `movies`;

3. Copiar o conteúdo do arquivo .env.example `.env`

4. Executar o comando abaixo para iniciar a aplicação:

* `python server.py`

> Por padrão a aplicação será iniciada na porta 5000.

## Funcionamento

Para utilizar a aplicação é necessário primeiro registrar um usuário no banco de dados através da rota `/api/register`. Feito isto é possível utilizar as credencias deste usuário para receber um token JWT de autorização através da rota `/api/login`. Este token é utilizado header da requisição com a chave `Authorization` em endpoints que exigem autorização.


## Endpoints

1. **GET /api/register** - Cria um usuário;

> Campos obrigatórios - Formato JSON:
> * `name` (String) - nome do usuário,
> * `email` (String) - e-mail do usuário,
> * `password` (String) - senha do usuário.

3. **POST /api/login** - Recebe o token JWT para utilizar nos endpoints que exigem autorização;

> Campos obrigatórios - Formato JSON:
> * `email` (String) - e-mail do usuário,
> * `password` (String) - senha do usuário.

4. **GET /api/movies** - <span style="color:yellow">Requer autorização</span> - Lista os filmes;
5. **POST /api/movies** - <span style="color:yellow">Requer autorização</span> - Cria um filme;
> Campos obrigatórios - Formato JSON:
> * `title` (String) - Título original do filme,
> * `brazilian_title` (String) - Título do filme no Brasil,
> * `year_of_production` (Number) - Ano do filme,
> * `director` (String) - Diretor do filme (pode ser separado por vírgulas quando houver múltiplos),
> * `genre` (String) - Gênero (pode ser separado por vírgulas quando houver múltiplos),
> * `cast` (Array) - Lista do elenco

> Campos obrigatórios de um item no array `cast`:
> * `role` (String) - nome da personagem,
> * `name` (String) - nome do ator/atriz.

6. **GET /api/movies/{movie_id}** - <span style="color:yellow">Requer autorização</span> - Exibe um filme;

> Parâmetro `movie_id` representa o ID do filme no banco de dados.

7. **PUT /api/movies/{movie_id}/update** - <span style="color:yellow">Requer autorização</span> - Remove um filme;

> Parâmetro `movie_id` representa o ID do filme no banco de dados.

> Campos obrigatórios - Formato JSON: Pelo menos um dos campos do item 5.

8. **DELETE /api/movies/{movie_id}/delete** - <span style="color:yellow">Requer autorização</span> - Remove um filme;

> Parâmetro `movie_id` representa o ID do filme no banco de dados.

9. **GET /api/movies/import-from-omdb/** - <span style="color:yellow">Requer autorização</span> - Cria um novo filme com dados do OMDb;

> Campos obrigatórios - Formato JSON:
> * `movie_id` (String) - id do filme na base do [IMDb](https://www.imdb.com/).

## Postman

Para testar os endpoints com o Postman é necessário importar os arquivos para `collection` e `environment` na pasta `postman`.
Por padrão o endereço base da aplicação é `http://localhost:5000` mas é possível especificar outro alterando a variável `baseUrl` da coleção.
Rotas que necessitam autorização utilizam a variável de ambiente `token` que é definida na rota `login`.
Os endpoints que enviam dados no corpo da requisição possuem exemplos.

## Testes

Siga os passos:

1. Definir a variável de ambiente `APP_CONFIG="TestConfig"` no arquivo `.env`
2. Executar o comando abaixo para executar os testes unitários:

* `python tests.py -v`