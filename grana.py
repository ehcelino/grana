import PySimpleGUI as sg
import locale
from datetime import datetime
import sqlite3
import gettext
import re
import logging
import grafico as gr
from dateutil.relativedelta import relativedelta
import operator
import img
import os
_ = gettext.gettext

# en = gettext.translation('en', localedir='locale', languages=['en'])
# en.install()
# _ = en.gettext # English

# #############################################
# GRANA! gerenciador de finanças pessoais
#
# para criar requirements.txt: comando pipreqs no prompt
# #############################################

meses = [(_('Janeiro')), (_('Fevereiro')), (_('Março')), (_('Abril')), (_('Maio')), (_('Junho')),
         (_('Julho')), (_('Agosto')), (_('Setembro')),
         (_('Outubro')), (_('Novembro')), (_('Dezembro'))]
dias = [(_('Dom')), (_('Seg')), (_('Ter')), (_('Qua')), (_('Qui')), (_('Sex')), (_('Sab'))]
ano_inicio = sg.user_settings_get_entry('-anoinicial-', datetime.today().year)
ano_agora = datetime.today().year
anos = list(range(ano_inicio, ano_agora + 6, +1))

arqdb = './db/grana.db'
caminho = './db/'


logging.basicConfig(filename='errorlog.txt', level=logging.ERROR,
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())

locale.setlocale(locale.LC_ALL, '')
sg.user_settings_filename('grana.json','./')

regexData = re.compile(r'\d{2}/\d{2}/\d{4}')
regexDinheiro = re.compile(r'^(\d{1,}\,\d{2}?)$')
regexDia = re.compile(r'\b[0-3]{0,1}[0-9]{1}\b')

def mesatual():
    res = ''
    mesat = datetime.now()
    m = mesat.strftime('%m')
    if m == '01':
        res = meses[0]
    elif m == '02':
        res = meses[1]
    elif m == '03':
        res = meses[2]
    elif m == '04':
        res = meses[3]
    elif m == '05':
        res = meses[4]
    elif m == '06':
        res = meses[5]
    elif m == '07':
        res = meses[6]
    elif m == '08':
        res = meses[7]
    elif m == '09':
        res = meses[8]
    elif m == '10':
        res = meses[9]
    elif m == '11':
        res = meses[10]
    elif m == '12':
        res = meses[11]
    return res

def cria_db():
    try:
        os.makedirs(caminho, exist_ok=True)
    except Exception as err:
        logger.error(err, exc_info=True)
        print('Não foi possível criar o caminho do banco de dados: ', err)

    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    try:
        c.execute(
            'CREATE TABLE "movimento" ("mo_index" INTEGER, "mo_data" TEXT, '
            '"mo_tipo" TEXT, "mo_categoria" TEXT, '
            '"mo_descricao" TEXT, "mo_valor" REAL, "mo_relrec" INTEGER, PRIMARY KEY("mo_index"))'
        )
        conexao.commit()
        c.execute(
            'CREATE TABLE "categoria" ("ca_index" INTEGER, "ca_categoria" TEXT, PRIMARY KEY("ca_index"))'
        )
        conexao.commit()
        c.execute(
            'CREATE TABLE "recorrente" ("re_index" INTEGER, "re_dia" TEXT, '
            '"re_tipo" TEXT, "re_categoria" TEXT, "re_descricao" TEXT, '
            '"re_valor" REAL, "re_data_inicio" TEXT, PRIMARY KEY("re_index"))'
        )
        conexao.commit()
    except Exception as err:
        logger.error(err, exc_info=True)
        print('Não foi possível criar o banco de dados: ', err)
    conexao.close()

def movimento_calcula_total(mesano):
    # retorna o valor total do movimento do mês
    mesano = '%' + mesano + '%'
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT mo_tipo, mo_valor FROM movimento WHERE mo_data LIKE ?', (mesano,))
    resultado = c.fetchall()
    valor = 0.0
    for idx, x in enumerate(resultado):
        if x[0] == 'Entrada':
            valor = valor + x[1]
        else:
            valor = valor - x[1]
    return valor

def movimento_ler_indice(indice):
    # retorna data, tipo, categoria, descrição, valor, recorrente
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT mo_data, mo_tipo, mo_categoria, '
              'mo_descricao, mo_valor, mo_relrec FROM movimento WHERE mo_index = ?', (indice,))
    resultado = c.fetchone()
    temp = str(resultado[4])
    temp = temp.replace('.', ',') + '0'
    resultado_final = [resultado[0], resultado[1], resultado[2], resultado[3], temp, resultado[5]]
    return resultado_final


def movimento_ler(mesano):
    # retorna indice, data, tipo, categoria, descrição, valor, R para recorrente e índice do recorrente
    mesano = '%' + mesano + '%'
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT * FROM movimento WHERE mo_data LIKE ?', (mesano,))
    resultado = c.fetchall()
    resultado_final = []
    for idx, x in enumerate(resultado):
        if x[6] != 0:
            tmp_rec = 'R'
        else:
            tmp_rec = ''
        if x[2] == 'Saída':
            tmp_val = - x[5]
        else:
            tmp_val = x[5]
        temp = [x[0], x[1], x[2], x[3], x[4], locale.currency(tmp_val), tmp_rec, x[6]]
        resultado_final.append(temp)
    return resultado_final

def movimento_ler_recorrente(indice):
    # retorna dia e data de início
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT re_dia, re_data_inicio FROM recorrente WHERE re_index = ?', (indice,))
    resultado = c.fetchone()
    return resultado


def movimento_grava(data, tipo, categoria, descricao, valor, relrec):
    dados = [data, tipo, categoria, descricao, valor, relrec]
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'INSERT INTO movimento(mo_data, mo_tipo, mo_categoria, ' \
              'mo_descricao, mo_valor, mo_relrec) VALUES (?, ?, ?, ?, ?, ?)'
    c.execute(comando, dados)
    conexao.commit()
    conexao.close()

def movimento_grava_recorrente(dia, tipo, categoria, descricao, valor, datainicio):
    dataultimaatualizacao = str(dia) + datetime.strftime(datetime.now(), '/%m/%Y')
    dados = [dia, tipo, categoria, descricao, valor, datainicio, dataultimaatualizacao]
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'INSERT INTO recorrente(re_dia, re_tipo, re_categoria, ' \
              're_descricao, re_valor, re_data_inicio, re_ultima_atualizacao) VALUES (?, ?, ?, ?, ?, ?, ?)'
    c.execute(comando, dados)
    conexao.commit()
    indice_recorrente = c.lastrowid
    data_insercao = str(dia) + datainicio[2:]
    dif_meses = datetime.now().month - datetime.strptime(data_insercao, '%d/%m/%Y').month
    data_tmp = datetime.now() + relativedelta(day=int(dia))
    x = 0
    while x < dif_meses + 1:
        data_final = data_tmp - relativedelta(months=x)
        # print(datetime.strftime(data_final, '%d/%m/%Y'))
        data_final_str = datetime.strftime(data_final, '%d/%m/%Y')
        movimento_grava(data_final_str, tipo, categoria, descricao, valor, indice_recorrente)
        x = x + 1
    conexao.close()

def movimento_integra():
    # ultima_ativacao = sg.user_settings_get_entry('-ultimaativacao-')
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = ('SELECT * FROM recorrente')
    c.execute(comando)
    resultado = c.fetchall()
    data = None
    for idx, x in enumerate(resultado):
        data = datetime.strptime(x[7], '%d/%m/%Y')
        diferenca = datetime.now().month - data.month
        if diferenca > 0:
            y = 0
            while y < diferenca:
                data_tmp = datetime.now() + relativedelta(day=int(x[1]))
                data_final = data_tmp - relativedelta(months=y)
                # print(datetime.strftime(data_final, '%d/%m/%Y'))
                data_final_str = datetime.strftime(data_final, '%d/%m/%Y')
                movimento_grava(data_final_str, x[2], x[3], x[4], x[5], x[0])
                y = y + 1
            # ATUALizA DATA RECORRENTE
            data_tmp_str = datetime.strftime(data_tmp, '%d/%m/%Y')
            dados = (data_tmp_str, x[0])
            c.execute('UPDATE recorrente SET re_ultima_atualizacao = ? WHERE re_index = ?', dados)
            conexao.commit()
    conexao.close()
    # print(resultado)

def movimento_atualiza(indice, data, tipo, categoria, descricao, valor):
    dados = [data, tipo, categoria, descricao, valor, indice]
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'UPDATE movimento SET mo_data = ?, mo_tipo = ?, ' \
              'mo_categoria = ?, mo_descricao = ?, mo_valor = ? WHERE mo_index = ?'
    c.execute(comando, dados)
    conexao.commit()
    conexao.close()


def movimento_atualiza_recorrente(indice, dia, tipo, categoria, descricao, valor, data_inicio):
    dados = [dia, tipo, categoria, descricao, valor, data_inicio, indice]
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'UPDATE recorrente SET re_dia = ?, re_tipo = ?, ' \
              're_categoria = ?, re_descricao = ?, re_valor = ?, re_data_inicio WHERE mo_index = ?'
    c.execute(comando, dados)
    conexao.commit()
    conexao.close()

def movimento_apaga(index):
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'DELETE FROM movimento WHERE mo_index = ?'
    c.execute(comando, (index,))
    conexao.commit()
    conexao.close()

def movimento_apaga_recorrente(index):
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'DELETE FROM recorrente WHERE re_index = ?'
    c.execute(comando, (index,))
    conexao.commit()
    dados = [0, index]
    comando = 'UPDATE movimento SET mo_relrec = ? WHERE mo_relrec = ?'
    c.execute(comando, dados)
    conexao.commit()
    conexao.close()

def movimento_apaga_recorrente_retro(index):
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'DELETE FROM recorrente WHERE re_index = ?'
    c.execute(comando, (index,))
    conexao.commit()
    dados = [index,]
    comando = 'DELETE FROM movimento WHERE mo_relrec = ?'
    c.execute(comando, dados)
    conexao.commit()
    conexao.close()

def mov_anual_categoria(categoria, ano):
    # retorna data da operação, descrição , valor
    tipo = 'Saída'
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = ('SELECT mo_data, mo_descricao, mo_valor FROM movimento '
               'WHERE mo_data LIKE ? AND mo_categoria LIKE ? AND mo_tipo = ?')
    categoria = '%' + categoria + '%'
    ano2 = '%' + str(ano) + '%'
    c.execute(comando, (ano2, categoria, tipo))
    resultado = c.fetchall()
    return resultado

def mov_anual_recebido(ano):
    # retorna data da operação, descrição , valor
    tipo = 'Entrada'
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = ('SELECT mo_data, mo_descricao, mo_valor FROM movimento '
               'WHERE mo_data LIKE ? AND mo_tipo = ?')
    ano2 = '%' + str(ano) + '%'
    c.execute(comando, (ano2, tipo))
    resultado = c.fetchall()
    return resultado

def categorias_ler():
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT ca_categoria FROM categoria')
    resultado = c.fetchall()
    resultado_list = []
    for idx, x in enumerate(resultado):
        resultado_list.append(''.join(x))
    conexao.close()
    return resultado_list

def categorias_apaga(categoria):
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    dados = ['Sem categoria', categoria]
    comando = 'UPDATE movimento SET mo_categoria = ? WHERE mo_categoria = ?'
    c.execute(comando, dados)
    conexao.commit()
    comando = 'DELETE FROM categoria WHERE ca_categoria = ?'
    c.execute(comando, (categoria,))
    conexao.commit()
    conexao.close()

def categorias_criar(categoria):
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('INSERT INTO categoria(ca_categoria) VALUES (?)', (categoria,))
    conexao.commit()
    conexao.close()

def sort_table(table, cols):
    """ sort a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        try:
            table = sorted(table, key=operator.itemgetter(col))
        except Exception as err:
            logger.error(err, exc_info=True)
            sg.popup_error('Erro', 'Erro na função de organizar tabela', err)
    return table

class splashscreen():
    tmp = sg.user_settings_get_entry('-splashscreen-', True)
    if tmp == True:
        sg.Window('Nada', [[sg.Image(data=img.logo_grande64)]], transparent_color=sg.theme_background_color(),
                  no_titlebar=True, keep_on_top=True).read(timeout=2000, close=True)


class funcao_principal:
    global _
    titulos = [(_('Indice')), (_('Data')), (_('Tipo')), (_('Categoria')),
               (_('Descrição')), (_('Valor')), (_('R')), (_('Indice recorrente'))]
    largura = [0, 10, 10, 30, 35, 10, 2, 0]
    visibilidade = [False, True, True, True, True, True, True, False]
    row = []
    dados = []
    tam_texto = 7
    tam_imput = 1
    atualiza = True
    indice_tmp = None
    indice_recorrente = 0
    linha_tmp = []
    def janela_recorrente(self):
        layout = [
            [sg.Text((_('Você está prestes a apagar um lançamento recorrente.')))],
            [sg.Text('Este lançamento começou a partir de {}.'.format(self.linha_tmp[1]))],
            [sg.Text((_('Você deseja apagá-lo daqui por diante ou retroativamente?')))],
            [sg.Push(), sg.B((_('Daqui por diante')), k='-DAQUI-'), sg.B((_('Retroativamente')), k='-RETRO-'),
             sg.B((_('Cancelar')), k='-CANCELA-')]
        ]
        return sg.Window((_('Apagar')), layout,
                         finalize=True)

    def janela_sobre(self):
        layout = [
            [sg.Text((_('Sobre')), font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Text((_('A fazer...')))],
            [sg.Text((_('Quer personalizar sua cópia do programa? Digite seu nome abaixo:')))],
            [sg.I(s=(20, 1), k='-NOME-', default_text=sg.user_settings_get_entry('-usuario-', '')),
             sg.B((_('Gravar')), k='-GRAVA-')],
            [sg.Checkbox('Splashscreen', k='-SPLASH-', default=sg.user_settings_get_entry('-splashscreen-', True),
                         enable_events=True)],
            [sg.Push(), sg.B((_('Voltar')), k='-SAIR-')]
        ]
        return sg.Window((_('Sobre...')), layout,
                         finalize=True)

    def janela_cat(self):
        layout = [
            [sg.Text((_('Categorias')), font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.T((_('Categorias existentes: '))), sg.Combo(categorias_ler(), k='-CATEGORIAS-', s=30, readonly=True),
             sg.B((_('Apagar')), k='-APAGA-')],
            [sg.T((_('Cria nova categoria')))],
            [sg.Text((_('Nome da categoria:'))), sg.I(size=30, k='-NOMECAT-')],
            [sg.Push(), sg.B((_('Adicionar')), k='-ADICIONAR-'), sg.B((_('Voltar')), k='-VOLTAR-')]
        ]
        return sg.Window((_('Categorias')), layout,
                         finalize=True)


    def janela_gasto_anual_cat(self):
        tbl_titulos = [(_('Data')), (_('Descrição')), (_('Valor'))]
        tbl_largura = [10, 30, 10]
        layout = [
            [sg.Text((_('Gasto anual por categoria')), font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.T((_('Categoria: '))), sg.Combo(categorias_ler(), k='-CATEGORIAS-', s=30, readonly=True),
             sg.T((_('Ano:'))),
                        sg.Combo(anos, key='-ANO-', default_value=datetime.now().year,
                                 enable_events=True, readonly=True)],
            [sg.Table(values=[], headings=tbl_titulos,
                         # values=le_movimento(datetime.strftime(datetime.now(), '%m/%Y'))
                         col_widths=tbl_largura,
                         # visible_column_map=self.visibilidade,
                         auto_size_columns=False,  # justification='Left',
                         k='-TABELA-',
                         enable_events=True,
                         enable_click_events=True,
                         expand_x=True,
                         expand_y=True,
                         num_rows=16)],
            [sg.Push(), sg.T((_('Total:'))), sg.I(k='-TOTAL-', s=(14, 1))],
            [sg.Push(), sg.B((_('Preencher tabela')), k='-RESULTADO-'),sg.B((_('Voltar')), k='-VOLTAR-')]
        ]
        return sg.Window((_('Gasto anual por categoria')), layout,
                         finalize=True)

    def janela_recebido_anual(self):
        tbl_titulos = [(_('Data')), (_('Descrição')), (_('Valor'))]
        tbl_largura = [10, 30, 10]
        layout = [
            [sg.Text((_('Valor recebido por ano')), font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.T('Ano:'),
                        sg.Combo(anos, key='-ANO-', default_value=datetime.now().year,
                                 enable_events=True, readonly=True)],
            [sg.Table(values=[], headings=tbl_titulos,
                         # values=le_movimento(datetime.strftime(datetime.now(), '%m/%Y'))
                         col_widths=tbl_largura,
                         # visible_column_map=self.visibilidade,
                         auto_size_columns=False,  # justification='Left',
                         k='-TABELA-',
                         enable_events=True,
                         expand_x=True,
                         expand_y=True,
                         num_rows=16)],
            [sg.Push(), sg.T((_('Total:'))), sg.I(k='-TOTAL-', s=(14, 1))],
            [sg.Push(), sg.B((_('Preencher tabela')), k='-RESULTADO-'),sg.B((_('Voltar')), k='-VOLTAR-')]
        ]
        return sg.Window((_('Valor recebido anual')), layout,
                         finalize=True)


    def cria_janela(self):
        global _
        sg.theme(sg.user_settings_get_entry('-tema-', None))
        coluna1_def = sg.Column(
            [[sg.T(_('Data:')), sg.I(default_text=datetime.strftime(datetime.now(), '%d/%m/%Y'), k='-DATAMOV-',
                                  size=10),
              sg.CalendarButton((_('Data')), locale='pt_BR', format='%d/%m/%Y',
                                month_names=meses, day_abbreviations=dias, no_titlebar=False, title='Data'),
              sg.T((_('Tipo:'))),
              # sg.Combo(['Entrada', 'Saída'], default_value='Entrada'),
              sg.Radio((_('Entrada')), group_id='-ENSAI-', k='-ENTRADA-', default=True),
              sg.Radio((_('Saída')), group_id='-ENSAI-', k='-SAIDA-'),
              sg.T((_('Categoria:'))), sg.Combo(categorias_ler(), size=25, k='-CATEGORIA-', readonly=True)],
             [sg.T((_('Descrição:'))), sg.I(size=50, k='-DESCRICAO-'), sg.Push(), sg.T((_('Valor: R$'))),
              sg.I(size=15, k='-VALORMOV-')],
             [sg.B((_('Categorias')), k='-CATEGORIAS-')],
             # disabled=True,
             ])
        coluna3_def = sg.Column([
            [sg.B((_('Adicionar')), k='-ADICIONAR-', bind_return_key=True)],
            [sg.B((_('Atualizar')), k='-ATUALIZAR-', disabled=True)],

            [sg.B((_('Cancelar')), k='-CANCELAR-', disabled=True)]
        ])
        coluna2_def = sg.Column([
            [sg.Checkbox((_('É recorrente?')), k='-RECORRENTE-')],
            [sg.T((_('Dia do mês:'))), sg.I(size=3, k='-DIARECORRENTE-')],
            [sg.T((_('A partir de:'))),
             sg.I(default_text=datetime.strftime(datetime.now(), '%d/%m/%Y'), k='-DATARECORRENTE-', size=10)]
        ])

        # bloco_def = [[coluna1_def], [coluna2_def]
        #             ]

        menu_def = [['&Arquivo', ['Adicionar aluno', 'Imprimir relatório', 'Informações do aluno', '---', '&Sair']],
                    # 'Save::savekey',
                    ['&Editar', ['!Configurações', 'Mudar tema'], ],
                    ['&Relatórios', ['Categorias anual', 'Recebido anual']],
                    ['Gráficos',['Mensal por categorias', 'Anual por categorias']],
                    ['&Ferramentas', ['Backup parcial', 'Backup completo', 'Administração', ['Limpar banco de dados']]],
                    ['A&juda', ['Tela principal', 'Sobre...', 'Erro']], ]

        self.layout = [[sg.Menu(menu_def)],
                       [sg.Image(data=img.logo64),
                        sg.Text((_('Grana! finanças pessoais')), font='_ 25', key='-TITULO-')],
                       [sg.HorizontalSeparator(k='-SEP-')],
                       [sg.T((_('Mês:'))), sg.Combo(meses, key='-MES-',
                                               default_value=mesatual(), enable_events=True, readonly=True),
                        sg.T((_('Ano:'))),
                        sg.Combo(anos, key='-ANO-', default_value=datetime.now().year,
                                 enable_events=True, readonly=True)],
                       [
                        sg.Table(values=[], headings=self.titulos,
                                 # values=le_movimento(datetime.strftime(datetime.now(), '%m/%Y'))
                                 col_widths=self.largura,
                                 visible_column_map=self.visibilidade,
                                 auto_size_columns=False,  # justification='Left',
                                 k='-TABELA-',
                                 enable_events=True,
                                 enable_click_events=True,
                                 expand_x=True,
                                 expand_y=True,
                                 num_rows=16)],
                       [sg.B((_('Alterar registro')), k='-ALTERA-'), sg.B((_('Apagar registro')), k='-APAGA-'),
                        sg.B((_('Gráfico do mês')), k='Mensal por categorias'),
                        sg.Push(), sg.T((_('Saldo:'))),
                        sg.I(
                             size=10, k='-SALDO-')],
                       [sg.Frame((_('Movimento')), [[coluna1_def, coluna2_def, coluna3_def]],
                                 k='-FRAME-')],  # , background_color='#a4a3a1'
                       # s=(800, 100),
                       [sg.Push(), sg.Button((_('Sair')), k='-SAIR-')]]

        return sg.Window('Grana!', self.layout, enable_close_attempted_event=True,
                         location=sg.user_settings_get_entry('-posicao-', (None, None)),
                         finalize=True)

    def __init__(self):
        self.window = self.cria_janela()

    def run(self):
        global _
        if self.atualiza:
            self.window.write_event_value('-ATUALIZA-', '')
            tmp = sg.user_settings_get_entry('-usuario-', '')
            if tmp != '':
                self.window['-TITULO-'].update(value='Grana! finanças pessoais de ' + tmp)
            else:
                self.window['-TITULO-'].update(value=(_('Grana! finanças pessoais')))
            atualiza = False

        while True:
            self.event, self.values = self.window.read()

            # teste do logger de erros
            if self.event == 'Erro':
                try:
                    minha_funcao()
                except Exception as err:
                    logger.error(err, exc_info=True)
                    sg.popup_error('Error', err)
                finally:
                    pass

            if self.event == '-TABELA-':
                self.row = self.values[self.event]
                self.dados = self.window['-TABELA-'].Values

            if self.event == '-ATUALIZA-':
                mes_int = datetime.strptime(self.values['-MES-'], '%B').month
                if mes_int < 10:
                    mes = '0' + str(mes_int)
                else:
                    mes = str(mes_int)
                mesano = mes + '/' + str(self.values['-ANO-'])
                tabelasort = sort_table(movimento_ler(mesano), (1, 0))
                self.window['-TABELA-'].update(values=tabelasort)
                valor_total = locale.currency(movimento_calcula_total(mesano))
                self.window['-SALDO-'].update(value=valor_total)
                self.window['-CATEGORIA-'].update(values=categorias_ler())

            if self.event in ('-MES-', '-ANO-'):
                self.window.write_event_value('-ATUALIZA-', '')

            if self.event == (_('Recebido anual')):

                self.win = self.janela_recebido_anual()
                while True:
                    self.ev, self.val = self.win.read()
                    if self.ev == '-RESULTADO-':
                        tabela = []
                        valortotal = 0.0
                        if self.val['-ANO-'] != '':
                            tabela_tmp = mov_anual_recebido(self.val['-ANO-'])
                            for idx, x in enumerate(tabela_tmp):
                                tabela.append([x[0], x[1], locale.currency(x[2])])
                                valortotal = valortotal + x[2]
                            self.win['-TABELA-'].update(values=tabela)
                            self.win['-TOTAL-'].update(value=locale.currency(valortotal))
                        else:
                            sg.popup('Selecione um ano.')
                    if self.ev in (sg.WINDOW_CLOSED, '-VOLTAR-'):
                        break
                self.win.close()

            if self.event == (_('Categorias anual')):
                self.win = self.janela_gasto_anual_cat()
                while True:
                    self.ev, self.val = self.win.read()
                    if self.ev == '-RESULTADO-':
                        tabela = []
                        valortotal = 0.0
                        if self.val['-CATEGORIAS-'] != '':
                            # print('categoria: ', self.val['-CATEGORIAS-'])
                            tabela_tmp = mov_anual_categoria(self.val['-CATEGORIAS-'], self.val['-ANO-'])
                            for idx, x in enumerate(tabela_tmp):
                                tabela.append([x[0], x[1], locale.currency(x[2])])
                                valortotal = valortotal + x[2]
                            self.win['-TABELA-'].update(values=tabela)
                            self.win['-TOTAL-'].update(value=locale.currency(valortotal))
                        else:
                            sg.popup((_('Selecione uma categoria.')))
                    if self.ev in (sg.WINDOW_CLOSED, '-VOLTAR-'):
                        break
                self.win.close()
                
            if self.event == (_('Mensal por categorias')):
                mes_int = datetime.strptime(self.values['-MES-'], '%B').month
                if mes_int < 10:
                    mes = '0' + str(mes_int)
                else:
                    mes = str(mes_int)
                mesano = mes + '/' + str(self.values['-ANO-'])
                gr.grafico_cat_mensal(mesano)

            if self.event == (_('Anual por categorias')):
                gr.grafico_cat_anual(str(self.values['-ANO-']))

            if self.event == (_('Mudar tema')):
                self.ev, self.vals = sg.Window((_('Escolha o tema')), [
                    [sg.Text(text=('Tema atual: {}'.format(sg.user_settings_get_entry('-tema-'))))],
                    [sg.Combo(sg.theme_list(), readonly=True, k='-THEME LIST-'),
                     sg.OK(button_text=(_('Aceitar'))), sg.Cancel(button_text=(_('Cancelar')))]]).read(
                    close=True)
                if self.ev == (_('Aceitar')):
                    self.window.close()
                    sg.user_settings_set_entry('-tema-', self.vals['-THEME LIST-'])
                    self.window = self.cria_janela()
                    self.window.write_event_value('-ATUALIZA-', '')

            if self.event == '-ADICIONAR-':
                ensai = ''
                if self.values['-ENTRADA-']:
                    ensai = 'Entrada'
                else:
                    ensai = 'Saída'
                 # começa checando os valores por erros
                if self.values['-DATAMOV-'] == '' or not re.fullmatch(regexData, self.values['-DATAMOV-']):
                    sg.popup((_('Campo data inválido.')))
                elif self.values['-CATEGORIA-'] == '':
                    sg.popup((_('Você deve escolher uma categoria.')))
                elif self.values['-DESCRICAO-'] == '':
                    sg.popup((_('Campo descrição não pode estar vazio.')))
                elif self.values['-VALORMOV-'] == '' or not re.fullmatch(regexDinheiro, self.values['-VALORMOV-']):
                    sg.popup((_('Campo valor inválido.')))
                elif self.values['-RECORRENTE-'] and self.values['-DIARECORRENTE-'] == '':
                    sg.popup((_('Se o movimento é recorrente, preencha o campo Dia do mês.')))
                elif self.values['-RECORRENTE-'] and not re.fullmatch(regexData, self.values['-DATARECORRENTE-']):
                    sg.popup((_('A data de início do movimento recorrente está errada.')))
                else:
                    self.ev, self.vals = sg.Window((_('Confirma')), [
                        [sg.Text((_('Deseja gravar este movimento:')))],
                        [sg.Text((_('Data:')), size=self.tam_texto), sg.I(default_text=self.values['-DATAMOV-'], size=10),
                         sg.Push(), sg.Text((_('Tipo:')), size=self.tam_texto), sg.I(default_text=ensai, size=10)],
                        [sg.Text((_('Categoria:')), size=self.tam_texto), sg.I(default_text=self.values['-CATEGORIA-'])],
                        [sg.Text((_('Descrição:')), size=self.tam_texto), sg.I(default_text=self.values['-DESCRICAO-'])],
                        [sg.Text((_('Valor:')), size=self.tam_texto), sg.I(default_text=self.values['-VALORMOV-'], size=12)],
                        [sg.Push(), sg.OK(button_text=(_('Sim'))), sg.Cancel(button_text=(_('Não')))]]).read(
                        close=True)
                    if self.ev == (_('Não')):
                        sg.popup('Operação cancelada.')
                    else:
                        valor = float(self.values['-VALORMOV-'].replace(',', '.'))
                        if not self.values['-RECORRENTE-']:
                            try:
                                movimento_grava(
                                    self.values['-DATAMOV-'],
                                    ensai,
                                    self.values['-CATEGORIA-'],
                                    self.values['-DESCRICAO-'],
                                    valor,
                                    0
                                )
                                sg.popup((_('Movimento gravado com sucesso.')))
                            except Exception as err:
                                logger.error(err, exc_info=True)
                                sg.popup((_('Ocorreu um erro durante a gravação dos dados.')))
                            finally:
                                pass
                        else:
                            try:
                                tmp_data = self.values['-DIARECORRENTE-'] + self.values['-DATARECORRENTE-'][2:]
                                movimento_grava_recorrente(
                                    self.values['-DIARECORRENTE-'],
                                    ensai,
                                    self.values['-CATEGORIA-'],
                                    self.values['-DESCRICAO-'],
                                    valor,
                                    tmp_data
                                )
                                sg.popup((_('Movimento recorrente gravado com sucesso!')))
                            except Exception as err:
                                sg.popup((_('Erro na gravação do movimento.')))
                                logger.error(err, exc_info=True)
                            finally:
                                pass
                            self.window['-DIARECORRENTE-'].update(value='')
                            self.window['-RECORRENTE-'].update(value=False)
                        self.window.write_event_value('-ATUALIZA-', '')
                        self.window['-DATAMOV-'].update(value=datetime.strftime(datetime.now(), '%d/%m/%Y'))
                        self.window['-ENTRADA-'].update(value=True)
                        self.window['-CATEGORIA-'].update(value='')
                        self.window['-DESCRICAO-'].update(value='')
                        self.window['-VALORMOV-'].update(value='')

            # SORT TABLE
            if isinstance(self.event, tuple):
                # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
                if self.event[0] == '-TABELA-':
                    mes_int = datetime.strptime(self.values['-MES-'], '%B').month
                    if mes_int < 10:
                        mes = '0' + str(mes_int)
                    else:
                        mes = str(mes_int)
                    mesano = mes + '/' + str(self.values['-ANO-'])
                    movimento = movimento_ler(mesano)
                    if self.event[2][0] == -1 and self.event[2][1] != -1:  # Header was clicked and wasn't the "row" column
                        col_num_clicked = self.event[2][1] + 1
                        # print('n. da coluna: ', col_num_clicked)
                        new_table = sort_table(movimento, (col_num_clicked, 0))
                        self.window['-TABELA-'].update(new_table)
                        # data = [data[0]] + new_table
            # SORT TABLE

            if self.event == '-ALTERA-':
                if len(self.row) != 0:
                    self.window['-CANCELAR-'].update(disabled=False)
                    self.indice_tmp = self.dados[self.row[0]][0]
                    dados_tmp = movimento_ler_indice(self.indice_tmp)
                    # print(dados_tmp)
                    self.window['-DATAMOV-'].update(value=dados_tmp[0])
                    if dados_tmp[1] == 'Entrada':
                        self.window['-ENTRADA-'].update(value=True)
                    else:
                        self.window['-SAIDA-'].update(value=True)
                    self.window['-CATEGORIA-'].update(value=dados_tmp[2])
                    self.window['-DESCRICAO-'].update(value=dados_tmp[3])
                    self.window['-VALORMOV-'].update(value=dados_tmp[4])
                    if dados_tmp[5] != 0:
                        self.indice_recorrente = dados_tmp[5]
                        self.window['-RECORRENTE-'].update(value=True)
                        dados_recorrente = movimento_ler_recorrente(dados_tmp[5])
                        # print(dados_tmp[5])
                        # print(dados_recorrente)
                        self.window['-DIARECORRENTE-'].update(value=dados_recorrente[0])
                        self.window['-DATARECORRENTE-'].update(value=dados_recorrente[1])
                    self.window['-ATUALIZAR-'].update(disabled=False)
                    self.window['-ADICIONAR-'].update(disabled=True)
                else:
                    sg.popup((_('Selecione um registro da tabela.')))

            if self.event == '-CANCELAR-':
                self.window['-ENTRADA-'].update(value=True)
                self.window['-CATEGORIA-'].update(value='')
                self.window['-DESCRICAO-'].update(value='')
                self.window['-VALORMOV-'].update(value='')
                self.window['-RECORRENTE-'].update(value=False)
                self.window['-DIARECORRENTE-'].update(value='')
                self.window['-DATARECORRENTE-'].update(value=datetime.strftime(datetime.now(), '%d/%m/%Y'))
                self.window['-ATUALIZAR-'].update(disabled=True)
                self.window['-ADICIONAR-'].update(disabled=False)
                self.window['-CANCELAR-'].update(disabled=True)
                self.window['-DATAMOV-'].update(value=datetime.strftime(datetime.now(), '%d/%m/%Y'))

            if self.event == '-ATUALIZAR-':
                ensai = ''
                if self.values['-ENTRADA-']:
                    ensai = 'Entrada'
                else:
                    ensai = 'Saída'
                 # começa checando os valores por erros
                if self.values['-DATAMOV-'] == '' or not re.fullmatch(regexData, self.values['-DATAMOV-']):
                    sg.popup((_('Campo data inválido.')))
                elif self.values['-CATEGORIA-'] == '':
                    sg.popup((_('Você deve escolher uma categoria.')))
                elif self.values['-DESCRICAO-'] == '':
                    sg.popup((_('Campo descrição não pode estar vazio.')))
                elif self.values['-VALORMOV-'] == '' or not re.fullmatch(regexDinheiro, self.values['-VALORMOV-']):
                    sg.popup((_('Campo valor inválido.')))
                elif self.indice_recorrente != 0 and self.values['-DIARECORRENTE-'] == '':
                    sg.popup((_('Dia de recorrência não pode ser vazio.')))
                elif self.indice_recorrente != 0 and not re.fullmatch(regexData, self.values['-DATARECORRENTE-']):
                    sg.popup((_('Data de início da recorrência inválida.')))
                elif self.indice_recorrente != 0 and not self.values['-RECORRENTE-']:
                    sg.popup((_('Atenção: este registro é recorrente. '
                                'Não é possível converter entre tipos de registro.')))
                elif self.indice_recorrente == 0 and self.values['-RECORRENTE-']:
                    sg.popup((_('Atenção: este registro não é recorrente. '
                             'Não é possível converter entre tipos de registro.')))
                else:
                    valor = float(self.values['-VALORMOV-'].replace(',', '.'))
                    if self.indice_recorrente != 0:
                        try:
                            movimento_atualiza_recorrente(
                                self.indice_recorrente,
                                self.values['-DIARECORRENTE-'],
                                ensai,
                                self.values['-CATEGORIA-'],
                                self.values['-DESCRICAO-'],
                                valor,
                                self.values['-DATARECORRENTE-']
                            )
                            sg.popup((_('Movimento atualizado com sucesso.')))
                            self.window['-DIARECORRENTE-'].update(value='')
                            self.window['-RECORRENTE-'].update(value=False)
                        except Exception as err:
                            logger.error(err, exc_info=True)
                            sg.popup((_('Ocorreu um erro durante a gravação dos dados.')))
                        finally:
                            pass
                    else:
                        try:
                            movimento_atualiza(
                                self.indice_tmp,
                                self.values['-DATAMOV-'],
                                ensai,
                                self.values['-CATEGORIA-'],
                                self.values['-DESCRICAO-'],
                                valor
                            )
                            sg.popup((_('Movimento atualizado com sucesso.')))
                        except Exception as err:
                            logger.error(err, exc_info=True)
                            sg.popup((_('Ocorreu um erro durante a gravação dos dados.')))
                        finally:
                            pass
                    self.window.write_event_value('-ATUALIZA-', '')
                    self.window['-ATUALIZAR-'].update(disabled=True)
                    self.window['-ADICIONAR-'].update(disabled=False)
                    self.window['-DATAMOV-'].update(value=datetime.strftime(datetime.now(), '%d/%m/%Y'))
                    self.window['-ENTRADA-'].update(value=True)
                    self.window['-CATEGORIA-'].update(value='')
                    self.window['-DESCRICAO-'].update(value='')
                    self.window['-VALORMOV-'].update(value='')

            if self.event == '-CATEGORIAS-':
                self.win = self.janela_cat()
                while True:
                    self.ev, self.val = self.win.read()

                    if self.ev == '-APAGA-':
                        categoria = self.val['-CATEGORIAS-']
                        opcao, _ = sg.Window((_('Continuar?')), [[sg.T((_('Tem certeza? Os registros não serão apagados.')))],
                                                            [sg.Yes(s=10, button_text=(_('Sim'))),
                                                             sg.No(s=10, button_text=(_('Não')))]],
                                             disable_close=True, modal=True).read(close=True)
                        if opcao == (_('Sim')):
                            categorias_apaga(categoria)
                            sg.popup((_('Categoria excluída com sucesso.')))
                            self.win['-CATEGORIAS-'].update(values=categorias_ler())

                    if self.ev == '-ADICIONAR-':
                        categoria = self.val['-NOMECAT-']
                        categorias_criar(categoria)
                        sg.popup((_('Nova categoria criada com sucesso.')))
                        self.win['-CATEGORIAS-'].update(values=categorias_ler())
                        self.win['-NOMECAT-'].update(value='')

                    if self.ev in (sg.WINDOW_CLOSED, '-VOLTAR-'):
                        self.window.write_event_value('-ATUALIZA-', '')
                        break
                self.win.close()

            if self.event == 'Sobre...':
                self.win = self.janela_sobre()
                while True:
                    self.ev, self.val = self.win.read()

                    if self.ev == '-GRAVA-':
                        if self.val['-NOME-'] != sg.user_settings_get_entry('-usuario-', ''):
                            sg.user_settings_set_entry('-usuario-', self.val['-NOME-'])
                            sg.popup((_('Usuário gravado com sucesso!')))
                            self.window['-TITULO-'].update(value='Grana! finanças pessoais de ' + self.val['-NOME-'])
                        else:
                            sg.popup((_('Campo deve ser diferente do valor anterior.')))
                    if self.ev == '-SPLASH-':
                        if self.val['-SPLASH-']:
                            sg.user_settings_set_entry('-splashscreen-', True)
                        else:
                            sg.user_settings_set_entry('-splashscreen-', False)
                    if self.ev in (sg.WINDOW_CLOSED, '-SAIR-'):
                        break
                self.win.close()

            if self.event == '-APAGA-':
                if len(self.row) != 0:
                    if self.dados[self.row[0]][6] != '':
                        # print('é recorrente!')
                        self.linha_tmp = movimento_ler_recorrente(self.dados[self.row[0]][7])
                        # print(self.dados[self.row[0]][7])
                        # print(self.linha_tmp)
                        self.win = self.janela_recorrente()
                        while True:
                            self.ev, self.val = self.win.read()
                            if self.ev == '-DAQUI-':
                                # print('daqui por diante')
                                try:
                                    movimento_apaga_recorrente(self.dados[self.row[0]][7])
                                    sg.popup((_('Movimento excluído com sucesso.')))
                                    self.window.write_event_value('-ATUALIZA-', '')
                                except Exception as err:
                                    logger.error(err, exc_info=True)
                                    sg.popup((_('Ocorreu um erro durante a exclusão do movimento.')))
                                finally:
                                    break
                            elif self.ev == '-RETRO-':
                                # print('retroativamente')
                                try:
                                    movimento_apaga_recorrente_retro(self.dados[self.row[0]][7])
                                    sg.popup((_('Movimento excluído com sucesso.')))
                                    self.window.write_event_value('-ATUALIZA-', '')
                                except Exception as err:
                                    logger.error(err, exc_info=True)
                                    sg.popup((_('Ocorreu um erro durante a exclusão do movimento.')))
                                finally:
                                    break
                            elif self.ev == '-CANCELA-':
                                sg.popup((_('Operação cancelada.')))
                                break
                        self.win.close()
                    else:
                        # print('self dados self row 0 ', self.dados[self.row[0]])
                        # print('self row ', self.row)
                        # print('self dados', self.dados)
                        self.ev, self.vals = sg.Window((_('Confirma')), [
                            [sg.Text((_('Tem certeza que deseja apagar este lançamento?')))],
                            [sg.Text((_('Data:')), size=self.tam_texto),
                             sg.I(default_text=self.dados[self.row[0]][1], size=10),
                             sg.Push(), sg.Text((_('Tipo:')), size=self.tam_texto),
                             sg.I(default_text=self.dados[self.row[0]][2], size=10)],
                            [sg.Text((_('Categoria:')), size=self.tam_texto), sg.I(default_text=self.dados[self.row[0]][3])],
                            [sg.Text((_('Descrição:')), size=self.tam_texto), sg.I(default_text=self.dados[self.row[0]][4])],
                            [sg.Text((_('Valor:')), size=self.tam_texto),
                             sg.I(default_text=self.dados[self.row[0]][5], size=12)],
                            [sg.Push(), sg.OK(button_text=(_('Sim'))), sg.Cancel(button_text=(_('Não')))]]).read(
                            close=True)
                        if self.ev == (_('Sim')):
                            try:
                                movimento_apaga(self.dados[self.row[0]][0])
                                sg.popup((_('Movimento excluído com sucesso.')))
                                self.window.write_event_value('-ATUALIZA-', '')
                            except Exception as err:
                                logger.error(err, exc_info=True)
                                sg.popup((_('Ocorreu um erro durante a exclusão do movimento.')))
                            finally:
                                pass

            if self.event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, '-SAIR-', (_('Sair'))):
                sg.user_settings_set_entry('-posicao-', self.window.current_location())
                break
        self.window.close()


firstrun = sg.user_settings_get_entry('-firstrun-', True)
if firstrun:
    cria_db()
    sg.user_settings_set_entry('-anoinicial-', datetime.today().year)
    sg.user_settings_set_entry('-firstrun-', False)

try:
    movimento_integra()
except Exception as err:
    logger.error(err, exc_info=True)
    print('Erro na função de integração de recorrentes ', err)
finally:
    pass
splashscreen()
obj_principal = funcao_principal()
obj_principal.run()

