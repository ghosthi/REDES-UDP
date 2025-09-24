# REDES-UDP

# Configuração
Editar constantes SERVER_PORT e SERVER_IP em /Server.py

# Funcionamento
Inserir arquivos a serem lidos dentro de uma pasta /files/
Executar em CLI linha de comando ```py /main.py server``` para iniciar o servidor
Executar em outro CLI ```py /main.py client``` para iniciar o cliente

Para sair do cliente use os comandos ```exit```, ```quit```, ```/q```, ```:wq``` no momento de input, ou utilize  ```CTRL + C``` para interromper a execução.

Para interromper o servidor, use ```CTRL + C```.

# Opcional
Executar ```py /main.py client --debug``` para executar o cliente com verificação de corretude de arquivo, busca default no ip e porta configurado no server

# Resultado
A cada solicitação do cliente, deve ser inputado ```{IP}:{PORT}/{filename}``` via linha de comando e a transferência se iniciará.
O lado do servidor irá exibir informações sobre o envio, enquanto o lado do cliente exibirá informações de controle e recepção de pacotes.