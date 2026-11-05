% No SWI-Prolog, carregar queries.pl tambem carrega a base ao lado dele.
% No SWISH, cole base.pl e depois este arquivo, removendo ensure_loaded/1.
:- ensure_loaded('base.pl').
:- use_module(library(lists), [member/2, sum_list/2]).

sexo_conhecido(Sexo) :-
    passageiro(_, _, Sexo, _, _, _, _, _),
    Sexo \= desconhecido.

classe_conhecida(Classe) :-
    passageiro(_, Classe, _, _, _, _, _, _),
    number(Classe).

% setof remove grupos repetidos; findall preserva passageiros identicos.
sobreviventes_por_sexo(Sexo, Total) :-
    setof(S, sexo_conhecido(S), Sexos),
    member(Sexo, Sexos),
    findall(1, passageiro(1, _, Sexo, _, _, _, _, _), Sobreviventes),
    length(Sobreviventes, Total).

sobreviventes_por_classe(Classe, Total) :-
    setof(C, classe_conhecida(C), Classes),
    member(Classe, Classes),
    findall(1, passageiro(1, Classe, _, _, _, _, _, _), Sobreviventes),
    length(Sobreviventes, Total).

% Retorna todas as classes empatadas no maior total, inclusive se for zero.
classe_mais_sobreviventes(Classe, Total) :-
    sobreviventes_por_classe(Classe, Total),
    \+ (sobreviventes_por_classe(_, OutroTotal), OutroTotal > Total).

% Tarifas desconhecidas nao entram na soma nem no denominador.
tarifa_media_sobreviventes(Classe, Media) :-
    setof(C, classe_conhecida(C), Classes),
    member(Classe, Classes),
    findall(Tarifa,
            (passageiro(1, Classe, _, _, _, _, Tarifa, _), number(Tarifa)),
            Tarifas),
    length(Tarifas, Quantidade),
    Quantidade > 0,
    sum_list(Tarifas, Soma),
    Media is Soma / Quantidade.

% ?- sobreviventes_por_sexo(Sexo, Total).
% ?- sobreviventes_por_classe(Classe, Total).
% ?- classe_mais_sobreviventes(Classe, Total).
% ?- tarifa_media_sobreviventes(Classe, Media).
