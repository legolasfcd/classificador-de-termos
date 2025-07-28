import os
import time
import openai
import pandas as pd

# Configurar chave da API com variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carregar termos
df_termos = pd.read_excel("termos.xlsx")
termos = df_termos["Termo"].dropna().tolist()

# Carregar estrutura de categorias
df_categorias = pd.read_excel("categorias.xlsx")
classes_validas = df_categorias["Classe"].dropna().unique().tolist()
subclasses_validas = df_categorias["Subclasse"].dropna().unique().tolist()

# Gerar strings para injetar no prompt
classes_str = ", ".join(classes_validas)
subclasses_str = ", ".join(subclasses_validas)

# Parâmetros
bloco_tamanho = 30
modelo = "gpt-3.5-turbo"
resultados = []

# Loop de classificação por blocos
for i in range(0, len(termos), bloco_tamanho):
    lote = termos[i:i + bloco_tamanho]

    prompt = f"""
Você é um classificador de termos. Para cada termo abaixo, atribua:

- Uma **Classe** entre as seguintes: {classes_str}
- Uma **Subclasse** entre as seguintes: {subclasses_str}

Se nenhuma subclasse for apropriada, crie uma nova subclasse e marque com asterisco (*).

Formato da resposta:
Termo | Classe | Subclasse

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
        print(f"\n🔹 Bloco {i//bloco_tamanho + 1} processado")
        print(resposta)

        for linha in resposta.strip().split("\n"):
            if "|" in linha:
                partes = [p.strip() for p in linha.split("|")]
                if len(partes) == 3:
                    termo, classe, subclasse = partes

                    # Verifica se subclasse não reconhecida foi criada
                    if subclasse not in subclasses_validas:
                        print(f"⚠️ Nova subclasse sugerida: {subclasse}")

                    resultados.append([termo, classe, subclasse])

        time.sleep(1)

    except Exception as e:
        print(f"❌ Erro no bloco {i // bloco_tamanho + 1}: {e}")

# Salvar resultados
if resultados:
    df_resultado = pd.DataFrame(resultados, columns=["Termo", "Classe", "Subclasse"])
    df_resultado.to_excel("resultado-classificado.xlsx", index=False)
    df_resultado.to_csv("resultado-classificado.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ Classificação finalizada. {len(df_resultado)} termos salvos.")
else:
    print("\n⚠️ Nenhum resultado classificado foi gerado.")
