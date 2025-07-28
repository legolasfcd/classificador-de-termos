import openai
import os
import pandas as pd
import time

# Configurar chave da API (via variável de ambiente segura)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carregar arquivos
df = pd.read_excel("termos.xlsx")
categorias_df = pd.read_excel("categorias.xlsx")

# Obter listas de classes e subclasses válidas
classes_validas = set(categorias_df["Classe"].dropna().unique())
subclasses_validas = set(categorias_df["Subclasse"].dropna().unique())

# Parâmetros
modelo = "gpt-3.5-turbo"
bloco_tamanho = 30
termos = df["Termo"].dropna().tolist()
resultados = []

# Loop por blocos
for i in range(0, len(termos), bloco_tamanho):
    lote = termos[i:i+bloco_tamanho]

    prompt = f"""
Você é um classificador de termos. Seu objetivo é analisar semanticamente os termos recebidos e atribuir a cada um deles uma Classe e uma Subclasse, com base em um modelo de conhecimento pré-definido.

Suas regras:
- Use sempre uma Classe e uma Subclasse para cada termo.
- As Classes e Subclasses válidas estão na tabela fornecida pelo conhecimento (documento categorias.xlsx).
- Se você sugerir uma nova Subclasse que não estiver na lista conhecida, adicione um asterisco (*) ao final da Subclasse.
- Mantenha o nome original do termo.
- Utilize este formato: Termo | Classe | Subclasse

Termos:
{chr(10).join(f"- {termo}" for termo in lote)}

Retorne apenas a tabela formatada.
"""

    try:
        resposta = openai.ChatCompletion.create(
            model=modelo,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        texto = resposta.choices[0].message["content"]

        # Parse da resposta
        for linha in texto.split("\n"):
            if "|" in linha:
                partes = [p.strip() for p in linha.split("|")]
                if len(partes) == 3:
                    termo, classe, subclasse = partes
                    if classe not in classes_validas:
                        classe += "*"  # Classe nova
                    if subclasse not in subclasses_validas:
                        subclasse += "*"  # Subclasse nova
                    resultados.append([termo, classe, subclasse])

        time.sleep(1)  # Evitar rate limit

    except Exception as e:
        print(f"Erro no bloco {i}: {e}")

# Salvar resultado
resultado_df = pd.DataFrame(resultados, columns=["Termo", "Classe", "Subclasse"])
resultado_df.to_excel("resultado.xlsx", index=False)

print("Classificação concluída com sucesso. Arquivo salvo como resultado.xlsx.")
