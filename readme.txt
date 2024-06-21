Olá usuário da IQA Tool!

Primeiramente, abra seu Terminal ou Windows PowerShel e certifique-se que o Docker está operando corretamente. Execute:
> docker run hello-world

Para construir pela primeira vez a Ferramenta web IQA Tool, vá ao diretório onde constam os arquivos baixados via Github (docker-compose.yml) e execute os seguintes comandos:

> docker compose build

para construir a imagem. Então:

> docker compose up -d

para iniciar o container. Acesse a ferramenta pelo browser: "localhost:80".




