# SAFS - Sistema de Automação do Fluxo de Simulação

## Introdução

O SAFS é um sistema desenvolvido para automatizar o fluxo de simulação de sistemas, facilitando a criação, execução e análise de simulações.

## Funcionalidades

-   Geração de gráficos a partir de dados de simulação.
-   Exportação de resultados (média e erro padrão) em arquivos XLSX.

## Requisitos

-   Python 3.8 ou superior
-   Bibliotecas: `Flask`, `Jinja2`, `pandas`, `openpyxl`, `matplotlib`

## Instalação

1. Clone o repositório:
    ```bash
    git clone https://github.com/iuryFilho/safs.git
    ```
2. Navegue até o diretório do projeto:
    ```bash
    cd safs
    ```
3. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1. Inicie o servidor Flask:

    ```bash
    python app.py --port PORT
    ```

    - Substitua `PORT` pela porta desejada.
    - Se não especificar a porta, o padrão será 5000.
    - Exemplo:

    ```bash
    python app.py --port 8000
    ```

2. Acesse a aplicação no navegador: `http://localhost:PORT`

    - Substitua `PORT` pela porta que você especificou.

3. Utilize a interface para carregar os dados de simulação e gerar gráficos.
