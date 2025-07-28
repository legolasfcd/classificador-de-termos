import os
import openai
import pandas as pd
import time

# Chave da API via variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carregar os arquivos de entrada
df_termos = pd.read_excel("termos.xlsx")
df_categorias = pd.read_excel("categorias.xlsx")

# Extrair termos da planilha
termos = df_termos["Termo"].dropna().tolist()

# Gerar string com as categorias e subcategorias no formato "- Classe > Subclasse"
categorias_subcategorias = "\n".join(
    df_categorias.apply(lambda row: f"- {row['Classe']} > {row['Subclasse']}", axis=1)
)

# Configurações
bloco_tamanho = 30
resultados = []

# Processamento por blocos
for i in range(0, len(termos), bloco_tamanho):
    lote = termos[i:i + bloco_tamanho]

    prompt = f"""
Você deve classificar semanticamente os seguintes termos com base nas categorias abaixo.

Categorias válidas:
{categorias_subcategorias}

Para cada termo, atribua:
- uma Classe (categoria principal)
- uma Subclasse (subcategoria listada acima)

Se nenhuma subclasse for apropriada, crie uma nova e marque com asterisco (*)

Formato da resposta: Termo | Classe | Subclasse

Termos:
{chr(10).join(f"- {termo}" for termo in lote)}

Responda apenas com a tabela.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        resposta = response["choices"][0]["message"]["content"]

        for linha in resposta.strip().split("\n"):
            if "|" in linha:
                partes = [p.strip() for p in linha.split("|")]
                if len(partes) == 3:
                    resultados.append(partes)

        time.sleep(1)  # Evita atingir o rate limit da API

    except Exception as e:
        print(f"Erro no bloco {i}:", e)

# Gerar a planilha final com os resultados
df_resultado = pd.DataFrame(resultados, columns=["Termo", "Classe", "Subclasse"])
df_resultado.to_excel("resultado.xlsx", index=False)
print("Classificação concluída com sucesso. Arquivo salvo como resultado.xlsx.")
