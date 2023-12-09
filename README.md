# Modelo Booleano de RI

É um sistema de recuperação de informações que lê um arquivo contendo a base de documentos, extrai o conteúdo de cada documento e realiza o pré-processamento (tokenização, remoção de stopwords e extração de radicais).

Com o texto pré-processado, é gerado o índice invertido, que representa a relação entre o termo e os documentos da base no seguinte formato: termo:(documento, frequência).

Após isso, o sistema lê a consulta e a pré-processa, incluindo a extração dos operadores lógicos (& (AND), | (OR) e ! (NOT)).

Em seguida, retorna a lista de documentos relevantes para a consulta realizada.

Para executar, digite no terminal: python modelo_booleano.py base.txt consulta.txt