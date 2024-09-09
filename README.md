# Projeto - Versão Reduzida do Trello

## Descrição
Este projeto é uma versão simplificada do Trello, desenvolvido como parte da disciplina Tópicos Especiais de Software. Ele permite a criação e gerenciamento de quadros, colunas e cartões de tarefas, além de funcionalidades de controle de usuários e permissões de acesso a quadros.

## Tecnologias Utilizadas
- Python
- Flask (framework web)
- Bootstrap (para o design responsivo)

## Funcionalidades

### Autenticação de Usuários
- **Registrar**: Criação de uma nova conta de usuário.
<img src="imagens/Captura de tela 2024-09-08 221110.png" alt="Exemplo de Quadro" width="500">
- **Login**: Acesso à plataforma com credenciais previamente cadastradas.
  <img src="imagens/Captura de tela 2024-09-08 221102.png" alt="Exemplo de Quadro" width="500">

### Interface Principal
Na tela principal, o usuário tem acesso a três funcionalidades principais:

- **Criar um Quadro**: O usuário pode criar um novo quadro, nomeá-lo e personalizá-lo com colunas e cartões.
- **Listar Quadros**: Visualizar a lista de todos os quadros criados e pedir permissão para ingressar em quadros de outros usuários.
 <img src="imagens/Captura de tela 2024-09-08 221024.png" alt="Exemplo de Quadro" width="500">
imagens/Captura de tela 2024-09-08 221024.png
- **Solicitações**: Exibe duas categorias de solicitações:
<img src="imagens/Captura de tela 2024-09-08 221036.png" alt="Exemplo de Quadro" width="500">
  - Solicitações de ingresso em quadros feitas pelo usuário.
  - Solicitações de ingresso em quadros do próprio usuário, que ele pode aceitar ou rejeitar.

### Gerenciamento de Quadros
<img src="imagens/Captura de tela 2024-09-08 221008.png" alt="Exemplo de Quadro" width="500">
Ao criar um quadro, o usuário tem as seguintes opções:

- **Adicionar Colunas**: Criar novas colunas dentro do quadro.
- **Renomear Colunas**: Alterar o nome das colunas existentes.
- **Excluir Colunas**: Remover colunas do quadro.

### Gerenciar Cards
- **Criar novos cards** (tarefas) dentro de uma coluna.
- **Editar cards** já existentes.
- **Excluir cards**.

## Como Executar

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
```
  
2. Instale as depêndencias:
  ```bash
  pip install flask
  pip install flask_login
  pip install SQLAlchemy
  pip install Werkzeug
```
3. Execute:
```bash
 a. Pelo Pycharm: clique no botão de play do lado do trecho no app.py
  if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

b. Pelo terminal, rode:
flask run
```
4. Divirta-se ;)

