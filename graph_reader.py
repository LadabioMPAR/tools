import tkinter as tk
from tkinter import filedialog, simpledialog
import matplotlib.pyplot as plt
import cv2
import pandas as pd


# Função para selecionar a imagem através de uma interface gráfica
def select_image():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter
    file_path = filedialog.askopenfilename(title="Selecione a Imagem do Gráfico",
                                           filetypes=[("Imagem PNG", "*.png"), ("Imagem JPEG", "*.jpg")])
    return file_path


# Função para exibir a imagem e coletar pontos para o eixo (X ou Y)
def select_axis_points(axis_name, graph_image_rgb):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(graph_image_rgb)
    ax.set_title(f"Selecione os pontos para o eixo {axis_name} e pressione Enter ao terminar")

    # Coletar dois pontos: um para o início e outro para o fim do eixo
    points = plt.ginput(n=2, timeout=0)  # n=2 para selecionar dois pontos
    plt.close()  # Fecha a janela após coletar os pontos

    # Mostrar as coordenadas dos pontos selecionados
    print(f"Pontos selecionados para o eixo {axis_name} (coordenadas x, y):")
    for idx, point in enumerate(points, start=1):
        print(f"Ponto {idx}: {point}")

    return points


# Função para criar a interface gráfica para os valores dos eixos e seus nomes
def get_axis_values_from_user(axis_name):
    def submit(event=None):
        # Função chamada ao clicar em "Confirmar" ou pressionar Enter
        global axis_start, axis_end, axis_label
        axis_start = float(entry_start.get())
        axis_end = float(entry_end.get())
        axis_label = entry_label.get()
        root.quit()  # Fecha a janela após confirmar os valores
        root.destroy()  # Fecha a janela de forma definitiva

    # Criar a janela de entrada com Tkinter
    root = tk.Tk()
    root.title(f"Definir valores e nome do eixo {axis_name}")

    label_start = tk.Label(root, text=f"Início do eixo {axis_name}:")
    label_start.pack(pady=5)
    entry_start = tk.Entry(root)
    entry_start.pack(pady=5)

    label_end = tk.Label(root, text=f"Fim do eixo {axis_name}:")
    label_end.pack(pady=5)
    entry_end = tk.Entry(root)
    entry_end.pack(pady=5)

    label_name = tk.Label(root, text=f"Nome do eixo {axis_name}:")
    label_name.pack(pady=5)
    entry_label = tk.Entry(root)
    entry_label.pack(pady=5)

    submit_button = tk.Button(root, text="Confirmar", command=submit)
    submit_button.pack(pady=10)

    root.bind("<Return>", submit)  # Permite confirmar com Enter
    root.mainloop()  # Exibe a janela e aguarda a interação do usuário


# Função para definir e salvar os dados experimentais
def process_graph():
    # Seleção da imagem
    image_path = select_image()
    graph_image = cv2.imread(image_path)

    # Converter de BGR para RGB para visualização com Matplotlib
    graph_image_rgb = cv2.cvtColor(graph_image, cv2.COLOR_BGR2RGB)

    # Coletar os pontos dos eixos X e Y
    axis_x_points = select_axis_points("X", graph_image_rgb)
    axis_y_points = select_axis_points("Y", graph_image_rgb)

    # Usar os pontos selecionados para definir os limites dos eixos
    x_start, x_end = axis_x_points[0][0], axis_x_points[1][0]
    y_start, y_end = axis_y_points[0][1], axis_y_points[1][1]

    # Definir valores dos eixos X e Y (início, fim e nome) com a interface gráfica
    get_axis_values_from_user("X")
    x_start, x_end, x_label = axis_start, axis_end, axis_label

    get_axis_values_from_user("Y")
    y_start, y_end, y_label = axis_start, axis_end, axis_label

    # Agora, vamos definir a quantidade de conjuntos de dados
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter
    num_datasets = tk.simpledialog.askinteger("Número de Conjuntos", "Quantos conjuntos de dados você deseja extrair?",
                                              minvalue=1)

    all_selected_points = []

    for i in range(num_datasets):
        # Reabrir o gráfico para selecionar pontos para cada conjunto de dados
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(graph_image_rgb)
        ax.set_title(f"Selecione os pontos para o conjunto de dados {i + 1} e pressione Enter ao terminar")

        points = plt.ginput(n=-1, timeout=0)  # Seleção de pontos
        plt.close()  # Fecha a janela após coletar os pontos

        # Armazenar os pontos selecionados no conjunto
        x_values = []
        y_values = []

        for point in points:
            x_pixel, y_pixel = point
            # Extrapolar os pontos para valores reais baseados nos eixos definidos
            x_value = x_start + (x_end - x_start) * (x_pixel - axis_x_points[0][0]) / (
                        axis_x_points[1][0] - axis_x_points[0][0])
            y_value = y_start + (y_end - y_start) * (y_pixel - axis_y_points[0][1]) / (
                        axis_y_points[1][1] - axis_y_points[0][1])
            x_values.append(x_value)
            y_values.append(y_value)

        # Coletar o nome do conjunto de dados
        dataset_name = tk.simpledialog.askstring("Nome do Conjunto de Dados", f"Nome do Conjunto de Dados {i + 1}")

        # Salvar o conjunto de dados em um arquivo CSV separado
        data_to_save = pd.DataFrame({'X': x_values, 'Y': y_values})
        dataset_filename = f"{dataset_name}.csv"
        data_to_save.to_csv(dataset_filename, index=False)
        print(f"Conjunto de dados {dataset_name} salvo em {dataset_filename}")

        # Armazenar os dados para possíveis usos futuros
        all_selected_points.append({
            'dataset': dataset_name,
            'x_values': x_values,
            'y_values': y_values
        })

        # Gerar o gráfico com os dados selecionados
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x_values, y_values, color='blue', label=f'{dataset_name}')
        ax.set_title(f"{dataset_name}")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        # Definir os limites dos eixos de acordo com os valores selecionados
        ax.set_xlim(0, 1.1 * max(x_values))
        ax.set_ylim(0, 1.1 * max(y_values))

        # Mostrar o gráfico
        plt.legend()
        plt.draw()

        # Fechar o gráfico após pressionar Enter
        def close_on_enter(event):
            plt.close(fig)

        fig.canvas.mpl_connect('key_press_event', close_on_enter)
        plt.show()

    print("Processo concluído!")


# Executar o processo
process_graph()
