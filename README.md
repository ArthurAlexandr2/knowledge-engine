# Knowledge Engine — Titanic

Projeto acadêmico de Lógica e Matemática Discreta: ETL em Python que converte
uma tabela pública do Titanic em fatos Prolog e responde perguntas sofisticadas
com agregação, comparação, cálculo e composição de regras.

## Dataset e fonte

**Titanic dataset — pandas-dev/pandas**. Arquivo original: `doc/data/titanic.csv`.
Tabela de passageiros disponibilizada como dado de exemplo na documentação do
repositório oficial do pandas, com características dos passageiros e indicação
de sobrevivência.

- [Arquivo original no GitHub](https://github.com/pandas-dev/pandas/blob/main/doc/data/titanic.csv).
- [CSV RAW utilizado](https://raw.githubusercontent.com/pandas-dev/pandas/main/doc/data/titanic.csv).
- Data de acesso: **15/11/2026**.
- Cópia original preservada em `dados.csv`: **891 registros e 12 colunas**.
- Utiliza-se **apenas uma tabela-fonte**, sem combinar datasets. O ETL seleciona
  somente os **8 campos** abaixo e ignora as outras quatro colunas.
- SHA-256 do CSV incluído: `cd888141e6a2ca5906114d0b6a63d8a3e14edb3326f7bdd56327d14646b68c36`.

| Campo selecionado | Tipo e significado |
| --- | --- |
| survived | Qualitativa binária codificada: 0 = morreu; 1 = sobreviveu |
| pclass | Qualitativa ordinal codificada: classe 1, 2 ou 3 |
| sex | Qualitativa nominal: sexo registrado (`female`, `male`) |
| age | Quantitativa: idade em anos, incluindo frações |
| sibsp | Quantitativa inteira: irmãos/cônjuges a bordo |
| parch | Quantitativa inteira: pais/filhos a bordo |
| fare | Quantitativa: tarifa registrada |
| embarked | Qualitativa nominal: porto de embarque (`c` = Cherbourg, `q` = Queenstown, `s` = Southampton) |

## Processo ETL

```text
dados.csv → gerar_base.py → limpeza/normalização → base.pl
```

O conversor usa somente a biblioteca padrão do Python, sem dependência de
pandas. Normaliza cabeçalhos para minúsculas, seleciona os oito campos e remove
espaços externos. Categorias são convertidas em átomos ASCII minúsculos seguros
para Prolog. Números são preservados como números, com notação decimal fixa.

Campos vazios e marcadores `NA`, `N/A`, `NaN`, `null`, `none`, `?` e
`desconhecido` tornam-se o átomo `desconhecido`, sem imputação ou descarte da
linha. Nesta tabela há **177 idades ausentes e 2 portos ausentes**; os demais
campos selecionados estão completos.

O dataset possui 891 passageiros, mas `passageiro/8` utiliza somente oito
atributos: `PassengerId`, nome (`Name`), bilhete (`Ticket`) e cabine (`Cabin`)
não fazem parte da base. Assim, passageiros diferentes podem gerar fatos
Prolog textualmente idênticos. Essas ocorrências não são removidas: cada uma
representa uma linha/passageiro do dataset original. Preservar a multiplicidade
mantém a contribuição de cada passageiro; deduplicar os fatos alteraria
incorretamente as contagens e médias.

O ETL exige os oito cabeçalhos selecionados e valida os valores necessários
para gerar `passageiro/8`. Descarta com aviso linhas com valores numéricos
inválidos, negativos ou infinitos, sobrevivência fora de 0/1, classe fora de
1/2/3 ou frações em campos inteiros. Também descarta linhas com mais valores
que cabeçalhos ou nas quais um campo selecionado esteja estruturalmente
ausente. Células vazias presentes seguem o tratamento de ausências acima.
Uma linha curta pode ser aceita se faltarem apenas campos ignorados.
As categorias são normalizadas em átomos seguros, sem validação adicional
de domínio para sexo e porto. CSV sem cabeçalhos válidos ou sem linhas válidas
encerra com código 1 e preserva a base anterior. A saída é substituída somente
após a conversão completa.

Resultado da execução com o CSV incluído, código de saída **0**:

```text
891 fatos gerados em base.pl; 0 linhas descartadas.
```

Cada fato tem oito argumentos na ordem:

```prolog
passageiro(Survived, Pclass, Sex, Age, SibSp, Parch, Fare, Embarked).
```

Exemplo real da primeira linha:

```prolog
passageiro(0, 3, male, 22, 1, 0, 7.25, s).
```

## Como executar

Requisitos: Python 3.10 ou superior e
[SWI-Prolog](https://www.swi-prolog.org/download/stable) no `PATH`.
O dataset e a base gerada já estão incluídos no repositório.

### 1. Clonar

```bash
git clone https://github.com/ArthurAlexandr2/knowledge-engine.git
cd knowledge-engine
```

### 2. Verificar Python

```bash
python --version
```

### 3. Gerar a base

```bash
python gerar_base.py
```

### 4. Usar SWI-Prolog

Se instalado localmente e disponível no `PATH`:

```bash
swipl -s queries.pl
```

`queries.pl` carrega automaticamente `base.pl`. No prompt do Prolog, teste:

```prolog
?- sobreviventes_por_sexo(Sexo, Total).
?- sobreviventes_por_classe(Classe, Total).
?- classe_mais_sobreviventes(Classe, Total).
?- tarifa_media_sobreviventes(Classe, Media).
```

Use `;` para obter as próximas respostas. Para sair, use `halt.`. Também é
possível executar todas as respostas de uma consulta pelo terminal, sem sessão
interativa:

```console
swipl -q -s queries.pl -g "forall(sobreviventes_por_sexo(S,T),format('~w: ~d~n',[S,T]))" -t halt
```

### 5. Alternativa com SWISH

Acesse [SWISH](https://swish.swi-prolog.org/). Na área **Program**, cole o
conteúdo de `base.pl` seguido de `queries.pl`, removendo apenas da cópia no
editor a diretiva `:- ensure_loaded('base.pl').`, pois os fatos já estarão no
mesmo programa. Na área **Query**, execute uma das consultas acima sem o
prefixo `?-`.

## Perguntas sofisticadas

### A. Quantos sobreviventes há por sexo?

Predicado: `sobreviventes_por_sexo/2`. É sofisticada por **agregação**:
`sexo_conhecido/1` identifica grupos, `setof/3` elimina grupos repetidos,
`member/2` os enumera, `findall/3` coleta os sobreviventes de cada sexo e
`length/2` os conta, preservando passageiros com atributos idênticos.

```prolog
?- sobreviventes_por_sexo(Sexo, Total).
Sexo = female, Total = 233 ;
Sexo = male, Total = 109.
```

### B. Qual classe teve o maior número de sobreviventes?

Predicado: `classe_mais_sobreviventes/2`. É sofisticada por **agregação,
comparação e composição de regras**: usa `sobreviventes_por_classe/2` para
calcular os totais e verifica, com `\+/1` e `>/2`, que nenhuma outra classe
possui total maior. Retorna todas as classes empatadas no máximo.

```prolog
?- classe_mais_sobreviventes(Classe, Total).
Classe = 1, Total = 136.
```

A consulta auxiliar também é agregada: `classe_conhecida/1`, `setof/3`,
`member/2`, `findall/3` e `length/2` calculam sobreviventes por classe:

```prolog
?- sobreviventes_por_classe(Classe, Total).
Classe = 1, Total = 136 ;
Classe = 2, Total = 87 ;
Classe = 3, Total = 119.
```

### C. Qual a tarifa média dos passageiros sobreviventes por classe?

Predicado: `tarifa_media_sobreviventes/2`. É sofisticada por **agregação e
cálculo**: enumera classes com predicado auxiliar, coleta tarifas numéricas
com `findall/3` e `number/1`, conta com `length/2`, soma com `sum_list/2` e
calcula a média com `is/2`. Exige quantidade maior que zero para evitar divisão
por zero. Tarifas desconhecidas são excluídas da soma e do denominador.

```prolog
?- tarifa_media_sobreviventes(Classe, Media).
Classe = 1, Media = 95.60802867647055 ;
Classe = 2, Media = 22.0557 ;
Classe = 3, Media = 13.694887394957966.
```

As últimas casas decimais podem variar com a representação de ponto flutuante.
Grupos conhecidos sem sobreviventes retornam contagem zero; grupos de sexo ou
classe desconhecidos são excluídos. Sobrevivência desconhecida não conta como
sobrevivente. As contagens são absolutas, não taxas de sobrevivência; as
consultas não estabelecem causalidade.

## Relação com Lógica de Primeira Ordem

### Fatos e inferência

Cada linha válida do dataset gera uma ocorrência de fato `passageiro/8`,
representando uma instância verdadeira desse predicado na base de conhecimento.
As regras derivam informações a partir desses fatos, e as queries solicitam ao
Prolog valores que tornam determinados objetivos verdadeiros. As contagens
preservam as ocorrências dos passageiros, inclusive cláusulas textualmente
idênticas; repetir uma sentença não acrescenta uma nova verdade na LPO clássica.

### Unificação

Ao executar uma consulta, o Prolog busca substituições para as variáveis que
tornem os objetivos compatíveis com os fatos e as cabeças das regras da base,
prosseguindo com a resolução dos respectivos corpos.

### Quantificação implícita

As variáveis das cláusulas são implicitamente quantificadas universalmente,
permitindo formular regras gerais sobre os passageiros. Nas consultas,
buscam-se substituições que satisfaçam os objetivos; predicados de agregação
também estabelecem escopos próprios para suas variáveis.

A negação como falha (`\+`) usada na busca do máximo verifica a ausência de
uma prova de total maior na base conhecida; não é negação clássica irrestrita.
`findall`, `setof`, `sum_list` e a aritmética são recursos operacionais do
Prolog empregados nas análises, não conectivos da LPO.

## Validação realizada

- ETL executado sobre o CSV real: código 0, 891 fatos e zero linhas descartadas.
- Conferência de todos os fatos contra as oito colunas selecionadas do CSV:
  aridade 8, ponto final, átomos minúsculos, tipos e ausências consistentes.
- Regras e base carregadas sem erros ou avisos no **SWI-Prolog 10.1.20 via
  WebAssembly**, pacote oficial `swipl-wasm` 8.3.0, executado em Node.js fora do
  repositório. O executável nativo `swipl` não estava disponível no ambiente.
- As quatro consultas foram executadas e seus resultados completos foram
  verificados por asserções; contagens e médias também conferidas
  independentemente em Python (tolerância de `1e-9` para as médias).
- Contagem total e ausências verificadas também em Prolog; nova execução do
  ETL confirmada como reprodutível, sem alterar o conteúdo da base.

## Estrutura

```text
knowledge-engine/
├── README.md
├── dados.csv      # CSV original: única tabela-fonte
├── gerar_base.py  # ETL Python: seleciona oito campos
├── base.pl        # 891 fatos passageiro/8 gerados
├── queries.pl     # regras auxiliares e perguntas sofisticadas
└── .gitignore
```
