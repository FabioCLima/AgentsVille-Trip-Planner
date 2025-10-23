# AgentsVille Trip Planner - Ambiente Local

## 📋 O que foi adaptado

✅ **Removido**: Todas as referências ao workspace da Udacity  
✅ **Removido**: Endpoint do Vocareum  
✅ **Adaptado**: Cliente OpenAI para usar sua API key local  
✅ **Adaptado**: Modelos para usar os modelos reais da OpenAI (gpt-4o, gpt-4o-mini, etc)  
✅ **Adicionado**: Carregamento automático do arquivo .env

## 🚀 Como executar

### 1. Pré-requisitos

Certifique-se de ter o Python 3.13+ instalado e um ambiente virtual configurado:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

O notebook instalará automaticamente as dependências necessárias, mas você também pode instalá-las manualmente:

```bash
pip install json-repair==0.47.1 numexpr==2.11.0 openai==1.74.0 pandas==2.3.0 pydantic==2.11.7 python-dotenv==1.1.0
```

### 3. Configurar .env

O arquivo `.env` já está incluído com suas credenciais:

```
OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-dev-...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=AgentsVille Trip Planner - Fabio Lima
```

**⚠️ IMPORTANTE**: Verifique se você tem créditos suficientes na sua conta da OpenAI!

### 4. Executar o notebook

```bash
jupyter notebook project_starter_local.ipynb
# ou
code project_starter_local.ipynb  # se estiver usando VS Code
```

## 📝 Arquivos incluídos

- `project_starter_local.ipynb` - Notebook principal (adaptado para ambiente local)
- `.env` - Variáveis de ambiente com suas credenciais
- `pyproject.toml` - Configuração do projeto
- `project_lib.py` - Biblioteca auxiliar (certifique-se de que está no mesmo diretório)
- `README.md` - Este arquivo

## 🔧 Alterações principais

### Antes (Udacity):
```python
WORKSPACE_DIRECTORY = "/workspace"
if os.path.exists(WORKSPACE_DIRECTORY):
    sys.path.append(WORKSPACE_DIRECTORY)
    
client = OpenAI(
    base_url="https://openai.vocareum.com/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
)

MODEL = OpenAIModel.GPT_41_MINI  # Modelo Udacity
```

### Depois (Local):
```python
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = OpenAIModel.GPT_4O_MINI  # Modelo OpenAI real
```

## 🎯 Modelos disponíveis

O notebook está configurado para usar os modelos reais da OpenAI:

- `gpt-4o` - Modelo mais poderoso
- `gpt-4o-mini` - Rápido e acessível ✅ (recomendado)
- `gpt-4-turbo` - Alternativa robusta  
- `gpt-3.5-turbo` - Mais econômico

Você pode alterar o modelo na célula onde `MODEL` é definido.

## ⚠️ Troubleshooting

### Erro: "Insufficient budget available"
**Solução**: Seu crédito da API da OpenAI acabou. Adicione créditos em https://platform.openai.com/account/billing

### Erro: "API Key not found"
**Solução**: Verifique se o arquivo `.env` está no mesmo diretório do notebook e se a chave está correta.

### Erro: "project_lib not found"
**Solução**: Certifique-se de que o arquivo `project_lib.py` está no mesmo diretório do notebook.

## 📞 Próximos passos

1. ✅ Execute a primeira célula para carregar o .env
2. ✅ Execute a segunda célula para configurar o cliente OpenAI
3. ✅ Continue executando as células sequencialmente
4. ✅ O notebook irá guiá-lo através de todo o processo!

Bom projeto! 🎉
