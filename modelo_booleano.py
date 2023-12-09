import nltk
import string
import sys

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords as nltk_stopwords

nltk.download("stopwords") # lista de palavras irrelevantes
nltk.download('punkt') # tokenizador
nltk.download("rslp") # extrator de radical

'''
Modelo booleano

- Entrada dos argumentos(nome do arquivo com a lista de documentos a serem avaliados, nome do arquivo com a lista de consultas a serem avaliadas)
- Carregar os documentos
- Pre-processar os documentos (tokenizar, remover stopwords, extrair radical, tirar pontuação) -> e gerar o indice invertido de cada documento
- Salvar os indices invertidos em um arquivo chamado indice.txt
- Carregar as consultas
- Pre-processar as consultas (tokenizar, remover stopwords, extrair radical)
- Executar as consultas -> comparar o indice invertido da consulta com o indice invertido dos documentos
- Salvar os resultados no arquivo respostas.txt com a quantidade de documentos que correspondem a consulta e o nome dos documentos
'''

# carregar os documentos
def ler_base(base_filename):
    documentos = []

    with open(base_filename, 'r', encoding='utf-8') as base_file:
        for line in base_file:
            # Suponha que cada linha do arquivo "base.txt" contenha o nome de um documento
            documento_filename = line.strip()
            with open(documento_filename, 'r', encoding='utf-8') as doc_file:
                documento = doc_file.read()
                documentos.append(documento)

    return documentos
    
# carregar as consultas
def ler_query(consulta_filename):
    with open(consulta_filename, 'r', encoding='utf-8') as consulta_file:
        consulta = consulta_file.read()
    return consulta

# fezer pre processamento do texto
def preprocessar_texto(texto):
    # Tokenização
    tokens = word_tokenize(texto.lower())

    # Remoção de stopwords e pontuação
    stop_words = set(nltk_stopwords.words('portuguese') + list(string.punctuation))
    tokens_sem_stopwords = [token for token in tokens if token not in stop_words]

    # Extração de radical
    stemmer = nltk.stem.RSLPStemmer()
    tokens_stemizados = [stemmer.stem(token) for token in tokens_sem_stopwords]

    return tokens_stemizados

# gerar o indice invertido de cada documento
def construir_indice_invertido(documentos):
    indice_invertido = {}
    
    for doc_id, documento in enumerate(documentos, start=1):
        tokens_stemizados = preprocessar_texto(documento)
        
        for token in tokens_stemizados:
            if token not in indice_invertido:
                indice_invertido[token] = [(doc_id, 1)]
            else:
                # Verificar se o documento já está na lista associada à palavra
                doc_na_lista = False
                for i, (doc, freq) in enumerate(indice_invertido[token]):
                    if doc == doc_id:
                        indice_invertido[token][i] = (doc, freq + 1)
                        doc_na_lista = True
                        break
                if not doc_na_lista:
                    indice_invertido[token].append((doc_id, 1))
    
    indice_invertido_ordenado = dict(sorted(indice_invertido.items()))

    return indice_invertido_ordenado

# salvar indice
def salvar_indice_invertido(indice_invertido):
    nome_arquivo = 'indice.txt'
    with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
        for palavra, ocorrencias in indice_invertido.items():
            linha = f'{palavra}:'
            for doc_id, freq in ocorrencias:
                linha += f' {doc_id},{freq}'
            arquivo.write(linha + '\n')

# funcao vai retornar true se o termo da consulta foi encontrado no indice invertido
def busca_termo(termo, id_doc, doc_ord):
    stemmer = nltk.stem.RSLPStemmer()
    for termo_indice, doc_freqs in doc_ord.items():
        if stemmer.stem(termo) == termo_indice:
            for doc, _ in doc_freqs.items():
                if doc == id_doc:
                    return True
    return False

# função que vai retornar um dicionario com os documentos ordenados
def gerar_doc_ord(indice_invertido):
    doc_ord = {}
    for termo, freqs_doc in indice_invertido.items():
        for doc_id, freq in freqs_doc:
            if termo in doc_ord:
                doc_ord[termo][doc_id] = freq
            else:
                doc_ord[termo] = {doc_id: freq}
    return doc_ord

# função que analisa uma consulta em formato de string e a divide em termos e operadores
def carregar_consulta(consulta):
    termos_consulta = []
    termo_atual = ""

    for caractere in consulta:
        if caractere == " ":
            if termo_atual != "":
                termos_consulta.append(termo_atual)
                termo_atual = ""
        elif caractere in ["&", "|"]:
            if termo_atual != "":
                termos_consulta.append(termo_atual)
                termo_atual = ""
            termos_consulta.append(caractere)
        elif caractere == "!":
            if termo_atual != "":
                termos_consulta.append(termo_atual)
                termo_atual = ""
            termo_atual = "!" + termo_atual
        else:
            termo_atual += caractere

    if termo_atual != "":
        termos_consulta.append(termo_atual)

    return termos_consulta

# função que vai ler as consultas e retornar um dicionario com os resultados
def ler_consultas(consulta, doc_ord, documentos):
    termos_consulta = carregar_consulta(consulta)

    resultados_consulta = {}
    termo_individual = True
    contador_operador_and = 0

    for i, termo in enumerate(termos_consulta):
        if termo == "&":
            contador_operador_and += 1

            for id_doc in range(1, len(documentos) + 1):
                if termos_consulta[i - 1][0] == "!":
                    resultado_termo1 = not busca_termo(
                        termos_consulta[i - 1][1:], id_doc, doc_ord
                    )
                else:
                    resultado_termo1 = busca_termo(termos_consulta[i - 1], id_doc, doc_ord)

                if termos_consulta[i + 1][0] == "!":
                    resultado_termo2 = not busca_termo(
                        termos_consulta[i + 1][1:], id_doc, doc_ord
                    )
                else:
                    resultado_termo2 = busca_termo(termos_consulta[i + 1], id_doc, doc_ord)

                resultado_final_termo = resultado_termo1 and resultado_termo2

                if id_doc in resultados_consulta:
                    resultados_consulta[id_doc].append(resultado_final_termo)
                else:
                    resultados_consulta[id_doc] = [resultado_final_termo]

            termo_individual = False

    for i, termo in enumerate(termos_consulta):
        if termo_individual:
            for id_doc in range(1, len(documentos) + 1):
                if termo[0] == "!":
                    resultado_termo = not busca_termo(termo[1:], id_doc, doc_ord)
                else:
                    resultado_termo = busca_termo(termo, id_doc, doc_ord)

                resultados_consulta.setdefault(id_doc, []).append(resultado_termo)

    for i, termo in enumerate(termos_consulta):
        for id_doc in range(1, len(documentos) + 1):
            if termo == "|":
                if len(resultados_consulta) != 0:
                    if termos_consulta[i - 2] != "&":
                        if termos_consulta[i - 1][0] == "!":
                            resultado_termo1 = not busca_termo(
                                termos_consulta[i - 1][1:], id_doc, doc_ord
                            )
                        else:
                            resultado_termo1 = busca_termo(
                                termos_consulta[i - 1], id_doc, doc_ord
                            )

                        resultado_termo2 = resultados_consulta[id_doc][-1]

                        resultado_final_termo = resultado_termo1 or resultado_termo2

                        resultados_consulta.setdefault(id_doc, []).append(
                            resultado_final_termo
                        )

                    if len(termos_consulta) > i + 1:
                        if termos_consulta[i + 1] != "&":
                            if termos_consulta[i + 1][0] == "!":
                                resultado_termo3 = not busca_termo(
                                    termos_consulta[i + 1][1:], id_doc, doc_ord
                                )
                            else:
                                resultado_termo3 = busca_termo(
                                    termos_consulta[i + 1], id_doc, doc_ord
                                )

                            resultado_termo4 = resultados_consulta[id_doc][-1]

                            resultado_final_termo = resultado_termo3 or resultado_termo4

                            resultados_consulta.setdefault(id_doc, []).append(
                                resultado_final_termo
                            )

    return resultados_consulta

# função que vai gravar os resultados no arquivo respostas.txt com a quantidade de documentos que correspondem a consulta e o nome dos documentos
def gravar_resultados(resultado):
    output_filename = 'resposta.txt'
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        # Conta quantos documentos correspondem à busca
        num_documentos_correspondentes = sum(1 for doc_resultados in resultado.values() if all(doc_resultados))
        
        # Grava o número de documentos correspondentes
        output_file.write(str(num_documentos_correspondentes) + '\n')
        
        # Grava os nomes dos documentos correspondentes
        for doc_id, doc_resultados in resultado.items():
            if all(doc_resultados):
                output_file.write(f'doc{doc_id}.txt\n')

def main(base_filename, consulta_filename):
    documentos = ler_base(base_filename)
    indice_invertido = construir_indice_invertido(documentos)
    salvar_indice_invertido(indice_invertido)
    consulta = ler_query(consulta_filename)
    document_sort = gerar_doc_ord(indice_invertido)
    documentosConsulta = ler_consultas(consulta, document_sort, documentos)
    gravar_resultados(documentosConsulta)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python modelo_booleano.py base.txt consulta.txt")
    else:
        base_filename = sys.argv[1]
        consulta_filename = sys.argv[2]
        main(base_filename, consulta_filename)


'''
Tentativas anteriores

def encontrar_documentos(consulta, indice_invertido):
    # Separa a consulta em termos e operadores
    termos = re.findall(r'\w+', consulta)
    operadores = re.findall(r'[!&|]', consulta)

    # Inicializa a lista de documentos com todos os documentos
    documentos = set(range(1, len(ler_base("base.txt"))))

    # Inicializa listas para termos NOT, AND e OR
    termos_not = []
    termos_and = []
    termos_or = []

    # Separa os termos de acordo com os operadores
    termo_atual = []
    for term, operador in zip(termos, operadores):
        if operador == '!':
            termos_not.append(term)
        else:
            termo_atual.append(term)
            if operador == '&':
                termos_and.append(termo_atual)
                termo_atual = []

    # Adiciona o último termo à lista de OR, se houver
    if termo_atual:
        termos_or.append(termo_atual)

    # Aplica os termos NOT
    for termo in termos_not:
        termos_and = [[doc_id for doc_id in documentos if not busca_termo(termo, indice_invertido, doc_id)]]

    # Aplica os termos AND
    for termo_and in termos_and:
        documentos_and = set(documentos)
        for termo in termo_and:
            documentos_and &= set([doc_id for doc_id in documentos if busca_termo(termo, indice_invertido, doc_id)])
        documentos = documentos_and

    # Aplica os termos OR
    for termo_or in termos_or:
        documentos_or = set()
        for termo in termo_or:
            documentos_or |= set([doc_id for doc_id in documentos if busca_termo(termo, indice_invertido, doc_id)])
        documentos = documentos_or

    return list(documentos)


def encontrar_documentos2(consulta, indice_invertido):
    # Separe a consulta em cláusulas usando o operador |
    clausulas = consulta.split('|')
    resultados = []

    for clausula in clausulas:
        clausula = clausula.strip()
        termos = re.findall(r'\w+', clausula)
        operadores = re.findall(r'[!&]', clausula)
        documentos_clausula = set(range(1, len(indice_invertido) + 1))

        for i, termo in enumerate(termos):
            termo = termo.strip()
            if operadores and operadores[i] == '!':
                termo = termo[1:]  # Remova o ! do termo
                documentos_termo = set()
                for doc_id in range(1, len(indice_invertido) + 1):
                    if doc_id not in indice_invertido.get(preprocessar_texto(termo), []):
                        documentos_termo.add(doc_id)
            else:
                documentos_termo = set([doc_id for doc_id in indice_invertido.get(preprocessar_texto(termo), [])])

            if i == 0:
                documentos_clausula = documentos_termo
            elif operadores[i - 1] == '&':
                documentos_clausula &= documentos_termo
            else:
                documentos_clausula |= documentos_termo

        resultados.append(documentos_clausula)

    # Combine os resultados de todas as cláusulas usando |
    documentos_finais = set()
    for docs in resultados:
        documentos_finais |= docs

    return list(documentos_finais)

'''