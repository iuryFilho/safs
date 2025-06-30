# SAFS - Sistema de Automação do Fluxo de Simulação

## Introdução

O SAFS é um sistema desenvolvido para automatizar o fluxo de simulação de sistemas, facilitando a criação, execução e análise de simulações.

## Funcionalidades

-   Geração de gráficos a partir de dados de simulação.
-   Exportação de resultados (média e erro padrão) em arquivos XLSX.

## Requisitos

-   Python 3.8 ou superior
-   Bibliotecas: `Flask`, `Jinja2`, `pandas`, `openpyxl`, `matplotlib`, `scipy`

## Instalação

Siga os passos abaixo para instalar e preparar o ambiente do projeto:

1. **Baixe o repositório:**

    - Para baixar diretamente, clique [neste link](https://github.com/iuryFilho/safs/archive/refs/heads/master.zip) e extraia o arquivo ZIP.
    - Ou, se preferir usar o Git, execute no terminal:

        ```bash
        git clone https://github.com/iuryFilho/safs.git
        ```

2. **Acesse o diretório do projeto:**

    ```bash
    cd safs
    ```

3. **(Opcional, mas recomendado) Crie e ative um ambiente virtual:**

    - **Windows:**
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
    - **macOS / Linux:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

4. **Instale as dependências do projeto:**

    ```bash
    pip install -r requirements.txt
    ```

5. **(Opcional) Para desativar o ambiente virtual:**

    ```bash
    deactivate
    ```

## Uso

1. Inicie o servidor Flask:

    ```bash
    python src/app.py --port PORT
    ```

    - Substitua `PORT` pela porta desejada.
    - Se não especificar a porta, o padrão será 5000.
    - Exemplo:

    ```bash
    python src/app.py --port 8000
    ```

2. Acesse a aplicação no navegador: `http://localhost:PORT`

    - Substitua `PORT` pela porta que você especificou.

3. Utilize a interface para carregar os dados de simulação e gerar gráficos.
