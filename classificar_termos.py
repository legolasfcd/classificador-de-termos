import openai
import pandas as pd
import time
import os

# Carregar chave da API do segredo de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carregar o arquivo Excel com os termos
df = pd.read_excel("termos.xlsx")
termos = df["Termo"].dropna().tolist()

# Dividir em blocos
bloco_tamanho = 30
resultados = []

for i in range(0, len(termos), bloco_tamanho):
    lote = termos[i:i+bloco_tamanho]
    prompt = f"""
Classifique semanticamente os seguintes termos com base em um modelo de conhecimento que possui categorias e subcategorias.

Para cada termo, atribua:
- uma Classe (categoria principal)
- uma Subclasse (subcategoria mais apropriada)
- Se necessário, crie uma subclasse nova e adicione um asterisco (*)

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
        resposta = response['choices'][0]['message']['content']
        for linha in resposta.strip().split("\n"):
            if "|" in linha:
                partes = [p.strip() for p in linha.split("|")]
                if len(partes) == 3:
                    resultados.append(partes)
        time.sleep(1)
    except Exception as e:
        print(f"Erro no bloco {i}: {e}")

# Gerar planilha com os resultados
df_resultado = pd.DataFrame(resultados, columns=["Termo", "Classe", "Subclasse"])
df_resultado.to_excel("resultado.xlsx", index=False)
print("Classificação concluída e salva em resultado.xlsx")
