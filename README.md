[README_Sistema_IoT_Irrigacao.md](https://github.com/user-attachments/files/34430750/README_Sistema_IoT_Irrigacao.md)[# Sistema IoT para Monitoramento e Irrigação

Projeto Integrador IV --- UNIVESP\
**Título:** Sistema IoT para Monitoramento e Irrigação\
**Local de referência:** SENAI "Euclides Facchini", Votuporanga -- SP

## 1. Visão geral

Este projeto apresenta um protótipo acadêmico de monitoramento da
umidade do solo utilizando Internet das Coisas (IoT), integração de
dados meteorológicos, armazenamento em banco de dados e visualização por
meio de um painel web.

A solução demonstra como medições obtidas por um sensor físico podem ser
transmitidas, armazenadas, integradas a informações meteorológicas e
analisadas em uma aplicação.

> **Escopo:** o protótipo realiza monitoramento e análise de dados. Não
> aciona automaticamente bombas ou válvulas de irrigação e não deve ser
> utilizado como sistema operacional de controle agrícola.

## 2. Funcionalidades implementadas

-   Aquisição de leituras de umidade do solo por sensor conectado a um
    ESP32.
-   Transmissão das medições por Wi-Fi utilizando o protocolo MQTT.
-   Recepção das mensagens por uma aplicação Python.
-   Armazenamento das medições em banco de dados SQLite.
-   Coleta de variáveis meteorológicas por meio da API Open-Meteo.
-   Integração temporal entre medições do solo e dados meteorológicos,
    em intervalos de 15 minutos.
-   Análise exploratória e diagnóstico da qualidade dos dados.
-   Visualização de indicadores, séries temporais e informações
    meteorológicas em dashboard Streamlit.
-   Modelo demonstrativo de aprendizado de máquina com Regressão Linear
    e avaliação por validação cruzada.

## 3. Arquitetura simplificada

``` text
Sensor de umidade do solo
          |
          v
        ESP32
          |
        Wi-Fi
          |
          v
    Broker MQTT (HiveMQ)
          |
          v
 Receptor MQTT em Python
          |
          v
 Banco de dados SQLite
          |
          +----------------------+
          |                      |
          v                      v
 Dados meteorológicos       Base integrada
 (Open-Meteo)               (intervalos de 15 min)
                                 |
                    +------------+------------+
                    |                         |
                    v                         v
             Análise exploratória      Modelo demonstrativo
                    |                  (Regressão Linear)
                    +------------+------------+
                                 |
                                 v
                         Dashboard Streamlit
```

## 4. Tecnologias utilizadas

  Tecnologia                  Finalidade
  --------------------------- ---------------------------------------------------
  Python                      Integração, processamento, análise e aplicação
  C++ com framework Arduino   Programação do ESP32
  ESP32                       Aquisição e transmissão das medições
  Sensor de umidade do solo   Leitura física do solo
  MQTT / HiveMQ               Comunicação entre dispositivo e receptor
  SQLite                      Persistência dos dados
  Open-Meteo API              Consulta de variáveis meteorológicas
  Pandas                      Tratamento e integração dos dados
  Scikit-learn                Implementação e avaliação do modelo demonstrativo
  Plotly                      Gráficos interativos
  Streamlit                   Interface web e dashboard
  Git e GitHub                Versionamento e disponibilização do código

## 5. Organização do repositório

O repositório separa códigos-fonte, dados e resultados. Entre os
principais módulos da implementação estão:

  -----------------------------------------------------------------------
  Arquivo ou módulo                   Responsabilidade
  ----------------------------------- -----------------------------------
  `main.py`                           Ponto de entrada auxiliar do
                                      projeto

  `banco_dados.py`                    Operações de armazenamento no
                                      SQLite

  `receptor_mqtt.py`                  Recepção das mensagens MQTT

  `simulador_esp32.py`                Simulação de envio de medições

  `consultar_banco.py`                Consulta e inspeção dos registros
                                      armazenados

  `meteorologia.py`                   Consulta à API Open-Meteo

  `coletor_meteorologia.py`           Coleta periódica de dados
                                      meteorológicos

  `base_integrada.py`                 Integração temporal dos dados
                                      físicos e meteorológicos

  `analise_base_integrada.py`         Diagnóstico da base integrada

  `analise_exploratoria.py`           Análises exploratórias e
                                      visualizações

  `modelo_demonstrativo.py`           Treinamento e avaliação do modelo
                                      de Regressão Linear

  `dashboard.py`                      Interface de visualização em
                                      Streamlit
  -----------------------------------------------------------------------

Os dados e resultados gerados ficam organizados nas pastas
correspondentes do repositório. A estrutura pode receber ajustes
conforme a evolução da implementação.

## 6. Acesso ao dashboard

A aplicação Streamlit foi publicada e pode ser acessada pelo endereço:

**[Abrir Sistema Inteligente de
Irrigação](https://sistemairrigacao-a4jnry8wyzdclyvpdtlsaf.streamlit.app/)**

O painel apresenta indicadores de umidade do solo, evolução temporal das
medições, informações meteorológicas e recursos de consulta e análise.

## 7. Como executar localmente

### Requisitos

-   Python 3.11 (utilizado no desenvolvimento)
-   Git
-   Acesso à internet para comunicação MQTT e consulta à API
    meteorológica

### Instalação

Clone o repositório:

``` bash
git clone https://github.com/pedropelegrini/sistema_irrigacao.git
cd sistema_irrigacao
```

Crie e ative um ambiente virtual (opcional, mas recomendado):

``` bash
python -m venv .venv
```

No Windows PowerShell:

``` powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

``` bash
pip install -r requisitos.txt
```

### Executar o dashboard

Na raiz do projeto, execute:

``` bash
streamlit run src/dashboard.py
```

Se o nome ou caminho do arquivo principal tiver sido alterado na versão
do repositório, utilize o caminho correspondente à estrutura atual.

> A execução dos módulos de coleta e recepção depende da disponibilidade
> do broker MQTT, da API meteorológica e, para medições físicas, do
> ESP32 e do sensor configurados.

## 8. Modelo demonstrativo de aprendizado de máquina

Foi implementado um modelo de Regressão Linear com Scikit-learn. As
variáveis meteorológicas utilizadas como entradas são temperatura do ar,
umidade relativa e velocidade do vento. A variável estimada é a umidade
média do solo.

Na execução registrada com 15 intervalos integrados, foram obtidos os
seguintes indicadores por validação cruzada:

  Métrica                   Resultado
  --------- -------------------------
  MAE         3,23 pontos percentuais
  RMSE        3,82 pontos percentuais
  R²                            0,571

Esses resultados são exclusivamente demonstrativos. A amostra é pequena,
corresponde a um período limitado e a calibração física do sensor não
foi validada. Portanto, as métricas não comprovam capacidade de
generalização nem autorizam o uso do modelo para decisões operacionais
de irrigação.

## 9. Limitações conhecidas

-   A calibração do sensor de umidade do solo não passou por validação
    agronômica independente.
-   Foram observadas leituras extremas de 0% e 100%, que podem indicar
    saturação da conversão do sinal ADC para percentual.
-   O protótipo não possui mecanismo implementado de acionamento
    automático da irrigação.
-   Não foi instalado sensor de temperatura do solo; esse campo pode
    permanecer sem valores.
-   A base integrada utilizada na demonstração do modelo contém apenas
    15 intervalos temporais.
-   A coleta meteorológica depende da disponibilidade do serviço externo
    Open-Meteo.
-   O modelo de Regressão Linear é experimental e não foi validado com
    uma base independente de longo prazo.

## 10. Considerações finais

O projeto demonstra a integração de hardware IoT, comunicação MQTT,
armazenamento de dados, consulta a serviço meteorológico, processamento
em Python e visualização web. O protótipo permite acompanhar medições e
explorar relações entre variáveis do solo e da atmosfera, constituindo
uma base acadêmica para futuras melhorias, como calibração experimental
do sensor, ampliação da série histórica e avaliação de modelos
preditivos com dados independentes.

## 11. Equipe

-   **Alessandra Mara Salvioni Rondini** --- 232005516
-   **Almir Lotito Lima** --- 2215946
-   **Pedro Henrique Ferreira Pelegrini** --- 23218607

**Instituição:** Universidade Virtual do Estado de São Paulo (UNIVESP)\
**Disciplina:** Projeto Integrador IV
Uploading README_Sistema_IoT_Irrigacao.md…]()
