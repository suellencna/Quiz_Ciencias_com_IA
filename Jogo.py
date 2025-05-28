import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import google.generativeai as genai
import random
import unicodedata
import re
import sys

# Importa a biblioteca Pillow para manipulação de imagens.
# Certifique-se de que está instalada: pip install Pillow
from PIL import Image, ImageTk

# --- A FUNÇÃO resource_path DEVE VIR AQUI, LOGO APÓS OS IMPORTS ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# --- FIM DA FUNÇÃO resource_path ---


# --- Configuração de Estilos e Aparência da GUI ---
def configurar_estilos():
    """
    Configura os estilos visuais para os widgets ttk (Tema, Fontes, Cores).
    Isso padroniza a aparência dos elementos da interface.
    """
    style = ttk.Style()

    # Define o tema base da janela. 'vista' é um bom ponto de partida no Windows.
    # Experimente outros como 'clam', 'alt', 'default', 'xpnative', 'winnative'
    style.theme_use('winnative')

    # Vamos tentar definir um fundo para os labels para eles não usarem o cinza padrão do winnative
    # Assumindo que seu background2.JPG é predominantemente claro, podemos tentar 'white' ou um tom pastel.
    # Se o fundo for escuro, mude para uma cor que contraste.
    fundo_para_labels = '#F0F0F0' # Um cinza bem clarinho, quase branco. Ajuste se necessário.

    # Estilos para Labels (rótulos de texto)
    # Define a fonte e cor padrão para todos os TLabel
    style.configure('TLabel', font=('Arial', 14), foreground='#333333', background=fundo_para_labels)
    # Estilo específico para o título principal
    style.configure('Titulo.TLabel', font=('Arial', 24, 'bold'), foreground='#0055AA', background=fundo_para_labels)
    # Estilo para o texto do robô na tela inicial
    style.configure('RoboFala.TLabel', font=('Arial', 16, 'italic'), foreground='#555555', background=fundo_para_labels)
    # Estilo para o texto da pergunta
    style.configure('Pergunta.TLabel', font=('Arial', 18, 'bold'), foreground='#333333', background=fundo_para_labels)
    # Estilo para mensagens de feedback positivo
    style.configure('Feedback.TLabel', font=('Arial', 16, 'bold'), foreground='#008000', background=fundo_para_labels)
    # Estilo para mensagens de erro
    style.configure('Erro.TLabel', font=('Arial', 16, 'bold'), foreground='#FF0000', background=fundo_para_labels)
    # Estilo para o texto da dica
    style.configure('Dica.TLabel', font=('Arial', 16, 'italic'), foreground='#777777', background=fundo_para_labels)
    # Estilo para a explicação da resposta correta
    style.configure('Resposta.TLabel', font=('Arial', 16), foreground='#000000', background=fundo_para_labels)
    # Novo estilo para o texto das alternativas dentro do Radiobutton
    style.configure('Alternativa.TLabel', font=('Arial', 14), foreground='#444444', background=fundo_para_labels)

    # Estilos para Botões
    # Define a fonte, cor de fundo, cor do texto, relevo e padding para todos os TButton
    style.configure('TButton', font=('Arial', 14, 'bold'), background='#007BFF', foreground='#145da0', relief='flat',
                    padding=10)

    # Mapeia a cor de fundo e do texto quando o botão está ativo (mouse sobre ele)
    style.map('TButton',
              background=[('active', '#0056b3')],
              foreground=[('active', '#43b0f1')])

    # Estilos para Radiobuttons (apenas para o círculo e o valor, não o texto completo)
    #style.configure('TRadiobutton',
    #                foreground='#444444')  # Cor do texto do radiobutton (se houver, mas usaremos um label separado)

    style.configure('TRadiobutton', foreground='#444444', background=fundo_para_labels) # Adicionar background aqui também
    style.map('TRadiobutton',
              background=[('active', '#DDDDDD')])


    # IMPORTANTE: Adicione um estilo para TFrame, pois você os usa para agrupar botões/alternativas
    style.configure('TFrame', background=fundo_para_labels) # Garante que frames também tenham um fundo claro

# --- Configuração da Janela Principal do Quiz ---
janela = tk.Tk()
janela.title("QUIZ DE CIÊNCIAS DIVERTIDO")  # Título da janela em maiúsculas

# Chama a função para aplicar os estilos visuais
configurar_estilos()

# Define o tamanho fixo da janela e impede redimensionamento pelo usuário
janela.geometry("1024x1024")
janela.resizable(False, False)


# Função para centralizar a janela na tela
def centralizar_janela(janela, largura, altura):
    """
    Centraliza a janela Tkinter na tela do usuário.
    """
    screen_width = janela.winfo_screenwidth()
    screen_height = janela.winfo_screenheight()
    x = (screen_width / 2) - (largura / 2)
    y = (screen_height / 2) - (altura / 2)
    janela.geometry(f'{largura}x{altura}+{int(x)}+{int(y)}')


# Centraliza a janela logo após configurá-la
centralizar_janela(janela, 1024, 1024)

# --- Variáveis Globais para Imagem de Fundo ---
# Referência para a imagem de fundo para evitar que seja coletada pelo garbage collector
background_image_tk = None
canvas_background = None


def configurar_imagem_fundo(janela, image_path):
    """
    Configura uma imagem como fundo da janela Tkinter usando um Canvas.
    Todos os outros widgets precisarão ser criados com master=canvas_background
    e usando .place() ou .grid() para posicionamento no canvas.
    """
    global background_image_tk, canvas_background

    # Destroi o canvas anterior se existir, para evitar sobreposição
    if canvas_background:
        canvas_background.destroy()

    canvas_background = tk.Canvas(janela, width=janela.winfo_width(), height=janela.winfo_height())
    canvas_background.pack(fill="both", expand=True)

    try:
        # Carrega a imagem e redimensiona para o tamanho da janela
        img_pil = Image.open(image_path)
        img_pil = img_pil.resize((janela.winfo_width(), janela.winfo_height()), Image.LANCZOS)
        background_image_tk = ImageTk.PhotoImage(img_pil)

        # Adiciona a imagem ao canvas
        canvas_background.create_image(0, 0, image=background_image_tk, anchor="nw")
        canvas_background.image = background_image_tk  # Manter referência
    except FileNotFoundError:
        print(f"ATENÇÃO: Imagem de fundo '{image_path}' não encontrada. Continuando sem imagem de fundo.")
        # Opcional: define uma cor de fundo sólida se a imagem não for encontrada
        canvas_background.configure(bg='#CCE5FF')  # Um azul claro

    except Exception as e:
        print(f"ATENÇÃO: Erro ao carregar imagem de fundo '{image_path}': {e}. Continuando sem imagem de fundo.")
        canvas_background.configure(bg='#CCE5FF')  # Um azul claro


# --- Configuração da API Key e Modelo Gemini ---

# A melhor prática é carregar a API Key de uma variável de ambiente do sistema.
# No Windows, defina a variável de ambiente GOOGLE_API_KEY com sua chave.
api_key = os.getenv('GOOGLE_API_KEY')

# Verifica se a API Key foi definida. Caso contrário, exibe um erro e encerra o programa.
if not api_key:
    print(
        "ERRO: A VARIÁVEL DE AMBIENTE GOOGLE_API_KEY NÃO ESTÁ DEFINIDA OU A CHAVE NÃO FOI INSERIDA NO CÓDIGO.".upper())
    print(
        "POR FAVOR, DEFINA A VARIÁVEL DE AMBIENTE 'GOOGLE_API_KEY' OU INSIRA SUA CHAVE DIRETAMENTE NO CÓDIGO PARA TESTES.".upper())
    sys.exit()

# Tenta configurar a biblioteca genai com a API Key. Em caso de falha, exibe erro e encerra.
try:
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"ERRO AO CONFIGURAR A BIBLIOTECA GENAI COM A API KEY: {e}".upper())
    sys.exit()

# Tenta inicializar o modelo Gemini. 'gemini-2.0-flash' é um modelo rápido e eficiente.
# Em caso de falha, exibe erro e encerra.
try:
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except Exception as e:
    print(f"ERRO AO INICIALIZAR O MODELO GEMINI: {e}".upper())
    sys.exit()

# --- Variáveis Globais de Estado do Jogo ---
# Estas variáveis armazenam o estado atual do quiz (nível, pergunta, acertos, etc.).
nivel_atual = ""
pergunta_atual = ""
alternativas_atuais = {}
resposta_correta_atual = ""
dica_atual = ""
explicacao_atual = ""
tentativas = 0  # Contador de tentativas por pergunta
acertos = 0  # Contador total de acertos no jogo


# --- Funções Utilitárias ---
def remover_acentos(texto):
    """Remove acentos de uma string para facilitar comparações."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


# --- Agente de Curadoria: Geração de Perguntas com Gemini ---
def agente_curadoria(nivel_dificuldade):
    """
    Gera UMA ÚNICA pergunta de ciências com alternativas, dica e explicação usando o modelo Gemini.
    O prompt instrui o modelo sobre o formato e conteúdo da pergunta, enfatizando a unicidade.
    """
    prompt = f"""
    VOCÊ É UM PROFESSOR MUITO BEM HUMORADO E DIVERTIDO QUE ADORA CRIANÇAS E VAI CRIAR PERGUNTAS DE CIÊNCIAS PARA CRIANÇAS DE 6 A 11 ANOS.
    GERE SOMENTE UMA ÚNICA PERGUNTA DE CIÊNCIAS DE NÍVEL '{nivel_dificuldade.upper()}'. NÃO ADICIONE PERGUNTAS EXTRAS OU EXEMPLOS.
    PARA O NÍVEL INICIAL, PENSE EM PERGUNTAS SOBRE FENÔMENOS SIMPLES E OBSERVÁVEIS, SEMPRE COM ALTERNATIVAS (A, B, C, D) FORMATADAS EM LINHAS SEPARADAS.
    PARA O NÍVEL MÉDIO, INTRODUZA CONCEITOS UM POUCO MAIS ABSTRATOS, MAS AINDA RELACIONADOS AO COTIDIANO, TAMBÉM SEMPRE COM ALTERNATIVAS (A, B, C, D) EM LINHAS SEPARADAS.
    PARA O NÍVEL AVANÇADO, PODE ABORDAR PRINCÍPIOS CIENTÍFICOS COM MAIS DETALHES, TAMBÉM COM ALTERNATIVAS (A, B, C, D) EM LINHAS SEPARADAS.
    TENTE ADICIONAR UM TOQUE DE HUMOR LEVE, TALVEZ UMA PEQUENA OBSERVAÇÃO ENGRAÇADA RELACIONADA AO TEMA, SEM CONFUNDIR A PERGUNTA.
    INCLUA CLARAMENTE A RESPOSTA CORRETA, UMA DICA CURTA E UMA EXPLICAÇÃO MAIS DETALHADA EM SUA RESPOSTA.

    FORMATE SUA RESPOSTA DA SEGUINTE MANEIRA EXATA E **APENAS NESTE FORMATO**, SEM INTRODUÇÃO OU CONCLUSÃO ADICIONAIS:
    PERGUNTA: [A PERGUNTA DE CIÊNCIAS AQUI]
    A) [PRIMEIRA ALTERNATIVA]
    B) [SEGUNDA ALTERNATIVA]
    C) [TERCEIRA ALTERNATIVA]
    D) [QUARTA ALTERNATIVA]
    RESPOSTA: [A LETRA DA ALTERNATIVA CORRETA] - [UMA DICA CURTA SOBRE A RESPOSTA] - [A EXPLICAÇÃO COMPLETA DA RESPOSTA CORRETA]
    """

    try:
        response = model.generate_content(prompt)
        # print(f"DEBUG - RESPOSTA BRUTA DO GEMINI PARA '{nivel_dificuldade.upper()}':\n{response.text}\n---") # Descomente para depurar

        if response.text:
            # Garante que estamos pegando a primeira ocorrência do padrão de resposta.
            pergunta_match = re.search(r"PERGUNTA:\s*(.*?)(?=\n[A-D]\)|\nRESPOSTA:|$)", response.text,
                                       re.DOTALL | re.IGNORECASE)
            alternativas = re.findall(r"^([A-D])\)\s*(.*?)(?:\n|$)", response.text, re.MULTILINE | re.IGNORECASE)
            resposta_completa_match = re.search(r"(?s)RESPOSTA:\s*([A-D])(?: - (.*?))?(?: - (.*))?$", response.text,
                                                re.IGNORECASE)

            if pergunta_match and alternativas and resposta_completa_match:
                pergunta_raw = pergunta_match.group(1).strip()
                alternativa_correta_raw = resposta_completa_match.group(1).strip()
                dica_curta = resposta_completa_match.group(2).strip() if resposta_completa_match.group(
                    2) else "PENSE UM POUCO MAIS!"
                explicacao_completa = resposta_completa_match.group(3).strip() if resposta_completa_match.group(
                    3) else "A EXPLICAÇÃO ESTÁ NA RESPOSTA CORRETA."

                pergunta_formatada = f"PERGUNTA: {pergunta_raw}\n" + "\n".join(
                    [f"{alt[0]}) {alt[1].strip()}" for alt in alternativas])
                alternativa_correta = alternativa_correta_raw.lower()

                return pergunta_formatada, alternativa_correta, dica_curta, explicacao_completa, nivel_dificuldade, False
            else:
                print(f"DEBUG - ERRO DE FORMATO NA RESPOSTA DO GEMINI PARA '{nivel_dificuldade.upper()}':")
                print(f"   RESPOSTA COMPLETA:\n{response.text}")
                print(f"   PERGUNTA MATCH: {bool(pergunta_match)}")
                print(f"   ALTERNATIVAS MATCH: {bool(alternativas)}")
                print(f"   RESPOSTA COMPLETA MATCH: {bool(resposta_completa_match)}")
                return "ERRO AO EXTRAIR INFORMAÇÕES DA RESPOSTA DO GEMINI. FORMATO INESPERADO.", "", "", "", nivel_dificuldade, True
        else:
            print(f"DEBUG - RESPOSTA VAZIA DO GEMINI PARA '{nivel_dificuldade.upper()}'.")
            return "RESPOSTA VAZIA DO GEMINI.", "", "", "", nivel_dificuldade, True

    except Exception as e:
        print(f"DEBUG - EXCEÇÃO AO COMUNICAR COM GEMINI PARA '{nivel_dificuldade.upper()}': {e}")
        return f"ERRO AO COMUNICAR COM O GEMINI: {e}", "", "", "", nivel_dificuldade, True


# --- Agente de Avaliação: Verifica a Resposta do Usuário ---
def agente_avaliacao(resposta_usuario, resposta_correta):
    """
    Compara a resposta do usuário com a resposta correta e gera um feedback.
    Normaliza as respostas (remove acentos, espaços, converte para minúsculas) para comparação.
    """
    resposta_usuario = remover_acentos(resposta_usuario).strip().lower()
    resposta_correta = remover_acentos(resposta_correta).strip().lower()

    if len(resposta_usuario) > 1 and resposta_usuario.endswith(')'):
        resposta_usuario = resposta_usuario[:-1]

    if resposta_usuario == resposta_correta:
        feedback_positivo = random.choice([
            "VOCÊ ACERTOU EM CHEIO! QUE MENTE BRILHANTE!",
            "RESPOSTA CORRETA! VOCÊ É UM VERDADEIRO GÊNIO DA CIÊNCIA!",
            "ISSO MESMO! VOCÊ DESVENDOU O MISTÉRIO!",
            "EXCELENTE! SEU CONHECIMENTO CIENTÍFICO É INCRÍVEL!",
            "BINGO! VOCÊ MANDOU MUITO BEM!",
        ]).upper()
        return feedback_positivo, True
    else:
        feedback_negativo = random.choice([
            "QUASE LÁ! MAS NÃO FOI DESSA VEZ.",
            "HMM, NÃO EXATAMENTE.",
            "ESSA NÃO É A RESPOSTA CORRETA.",
            "OH, QUASE!",
            "NÃO SE PREOCUPE! ERRAR FAZ PARTE DO APRENDIZADO.",
        ]).upper()
        return feedback_negativo, False


# --- Funções de Navegação e Exibição da Interface ---

def mostrar_tela_inicial():
    """
    Exibe a tela inicial do quiz, com o título, imagem do robô e botões de seleção de nível.
    """
    # Limpa todos os widgets existentes na janela
    for widget in janela.winfo_children():
        widget.destroy()

    # Configura a imagem de fundo
    configurar_imagem_fundo(janela, resource_path("background.jpeg"))  # Nome do arquivo da sua imagem de fundo

    # Todos os widgets a seguir serão empacotados dentro do canvas_background
    # para que fiquem sobre a imagem de fundo.

    # Título principal do quiz
    label_titulo = ttk.Label(canvas_background, text="QUIZ DE CIÊNCIAS DIVERTIDO!", style='Titulo.TLabel')
    canvas_background.create_window(500, 70, window=label_titulo, anchor="center")

    # Carrega e exibe a imagem do robô
    try:
        robo_image_path = resource_path("robot.png")

        # MUITO IMPORTANTE: Abra a imagem AQUI e atribua a imagem carregada a imagem_robo_pil
        imagem_robo_pil = Image.open(robo_image_path)  # <--- Esta linha é a que faltava!

        # E atualize para o método mais recente de resampling
        imagem_robo_pil = imagem_robo_pil.resize((150, 150), Image.Resampling.LANCZOS)  # Redimensiona a imagem

        imagem_robo = ImageTk.PhotoImage(imagem_robo_pil)
        label_robo = ttk.Label(canvas_background, image=imagem_robo)
        label_robo.image = imagem_robo  # Mantém a referência para evitar garbage collection
        canvas_background.create_window(500, 200, window=label_robo, anchor="center")
    except FileNotFoundError:
        label_robo_placeholder = ttk.Label(canvas_background,
                                           text="[IMAGEM DO ROBÔ - ARQUIVO 'ROBOT.PNG' NÃO ENCONTRADO]".upper(),
                                           style='Erro.TLabel')
        canvas_background.create_window(500, 200, window=label_robo_placeholder, anchor="center")
    except Exception as e:
        label_robo_placeholder = ttk.Label(canvas_background, text=f"[ERRO AO CARREGAR IMAGEM: {e}]".upper(),
                                           style='Erro.TLabel')
        canvas_background.create_window(500, 200, window=label_robo_placeholder, anchor="center")

    # Texto do robô convidando o usuário a escolher um nível
    label_robo_fala = ttk.Label(canvas_background,
                                text="OLÁ, PEQUENO CIENTISTA! ESCOLHA UM NÍVEL PARA COMEÇAR NOSSA AVENTURA!".upper(),
                                style='RoboFala.TLabel')
    canvas_background.create_window(500, 350, window=label_robo_fala, anchor="center")

    # Frame para agrupar os botões de nível
    frame_niveis = ttk.Frame(canvas_background)
    canvas_background.create_window(500, 450, window=frame_niveis, anchor="center")  # Posiciona o frame no canvas

    # Botões para selecionar os níveis de dificuldade
    botao_inicial = ttk.Button(frame_niveis, text="NÍVEL INICIAL", style='TButton',
                               command=lambda: selecionar_nivel('inicial'))
    botao_inicial.pack(side="left", padx=10, pady=10)  # pady para espaçamento vertical entre botões

    botao_medio = ttk.Button(frame_niveis, text="NÍVEL MÉDIO", style='TButton',
                             command=lambda: selecionar_nivel('medio'))
    botao_medio.pack(side="left", padx=10, pady=10)

    botao_avancado = ttk.Button(frame_niveis, text="NÍVEL AVANÇADO", style='TButton',
                                command=lambda: selecionar_nivel('avancado'))
    botao_avancado.pack(side="left", padx=10, pady=10)


def selecionar_nivel(nivel):
    """
    Define o nível de dificuldade selecionado e inicia a exibição da primeira pergunta.
    """
    global nivel_atual
    nivel_atual = nivel
    mostrar_tela_pergunta()


def mostrar_tela_pergunta():
    """
    Prepara a tela para exibir uma nova pergunta. Limpa o conteúdo anterior e chama gerar_pergunta.
    """
    # Limpa todos os widgets existentes na janela (incluindo o canvas anterior)
    for widget in janela.winfo_children():
        widget.destroy()

    # Configura a imagem de fundo novamente para a nova tela
    configurar_imagem_fundo(janela, resource_path("background2.jpg"))

    gerar_pergunta()


def gerar_pergunta():
    """
    Chama o agente de curadoria para obter uma nova pergunta e a processa para exibição.
    Lida com erros na geração da pergunta, exibindo uma mensagem e retornando à tela inicial.
    """
    global pergunta_atual, alternativas_atuais, resposta_correta_atual, dica_atual, explicacao_atual, tentativas

    # Tenta gerar a pergunta usando o agente_curadoria
    pergunta_formatada, resposta_correta, dica_curta, explicacao_completa, nivel_pergunta, erro = agente_curadoria(
        nivel_atual)

    if not erro:
        # Se não houve erro na geração, processa a pergunta e alternativas
        partes = pergunta_formatada.split('\n')
        if partes:
            pergunta_atual = partes[0].replace("PERGUNTA: ", "").strip()
            alternativas_atuais = {}
            for parte in partes[1:]:
                match_alternativa = re.match(r"^([A-D])\)\s*(.*)", parte, re.IGNORECASE)
                if match_alternativa:
                    letra = match_alternativa.group(1)
                    texto = match_alternativa.group(2).strip()
                    alternativas_atuais[letra.upper()] = texto
            resposta_correta_atual = resposta_correta.strip().upper()
            dica_atual = dica_curta.strip()
            explicacao_atual = explicacao_completa.strip()
            tentativas = 0  # Reseta o contador de tentativas para a nova pergunta
            exibir_pergunta()  # Exibe a pergunta na tela
        else:
            messagebox.showerror("ERRO DE FORMATO",
                                 "A RESPOSTA DO AGENTE CURADORIA NÃO ESTÁ NO FORMATO ESPERADO.".upper())
            mostrar_tela_inicial()
    else:
        messagebox.showerror("ERRO", "FALHA AO GERAR A PERGUNTA. TENTE NOVAMENTE.".upper())
        mostrar_tela_inicial()


def exibir_pergunta():
    """
    Renderiza a interface da pergunta atual, incluindo a pergunta, alternativas,
    botão de envio e contador de acertos.
    """
    # Limpa todos os widgets existentes no canvas (mantendo o fundo)
    for item in canvas_background.find_all():
        if item != canvas_background.find_withtag("background_image"):  # Não apagar a imagem de fundo
            canvas_background.delete(item)

    # Label para exibir a pergunta
    label_pergunta = ttk.Label(canvas_background, text=pergunta_atual.upper(), style='Pergunta.TLabel', wraplength=950)
    canvas_background.create_window(500, 70, window=label_pergunta, anchor="center")

    # Frame para agrupar as alternativas (Radiobuttons)
    frame_alternativas = ttk.Frame(canvas_background)
    canvas_background.create_window(500, 300, window=frame_alternativas, anchor="center")  # Posição central vertical

    resposta_selecionada_var = tk.StringVar()
    if alternativas_atuais:
        resposta_selecionada_var.set(list(alternativas_atuais.keys())[0])

    for letra, texto in alternativas_atuais.items():
        alt_frame = ttk.Frame(frame_alternativas)
        alt_frame.pack(anchor="w", pady=5)  # Adiciona padding vertical entre as alternativas

        radio_alternativa = ttk.Radiobutton(alt_frame, variable=resposta_selecionada_var, value=letra,
                                            style='TRadiobutton',
                                            command=lambda l=letra: resposta_selecionada_var.set(l))
        radio_alternativa.pack(side="left")

        label_alternativa_texto = ttk.Label(alt_frame, text=f"{letra}) {texto}".upper(),
                                            style='Alternativa.TLabel', wraplength=800)
        label_alternativa_texto.pack(side="left", padx=5)

    # Botão para enviar a resposta selecionada
    botao_enviar_resposta = ttk.Button(canvas_background, text="ENVIAR RESPOSTA", style='TButton',
                                       command=lambda: verificar_resposta(resposta_selecionada_var.get()))
    canvas_background.create_window(500, 550, window=botao_enviar_resposta, anchor="center")  # Posiciona mais abaixo

    # Botão para mudar de nível (no rodapé)
    botao_mudar_nivel_pergunta = ttk.Button(canvas_background, text="MUDAR NÍVEL", style='TButton',
                                            command=mostrar_tela_inicial)
    canvas_background.create_window(500, 750, window=botao_mudar_nivel_pergunta, anchor="center")  # Posiciona no rodapé

    # Label para exibir o contador de acertos (no canto inferior direito)
    label_acertos = ttk.Label(canvas_background, text=f"ACERTOS: {acertos}".upper(), font=("Arial", 12))
    # Usamos place para maior controle no posicionamento exato no rodapé
    canvas_background.create_window(janela.winfo_width() - 80, janela.winfo_height() - 30, window=label_acertos,
                                    anchor="se")


def verificar_resposta(resposta_selecionada):
    """
    Verifica se a resposta do usuário está correta, exibe feedback e gerencia o fluxo do jogo (próxima pergunta, dica, etc.).
    """
    if not resposta_selecionada:
        messagebox.showwarning("ATENÇÃO", "POR FAVOR, SELECIONE UMA ALTERNATIVA ANTES DE ENVIAR!".upper())
        return

    global tentativas, acertos
    feedback, acertou = agente_avaliacao(resposta_selecionada, resposta_correta_atual)

    # Limpa todos os widgets existentes no canvas (mantendo o fundo)
    for item in canvas_background.find_all():
        if item != canvas_background.find_withtag("background_image"):
            canvas_background.delete(item)

    # Label para exibir o feedback (acertou/errou)
    label_feedback = ttk.Label(canvas_background, text=feedback, style='Feedback.TLabel' if acertou else 'Erro.TLabel')
    canvas_background.create_window(500, 200, window=label_feedback, anchor="center")

    if acertou:
        acertos += 1
        botao_continuar = ttk.Button(canvas_background, text="PRÓXIMA PERGUNTA", style='TButton',
                                     command=mostrar_tela_pergunta)
        canvas_background.create_window(500, 400, window=botao_continuar, anchor="center")  # Mais espaçado

        # Botão para mudar de nível (no rodapé)
        botao_mudar_nivel = ttk.Button(canvas_background, text="MUDAR NÍVEL", style='TButton',
                                       command=mostrar_tela_inicial)
        canvas_background.create_window(500, 750, window=botao_mudar_nivel, anchor="center")

    else:
        tentativas += 1
        if tentativas == 1:
            label_dica = ttk.Label(canvas_background, text=f"DICA: {dica_atual}".upper(), style='Dica.TLabel',
                                   wraplength=900)
            canvas_background.create_window(500, 350, window=label_dica, anchor="center")

            frame_tentar_mostrar = ttk.Frame(canvas_background)
            canvas_background.create_window(500, 500, window=frame_tentar_mostrar, anchor="center")

            botao_tentar_novamente = ttk.Button(frame_tentar_mostrar, text="TENTAR NOVAMENTE", style='TButton',
                                                command=exibir_pergunta)
            botao_tentar_novamente.pack(side="left", padx=10, pady=10)  # pady para espaçamento vertical
            botao_mostrar_resposta = ttk.Button(frame_tentar_mostrar, text="MOSTRAR RESPOSTA", style='TButton',
                                                command=mostrar_resposta)
            botao_mostrar_resposta.pack(side="left", padx=10, pady=10)
        else:
            mostrar_resposta()


def mostrar_resposta():
    """
    Exibe a resposta correta e sua explicação detalhada, além das opções de continuar, mudar nível ou parar.
    """
    # Limpa todos os widgets existentes no canvas (mantendo o fundo)
    for item in canvas_background.find_all():
        if item != canvas_background.find_withtag("background_image"):
            canvas_background.delete(item)

    label_resposta = ttk.Label(canvas_background,
                               text=f"A RESPOSTA CORRETA ERA: {resposta_correta_atual}) - {explicacao_atual}".upper(),
                               style='Resposta.TLabel', wraplength=900)
    canvas_background.create_window(500, 200, window=label_resposta, anchor="center")

    #frame_opcoes_fim_pergunta = ttk.Frame(canvas_background)
    #canvas_background.create_window(500, 500, window=frame_opcoes_fim_pergunta,
    #                                anchor="center")  # Posiciona mais abaixo

    frame_opcoes_fim_pergunta = ttk.Frame(canvas_background, style='TFrame')  # Adicione o estilo 'TFrame' para ter fundo
    # Posicione o frame centralizado e um pouco mais abaixo para que os botões não fiquem em cima da explicação
    canvas_background.create_window(500, 500, window=frame_opcoes_fim_pergunta, anchor="center")

    botao_continuar = ttk.Button(frame_opcoes_fim_pergunta, text="PRÓXIMA PERGUNTA", style='TButton',
                                 command=mostrar_tela_pergunta)
    botao_continuar.pack(side="left", padx=10, pady=10)

    # Botão para mudar de nível (no rodapé)
    botao_mudar_nivel = ttk.Button(canvas_background, text="MUDAR NÍVEL", style='TButton', command=mostrar_tela_inicial)
    botao_mudar_nivel.pack(side="left", padx=10, pady=10)  # Este irá no frame de opções, não no rodapé principal aqui.
    # O botão no rodapé é o abaixo.

    botao_parar = ttk.Button(frame_opcoes_fim_pergunta, text="PARAR JOGO", style='TButton', command=janela.destroy)
    botao_parar.pack(side="left", padx=10, pady=10)

    # Posiciona o botão "Mudar Nível" no rodapé aqui também, se desejado após ver a resposta final
    # Este é um exemplo de como seria, mas para evitar duplicidade com o do frame_opcoes_fim_pergunta,
    # talvez não precise se ele já está no frame.
    # Se você quiser que o botão Mudar Nível esteja *sempre* no rodapé sozinho,
    # teremos que ajustar como os outros botões são empacotados.
    # Por agora, ele está dentro do frame_opcoes_fim_pergunta.


# --- Início do Aplicativo ---
# Chama a função mostrar_tela_inicial() após a janela ser criada e renderizada.
janela.update_idletasks()
janela.update()
janela.after(0, mostrar_tela_inicial)


# Inicia o loop principal do Tkinter. Ele mantém a janela aberta e responsiva.
try:
    janela.mainloop()
except Exception as e:
    print(f"OCORREU UM ERRO NO LOOP PRINCIPAL DO TKINTER: {e}".upper())