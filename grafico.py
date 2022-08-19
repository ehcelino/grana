import sqlite3
from matplotlib import pyplot as plt
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

arqdb = './db/grana.db'

def mov_lista_cat_mensal(mesano):
    mesano = '%' + mesano + '%'
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT mo_categoria, mo_valor FROM movimento WHERE mo_data LIKE ? AND mo_tipo = "Saída"', (mesano,))
    movimentos = c.fetchall()
    categorias = []
    final = []
    valor = 0.0
    for idx, x in enumerate(movimentos):
        if x[0] not in categorias:
            categorias.append(x[0])
    for idx, x in enumerate(categorias):
        for idy, y in enumerate(movimentos):
            if y[0] == x:
               valor = valor + y[1]
        final.append([x, valor])
        valor = 0.0
    print(final)
    return final

def mov_lista_cat_anual(ano):
    ano = '%' + ano + '%'
    conexao = sqlite3.connect(arqdb)
    c = conexao.cursor()
    c.execute('SELECT mo_categoria, mo_valor FROM movimento WHERE mo_data LIKE ? AND mo_tipo = "Saída"', (ano,))
    movimentos = c.fetchall()
    categorias = []
    final = []
    valor = 0.0
    for idx, x in enumerate(movimentos):
        if x[0] not in categorias:
            categorias.append(x[0])
    for idx, x in enumerate(categorias):
        for idy, y in enumerate(movimentos):
            if y[0] == x:
               valor = valor + y[1]
        final.append([x, valor])
        valor = 0.0
    print(final)
    return final

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def grafico_cat_mensal(mesano):
    lista_tmp = mov_lista_cat_mensal(mesano)
    etiquetas = []
    pedacos = []
    for idx, x in enumerate(lista_tmp):
        etiquetas.append(x[0])
        pedacos.append(x[1])
    # plt.pie(pedacos, labels=etiquetas, shadow=True, wedgeprops={'edgecolor': 'black'}, autopct=f"%0.2f%%")  # , colors=colors
    # plt.title("Gastos mensais por categoria")
    # plt.tight_layout()
    # plt.show()
    fig, ax = plt.subplots()
    ax.pie(pedacos, labels=etiquetas, shadow=True, wedgeprops={'edgecolor': 'black'}, autopct=f"%0.2f%%")
    ax.axis('equal')

    layout = [[sg.Text('Gastos mensais por categoria', font='Helvetica 18')],
              [sg.Canvas(key='-CANVAS-')],
              [sg.Push(), sg.Button('Voltar')]]

    window = sg.Window('Gastos mensais por categoria', layout, location=(10, 10), finalize=True,
                       element_justification='center')
    fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
    event, values = window.read()
    window.close()

def grafico_cat_anual(ano):
    lista_tmp = mov_lista_cat_anual(ano)
    etiquetas = []
    pedacos = []
    for idx, x in enumerate(lista_tmp):
        etiquetas.append(x[0])
        pedacos.append(x[1])
    # plt.pie(pedacos, labels=etiquetas, shadow=True, wedgeprops={'edgecolor': 'black'}, autopct=f"%0.2f%%")  # , colors=colors
    # plt.title("Gastos de {} por categoria".format(ano))
    # plt.tight_layout()
    # plt.show()
    fig, ax = plt.subplots()
    ax.pie(pedacos, labels=etiquetas, shadow=True, wedgeprops={'edgecolor': 'black'}, autopct=f"%0.2f%%")
    ax.axis('equal')

    layout = [[sg.Text("Gastos de {} por categoria".format(ano), font='Helvetica 18')],
              [sg.Canvas(key='-CANVAS-')],
              [sg.Push(), sg.Button('Voltar')]]

    window = sg.Window('Gastos anuais por categoria', layout, location=(10, 10), finalize=True,
                       element_justification='center')

    fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
    event, values = window.read()
    window.close()