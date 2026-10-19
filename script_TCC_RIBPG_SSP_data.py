# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 14:29:02 2025

@author: malu_
"""

# -*- coding: utf-8 -*-

"Script elaborado como parte do Artigo DESEMPENHO DO BANCO DE PERFIS GENÉTICOS DE SÃO PAULO E A RELAÇÃO COM OS INDICADORES DE CRIMINALIDADE DO ESTADO, submetido para apreciação e publicação na Revista Brasileira de Criminalística (RBC)"


#%% IMPORTAR PACOTES

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import numpy as np
import pymannkendall as mk

#%% GRÁFICOS HITS RIBPG e BPG/SP

# Ler o arquivo Excel ou CSV
df = pd.read_excel('hits2python.xlsx', sheet_name='Planilha1')

# Definir colunas
df.columns = ['Número do Relatório', 'Banco', 'Hit Rate', 'Forensic Hit Rate', 'Índice de Retorno', 'Representatividade Criminal']

# Configurar estilo
sns.set(style='whitegrid', palette='colorblind')

variaveis = ['Hit Rate', 'Forensic Hit Rate', 'Índice de Retorno', 'Representatividade Criminal']

for var in variaveis:
    plt.figure(figsize=(8, 4))
    sns.lineplot(data=df, x='Número do Relatório', y=var, hue='Banco', marker='o')
    plt.title(f'Gráfico de {var}')
    plt.xlabel('Número do Relatório')
    plt.ylabel(var)
    plt.legend(title='Banco', loc='best')
    plt.tight_layout()
    
    # Salvar cada gráfico individualmente
    nome_arquivo = f'grafico_{var}.png'
    plt.savefig(nome_arquivo, dpi=1200, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {nome_arquivo}")
    
    plt.close()  # fecha a figura para liberar memória

print("\nTodos os gráficos foram salvos com sucesso!")


#%% CORRELAÇÕES HITS E PERFIS - DIFERENÇA


# Ler o novo arquivo
df = pd.read_excel('correlaçãohits2python.xlsx', sheet_name='semestral')

# Definir Colunas
df.columns = ['Número do Relatório', 'Banco', 'Referência Criminal', 'Vestígios', 'Soma Perfis', 'Forensic Hit', 'Offender Hit', 'Soma Hits']

# Dicionário com as correlações desejadas
correlacoes = {
    'Correlação 1 (Col7 vs Col3)': ('Offender Hit', 'Referência Criminal'),
    'Correlação 2 (Col7 vs Col4)': ('Offender Hit', 'Vestígios'),
    'Correlação 3 (Col6 vs Col4)': ('Forensic Hit', 'Vestígios'),
    'Correlação 4 (Col8 vs Col5)': ('Soma Hits', 'Soma Perfis')
}

# Lista para armazenar resultados
resultados = []

# Loop pelas tags (categorias da coluna 2)
for tag, grupo in df.groupby('Banco'):
    for nome_corr, (col_a, col_b) in correlacoes.items():
        # Remove linhas com valores ausentes
        grupo_limpo = grupo[[col_a, col_b]].dropna()
        
        if len(grupo_limpo) >= 2:  # precisa de pelo menos 2 pontos
            r, p = pearsonr(grupo_limpo[col_a], grupo_limpo[col_b])
        else:
            r, p = None, None
        
        resultados.append({
            'Tag': tag,
            'Correlação': nome_corr,
            'Variável X': col_a,
            'Variável Y': col_b,
            'r (coeficiente)': r,
            'p-valor': p
        })

# Converter resultados em DataFrame
df_resultados = pd.DataFrame(resultados)

# Mostrar na tela
print(df_resultados)

# Salvar em Excel
df_resultados.to_excel('resultados_correlacoes_pearson_DIFF.xlsx', index=False)
print("\nArquivo 'resultados_correlacoes_pearson_DIFF.xlsx' salvo com sucesso!")


#%% SÉRIES TEMPORAIS SSP/SP E BPG/SP - DIFERENÇA - MAIS TESTE DE MANN-KENDALL
# com linhas de tendência por média móvel e tendência linear
 
    
# Ler o arquivo Excel 
df = pd.read_excel('sériestemporais2python.xlsx')

# Ajuste os nomes das colunas conforme seu arquivo
df.columns = ['Período', 'Banco', 'Vida', 'Patrimônio e Vida', 'Sexual', 'Patrimônio']

# Converter a coluna de período para categoria ordenada
df['Período'] = pd.Categorical(df['Período'], categories=df['Período'].unique(), ordered=True)

# Lista de variáveis
variaveis = ['Vida', 'Patrimônio e Vida', 'Sexual', 'Patrimônio']

# Estilo dos gráficos
sns.set(style="whitegrid", palette="colorblind")

for var in variaveis:
    tags = df['Banco'].unique()

    fig, axes = plt.subplots(len(tags), 1, figsize=(10, 6 * len(tags)), sharex=True)
    if len(tags) == 1:
        axes = [axes]

    for ax, tag in zip(axes, tags):
        grupo = df[df['Banco'] == tag].sort_values('Período')

        # Média móvel
        grupo['Tendência'] = grupo[var].rolling(window=3, center=True, min_periods=1).mean()

        # Tendência linear
        x_numeric = np.arange(len(grupo))
        coef = np.polyfit(x_numeric, grupo[var], 1)  # coeficientes da reta
        linha_linear = np.polyval(coef, x_numeric)

        # Plotar séries
        ax.plot(grupo['Período'], grupo[var], label='Original', marker='o')
        ax.plot(grupo['Período'], grupo['Tendência'], label='Média móvel (3)', linewidth=2)
        ax.plot(grupo['Período'], linha_linear, label='Tendência linear', linestyle='--', linewidth=2, color='gray')

        # Títulos e legendas
        ax.set_title(f'Série Temporal e Tendência {tag} - Natureza Criminal: {var}', fontsize=18)
        ax.set_ylabel('Quantidade', fontsize=18)
        ax.legend(fontsize=16)
        ax.grid(True)

        # Ajustar tamanho dos ticks
        ax.tick_params(axis='x', rotation=45, labelsize=16)
        ax.tick_params(axis='y', labelsize=16)

    plt.xlabel('Período', fontsize=18)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Salvar gráfico
    nome_arquivo = f"serie_tendencia_dupla_{var}.png"
    plt.savefig(nome_arquivo, dpi=1200, bbox_inches='tight')
    print(f"✅ Gráfico salvo: {nome_arquivo}")

    plt.close()
   
    
# Teste de Mann-Kendall 

resultados_mk = []

for var in variaveis:
    for tag in df['Banco'].unique():
        grupo = df[df['Banco'] == tag]
        serie = grupo[var].dropna().values

        if len(serie) >= 3:  # precisa de pelo menos 3 pontos
            result = mk.original_test(serie)

            # Algumas versões retornam tuple, outras retornam objeto
            # Tentamos capturar tudo de forma segura
            try:
                trend = result.trend
                h = result.h
                p = result.p
                z = result.z if hasattr(result, "z") else getattr(result, "Z", None)
                s = result.s if hasattr(result, "s") else getattr(result, "S", None)
                tau = result.tau if hasattr(result, "tau") else getattr(result, "Tau", None)
                slope = result.slope if hasattr(result, "slope") else getattr(result, "Slope", None)
            except AttributeError:
                # Se for uma namedtuple ou tuple comum
                trend, h, p, z, Tau, s, slope, *_ = result
                tau = Tau

            # Se ainda faltar S ou Z, calcular manualmente
            if s is None or z is None:
                n = len(serie)
                s = 0
                for k in range(n - 1):
                    for j in range(k + 1, n):
                        s += np.sign(serie[j] - serie[k])

                var_s = (n * (n - 1) * (2 * n + 5)) / 18
                if s > 0:
                    z = (s - 1) / np.sqrt(var_s)
                elif s < 0:
                    z = (s + 1) / np.sqrt(var_s)
                else:
                    z = 0

            # Interpretação
            if h and trend == "increasing":
                tendencia = "Sim"
                direcao = "Crescente"
            elif h and trend == "decreasing":
                tendencia = "Sim"
                direcao = "Decrescente"
            else:
                tendencia = "Não"
                direcao = "Sem tendência"
        else:
            s = z = p = tau = slope = None
            tendencia = direcao = "Dados insuficientes"

        resultados_mk.append({
            "Banco": tag,
            "Variável": var,
            "S": s,
            "Z": z,
            "p-valor": p,
            "Tau de Kendall": tau,
            "Declividade (Slope)": slope,
            "Tendência significativa (p<0.05)": tendencia,
            "Direção da tendência": direcao
        })

# Converter e salvar
df_mk = pd.DataFrame(resultados_mk)
df_mk.to_excel("resultados_mann_kendall.xlsx", index=False)
print("\n✅ Resultados do teste de Mann-Kendall salvos em 'resultados_mann_kendall.xlsx'")

        
#%% CORRELAÇÕES SÉRIES TEMPORAIS SSP/SP E BPG/SP - DIFERENÇA 


# Ler o arquivo Excel
df = pd.read_excel('correlaçãoRIBPGSSP2python.xlsx')

# Definir nomes das colunas
df.columns = [
    'Período',
    'Vida (SSP)', 'Vida (BPG SP)',
    'Patrimônio e Vida (SSP)', 'Patrimônio e Vida (BPG SP)',
    'Sexual (SSP)', 'Sexual (BPG SP)',
    'Patrimônio (SSP)', 'Patrimônio (BPG SP)'
]

# Dicionário com pares de colunas a correlacionar
correlacoes = {
    'Correlação 1': ('Vida (SSP)', 'Vida (BPG SP)'),
    'Correlação 2': ('Patrimônio e Vida (SSP)', 'Patrimônio e Vida (BPG SP)'),
    'Correlação 3': ('Sexual (SSP)', 'Sexual (BPG SP)'),
    'Correlação 4': ('Patrimônio (SSP)', 'Patrimônio (BPG SP)')
}

# Calcular correlações
resultados = []

for nome_corr, (col_a, col_b) in correlacoes.items():
    grupo_limpo = df[[col_a, col_b]].dropna()

    if len(grupo_limpo) >= 2:  # pelo menos 2 pontos
        r, p = pearsonr(grupo_limpo[col_a], grupo_limpo[col_b])
    else:
        r, p = None, None

    resultados.append({
        'Correlação': nome_corr,
        'Variável X': col_a,
        'Variável Y': col_b,
        'r (coeficiente de Pearson)': r,
        'p-valor': p
    })

# Converter resultados em DataFrame
df_resultados = pd.DataFrame(resultados)

# Mostrar na tela
print(df_resultados)

# Salvar em Excel
df_resultados.to_excel('resultados_correlacoes_pearson_SÉRIES.xlsx', index=False)
print("\n✅ Arquivo 'resultados_correlacoes_pearson_SÉRIES.xlsx' salvo com sucesso!")


#%% FIM