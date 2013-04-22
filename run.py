# coding: utf-8

import sys


import sqlalchemy as sa

from edne2db import varredura, msg, tabelas, alchemy_utils


def run():

    engine = alchemy_utils.cria_engine('postgresql', 'localhost', 'cauelt',
                                       '', 'cep')

    msg.exibe('Testando conexao com o banco...', end='')
    if not alchemy_utils.testa_conexao(engine):
        print('FALHOU\n')
        sys.exit(1)

    # conexao estabelecida com sucesso
    print('OK')

    msg.exibe('Procurando diretorios com o e-DNE...', end='')
    dirs_encontrados = varredura.busca_recursiva('./edne2db')
    print('PRONTO\n')

    if not dirs_encontrados['basico']:
        print("Nenhum diretorio com e-DNE basico encontrado\n")
    else:
        print('Diretorio com e-DNE basico:')

        msg.identacao += 2
        msg.exibe(dirs_encontrados['basico']['caminho'])
        msg.identacao -= 2
        print('')

    if dirs_encontrados['delta']:
        print('Diretorios com e-DNE delta:')
        msg.identacao += 2
        for dir in dirs_encontrados['delta']:
            msg.exibe(dir['caminho'])
        msg.identacao -= 2

    else:
        print('Nenhum e-DNE delta encontrado.')

    print('')

    # cria as tabelas para a população dos dados
    tabelas.Base.metadata.create_all(engine)

    # cria a sessão que se comunicará com o BD
    sessao = sa.orm.sessionmaker(bind=engine)()

    if dirs_encontrados['basico']:
        # cria os leitores e dados, que lerão as linhas dos arquivos
        mapa_leitores = varredura.cria_leitores_dados(
            dirs_encontrados['basico'])

        print('Processando diretorio {}...'
              .format(dirs_encontrados['basico']['caminho']))

        msg.identacao += 2
        alchemy_utils.processa_tabelas(mapa_leitores, sessao)
        msg.identacao -= 2

    if dirs_encontrados['delta']:
        for dir in dirs_encontrados['delta']:
            print('Processando diretorio {}...'.format(dir['caminho']))

            mapa_leitores = varredura.cria_leitores_dados(dir)

            msg.identacao += 2
            alchemy_utils.processa_tabelas(mapa_leitores, sessao, envia_a_cada=50)
            msg.identacao -= 2

if __name__ == '__main__':
    run()
