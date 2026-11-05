# Knowledge Engine

Projeto acadêmico de Lógica e Matemática Discreta: converter uma tabela pública
do Titanic em uma base de conhecimento Prolog e responder perguntas com
agregação, comparação e composição de regras.

## Dataset e preparação

**Pendente: adicionar `dados.csv` na raiz deste repositório.** Nenhum CSV foi
fornecido e a `base.pl` inicial está vazia. Não há resultados empíricos ainda.

Use uma única tabela pública de passageiros do Titanic que contenha os oito
campos abaixo, incluindo o resultado de sobrevivência. Não combine tabelas.
Renomeie o arquivo para `dados.csv`, em UTF-8, separado por vírgulas, com cabeçalho.
Cabeçalhos como `Survived` e `Pclass` também são aceitos.

**Fonte do dataset: PENDENTE — inserir aqui a URL pública exata da tabela
escolhida, sua identificação/licença e a data de acesso ao adicionar o CSV.**
Não use uma tabela de teste sem a coluna `survived`.

| Campo | Tipo e significado |
| --- | --- |
| survived | Qualitativa binária codificada: 0 = morreu, 1 = sobreviveu |
| pclass | Qualitativa ordinal codificada: classe 1, 2 ou 3 |
| sex | Qualitativa nominal: sexo registrado |
| age | Quantitativa: idade em anos, aceita frações |
| sibsp | Quantitativa inteira: irmãos/cônjuges a bordo |
| parch | Quantitativa inteira: pais/filhos a bordo |
| fare | Quantitativa: tarifa registrada |
| embarked | Qualitativa nominal: porto de embarque |

## Conversão Python (ETL)

`gerar_base.py` lê apenas uma tabela e seleciona os oito campos; colunas extras
são ignoradas. Usa somente a biblioteca padrão: **não precisa de pandas**.
Remove espaços externos dos valores e normaliza cabeçalhos para minúsculas.
Categorias são convertidas em átomos ASCII em minúsculas, sem espaços, com
caracteres incompatíveis substituídos por `_`. Categorias iniciadas por número
recebem o prefixo `valor_`.

Campos vazios e marcadores `NA`, `N/A`, `NaN`, `null`, `none`, `?` e
`desconhecido` viram o átomo `desconhecido`. Números permanecem números;
valores negativos, infinitos, valores inválidos de classe/sobrevivência e
frações em campos inteiros fazem a linha ser descartada com aviso.
Linhas com quantidade inconsistente de colunas também são descartadas.
Ausências não causam descarte e não são imputadas. Linhas idênticas são
preservadas: podem representar passageiros distintos.

O script informa os totais de fatos gerados e linhas descartadas. CSV ausente,
cabeçalhos inválidos ou nenhuma linha válida produzem erro claro, código de
saída 1 e preservam a base anterior. A saída é substituída somente após a
conversão completa.

Cada fato tem oito argumentos nesta ordem e termina com ponto:

```prolog
% Estrutura do predicado; variáveis abaixo não são dados de passageiros.
passageiro(Survived, Pclass, Sex, Age, SibSp, Parch, Fare, Embarked).
```

## Execução

1. Instale Python 3.10 ou superior e [SWI-Prolog](https://www.swi-prolog.org/download/stable), caso ainda não estejam instalados.
2. Adicione o CSV público em `dados.csv` e registre a fonte acima.
3. No terminal, na raiz do repositório, execute:

```console
python gerar_base.py
swipl -s queries.pl
```

`queries.pl` carrega `base.pl` automaticamente. Em uma sessão SWI-Prolog já
aberta na raiz, também é possível carregar explicitamente:

```prolog
?- [base, queries].
```

No SWISH, cole o conteúdo de `base.pl` seguido de `queries.pl` no editor de
programa, **removendo a linha `:- ensure_loaded('base.pl').`**: a base já estará
no mesmo programa. Execute as consultas no painel de consultas, sem `?-`.

## Perguntas e consultas

**A. Quantos sobreviventes há por sexo?** Enumera sexos conhecidos com
`setof/3`, reúne sobreviventes com `findall/3` e conta com `length/2`.

```prolog
?- sobreviventes_por_sexo(Sexo, Total).
```

**B. Quantos sobreviventes há por classe e qual classe tem o maior total?**
Compõe a contagem por classe com comparação numérica entre totais.
Retorna todas as classes empatadas no máximo.

```prolog
?- sobreviventes_por_classe(Classe, Total).
?- classe_mais_sobreviventes(Classe, Total).
```

**C. Qual é a tarifa média dos sobreviventes de cada classe?** Reúne tarifas
numéricas, soma com `sum_list/2` e divide pela quantidade de tarifas conhecidas.
Uma classe sem tarifa válida de sobreviventes não retorna média, evitando
divisão por zero e um zero artificial.

```prolog
?- tarifa_media_sobreviventes(Classe, Media).
```

Use `;` no SWI-Prolog para pedir as próximas respostas. Grupos conhecidos sem
sobreviventes retornam contagem zero; grupos desconhecidos são excluídos das
análises por sexo/classe. Sobrevivência desconhecida não conta como sobrevivente.
Com a base vazia, as consultas retornam `false`, sem resultados inventados.
As contagens são absolutas; não representam taxas de sobrevivência e não
demonstram causalidade.

## Estrutura

```text
knowledge-engine/
├── gerar_base.py  # CSV -> fatos Prolog
├── dados.csv      # PENDENTE: única tabela pública, adicionada manualmente
├── base.pl        # gerada pelo conversor; inicialmente vazia
├── queries.pl     # regras auxiliares e análises
├── README.md
└── .gitignore
```

Antes do commit/push, adicione o dataset e sua fonte, execute
`python gerar_base.py`, carregue `queries.pl` e rode as quatro consultas acima.
Confira as linhas descartadas e revise `git diff` e `git status` antes de
versionar os arquivos.

## Validação realizada

O conversor foi executado com um CSV sintético isolado para verificar seleção
dos campos, duplicatas, ausências, normalização, descarte de valores inválidos
e preservação da base em caso de erro. As regras foram executadas no SWI-Prolog
(WebAssembly) para conferir sintaxe, contagens, empates, grupos sem
sobreviventes, base vazia e médias com tarifas ausentes. Esses dados serviram
apenas para testes e não integram `base.pl`. A validação com o dataset público
real permanece pendente da inclusão de `dados.csv`.
