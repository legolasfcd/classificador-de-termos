import os
import time
import openai
import pandas as pd

# Configurar a chave da API via variável de ambiente
openai.api_key = os.getenv("OPENAI_API_KEY")

# Leitura dos dados
df_termos = pd.read_excel("termos.xlsx")
termos = df_termos["Termo"].dropna().tolist()

# Leitura da ontologia
df_categorias = pd.read_excel("categorias.xlsx")
classes_validas = df_categorias["Classe"].dropna().unique().tolist()
subclasses_validas = df_categorias["Subclasse"].dropna().unique().tolist()
classes_str = ", ".join(classes_validas)
subclasses_str = ", ".join(subclasses_validas)

# Parâmetros
bloco_tamanho = 30
modelo = "gpt-3.5-turbo"
resultados = []

# Processamento por blocos
for i in range(0, len(termos), bloco_tamanho):
    lote = termos[i:i + bloco_tamanho]

    prompt = f"""
Você é um classificador semântico de termos, com base em uma **ontologia fechada** composta por categorias e subcategorias pré-estabelecidas.

Seu objetivo é:
- Interpretar o **significado e conceito** de cada termo fornecido
- Atribuir a **Classe** e a **Subclasse** mais apropriadas, com base na ontologia abaixo
- Respeitar rigorosamente os nomes disponíveis (sem criar novos termos)

📚 Esta é uma estrutura ontológica — ou seja, um modelo de conhecimento onde os conceitos e relações já estão definidos. Você deve encontrar o melhor encaixe para o significado de cada termo, e **não criar categorias novas**, mesmo que alguma pareça mais precisa.

✔️ Classes permitidas:
{classes_str}

✔️ Subclasses permitidas:
{subclasses_str}

⚠️ Se um termo não puder ser classificado com precisão dentro da ontologia, retorne:
Termo | - | -

⚠️ Não crie novas Classes nem Subclasses.
⚠️ Não altere nomes existentes. Use apenas as Classes e Subclasses listadas.

📌 Formato obrigatório:
Termo | Classe | Subclasse

Termos:
{chr(10).join(f"- {termo}" for termo in lote)}

Responda apenas com a tabela. Nada mais.
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
