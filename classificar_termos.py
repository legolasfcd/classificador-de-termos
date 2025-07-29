import os
import time
import openai
import pandas as pd

# Configurar a chave da API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carregar dados
termos_df = pd.read_excel("termos.xlsx")
termos = termos_df["Termo"].dropna().tolist()

categorias_df = pd.read_excel("categorias.xlsx")

# Gerar pares Classe > Subclasse
linhas_formatadas = categorias_df.apply(lambda row: f"- {row['Classe']} > {row['Subclasse']}", axis=1)
categorias_relacionadas = "\n".join(linhas_formatadas)

# Criar dicionário Classe -> Subclasses válidas (uso futuro se necessário)
classe_para_subclasses = (
    categorias_df.dropna()
    .groupby("Classe")["Subclasse"]
    .apply(set)
    .to_dict()
)

# Parâmetros
bloco_tamanho = 30
modelo = "gpt-3.5-turbo"
resultados = []

# Processamento por blocos
for i in range(0, len(termos), bloco_tamanho):
    lote = termos[i:i + bloco_tamanho]

    prompt = f"""
Você deve classificar semanticamente os termos a seguir com base em uma lista **fechada de pares Classe > Subclasse**. Para cada termo, selecione:

- A Classe mais apropriada (categoria principal)
- A Subclasse correspondente, vinculada à Classe escolhida

⚠️ Cada Subclasse só pode ser usada com a Classe à qual ela está associada. Não combine livremente. Use **apenas os pares Classe > Subclasse listados abaixo**.

Categorias permitidas:
{categorias_relacionadas}

Se o termo **não se encaixar em nenhuma das combinações listadas**, retorne:
Termo | - | -

⚠️ Não crie novas classes ou subclasses.
⚠️ Não traduza ou altere nomes.
⚠️ Siga exatamente a estrutura: Termo | Classe | Subclasse

Termos:
{chr(10).join(f"- {termo}" for termo in lote)}

Responda apenas com a tabela.
"""

    try:
        response = openai.ChatCompletion.create(
            model=modelo,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        resposta = response.choices[0].message["content"]
        print(f"\n🔹 Bloco {i // bloco_tamanho + 1} processado")
        print(resposta)

        for linha in resposta.strip().split("\n"):
            if "|" in linha:
                partes = [p.strip() for p in linha.split("|")]
                if len(partes) == 3:
                    resultados.append(partes)

        time.sleep(1)

    except Exception as e:
        print(f"❌ Erro no bloco {i // bloco_tamanho + 1}: {e}")

# Salvar resultado
if resultados:
    df_resultado = pd.DataFrame(resultados, columns=["Termo", "Classe", "Subclasse"])
    df_resultado.to_excel("resultado-classificado.xlsx", index=False)
    df_resultado.to_csv("resultado-classificado.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ Classificação finalizada. {len(df_resultado)} termos salvos.")
else:
    print("\n⚠️ Nenhum resultado classificado foi gerado.")
