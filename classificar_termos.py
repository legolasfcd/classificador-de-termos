import os
import openai
import pandas as pd
import time

# Configurar chave da API (leitura da variável de ambiente)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Leitura dos dados
df = pd.read_excel("termos.xlsx")
termos = df["Termo"].dropna().tolist()

# Parâmetros
bloco_tamanho = 30
resultados = []

# Processamento em blocos
for i in range(0, len(termos), bloco_tamanho):
    lote = termos[i:i + bloco_tamanho]
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
        resultado = response.choices[0].message.content
        print(f"\n🔹 Bloco {i // bloco_tamanho + 1} processado:")
        print(resultado)

        for linha in resultado.strip().split("\n"):
            if "|" in linha:
                partes = [p.strip() for p in linha.split("|")]
                if len(partes) == 3:
                    resultados.append(partes)

    except Exception as e:
        print(f"❌ Erro no bloco {i // bloco_tamanho + 1}: {e}")
    
    time.sleep(1)  # Respeitar limites de requisição

# Verificação final
print(f"\n🔎 Total de termos classificados: {len(resultados)}")

# Geração dos arquivos de saída
if resultados:
    df_resultado = pd.DataFrame(resultados, columns=["Termo", "Classe", "Subclasse"])
    df_resultado.to_excel("resultado-classificado.xlsx", index=False)
    df_resultado.to_csv("resultado-classificado.csv", index=False, encoding="utf-8-sig")
    print("\n✅ Classificação concluída. Arquivos gerados com sucesso.")
else:
    print("\n⚠️ Nenhum resultado foi gerado. Verifique os logs.")
