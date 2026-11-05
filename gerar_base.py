"""Converte os oito campos do Titanic em fatos passageiro/8."""

import csv
import re
import sys
import unicodedata
from decimal import Decimal, InvalidOperation
from pathlib import Path


PASTA = Path(__file__).resolve().parent
CAMPOS = ('survived', 'pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked')
INTEIROS = {'survived', 'pclass', 'sibsp', 'parch'}
AUSENTES = {'', 'na', 'n/a', 'nan', 'null', 'none', '?', 'desconhecido'}


def converter_valor(campo, valor):
    """Preserva numeros e converte categorias em atomos Prolog seguros."""
    valor = valor.strip()
    if valor.lower() in AUSENTES:
        return 'desconhecido'
    if campo in {'sex', 'embarked'}:
        texto = unicodedata.normalize('NFKD', valor.lower())
        texto = texto.encode('ascii', 'ignore').decode('ascii')
        texto = re.sub(r'\s+', '', texto)
        texto = re.sub(r'[^a-z0-9_]', '_', texto).strip('_')
        if not texto:
            return 'desconhecido'
        return texto if texto[0].isalpha() else 'valor_' + texto

    try:
        numero = Decimal(valor)
    except InvalidOperation as erro:
        raise ValueError(f'{campo}: numero invalido {valor!r}') from erro
    if not numero.is_finite() or numero < 0:
        raise ValueError(f'{campo}: esperado numero finito e nao negativo')
    if campo in INTEIROS:
        if numero != numero.to_integral_value():
            raise ValueError(f'{campo}: esperado numero inteiro')
        if campo == 'survived' and numero not in (0, 1):
            raise ValueError('survived: esperado 0 ou 1')
        if campo == 'pclass' and numero not in (1, 2, 3):
            raise ValueError('pclass: esperado 1, 2 ou 3')
        return str(int(numero))
    # A notacao decimal fixa evita expoentes incompativeis com Prolog.
    return format(numero, 'f')


def ler_fatos(origem):
    fatos = []
    descartadas = 0
    with origem.open(encoding='utf-8-sig', newline='') as arquivo:
        leitor = csv.DictReader(arquivo)
        if not leitor.fieldnames:
            raise ValueError('CSV vazio ou sem cabecalho.')
        nomes = [nome.strip().lower() for nome in leitor.fieldnames]
        if len(nomes) != len(set(nomes)):
            raise ValueError('CSV com nomes de colunas duplicados.')
        leitor.fieldnames = nomes
        faltantes = sorted(set(CAMPOS) - set(nomes))
        if faltantes:
            raise ValueError('Colunas obrigatorias ausentes: ' + ', '.join(faltantes))
        for linha in leitor:
            try:
                if None in linha or any(linha[campo] is None for campo in CAMPOS):
                    raise ValueError('quantidade de colunas inconsistente')
                valores = [converter_valor(campo, linha[campo]) for campo in CAMPOS]
                fatos.append('passageiro(' + ', '.join(valores) + ').')
            except ValueError as erro:
                descartadas += 1
                print(f'Linha {leitor.line_num} descartada: {erro}', file=sys.stderr)
    return fatos, descartadas


def escrever_base(fatos, destino):
    # So substitui a base depois de concluir a leitura e escrita.
    cabecalho = (
        '% Gerado automaticamente por gerar_base.py. Nao editar.\n'
        '% Ordem: survived, pclass, sex, age, sibsp, parch, fare, embarked.\n'
        ':- dynamic passageiro/8.\n'
    )
    if not fatos:
        cabecalho += '% Base vazia: nenhum fato disponivel; adicione dados.csv e execute o conversor.\n'
    temporario = destino.with_suffix('.pl.tmp')
    try:
        temporario.write_text(cabecalho + ''.join(fato + '\n' for fato in fatos), encoding='utf-8')
        temporario.replace(destino)
    finally:
        temporario.unlink(missing_ok=True)


def main():
    origem = PASTA / 'dados.csv'
    if not origem.is_file():
        print(f'Erro: arquivo nao encontrado: {origem}. Coloque o CSV publico do Titanic '
              'nesse caminho e execute python gerar_base.py novamente. Consulte README.md.',
              file=sys.stderr)
        return 1
    try:
        fatos, descartadas = ler_fatos(origem)
        if not fatos:
            raise ValueError('Nenhuma linha valida encontrada; a base anterior foi preservada.')
        escrever_base(fatos, PASTA / 'base.pl')
    except (OSError, ValueError, csv.Error) as erro:
        print(f'Erro: {erro}', file=sys.stderr)
        return 1
    print(f'{len(fatos)} fatos gerados em base.pl; {descartadas} linhas descartadas.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
