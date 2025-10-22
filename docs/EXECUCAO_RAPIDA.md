# 🚀 AgentsVille Trip Planner - Guia de Execução Rápida

## ⚡ Execução Imediata

### 1. Configuração do Ambiente

```bash
# Navegar para o diretório do projeto
cd /home/fabiolima/Workdir/udacity_projects/AgentsVille-Trip-Planner

# Ativar ambiente virtual (criado com uv)
source .venv/bin/activate

# Verificar se as dependências estão instaladas
python -c "import models, agents, tools, evaluations; print('✅ Todos os módulos importados com sucesso!')"
```

### 2. Configuração da API

Edite o arquivo `config.env` e substitua `your_openai_api_key_here` pela sua chave real da API OpenAI:

```env
OPENAI_API_KEY=sua_chave_api_aqui
OPENAI_BASE_URL=https://openai.vocareum.com/v1
DEFAULT_MODEL=gpt-4.1-mini
MAX_REACT_STEPS=15
```

### 3. Execução do Sistema

```bash
# Executar o sistema completo
python main.py
```

### 4. Execução dos Testes

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar testes com cobertura
python -m pytest tests/ --cov=. --cov-report=html
```

## 🎯 O que o Sistema Faz

1. **Cria informações de viagem** para Yuri e Hiro em AgentsVille (10-12 de junho de 2025)
2. **Gera itinerário inicial** usando o ItineraryAgent com Chain-of-Thought reasoning
3. **Avalia o itinerário** usando múltiplas funções de validação
4. **Revisa o itinerário** usando o ItineraryRevisionAgent com ciclo ReAct
5. **Valida o resultado final** garantindo que atende a todos os critérios
6. **Gera narração** da viagem planejada

## 🔧 Componentes Principais

- **models.py**: Modelos Pydantic para validação de dados
- **agents.py**: ItineraryAgent e ItineraryRevisionAgent
- **tools.py**: Ferramentas (calculadora, API de atividades, avaliações)
- **evaluations.py**: Funções de avaliação de qualidade
- **main.py**: Script principal de execução
- **project_lib.py**: Biblioteca utilitária com dados simulados

## 📊 Critérios de Avaliação

O sistema verifica automaticamente:
- ✅ Datas de chegada e partida corretas
- ✅ Custo total preciso e dentro do orçamento
- ✅ Atividades correspondem aos dados reais (não alucinadas)
- ✅ Cobertura de interesses dos viajantes
- ✅ Compatibilidade entre atividades e clima
- ✅ Incorporação do feedback: "pelo menos 2 atividades por dia"

## 🎓 Técnicas de IA Demonstradas

- **Role-Based Prompting**: Agentes assumem papéis especializados
- **Chain-of-Thought Reasoning**: Planejamento passo a passo
- **ReAct Prompting**: Ciclo Pensamento → Ação → Observação
- **Feedback Loops**: Auto-avaliação e refinamento iterativo
- **Tool Integration**: Uso de ferramentas externas pelos agentes

## 🚨 Solução de Problemas

### Erro de API Key
```
❌ ERRO: Configure sua chave da API OpenAI no arquivo config.env
```
**Solução**: Edite `config.env` e substitua `your_openai_api_key_here` pela sua chave real.

### Erro de Módulos
```
ModuleNotFoundError: No module named 'pydantic'
```
**Solução**: Ative o ambiente virtual: `source venv/bin/activate`

### Erro de Dependências
```
error: externally-managed-environment
```
**Solução**: Use o ambiente virtual criado: `source venv/bin/activate`

## 📈 Resultados Esperados

Ao executar com sucesso, você verá:
- ✅ Itinerário inicial gerado
- ✅ Avaliação do itinerário inicial
- ✅ Revisão usando ciclo ReAct
- ✅ Avaliação final com sucesso
- ✅ Plano de viagem detalhado
- ✅ Narração da viagem

## 🎉 Sucesso!

Se todos os testes passarem e o sistema executar sem erros, você terá um sistema completo de planejamento de viagens baseado em IA funcionando perfeitamente!
