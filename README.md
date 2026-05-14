# Conversor RGB → HSV com OpenGL + Python

**Disciplina:** Computação Gráfica
**Aluna:** Emanuele Lima
**Professor:** Marcelo Costa Oliveira

---
##nota: O cálculo está no color_math.py

## O que é este projeto?

Este programa converte imagens do espaço de cores **RGB** para **HSV** usando OpenGL puro com Python. A janela é criada pelo **GLFW**  uma biblioteca nativa de OpenGL sem depender do Pygame para isso.

A tela exibe a imagem original e a imagem convertida lado a lado, com três sliders para ajustar os canais **H** (Matiz), **S** (Saturação) e **V** (Luminância) em tempo real.

O algoritmo de conversão segue as fórmulas apresentadas em aula, incluindo os offsets **0**, **2** e **4** do cálculo do Hue.


## Estrutura dos arquivos

```
📁 rgb_hsv_opengl/
│
├── main.py          →  Janela GLFW, callbacks, loop principal, layout
├── color_math.py    →  Algoritmos RGB for HSV 
├── gl_utils.py      →  Primitivas OpenGL: texturas, formas, texto
├── ui_widgets.py    →  Componentes Button e Slider
└── README.md        →  Este arquivo
```

---

## Pré-requisitos

Você precisa do **Python 3.10 ou superior**.



### Instalar todas as dependências de uma vez

```bash
pip install glfw PyOpenGL PyOpenGL_accelerate pygame Pillow numpy
```


### O que cada biblioteca faz

| Biblioteca | Para que serve |
|---|---|
| `glfw` | Cria a janela OpenGL nativa e gerencia eventos via callbacks |
| `PyOpenGL` | Bindings Python para a API OpenGL |
| `PyOpenGL_accelerate` | Acelera operações do PyOpenGL (opcional) |
| `pygame` | Usado apenas para renderizar fontes de texto em texturas OpenGL |
| `Pillow` | Abre e redimensiona imagens (PNG, JPG, BMP, WEBP, etc.) |
| `numpy` | Operações matemáticas vetorizadas sobre os pixels |

---

## Como executar

Navegue até a pasta do projeto e execute:

```bash
python main.py
```

## Como usar

### 1. Abrir uma imagem

Clique no botão **⬆ ENVIAR IMAGEM**.
Selecione o orquivo desejado.

### 2. Ver a conversão

A tela mostrará:
- **Esquerda:** imagem original em RGB
- **Direita:** imagem convertida (inicialmente igual à original)

### 3. Ajustar os canais H, S, V

Arraste os sliders no painel inferior para modificar a imagem em tempo real:

- **H — Matiz (Hue):** rotaciona as cores no círculo cromático. Varia de −180° a +180°.
- **S — Saturação:** aumenta ou reduz a pureza das cores. Varia de −1.0 a +1.0.
- **V — Luminância:** clarea ou escurece a imagem. Varia de −1.0 a +1.0.


### 4. Resetar

Clique em **↺ RESETAR** 

---

## Como o GLFW funciona no código

No Pygame, os eventos ficam em uma fila que você consulta a cada frame. No GLFW, você **registra funções** (callbacks) que são chamadas automaticamente quando um evento ocorre.



## Algoritmo de lógica da conversão RGB -> HSV

Implementado em `color_math.py`.

```
Dados R, G, B normalizados em [0, 1]:

  max = max(R, G, B)
  min = min(R, G, B)
  Δ   = max − min

  V = max
  S = Δ / max       (se max = 0 → S = 0)

  H = 60 × (offset + fração)

    se max = R  →  H = 60 × ( 0 + (G − B) / Δ )   →  0°–60°
    se max = G  →  H = 60 × ( 2 + (B − R) / Δ )   →  120°–180°
    se max = B  →  H = 60 × ( 4 + (R − G) / Δ )   →  240°–300°

    se H < 0  →  H = H + 360
```

### Por que os offsets 0, 2 e 4?

O círculo cromático tem **360°** em **6 setores de 60°**. As cores primárias estão a cada 120°, que equivale a 2 setores. Por isso o salto é de **2 em 2**:

- **`0`** → vermelho dominante → base = **0°**
- **`2`** → verde dominante → base = **120°** (60 × 2)
- **`4`** → azul dominante → base = **240°** (60 × 4)

---

### A Lógica dos Offsets da Matiz (0, 2 e 4)

No modelo HSV, a Matiz (Hue) é representada como um ângulo em um círculo cromático de 360º. Para otimizar o algoritmo e evitar cálculos trigonométricos pesados, o círculo é dividido matematicamente em blocos de 60º. Os valores **0, 2 e 4** não são arbitrários; eles atuam como pontos de ancoragem (offsets) baseados no canal de cor dominante:

- **0 (Vermelho):** $0 \times 60 = 0^\circ$
- **2 (Verde):** $2 \times 60 = 120^\circ$
- **4 (Azul):** $4 \times 60 = 240^\circ$

Os parâmetros `0`, `2` e `4` utilizados no cálculo do Hue na transformação RGB para HSV representam os setores principais do círculo de cores HSV. O círculo HSV possui 360°, divididos em 6 setores de 60° cada, correspondentes às transições entre as cores principais.

Quando o vermelho é o maior valor RGB, utiliza-se o parâmetro `0`, pois a região do vermelho começa em 0°. Quando o verde é o maior valor, utiliza-se `2`, representando o início do setor verde em 120° (`2 × 60`). Já quando o azul é o maior valor, utiliza-se `4`, indicando o início do setor azul em 240° (`4 × 60`).

Esses valores servem para posicionar corretamente a cor dentro do círculo HSV, enquanto o restante da fórmula calcula o ajuste fino da tonalidade dentro daquele setor específico.

## Recursos OpenGL utilizados

| Recurso | Onde é usado |
|---|---|
| `GL_TEXTURE_2D` | Exibe as imagens como texturas na tela |
| `GL_QUADS` + `glTexCoord2f` | Mapeia a textura em um retângulo |
| `glOrtho` | Projeção ortográfica 2D em coordenadas de pixel |
| `GL_LINE_LOOP` | Bordas e contornos dos elementos |
| `GL_BLEND` | Transparência nos textos e bordas |
| `glDeleteTextures` | Libera memória da GPU ao trocar de imagem |

---
