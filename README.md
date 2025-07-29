# Sistema de Análise de Mercado - Sofá Novo de Novo

Sistema completo de análise de mercado para expansão de franquias, desenvolvido com a biblioteca **Agno** (Multi-Agent AI System).

## 🎯 Objetivo

Realizar estudo mercadológico detalhado para entender a capacidade de vendas de franquias da Sofá Novo de Novo, substituindo a tese simplificada de "1 franquia a cada 100 mil habitantes" por uma análise precisa baseada em:

- Dados demográficos (população, PIB, IDH)
- Perfil socioeconômico (renda, classe social, público-alvo)
- Análise de concorrência (Dr. Lava Tudo, Acquazero, independentes)
- Capacidade de mercado calculada

## 🏗️ Arquitetura do Sistema

### Agentes Especializados (Agno AI)

1. **Demographic Agent** - Coleta dados demográficos do IBGE
2. **Socioeconomic Analyzer** - Analisa perfil de renda e público-alvo
3. **Competitor Analyzer** - Pesquisa concorrência no mercado
4. **Market Capacity Calculator** - Calcula capacidade de franquias
5. **Market Coordinator** - Coordena todos os agentes

### Sistemas de Apoio

- **City Prioritization System** - Prioriza cidades por potencial
- **Spreadsheet Generator** - Gera planilhas Excel detalhadas

## 📋 Funcionalidades

### ✅ Análise Completa Nacional
- Análise das principais cidades brasileiras (>20k habitantes)
- Cálculo de capacidade de franquias por cidade
- Priorização baseada em múltiplos critérios
- Geração de relatório executivo
- Planilha Excel com análise detalhada

### ✅ Análise de Cidades Específicas
- Análise customizada de cidades escolhidas
- Relatório focado nas cidades selecionadas

### ✅ Base de Dados
- Criação de base atualizada de municípios brasileiros
- Dados do IBGE integrados

## 🚀 Instalação e Configuração

### Pré-requisitos

```bash
# Python 3.8+
pip install agno pandas openpyxl requests beautifulsoup4 lxml
```

### Configuração da API Key

```bash
# Configure sua OpenAI API Key
export OPENAI_API_KEY="sua-chave-openai-aqui"
```

### Execução

```bash
# Executa o sistema principal
python main_analysis_system.py
```

## 📊 Tipos de Franquia

### Franquia Padrão
- **Investimento**: R$ 35.000
- **Royalties**: R$ 1.200/mês
- **Faturamento prometido**: R$ 15.000/mês
- **Faturamento ideal**: R$ 30.000/mês
- **Público**: Cidades >100k habitantes

### Franquia Sofázinho
- **Investimento**: R$ 12.000
- **Royalties**: R$ 400/mês
- **Faturamento prometido**: R$ 7.000/mês
- **Faturamento ideal**: R$ 10.000/mês
- **Público**: Cidades 20k-100k habitantes

## 🎯 Público-Alvo

- **Gênero**: Mulheres
- **Idade**: 25-45 anos
- **Perfil**: Presença de pets ou crianças
- **Ticket médio**: R$ 250
- **Frequência**: 1,5x por ano

## 📈 Metodologia de Análise

### 1. Score Demográfico (25%)
- População municipal
- Taxa de crescimento
- Densidade demográfica

### 2. Score Econômico (30%)
- PIB per capita
- IDH municipal
- Percentual classe A/B
- Renda média familiar

### 3. Score Concorrência (25%)
- Nível de saturação
- Franquias nacionais presentes
- Prestadores independentes
- Preços praticados

### 4. Score Potencial (20%)
- Número máximo de franquias
- Mercado servicível
- Receita potencial
- ROI estimado

## 📁 Estrutura de Arquivos

```
├── main_analysis_system.py          # Sistema principal
├── market_coordinator.py            # Coordenador de agentes
├── demographic_data_collector.py    # Coleta dados demográficos
├── socioeconomic_analyzer.py        # Análise socioeconômica
├── competitor_analyzer.py           # Análise de concorrência
├── market_capacity_calculator.py    # Cálculo de capacidade
├── city_prioritization_system.py    # Sistema de priorização
├── spreadsheet_generator.py         # Gerador de planilhas
├── franqueados_atuais.xlsx         # Base de franqueados atuais
└── README.md                       # Este arquivo
```

## 📊 Outputs Gerados

### 1. Relatório Executivo (.md)
- Sumário executivo
- Análise de mercado nacional
- Top 10 cidades prioritárias
- Recomendações estratégicas
- Próximos passos

### 2. Planilha Detalhada (.xlsx)
- **Resumo Executivo**: Visão geral dos resultados
- **Análise Detalhada**: Todos os municípios analisados
- **Análise Regional**: Dados por estado/região
- **Análise Concorrência**: Mapeamento de concorrentes
- **Projeções Financeiras**: Cenários de expansão
- **Metodologia**: Explicação dos cálculos

### 3. Base de Dados (.csv)
- Lista de municípios brasileiros >20k habitantes
- Dados demográficos básicos

## 🔧 Personalização

### Ajustar Parâmetros de Análise

Edite os arquivos para personalizar:

```python
# market_capacity_calculator.py
self.base_parameters = {
    'habitantes_por_franquia_base': 100000,  # Ajustar base de cálculo
    'percentual_publico_alvo_base': 8.5,     # Ajustar % público-alvo
    'taxa_penetracao_mercado': 0.10,         # Ajustar penetração
}

# city_prioritization_system.py
self.weights = {
    'demografico': 0.25,    # Peso critério demográfico
    'economico': 0.30,      # Peso critério econômico
    'concorrencia': 0.25,   # Peso critério concorrência
    'potencial': 0.20       # Peso critério potencial
}
```

## 🧪 Testes

```bash
# Teste individual dos componentes
python demographic_data_collector.py
python socioeconomic_analyzer.py
python competitor_analyzer.py
python market_capacity_calculator.py
```

## 📝 Exemplo de Uso

```python
from main_analysis_system import SofaNovoMarketAnalysis

# Inicializa sistema
system = SofaNovoMarketAnalysis("sua-openai-api-key")

# Análise completa nacional
results = system.run_complete_analysis(
    top_cities_count=50,
    generate_spreadsheet=True
)

# Análise de cidades específicas
cities = [
    {'municipio': 'Campinas', 'uf': 'SP', 'populacao': 1200000},
    {'municipio': 'Santos', 'uf': 'SP', 'populacao': 430000}
]
specific_results = system.analyze_specific_cities(cities)
```

## 🔍 Fontes de Dados

- **IBGE**: População, PIB per capita, dados municipais
- **Atlas do Desenvolvimento Humano**: IDH municipal
- **PNAD**: Dados socioeconômicos
- **Pesquisa Web**: Concorrência e preços de mercado
- **Base interna**: Franqueados atuais

## ⚠️ Limitações

1. **Dados de concorrência**: Baseados em pesquisa web, podem não estar 100% atualizados
2. **Dados socioeconômicos**: Alguns valores são estimados quando dados específicos não estão disponíveis
3. **API Limits**: Dependente dos limites da OpenAI API
4. **Conectividade**: Requer conexão com internet para pesquisas

## 🆘 Suporte

Para dúvidas ou problemas:

1. Verifique se a OpenAI API Key está configurada
2. Confirme se todas as dependências estão instaladas
3. Verifique a conexão com internet
4. Consulte os logs de erro para diagnóstico

## 📄 Licença

Sistema desenvolvido para uso interno da Sofá Novo de Novo.

---

**Desenvolvido com Agno AI** - Framework para Multi-Agent Systems
