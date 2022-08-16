import PySimpleGUI as sg
import locale
from datetime import datetime
import sqlite3
import gettext
import re
import logging
_ = gettext.gettext

logo64 = b'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'

# #############################################
# GRANA! gerenciador de finanças pessoais
#
# - criar lista de anos com uma função
# - Comparar se ja existe registro igual no banco
# #############################################

meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
         'Outubro', 'Novembro', 'Dezembro']
dias = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']
ano_inicio = sg.user_settings_get_entry('-anoinicial-', datetime.today().year)
ano_agora = datetime.today().year
anos = list(range(ano_inicio, ano_agora + 6, +1))

arqdb = './db/grana.db'

logging.basicConfig(filename='errorlog.txt', level=logging.DEBUG,
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

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
        logger.error(err)
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
        temp = [x[0], x[1], x[2], x[3], x[4], locale.currency(x[5]), tmp_rec, x[6]]
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
    dados = [dia, tipo, categoria, descricao, valor, datainicio]
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'INSERT INTO recorrente(re_dia, re_tipo, re_categoria, ' \
              're_descricao, re_valor, re_data_inicio) VALUES (?, ?, ?, ?, ?, ?)'
    c.execute(comando, dados)
    conexao.commit()
    indice_recorrente = c.lastrowid
    data_insercao = str(dia) + datainicio[2:]
    comando = 'SELECT mo_relrec FROM movimento WHERE mo_data LIKE ?'
    c.execute(comando, (data_insercao,))
    resultado = c.fetchone()
    if resultado == None:
        movimento_grava(data_insercao, tipo, categoria, descricao, valor, indice_recorrente)
    conexao.close()

def movimento_integra():
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    comando = 'SELECT re_index'

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

def categorias_ler():
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT ca_categoria FROM categoria')
    resultado = c.fetchall()
    resultado_list = []
    for idx, x in enumerate(resultado):
        resultado_list.append(''.join(x))
    print(resultado)
    print(resultado_list)
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


class categorias():
    lista = []

    def janela_cat(self):
        layout = [
            [sg.Text('Categorias', font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.T('Categorias existentes: '), sg.Combo(categorias_ler(), k='-CATEGORIAS-', s=30, readonly=True),
             sg.B('Apagar', k='-APAGA-')],
            [sg.T('Cria nova categoria')],
            [sg.Text('Nome da categoria:'), sg.I(size=30, k='-NOMECAT-')],
            [sg.Push(), sg.B('Adicionar', k='-ADICIONAR-'), sg.B('Voltar', k='-VOLTAR-')]
        ]
        return sg.Window('Categorias', layout,
                         finalize=True)

    def __init__(self):
        self.window = self.janela_cat()

    def run(self):
        while True:
            # self.window['-CATEGORIAS-'].update
            self.event, self.values = self.window.read()

            if self.event == '-APAGA-':
                categoria = self.values['-CATEGORIAS-']
                opcao, _ = sg.Window('Continuar?', [[sg.T('Tem certeza? Os registros não serão apagados.')],
                                                    [sg.Yes(s=10, button_text='Sim'), sg.No(s=10, button_text='Não')]],
                                     disable_close=True, modal=True).read(close=True)
                if opcao == 'Sim':
                    categorias_apaga(categoria)
                    sg.popup('Categoria excluída com sucesso.')
                    self.window['-CATEGORIAS-'].update(values=categorias_ler())

            if self.event == '-ADICIONAR-':
                categoria = self.values['-NOMECAT-']
                categorias_criar(categoria)
                sg.popup('Nova categoria criada com sucesso.')
                self.window['-CATEGORIAS-'].update(values=categorias_ler())
                self.window['-NOMECAT-'].update(value='')

            if self.event in (sg.WINDOW_CLOSED, '-VOLTAR-'):
                break
        self.window.close()

class funcao_principal:
    titulos = ['Indice', 'Data', 'Tipo', 'Categoria', 'Descrição', 'Valor', 'R', 'Indice recorrente']
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
            [sg.Text('Você está prestes a apagar um lançamento recorrente.')],
            [sg.Text('Este lançamento começou a partir de {}.'.format(self.linha_tmp[1]))],
            [sg.Text('Você deseja apagá-lo daqui por diante ou retroativamente?')],
            [sg.Push(), sg.B('Daqui por diante', k='-DAQUI-'), sg.B('Retroativamente', k='-RETRO-'),
             sg.B('Cancelar', k='-CANCELA-')]
        ]
        return sg.Window('Apagar', layout,
                         finalize=True)

    def janela_sobre(self):
        layout = [
            [sg.Text('Categorias', font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.Text('A fazer...')],
            [sg.Text('Quer personalizar sua cópia do programa? Digite seu nome abaixo:')],
            [sg.I(s=(20, 1), k='-NOME-', default_text=sg.user_settings_get_entry('-usuario-', '')),
             sg.B('Gravar', k='-GRAVA-')],
            [sg.Push(), sg.B('Voltar', k='-SAIR-')]
        ]
        return sg.Window('Sobre...', layout,
                         finalize=True)

    def janela_cat(self):
        layout = [
            [sg.Text('Categorias', font='_ 25')],
            [sg.HorizontalSeparator(k='-SEP-')],
            [sg.T('Categorias existentes: '), sg.Combo(categorias_ler(), k='-CATEGORIAS-', s=30, readonly=True),
             sg.B('Apagar', k='-APAGA-')],
            [sg.T('Cria nova categoria')],
            [sg.Text('Nome da categoria:'), sg.I(size=30, k='-NOMECAT-')],
            [sg.Push(), sg.B('Adicionar', k='-ADICIONAR-'), sg.B('Voltar', k='-VOLTAR-')]
        ]
        return sg.Window('Categorias', layout,
                         finalize=True)


    def cria_janela(self):
        sg.theme(sg.user_settings_get_entry('-tema-', None))
        coluna1_def = sg.Column(
            [[sg.T(_('Data:')), sg.I(default_text=datetime.strftime(datetime.now(), '%d/%m/%Y'), k='-DATAMOV-',
                                  size=10),
              sg.CalendarButton((_('Data')), locale='pt_BR', format='%d/%m/%Y',
                                month_names=meses, day_abbreviations=dias, no_titlebar=False, title='Data'),
              sg.T('Tipo:'),
              # sg.Combo(['Entrada', 'Saída'], default_value='Entrada'),
              sg.Radio((_('Entrada')), group_id='-ENSAI-', k='-ENTRADA-', default=True),
              sg.Radio((_('Saída')), group_id='-ENSAI-', k='-SAIDA-'),
              sg.T((_('Categoria:'))), sg.Combo(categorias_ler(), size=25, k='-CATEGORIA-', readonly=True)],
             [sg.T((_('Descrição:'))), sg.I(size=50, k='-DESCRICAO-'), sg.Push(), sg.T((_('Valor: R$'))),
              sg.I(size=15, k='-VALORMOV-')]
             # disabled=True,
             ])
        coluna3_def = sg.Column([
            [sg.B((_('Adicionar')), k='-ADICIONAR-', bind_return_key=True)],
            [sg.B((_('Atualizar')), k='-ATUALIZAR-', disabled=True)],
            [sg.B('Categorias', k='-CATEGORIAS-')],
            [sg.B('Cancelar', k='-CANCELAR-', disabled=True)]
        ])
        coluna2_def = sg.Column([
            [sg.Checkbox((_('É recorrente?')), k='-RECORRENTE-')],
            [sg.T('Dia do mês:'), sg.I(size=3, k='-DIARECORRENTE-')],
            [sg.T('A partir de:'),
             sg.I(default_text=datetime.strftime(datetime.now(), '%d/%m/%Y'), k='-DATARECORRENTE-', size=10)]
        ])

        # bloco_def = [[coluna1_def], [coluna2_def]
        #             ]

        menu_def = [['&Arquivo', ['Adicionar aluno', 'Imprimir relatório', 'Informações do aluno', '---', '&Sair']],
                    # 'Save::savekey',
                    ['&Editar', ['!Configurações', 'Mudar tema'], ],
                    ['&Relatórios', ['Relatório mensal', 'Devedores']],
                    ['&Ferramentas', ['Backup parcial', 'Backup completo', 'Administração', ['Limpar banco de dados']]],
                    ['A&juda', ['Tela principal', 'Sobre...']], ]

        self.layout = [[sg.Menu(menu_def)],
                       [sg.Image(data=logo64),
                        sg.Text('Grana! finanças pessoais', font='_ 25', key='-TITULO-')],
                       [sg.HorizontalSeparator(k='-SEP-')],
                       [sg.T('Mês:'), sg.Combo(meses, key='-MES-',
                                               default_value=mesatual(), enable_events=True, readonly=True),
                        sg.T('Ano:'),
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
                                 expand_x=True,
                                 expand_y=True,
                                 num_rows=16)],
                       [sg.B('Alterar registro', k='-ALTERA-'), sg.B('Apagar registro', k='-APAGA-'),
                        sg.B('Gerar relatório em PDF', k='-RELPDF-'),
                        sg.Push(), sg.T('Saldo:'),
                        sg.I(
                             size=10, k='-SALDO-')],
                       [sg.Frame('Movimento', [[coluna1_def, coluna2_def, coluna3_def]], k='-FRAME-')],
                       # s=(800, 100),
                       [sg.Push(), sg.Button('Sair', k='-SAIR-')]]

        return sg.Window('Grana!', self.layout, enable_close_attempted_event=True,
                         location=sg.user_settings_get_entry('-posicao-', (None, None)),
                         finalize=True)

    def __init__(self):
        self.window = self.cria_janela()

    def run(self):
        if self.atualiza:
            self.window.write_event_value('-ATUALIZA-', '')
            tmp = sg.user_settings_get_entry('-usuario-', '')
            if tmp != '':
                self.window['-TITULO-'].update(value='Grana! finanças pessoais de ' + tmp)
            else:
                self.window['-TITULO-'].update(value='Grana! finanças pessoais')
            atualiza = False

        while True:
            self.event, self.values = self.window.read()

            if self.event == '-TABELA-':
                self.row = self.values[self.event]
                self.dados = self.window['-TABELA-'].Values

            if self.event == 'Mudar tema':
                self.ev, self.vals = sg.Window('Choose Theme', [
                    [sg.Combo(sg.theme_list(), readonly=True, k='-THEME LIST-'), sg.OK(), sg.Cancel()]]).read(
                    close=True)
                if self.ev == 'OK':
                    self.window.close()
                    sg.user_settings_set_entry('-tema-', self.vals['-THEME LIST-'])
                    self.window = self.cria_janela()

            if self.event == '-ADICIONAR-':
                ensai = ''
                if self.values['-ENTRADA-']:
                    ensai = 'Entrada'
                else:
                    ensai = 'Saída'
                 # começa checando os valores por erros
                if self.values['-DATAMOV-'] == '' or not re.fullmatch(regexData, self.values['-DATAMOV-']):
                    sg.popup('Campo data inválido.')
                elif self.values['-CATEGORIA-'] == '':
                    sg.popup('Você deve escolher uma categoria.')
                elif self.values['-DESCRICAO-'] == '':
                    sg.popup('Campo descrição não pode estar vazio.')
                elif self.values['-VALORMOV-'] == '' or not re.fullmatch(regexDinheiro, self.values['-VALORMOV-']):
                    sg.popup('Campo valor inválido.')
                elif self.values['-RECORRENTE-'] and self.values['-DIARECORRENTE-'] == '':
                    sg.popup('Se o movimento é recorrente, preencha o campo Dia do mês.')
                elif self.values['-RECORRENTE-'] and not re.fullmatch(regexData, self.values['-DATARECORRENTE-']):
                    sg.popup('A data de início do movimento recorrente está errada.')
                else:
                    self.ev, self.vals = sg.Window('Confirma', [
                        [sg.Text('Deseja gravar este movimento:')],
                        [sg.Text('Data:', size=self.tam_texto), sg.I(default_text=self.values['-DATAMOV-'], size=10),
                         sg.Push(), sg.Text('Tipo:', size=self.tam_texto), sg.I(default_text=ensai, size=10)],
                        [sg.Text('Categoria:', size=self.tam_texto), sg.I(default_text=self.values['-CATEGORIA-'])],
                        [sg.Text('Descrição:', size=self.tam_texto), sg.I(default_text=self.values['-DESCRICAO-'])],
                        [sg.Text('Valor:', size=self.tam_texto), sg.I(default_text=self.values['-VALORMOV-'], size=12)],
                        [sg.Push(), sg.OK(button_text='Sim'), sg.Cancel(button_text='Não')]]).read(
                        close=True)
                    if self.ev == 'Não':
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
                                sg.popup('Movimento gravado com sucesso.')
                            except Exception as err:
                                logger.error(err)
                                sg.popup('Ocorreu um erro durante a gravação dos dados.')
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
                                sg.popup('Movimento recorrente gravado com sucesso!')
                            except Exception as err:
                                sg.popup('Erro na gravação do movimento.')
                                logger.error(err)
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

            if self.event == '-ATUALIZA-':
                mes_int = datetime.strptime(self.values['-MES-'], '%B').month
                if mes_int < 10:
                    mes = '0' + str(mes_int)
                else:
                    mes = str(mes_int)
                mesano = mes + '/' + str(self.values['-ANO-'])
                self.window['-TABELA-'].update(values=movimento_ler(mesano))
                valor_total = locale.currency(movimento_calcula_total(mesano))
                self.window['-SALDO-'].update(value=valor_total)
                self.window['-CATEGORIA-'].update(values=categorias_ler())

            if self.event == '-ALTERA-':
                if len(self.row) != 0:
                    self.window['-CANCELAR-'].update(disabled=False)
                    self.indice_tmp = self.dados[self.row[0]][0]
                    dados_tmp = movimento_ler_indice(self.indice_tmp)
                    print(dados_tmp)
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
                        print(dados_tmp[5])
                        print(dados_recorrente)
                        self.window['-DIARECORRENTE-'].update(value=dados_recorrente[0])
                        self.window['-DATARECORRENTE-'].update(value=dados_recorrente[1])
                    self.window['-ATUALIZAR-'].update(disabled=False)
                    self.window['-ADICIONAR-'].update(disabled=True)
                else:
                    sg.popup('Selecione um registro da tabela.')

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
                    sg.popup('Campo data inválido.')
                elif self.values['-CATEGORIA-'] == '':
                    sg.popup('Você deve escolher uma categoria.')
                elif self.values['-DESCRICAO-'] == '':
                    sg.popup('Campo descrição não pode estar vazio.')
                elif self.values['-VALORMOV-'] == '' or not re.fullmatch(regexDinheiro, self.values['-VALORMOV-']):
                    sg.popup('Campo valor inválido.')
                elif self.indice_recorrente != 0 and self.values['-DIARECORRENTE-'] == '':
                    sg.popup('Dia de recorrência não pode ser vazio.')
                elif self.indice_recorrente != 0 and not re.fullmatch(regexData, self.values['-DATARECORRENTE-']):
                    sg.popup('Data de início da recorrência inválida.')
                elif self.indice_recorrente != 0 and not self.values['-RECORRENTE-']:
                    sg.popup('Atenção: este registro é recorrente. Não é possível converter entre tipos de registro.')
                elif self.indice_recorrente == 0 and self.values['-RECORRENTE-']:
                    sg.popup('Atenção: este registro não é recorrente. '
                             'Não é possível converter entre tipos de registro.')
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
                            sg.popup('Movimento atualizado com sucesso.')
                            self.window['-DIARECORRENTE-'].update(value='')
                            self.window['-RECORRENTE-'].update(value=False)
                        except Exception as err:
                            logger.error(err)
                            sg.popup('Ocorreu um erro durante a gravação dos dados.')
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
                            sg.popup('Movimento atualizado com sucesso.')
                        except Exception as err:
                            logger.error(err)
                            sg.popup('Ocorreu um erro durante a gravação dos dados.')
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
                        opcao, _ = sg.Window('Continuar?', [[sg.T('Tem certeza? Os registros não serão apagados.')],
                                                            [sg.Yes(s=10, button_text='Sim'),
                                                             sg.No(s=10, button_text='Não')]],
                                             disable_close=True, modal=True).read(close=True)
                        if opcao == 'Sim':
                            categorias_apaga(categoria)
                            sg.popup('Categoria excluída com sucesso.')
                            self.win['-CATEGORIAS-'].update(values=categorias_ler())

                    if self.ev == '-ADICIONAR-':
                        categoria = self.val['-NOMECAT-']
                        categorias_criar(categoria)
                        sg.popup('Nova categoria criada com sucesso.')
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
                        if self.val['-NOME-'] != '' and \
                                self.val['-NOME-'] != sg.user_settings_get_entry('-usuario-', ''):
                            sg.user_settings_set_entry('-usuario-', self.val['-NOME-'])
                            sg.popup('Usuário gravado com sucesso!')
                            self.window['-TITULO-'].update(value='Grana! finanças pessoais de ' + self.val['-NOME-'])
                        else:
                            sg.popup('Campo não pode ser vazio, e deve ser diferente do valor anterior.')
                    if self.ev in (sg.WINDOW_CLOSED, '-SAIR-'):
                        break
                self.win.close()

            if self.event == '-APAGA-':
                if len(self.row) != 0:
                    if self.dados[self.row[0]][6] != '':
                        print('é recorrente!')
                        self.linha_tmp = movimento_ler_recorrente(self.dados[self.row[0]][7])
                        print(self.dados[self.row[0]][7])
                        print(self.linha_tmp)
                        self.win = self.janela_recorrente()
                        while True:
                            self.ev, self.val = self.win.read()
                            if self.ev == '-DAQUI-':
                                print('daqui por diante')
                                try:
                                    movimento_apaga_recorrente(self.dados[self.row[0]][7])
                                    sg.popup('Movimento excluído com sucesso.')
                                    self.window.write_event_value('-ATUALIZA-', '')
                                except Exception as err:
                                    logger.error(err)
                                    sg.popup('Ocorreu um erro durante a exclusão do movimento.')
                                finally:
                                    break
                            elif self.ev == '-RETRO-':
                                print('retroativamente')
                                try:
                                    movimento_apaga_recorrente_retro(self.dados[self.row[0]][7])
                                    sg.popup('Movimento excluído com sucesso.')
                                    self.window.write_event_value('-ATUALIZA-', '')
                                except Exception as err:
                                    logger.error(err)
                                    sg.popup('Ocorreu um erro durante a exclusão do movimento.')
                                finally:
                                    break
                            elif self.ev == '-CANCELA-':
                                sg.popup('Operação cancelada.')
                                break
                        self.win.close()
                    else:
                        print('self dados self row 0 ', self.dados[self.row[0]])
                        print('self row ', self.row)
                        print('self dados', self.dados)
                        self.ev, self.vals = sg.Window('Confirma', [
                            [sg.Text('Tem certeza que deseja apagar este lançamento?')],
                            [sg.Text('Data:', size=self.tam_texto),
                             sg.I(default_text=self.dados[self.row[0]][1], size=10),
                             sg.Push(), sg.Text('Tipo:', size=self.tam_texto),
                             sg.I(default_text=self.dados[self.row[0]][2], size=10)],
                            [sg.Text('Categoria:', size=self.tam_texto), sg.I(default_text=self.dados[self.row[0]][3])],
                            [sg.Text('Descrição:', size=self.tam_texto), sg.I(default_text=self.dados[self.row[0]][4])],
                            [sg.Text('Valor:', size=self.tam_texto),
                             sg.I(default_text=self.dados[self.row[0]][5], size=12)],
                            [sg.Push(), sg.OK(button_text='Sim'), sg.Cancel(button_text='Não')]]).read(
                            close=True)
                        if self.ev == 'Sim':
                            try:
                                movimento_apaga(self.dados[self.row[0]][0])
                                sg.popup('Movimento excluído com sucesso.')
                                self.window.write_event_value('-ATUALIZA-', '')
                            except Exception as err:
                                logger.error(err)
                                sg.popup('Ocorreu um erro durante a exclusão do movimento.')
                            finally:
                                pass

            if self.event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT, '-SAIR-', 'Sair'):
                sg.user_settings_set_entry('-posicao-', self.window.current_location())
                break
        self.window.close()

firstrun = sg.user_settings_get_entry('-firstrun-', True)
if firstrun:
    cria_db()
    sg.user_settings_set_entry('-anoinicial-', datetime.today().year)
    sg.user_settings_set_entry('-firstrun-', False)

obj_principal = funcao_principal()
obj_principal.run()