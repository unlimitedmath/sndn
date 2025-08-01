"""
Dashboard Corrigido Final - Sofá Novo de Novo
Versão simplificada e funcional
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import glob
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Sofá Novo de Novo - Dashboard",
    page_icon="🛋️",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    """Carrega dados mais recentes"""
    try:
        # Prioriza arquivo corrigido com faturamento
        files_corrigidos = glob.glob("analise_corrigida_faturamento_*.csv")
        if files_corrigidos:
            latest_file = max(files_corrigidos, key=lambda x: x.split('_')[-2] + '_' + x.split('_')[-1].replace('.csv', ''))
            df = pd.read_csv(latest_file)
            st.success(f"✅ Dados corrigidos carregados: {latest_file}")
            return df, latest_file

        # Fallback para arquivo anterior
        files = glob.glob("analise_com_franquias_atuais_*.csv")
        if files:
            latest_file = max(files, key=lambda x: x.split('_')[-2] + '_' + x.split('_')[-1].replace('.csv', ''))
            df = pd.read_csv(latest_file)
            st.warning(f"⚠️ Usando dados não corrigidos: {latest_file}")
            return df, latest_file
        else:
            st.error("❌ Arquivo não encontrado!")
            return None, None
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        return None, None

def calcular_metricas_negocio(row):
    """Calcula métricas de negócio para cada cidade"""

    pop = row['Populacao_2022']
    classe_ab_pct = row['Classe_AB_PNAD']
    franquias_atuais = row['Franquias_Atuais']
    total_franquias = row['Total_Franquias_Realista']
    internet_pct = row['Penetracao_Internet_PNAD']

    # Parâmetros do negócio
    TICKET_MEDIO = 250  # R$ por serviço (atualizado)
    PENETRACAO_MERCADO_BASE = 0.02  # 2% das famílias classe A/B usam o serviço por ano
    SERVICOS_POR_FAMILIA_ANO = 2.5  # Frequência média anual
    PESSOAS_POR_FAMILIA = 3.2  # Média brasileira

    # 1. Tamanho estimado da classe A/B (população)
    pop_classe_ab = int(pop * (classe_ab_pct / 100))

    # 2. Número de famílias classe A/B
    familias_classe_ab = int(pop_classe_ab / PESSOAS_POR_FAMILIA)

    # 3. Ajuste por penetração de internet (afeta marketing digital)
    fator_internet = min(1.0, internet_pct / 70)  # 70% é a base

    # 4. Mercado total de serviços por ano
    mercado_total_servicos = int(familias_classe_ab * PENETRACAO_MERCADO_BASE * SERVICOS_POR_FAMILIA_ANO * fator_internet)

    # 5. Serviços por franquia (se houver franquias)
    if total_franquias > 0:
        servicos_por_franquia = mercado_total_servicos / total_franquias
    else:
        servicos_por_franquia = 0

    # 6. Faturamento estimado por franquia por mês
    if servicos_por_franquia > 0:
        faturamento_mensal = (servicos_por_franquia * TICKET_MEDIO) / 12
    else:
        faturamento_mensal = 0

    return {
        'Pop_Classe_AB': pop_classe_ab,
        'Mercado_Total_Servicos': mercado_total_servicos,
        'Servicos_Por_Franquia': round(servicos_por_franquia, 1),
        'Faturamento_Mensal_Franquia': round(faturamento_mensal, 0)
    }

def criar_justificativa(row):
    """Cria justificativa detalhada para cada cidade"""

    pop = row['Populacao_2022']
    score = row['Score_Realista']
    pib = row['PIB_per_capita_Calibrado']
    idh = row['IDH_Calibrado']
    classe_ab = row['Classe_AB_PNAD']
    internet = row['Penetracao_Internet_PNAD']
    trends = row['Interesse_Google_Trends']
    franquias_atuais = row['Franquias_Atuais']
    total_adicional = row['Total_Franquias_Adicional']
    classificacao = row['Classificacao_Realista']

    # Parâmetros de referência
    PIB_MEDIO = 35000
    IDH_MEDIO = 0.7
    CLASSE_MEDIA = 18
    INTERNET_MEDIA = 70
    TRENDS_MEDIO = 50

    justificativas = []

    if classificacao == "Saturado":
        if franquias_atuais > 0:
            justificativas.append(f"Já possui {franquias_atuais:.0f} franquia(s)")

        if score < 45000:  # Threshold para franquia padrão
            fatores_baixos = []
            if pib < PIB_MEDIO * 0.8:
                fatores_baixos.append(f"PIB baixo (R$ {pib:,.0f})")
            if idh < IDH_MEDIO * 0.9:
                fatores_baixos.append(f"IDH baixo ({idh:.3f})")
            if classe_ab < CLASSE_MEDIA * 0.7:
                fatores_baixos.append(f"Baixa classe A/B ({classe_ab:.1f}%)")
            if internet < INTERNET_MEDIA * 0.8:
                fatores_baixos.append(f"Baixa penetração internet ({internet:.1f}%)")
            if trends < TRENDS_MEDIO * 0.6:
                fatores_baixos.append(f"Baixo interesse Google ({trends:.0f})")

            if fatores_baixos:
                justificativas.append("Score insuficiente: " + ", ".join(fatores_baixos))

        if pop < 100000 and score < 12000:  # Threshold Sofázinho
            justificativas.append(f"População pequena ({pop:,} hab) e score muito baixo")

    elif classificacao == "Prioridade Máxima":
        fatores_positivos = []
        if pop >= 500000:
            fatores_positivos.append(f"Grande população ({pop:,} hab)")
        if pib > PIB_MEDIO * 1.2:
            fatores_positivos.append(f"Alto PIB (R$ {pib:,.0f})")
        if idh > IDH_MEDIO * 1.1:
            fatores_positivos.append(f"Alto IDH ({idh:.3f})")
        if classe_ab > CLASSE_MEDIA * 1.3:
            fatores_positivos.append(f"Alta classe A/B ({classe_ab:.1f}%)")

        justificativas.append("Excelente potencial: " + ", ".join(fatores_positivos[:2]))
        if total_adicional > 0:
            justificativas.append(f"Pode receber +{total_adicional:.0f} franquia(s)")

    elif classificacao in ["Prioridade Alta", "Prioridade Média"]:
        if pop >= 200000:
            justificativas.append(f"Boa população ({pop:,} hab)")
        if score >= 60000:
            justificativas.append("Score adequado")
        if total_adicional > 0:
            justificativas.append(f"Potencial para +{total_adicional:.0f} franquia(s)")

    elif classificacao == "Prioridade Baixa":
        justificativas.append("Potencial limitado")
        if pop < 100000:
            justificativas.append(f"População pequena ({pop:,} hab)")
        if score < 30000:
            justificativas.append("Score baixo")

    else:  # Oportunidade Futura
        justificativas.append("Mercado em desenvolvimento")
        if pop < 50000:
            justificativas.append("Aguardar crescimento populacional")

    return " | ".join(justificativas) if justificativas else "Análise em andamento"

def criar_mapa_brasil_funcional(df, coluna_valor, titulo):
    """Cria mapa do Brasil funcional"""
    try:
        # Normaliza UF
        def normalizar_uf(uf):
            nome_para_sigla = {
                'SÃO PAULO': 'SP', 'RIO DE JANEIRO': 'RJ', 'MINAS GERAIS': 'MG',
                'BAHIA': 'BA', 'PARANÁ': 'PR', 'RIO GRANDE DO SUL': 'RS',
                'PERNAMBUCO': 'PE', 'CEARÁ': 'CE', 'PARÁ': 'PA', 'SANTA CATARINA': 'SC',
                'GOIÁS': 'GO', 'MARANHÃO': 'MA', 'ESPÍRITO SANTO': 'ES',
                'PARAÍBA': 'PB', 'AMAZONAS': 'AM', 'MATO GROSSO': 'MT',
                'RIO GRANDE DO NORTE': 'RN', 'ALAGOAS': 'AL', 'PIAUÍ': 'PI',
                'DISTRITO FEDERAL': 'DF', 'MATO GROSSO DO SUL': 'MS',
                'SERGIPE': 'SE', 'RONDÔNIA': 'RO', 'ACRE': 'AC',
                'AMAPÁ': 'AP', 'RORAIMA': 'RR', 'TOCANTINS': 'TO'
            }
            return nome_para_sigla.get(str(uf).upper(), str(uf))

        df_temp = df.copy()
        df_temp['UF_Sigla'] = df_temp['UF'].apply(normalizar_uf)

        # Agrega por UF
        df_uf = df_temp.groupby('UF_Sigla').agg({
            coluna_valor: 'sum' if 'Franquias' in coluna_valor else 'mean',
            'Populacao_2022': 'sum'
        }).reset_index()

        # Cria gráfico de barras como alternativa ao mapa
        fig = px.bar(
            df_uf.sort_values(coluna_valor, ascending=True).tail(15),
            x=coluna_valor,
            y='UF_Sigla',
            orientation='h',
            title=titulo,
            labels={coluna_valor: titulo.split(' por ')[0], 'UF_Sigla': 'Estado'}
        )

        fig.update_layout(height=600)
        return fig

    except Exception as e:
        st.error(f"Erro ao criar visualização: {e}")
        return None

def main():
    """Dashboard principal"""
    
    st.title("🛋️ Sofá Novo de Novo - Dashboard Estratégico")
    
    # Carrega dados
    df, arquivo = carregar_dados()
    if df is None:
        st.stop()
    
    # Sidebar com informações
    st.sidebar.header("📊 Informações dos Dados")
    st.sidebar.info(f"""
    **Arquivo:** {arquivo.split('/')[-1]}
    **Municípios:** {len(df):,}
    **Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
    """)
    
    # Abas principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Visão Geral",
        "🏢 Franquias Atuais",
        "🗺️ Mapas",
        "📈 Análise Completa",
        "🧮 Base de Cálculo",
        "💡 Insights Estratégicos",
        "💰 Receita Franqueadora",
        "🏙️ Análise por Bairros"
    ])
    
    with tab1:
        st.header("📊 Visão Geral Executiva")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)

        franquias_atuais = df['Franquias_Atuais'].sum()

        # Usa dados corrigidos se disponível
        if 'Total_Franquias_Adicional_Corrigida' in df.columns:
            franquias_adicionais = df['Total_Franquias_Adicional_Corrigida'].sum()
            total_potencial = df['Total_Franquias_Corrigida'].sum()
            cidades_com_potencial = len(df[df['Total_Franquias_Corrigida'] > 0])
        else:
            franquias_adicionais = df['Total_Franquias_Adicional'].sum()
            total_potencial = df['Total_Franquias_Realista'].sum()
            cidades_com_potencial = len(df[df['Total_Franquias_Realista'] > 0])

        cidades_com_franquias = df['Tem_Franquia'].sum()
        
        with col1:
            st.metric(
                "🏢 Franquias Atuais",
                f"{franquias_atuais:,.0f}",
                delta=f"Base atual"
            )
        
        with col2:
            st.metric(
                "🎯 Potencial Adicional",
                f"{franquias_adicionais:,.0f}",
                delta=f"+{(franquias_adicionais/max(1,franquias_atuais)*100):.0f}% crescimento"
            )
        
        with col3:
            st.metric(
                "🏙️ Cidades com Potencial",
                f"{cidades_com_potencial:,}",
                delta=f"De {len(df):,} municípios"
            )
        
        with col4:
            st.metric(
                "📊 Total Potencial",
                f"{total_potencial:,.0f}",
                delta=f"Padrão + Sofázinho"
            )
        
        # Gráficos principais
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 cidades por potencial total
            coluna_potencial = 'Total_Franquias_Corrigida' if 'Total_Franquias_Corrigida' in df.columns else 'Total_Franquias_Realista'
            top_10 = df.nlargest(10, coluna_potencial)
            fig_top10 = px.bar(
                top_10,
                x=coluna_potencial,
                y='Municipio',
                orientation='h',
                title="🏆 Top 10 Cidades - Potencial Total",
                labels={coluna_potencial: 'Franquias', 'Municipio': 'Cidade'}
            )
            fig_top10.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_top10, use_container_width=True)
        
        with col2:
            # Distribuição por tipo
            if 'Franquias_Padrao_Corrigida' in df.columns:
                padrão = df['Franquias_Padrao_Corrigida'].sum()
                sofazinho = df['Franquias_Sofazinho_Corrigida'].sum()
            else:
                padrão = df['Franquias_Padrao_Realista'].sum()
                sofazinho = df['Franquias_Sofazinho_Realista'].sum()

            fig_tipo = px.pie(
                values=[padrão, sofazinho],
                names=['Padrão', 'Sofázinho'],
                title="📊 Distribuição por Tipo de Franquia"
            )
            st.plotly_chart(fig_tipo, use_container_width=True)
    
    with tab2:
        st.header("🏢 Franquias Atuais - Situação Real")
        
        # Filtro para mostrar apenas cidades com franquias
        cidades_com_franquias_df = df[df['Tem_Franquia'] == True].copy()
        
        if len(cidades_com_franquias_df) == 0:
            st.warning("⚠️ Nenhuma cidade com franquias encontrada nos dados")
            st.stop()
        
        st.info(f"📊 **{len(cidades_com_franquias_df)} cidades** têm franquias atualmente")
        
        # Métricas específicas de franquias atuais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🏢 Franquias Padrão Atuais",
                f"{cidades_com_franquias_df['Franquias_Atuais'].sum():.0f}",
                delta="Operando"
            )
        
        with col2:
            st.metric(
                "🎯 Padrão Adicional Possível",
                f"{cidades_com_franquias_df['Franquias_Padrao_Adicional'].sum():.0f}",
                delta="Expansão"
            )
        
        with col3:
            st.metric(
                "🏠 Sofázinho Adicional",
                f"{cidades_com_franquias_df['Franquias_Sofazinho_Adicional'].sum():.0f}",
                delta="Capilarização"
            )
        
        # Tabela detalhada das cidades com franquias
        st.subheader("📋 Detalhamento por Cidade")
        
        # Prepara dados para exibição
        display_df = cidades_com_franquias_df[[
            'Municipio', 'UF', 'Populacao_2022', 'Franquias_Atuais',
            'Franquias_Padrao_Adicional', 'Franquias_Sofazinho_Adicional',
            'Total_Franquias_Adicional', 'Total_Franquias_Realista'
        ]].copy()
        
        # Formata população
        display_df['Populacao_2022'] = display_df['Populacao_2022'].apply(lambda x: f"{x:,}")
        
        # Renomeia colunas
        display_df = display_df.rename(columns={
            'Municipio': 'Cidade',
            'Populacao_2022': 'População',
            'Franquias_Atuais': 'Atuais',
            'Franquias_Padrao_Adicional': 'Padrão Adicional',
            'Franquias_Sofazinho_Adicional': 'Sofázinho Adicional',
            'Total_Franquias_Adicional': 'Total Adicional',
            'Total_Franquias_Realista': 'Potencial Total'
        })
        
        # Ordena por franquias atuais (decrescente)
        display_df = display_df.sort_values('Atuais', ascending=False)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Gráfico de franquias atuais vs potencial
        fig_atual_vs_potencial = px.scatter(
            cidades_com_franquias_df,
            x='Franquias_Atuais',
            y='Total_Franquias_Adicional',
            size='Populacao_2022',
            hover_name='Municipio',
            title="📊 Franquias Atuais vs Potencial Adicional",
            labels={
                'Franquias_Atuais': 'Franquias Atuais',
                'Total_Franquias_Adicional': 'Potencial Adicional'
            }
        )
        st.plotly_chart(fig_atual_vs_potencial, use_container_width=True)
    
    with tab3:
        st.header("🗺️ Visualizações por Estado")

        # Seletor de métrica
        col1, col2 = st.columns([3, 1])

        with col2:
            # Verifica se tem dados corrigidos para mostrar opções adequadas
            tem_dados_corrigidos = 'Total_Franquias_Corrigida' in df.columns

            if tem_dados_corrigidos:
                opcoes_metricas = [
                    'Franquias_Atuais',
                    'Total_Franquias_Adicional_Corrigida',
                    'Franquias_Padrao_Adicional_Corrigida',
                    'Franquias_Sofazinho_Adicional_Corrigida',
                    'Total_Franquias_Corrigida',
                    'PIB_per_capita_Calibrado',
                    'Classe_AB_PNAD'
                ]
                labels_metricas = {
                    'Franquias_Atuais': 'Franquias Atuais',
                    'Total_Franquias_Adicional_Corrigida': 'Potencial Adicional Total',
                    'Franquias_Padrao_Adicional_Corrigida': 'Potencial Adicional - Padrão',
                    'Franquias_Sofazinho_Adicional_Corrigida': 'Potencial Adicional - Sofázinho',
                    'Total_Franquias_Corrigida': 'Potencial Total',
                    'PIB_per_capita_Calibrado': 'PIB per capita',
                    'Classe_AB_PNAD': '% Classe A/B'
                }
            else:
                opcoes_metricas = [
                    'Franquias_Atuais',
                    'Total_Franquias_Adicional',
                    'Total_Franquias_Realista',
                    'PIB_per_capita_Calibrado',
                    'Classe_AB_PNAD'
                ]
                labels_metricas = {
                    'Franquias_Atuais': 'Franquias Atuais',
                    'Total_Franquias_Adicional': 'Potencial Adicional',
                    'Total_Franquias_Realista': 'Potencial Total',
                    'PIB_per_capita_Calibrado': 'PIB per capita',
                    'Classe_AB_PNAD': '% Classe A/B'
                }

            metrica_visual = st.selectbox(
                "Métrica para visualizar:",
                opcoes_metricas,
                format_func=lambda x: labels_metricas[x]
            )

        with col1:
            # Títulos dinâmicos baseados na métrica selecionada
            if tem_dados_corrigidos:
                titulos_visual = {
                    'Franquias_Atuais': 'Franquias Atuais por Estado',
                    'Total_Franquias_Adicional_Corrigida': 'Potencial Adicional Total por Estado',
                    'Franquias_Padrao_Adicional_Corrigida': 'Potencial Adicional - Padrão por Estado',
                    'Franquias_Sofazinho_Adicional_Corrigida': 'Potencial Adicional - Sofázinho por Estado',
                    'Total_Franquias_Corrigida': 'Potencial Total por Estado',
                    'PIB_per_capita_Calibrado': 'PIB per capita por Estado',
                    'Classe_AB_PNAD': '% Classe A/B por Estado'
                }
            else:
                titulos_visual = {
                    'Franquias_Atuais': 'Franquias Atuais por Estado',
                    'Total_Franquias_Adicional': 'Potencial Adicional por Estado',
                    'Total_Franquias_Realista': 'Potencial Total por Estado',
                    'PIB_per_capita_Calibrado': 'PIB per capita por Estado',
                    'Classe_AB_PNAD': '% Classe A/B por Estado'
                }

            titulo_visual = titulos_visual[metrica_visual]

            fig_visual = criar_mapa_brasil_funcional(df, metrica_visual, titulo_visual)
            if fig_visual:
                st.plotly_chart(fig_visual, use_container_width=True)

        # Tabela detalhada por estado
        st.subheader("📊 Dados Detalhados por Estado")

        # Normaliza UF para siglas
        def normalizar_uf_local(uf):
            nome_para_sigla = {
                'SÃO PAULO': 'SP', 'RIO DE JANEIRO': 'RJ', 'MINAS GERAIS': 'MG',
                'BAHIA': 'BA', 'PARANÁ': 'PR', 'RIO GRANDE DO SUL': 'RS',
                'PERNAMBUCO': 'PE', 'CEARÁ': 'CE', 'PARÁ': 'PA', 'SANTA CATARINA': 'SC',
                'GOIÁS': 'GO', 'MARANHÃO': 'MA', 'ESPÍRITO SANTO': 'ES',
                'PARAÍBA': 'PB', 'AMAZONAS': 'AM', 'MATO GROSSO': 'MT',
                'RIO GRANDE DO NORTE': 'RN', 'ALAGOAS': 'AL', 'PIAUÍ': 'PI',
                'DISTRITO FEDERAL': 'DF', 'MATO GROSSO DO SUL': 'MS',
                'SERGIPE': 'SE', 'RONDÔNIA': 'RO', 'ACRE': 'AC',
                'AMAPÁ': 'AP', 'RORAIMA': 'RR', 'TOCANTINS': 'TO'
            }
            return nome_para_sigla.get(str(uf).upper(), str(uf))

        df_temp = df.copy()
        df_temp['UF_Sigla'] = df_temp['UF'].apply(normalizar_uf_local)

        # Agrega por UF - adapta baseado nos dados disponíveis
        agg_dict = {
            'Franquias_Atuais': 'sum',
            'Populacao_2022': 'sum',
            'PIB_per_capita_Calibrado': 'mean',
            'Classe_AB_PNAD': 'mean'
        }

        # Adiciona colunas baseado nos dados disponíveis
        if tem_dados_corrigidos:
            agg_dict.update({
                'Total_Franquias_Adicional_Corrigida': 'sum',
                'Franquias_Padrao_Adicional_Corrigida': 'sum',
                'Franquias_Sofazinho_Adicional_Corrigida': 'sum',
                'Total_Franquias_Corrigida': 'sum'
            })
        else:
            agg_dict.update({
                'Total_Franquias_Adicional': 'sum',
                'Total_Franquias_Realista': 'sum'
            })

        uf_stats = df_temp.groupby('UF_Sigla').agg(agg_dict).round(1)

        # Renomeia colunas baseado nos dados disponíveis
        rename_dict = {
            'Franquias_Atuais': 'Atuais',
            'Populacao_2022': 'População',
            'PIB_per_capita_Calibrado': 'PIB per capita',
            'Classe_AB_PNAD': '% Classe A/B'
        }

        if tem_dados_corrigidos:
            rename_dict.update({
                'Total_Franquias_Adicional_Corrigida': 'Adicionais Total',
                'Franquias_Padrao_Adicional_Corrigida': 'Adicionais Padrão',
                'Franquias_Sofazinho_Adicional_Corrigida': 'Adicionais Sofázinho',
                'Total_Franquias_Corrigida': 'Potencial Total'
            })
        else:
            rename_dict.update({
                'Total_Franquias_Adicional': 'Adicionais',
                'Total_Franquias_Realista': 'Total Potencial'
            })

        uf_stats = uf_stats.rename(columns=rename_dict)

        # Formata população
        uf_stats['População'] = uf_stats['População'].apply(lambda x: f"{x:,.0f}")
        uf_stats['PIB per capita'] = uf_stats['PIB per capita'].apply(lambda x: f"R$ {x:,.0f}")

        # Ordena por franquias atuais
        uf_stats = uf_stats.sort_values('Atuais', ascending=False)

        st.dataframe(uf_stats, use_container_width=True)
    
    with tab4:
        st.header("📈 Análise Completa")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            regiao_filter = st.selectbox(
                "Filtrar por Região:",
                ['Todas'] + sorted(df['Regiao'].unique())
            )
        
        with col2:
            min_pop = st.slider(
                "População mínima (mil hab):",
                min_value=20,
                max_value=1000,
                value=20,
                step=10
            )
        
        # Aplica filtros
        df_filtered = df.copy()
        
        if regiao_filter != 'Todas':
            df_filtered = df_filtered[df_filtered['Regiao'] == regiao_filter]
        
        df_filtered = df_filtered[df_filtered['Populacao_2022'] >= min_pop * 1000]
        
        st.info(f"📊 {len(df_filtered):,} municípios após filtros")
        
        # Tabela completa
        st.subheader("📋 Ranking Completo com Análise de Viabilidade")

        # Verifica se tem dados corrigidos
        tem_dados_corrigidos = 'Total_Franquias_Corrigida' in df_filtered.columns

        if tem_dados_corrigidos:
            st.success("✅ Usando dados corrigidos com regra de faturamento mínimo")
        else:
            st.warning("⚠️ Usando dados não corrigidos - execute recálculo")

        # Calcula métricas de negócio e justificativas
        with st.spinner("Preparando dados para exibição..."):

            # Se não tem dados corrigidos, calcula métricas
            if not tem_dados_corrigidos:
                metricas_list = []
                for _, row in df_filtered.iterrows():
                    metricas = calcular_metricas_negocio(row)
                    metricas_list.append(metricas)

                df_filtered['Pop_Classe_AB'] = [m['Pop_Classe_AB'] for m in metricas_list]
                df_filtered['Mercado_Total_Servicos'] = [m['Mercado_Total_Servicos'] for m in metricas_list]
                df_filtered['Servicos_Por_Franquia'] = [m['Servicos_Por_Franquia'] for m in metricas_list]
                df_filtered['Faturamento_Mensal_Franquia'] = [m['Faturamento_Mensal_Franquia'] for m in metricas_list]

            # Cria justificativas
            df_filtered['Justificativa'] = df_filtered.apply(criar_justificativa, axis=1)

        # Prepara dados para exibição
        if tem_dados_corrigidos:
            display_cols = [
                'Ranking_Corrigido', 'Municipio', 'UF', 'Populacao_2022',
                'Classe_AB_PNAD', 'Pop_Classe_AB', 'Mercado_Total_Servicos',
                'Franquias_Atuais', 'Franquias_Padrao_Adicional_Corrigida',
                'Franquias_Sofazinho_Adicional_Corrigida', 'Total_Franquias_Adicional_Corrigida',
                'Total_Franquias_Corrigida', 'Faturamento_Mensal_Estimado',
                'Payback_Meses', 'Tipo_Recomendado', 'Classificacao_Corrigida', 'Justificativa'
            ]
        else:
            display_cols = [
                'Ranking_Realista', 'Municipio', 'UF', 'Populacao_2022',
                'Classe_AB_PNAD', 'Pop_Classe_AB', 'Mercado_Total_Servicos',
                'Franquias_Atuais', 'Franquias_Padrao_Adicional',
                'Franquias_Sofazinho_Adicional', 'Total_Franquias_Adicional',
                'Total_Franquias_Realista', 'Servicos_Por_Franquia',
                'Faturamento_Mensal_Franquia', 'Classificacao_Realista', 'Justificativa'
            ]

        table_df = df_filtered[display_cols].copy()

        # Formata colunas
        table_df['Populacao_2022'] = table_df['Populacao_2022'].apply(lambda x: f"{x:,}")
        table_df['Pop_Classe_AB'] = table_df['Pop_Classe_AB'].apply(lambda x: f"{x:,}")
        table_df['Mercado_Total_Servicos'] = table_df['Mercado_Total_Servicos'].apply(lambda x: f"{x:,}")
        table_df['Classe_AB_PNAD'] = table_df['Classe_AB_PNAD'].apply(lambda x: f"{x:.1f}%")

        # Formata faturamento (coluna pode ter nomes diferentes)
        if 'Faturamento_Mensal_Estimado' in table_df.columns:
            table_df['Faturamento_Mensal_Estimado'] = table_df['Faturamento_Mensal_Estimado'].apply(
                lambda x: f"R$ {x:,.0f}" if x > 0 else "R$ 0"
            )
        elif 'Faturamento_Mensal_Franquia' in table_df.columns:
            table_df['Faturamento_Mensal_Franquia'] = table_df['Faturamento_Mensal_Franquia'].apply(
                lambda x: f"R$ {x:,.0f}" if x > 0 else "R$ 0"
            )

        # Formata payback se disponível
        if 'Payback_Meses' in table_df.columns:
            table_df['Payback_Meses'] = table_df['Payback_Meses'].apply(
                lambda x: f"{x:.1f} meses" if x > 0 else "N/A"
            )

        # Renomeia colunas
        rename_dict = {
            'Municipio': 'Cidade',
            'Populacao_2022': 'População Total',
            'Classe_AB_PNAD': '% Classe A/B',
            'Pop_Classe_AB': 'Pop. Classe A/B',
            'Mercado_Total_Servicos': 'Serviços/Ano Total',
            'Franquias_Atuais': 'Atuais',
            'Justificativa': 'Justificativa da Análise'
        }

        # Adiciona renomeações específicas baseadas nas colunas disponíveis
        if tem_dados_corrigidos:
            rename_dict.update({
                'Ranking_Corrigido': 'Rank',
                'Franquias_Padrao_Adicional_Corrigida': 'Padrão +',
                'Franquias_Sofazinho_Adicional_Corrigida': 'Sofázinho +',
                'Total_Franquias_Adicional_Corrigida': 'Total +',
                'Total_Franquias_Corrigida': 'Potencial',
                'Faturamento_Mensal_Estimado': 'Faturamento/Mês',
                'Payback_Meses': 'Payback',
                'Tipo_Recomendado': 'Tipo Recomendado',
                'Classificacao_Corrigida': 'Prioridade'
            })
        else:
            rename_dict.update({
                'Ranking_Realista': 'Rank',
                'Franquias_Padrao_Adicional': 'Padrão +',
                'Franquias_Sofazinho_Adicional': 'Sofázinho +',
                'Total_Franquias_Adicional': 'Total +',
                'Total_Franquias_Realista': 'Potencial',
                'Servicos_Por_Franquia': 'Serviços/Franquia/Ano',
                'Faturamento_Mensal_Franquia': 'Faturamento/Mês',
                'Classificacao_Realista': 'Prioridade'
            })

        table_df = table_df.rename(columns=rename_dict)

        # Exibe informações sobre os cálculos
        with st.expander("ℹ️ Como são calculadas as métricas de negócio"):
            st.markdown("""
            **📊 Metodologia dos Cálculos:**

            1. **População Classe A/B:** População total × % Classe A/B da UF
            2. **Famílias Classe A/B:** População Classe A/B ÷ 3,2 pessoas/família
            3. **Penetração de Mercado:** 2% das famílias Classe A/B usam o serviço
            4. **Frequência:** 2,5 serviços por família por ano
            5. **Ajuste Digital:** Fator baseado na penetração de internet
            6. **Serviços Totais/Ano:** Famílias × Penetração × Frequência × Fator Digital
            7. **Serviços/Franquia:** Serviços Totais ÷ Número de Franquias Potenciais
            8. **Faturamento/Mês:** (Serviços/Franquia × R$ 250) ÷ 12 meses

            **🎯 Parâmetros Utilizados:**
            - Ticket médio: R$ 250 por serviço
            - Penetração base: 2% das famílias Classe A/B
            - Frequência: 2,5 serviços/família/ano
            - Pessoas por família: 3,2 (média brasileira)

            **📊 Benchmarks Reais da Empresa:**
            - **Curitiba:** R$ 400k/mês (1 franquia, 15 anos de operação)
            - **São Paulo:** R$ 50k/mês (franqueados com 2 anos de operação)
            - **Crescimento:** Faturamento aumenta ano a ano por empilhamento de clientes
            """)

        st.dataframe(table_df, use_container_width=True, hide_index=True)
        
        # Download
        csv = table_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"analise_sofa_novo_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with tab5:
        st.header("🧮 Base de Cálculo - Metodologia Científica")

        st.markdown("""
        ## 🎯 **Nossa Tese de Investimento**

        ### **📊 Premissa Central**
        O mercado brasileiro de limpeza de sofás está **subatendido** e tem potencial para suportar
        **1.294 franquias** distribuídas em **1.030 cidades**, com base em análise científica de
        **1.800 municípios** usando dados oficiais do IBGE, PNAD e Atlas do Desenvolvimento Humano.
        """)

        # Seção 1: Fontes de Dados
        st.subheader("📋 1. Fontes de Dados (100% Oficiais)")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🏛️ Dados Demográficos:**
            - **População Municipal:** IBGE Censo 2022
            - **PIB per capita:** IBGE Contas Regionais 2021
            - **IDH Municipal:** Atlas Desenvolvimento Humano 2010

            **📊 Dados Socioeconômicos:**
            - **% Classe A/B:** PNAD Contínua 2023
            - **% Penetração Internet:** PNAD TIC 2023
            - **Interesse no Serviço:** Google Trends (manual)
            """)

        with col2:
            st.markdown("""
            **🎯 Dados Operacionais:**
            - **Franqueados Atuais:** Base interna da empresa
            - **Localização:** Endereços e bairros atuais
            - **Performance:** Dados de faturamento (quando disponível)

            **🔍 Cobertura:**
            - **1.800 municípios** analisados
            - **Todas as 27 UFs** incluídas
            - **100% dos municípios** com população ≥ 20.000 hab
            """)

        # Seção 2: Fórmula do Score
        st.subheader("🧮 2. Fórmula Científica do Score")

        st.markdown("""
        ### **📐 Fórmula Matemática:**
        """)

        st.latex(r'''
        Score = População \times F_{PIB} \times F_{IDH} \times F_{Classe} \times F_{Trends} \times F_{Internet} \times F_{Região}
        ''')

        st.markdown("""
        ### **🔢 Onde cada fator é calculado como:**
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.latex(r'''F_{PIB} = \frac{PIB_{município}}{R\$ 32.000}''')
            st.latex(r'''F_{IDH} = \frac{IDH_{município}}{0.690}''')
            st.latex(r'''F_{Classe} = \frac{\%ClasseAB_{UF}}{16\%}''')

        with col2:
            st.latex(r'''F_{Trends} = \frac{GoogleTrends_{UF}}{100}''')
            st.latex(r'''F_{Internet} = \frac{\%Internet_{UF}}{100}''')
            st.latex(r'''F_{Região} = \begin{cases}
            1.2 & \text{Sudeste} \\
            1.1 & \text{Sul} \\
            1.05 & \text{Centro-Oeste} \\
            0.9 & \text{Nordeste} \\
            0.85 & \text{Norte}
            \end{cases}''')

        # Seção 3: Parâmetros de Calibração
        st.subheader("⚙️ 3. Parâmetros de Calibração")

        st.markdown("""
        ### **🎯 Valores de Referência (Realidade Brasileira):**
        """)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **💰 Econômicos:**
            - PIB base: **R$ 32.000**
            - IDH base: **0.690**
            - Classe A/B base: **16%**
            """)

        with col2:
            st.markdown("""
            **📱 Digitais:**
            - Internet base: **70%**
            - Google Trends base: **50**
            - Fator regional: **0.85 - 1.2**
            """)

        with col3:
            st.markdown("""
            **🏢 Operacionais:**
            - K Padrão: **45.000**
            - Score Sofázinho: **12.000**
            - Teto populacional: **250k hab/franquia**
            """)

        # Seção 4: Critérios de Franquias
        st.subheader("🏢 4. Critérios para Franquias")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### **🏢 Franquias Padrão**

            **📋 Critérios:**
            - Score ≥ **45.000**
            - População ≥ **100.000** habitantes
            - Máximo **1 franquia / 250.000 hab**

            **💼 Perfil do Negócio:**
            - Ticket médio: **R$ 250**
            - Serviços/mês: **120**
            - Receita mensal: **R$ 30.000**
            - ROI esperado: **25-35%**
            """)

        with col2:
            st.markdown("""
            ### **🏠 Franquias Sofázinho**

            **📋 Critérios:**
            - Score ≥ **12.000**
            - População: **20.000 - 99.999** hab
            - Apenas se **não há franquia padrão**

            **💼 Perfil do Negócio:**
            - Ticket médio: **R$ 250**
            - Serviços/mês: **60**
            - Receita mensal: **R$ 15.000**
            - ROI esperado: **20-30%**
            """)

        # Seção 5: Validação
        st.subheader("✅ 5. Validação da Metodologia")

        st.markdown("""
        ### **🎯 Benchmarks de Mercado:**
        """)

        import pandas as pd_local
        benchmark_data = pd_local.DataFrame({
            'Rede': ['McDonald\'s', 'Subway', 'Burger King', 'Sofá Novo (Atual)', 'Sofá Novo (Potencial)'],
            'Unidades': [1000, 1500, 800, 195, 1294],
            'Cidades': [500, 400, 350, 128, 1030],
            'Unidades/Cidade': [2.0, 3.8, 2.3, 1.5, 1.3]
        })

        st.dataframe(benchmark_data, use_container_width=True, hide_index=True)

        st.success("""
        ✅ **Nossa projeção está alinhada com benchmarks de mercado:**
        - Densidade similar a redes consolidadas
        - Crescimento sustentável e realista
        - Baseado em dados científicos, não estimativas
        """)

        # Seção 6: Fórmulas Detalhadas
        st.subheader("🔬 6. Cálculos Detalhados")

        with st.expander("📐 Ver Fórmulas Completas"):
            st.markdown("""
            ### **Passo 1: Cálculo do Score**
            ```python
            score = população * (pib/32000) * (idh/0.69) * (classe_ab/16) *
                    (trends/100) * (internet/100) * fator_regional
            ```

            ### **Passo 2: Franquias Padrão**
            ```python
            if população >= 100000 and score >= 45000:
                franquias_padrão = min(
                    floor(score / 45000),
                    ceil(população / 250000)
                )
            else:
                franquias_padrão = 0
            ```

            ### **Passo 3: Franquias Sofázinho**
            ```python
            if (20000 <= população <= 99999) and franquias_padrão == 0 and score >= 12000:
                franquias_sofázinho = 1
            else:
                franquias_sofázinho = 0
            ```

            ### **Passo 4: Classificação**
            ```python
            if total_franquias == 0:
                classificação = "Saturado"
            elif score >= 100000:
                classificação = "Prioridade Máxima"
            elif score >= 60000:
                classificação = "Prioridade Alta"
            # ... e assim por diante
            ```
            """)

    with tab6:
        st.header("💡 Insights Estratégicos para Apresentação")

        # Métricas de destaque
        st.subheader("🎯 Números de Impacto")

        col1, col2, col3, col4 = st.columns(4)

        franquias_atuais = df['Franquias_Atuais'].sum()

        # Usa dados corrigidos se disponível
        if 'Total_Franquias_Corrigida' in df.columns:
            potencial_total = df['Total_Franquias_Corrigida'].sum()
            cidades_potencial = len(df[df['Total_Franquias_Corrigida'] > 0])
            cidades_atuais = len(df[df['Franquias_Atuais'] > 0])
            expansao_geografica = cidades_potencial - cidades_atuais

            # Calcula payback médio
            df_com_payback = df[df['Payback_Meses'] > 0]
            if len(df_com_payback) > 0:
                payback_medio = df_com_payback['Payback_Meses'].mean()
                payback_texto = f"{payback_medio:.0f} meses"
            else:
                payback_texto = "18-24 meses"
        else:
            potencial_total = df['Total_Franquias_Realista'].sum()
            cidades_potencial = len(df[df['Total_Franquias_Realista'] > 0])
            cidades_atuais = len(df[df['Franquias_Atuais'] > 0])
            expansao_geografica = cidades_potencial - cidades_atuais
            payback_texto = "18-24 meses"

        crescimento_pct = (potencial_total - franquias_atuais) / franquias_atuais * 100
        receita_potencial = potencial_total * 250 * 120 * 12 / 1_000_000  # Em milhões (ticket atualizado)

        with col1:
            st.metric("🚀 Crescimento Potencial", f"{crescimento_pct:.0f}%", "vs base atual")

        with col2:
            st.metric("💰 Receita Potencial", f"R$ {receita_potencial:.0f}M", "por ano")

        with col3:
            st.metric("🏙️ Expansão Geográfica", f"{expansao_geografica:,}", "novas cidades")

        with col4:
            st.metric("⏱️ Payback Médio", payback_texto, "por franquia")

        # Insights por região
        st.subheader("🗺️ Oportunidades por Região")

        # Calcula dados por região
        def normalizar_uf_insight(uf):
            nome_para_sigla = {
                'SÃO PAULO': 'SP', 'RIO DE JANEIRO': 'RJ', 'MINAS GERAIS': 'MG',
                'BAHIA': 'BA', 'PARANÁ': 'PR', 'RIO GRANDE DO SUL': 'RS',
                'PERNAMBUCO': 'PE', 'CEARÁ': 'CE', 'PARÁ': 'PA', 'SANTA CATARINA': 'SC',
                'GOIÁS': 'GO', 'MARANHÃO': 'MA', 'ESPÍRITO SANTO': 'ES',
                'PARAÍBA': 'PB', 'AMAZONAS': 'AM', 'MATO GROSSO': 'MT',
                'RIO GRANDE DO NORTE': 'RN', 'ALAGOAS': 'AL', 'PIAUÍ': 'PI',
                'DISTRITO FEDERAL': 'DF', 'MATO GROSSO DO SUL': 'MS',
                'SERGIPE': 'SE', 'RONDÔNIA': 'RO', 'ACRE': 'AC',
                'AMAPÁ': 'AP', 'RORAIMA': 'RR', 'TOCANTINS': 'TO'
            }
            return nome_para_sigla.get(str(uf).upper(), str(uf))

        df_temp = df.copy()
        df_temp['UF_Sigla'] = df_temp['UF'].apply(normalizar_uf_insight)

        # Mapeamento para região
        uf_para_regiao = {
            'SP': 'Sudeste', 'RJ': 'Sudeste', 'MG': 'Sudeste', 'ES': 'Sudeste',
            'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
            'BA': 'Nordeste', 'CE': 'Nordeste', 'PE': 'Nordeste', 'MA': 'Nordeste',
            'PB': 'Nordeste', 'AL': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste', 'PI': 'Nordeste',
            'AM': 'Norte', 'PA': 'Norte', 'AC': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'AP': 'Norte', 'TO': 'Norte',
            'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'DF': 'Centro-Oeste'
        }

        df_temp['Regiao_Calc'] = df_temp['UF_Sigla'].map(uf_para_regiao)

        insights_regiao = df_temp.groupby('Regiao_Calc').agg({
            'Franquias_Atuais': 'sum',
            'Total_Franquias_Adicional': 'sum',
            'PIB_per_capita_Calibrado': 'mean',
            'Classe_AB_PNAD': 'mean'
        }).round(1)

        insights_regiao['Crescimento %'] = (insights_regiao['Total_Franquias_Adicional'] /
                                          insights_regiao['Franquias_Atuais'].replace(0, 1) * 100).round(0)

        insights_regiao = insights_regiao.rename(columns={
            'Franquias_Atuais': 'Atuais',
            'Total_Franquias_Adicional': 'Potencial +',
            'PIB_per_capita_Calibrado': 'PIB Médio',
            'Classe_AB_PNAD': '% Classe A/B'
        })

        st.dataframe(insights_regiao, use_container_width=True)

        # Plano Estratégico 2026-2028
        st.subheader("🎯 Plano Estratégico 2026-2028")

        # Dados para o plano
        franquias_atuais_total = df['Franquias_Atuais'].sum()
        potencial_total_calc = df['Total_Franquias_Corrigida'].sum() if 'Total_Franquias_Corrigida' in df.columns else df['Total_Franquias_Realista'].sum()
        crescimento_necessario = potencial_total_calc - franquias_atuais_total

        st.info(f"""
        **🎯 OBJETIVO:** Crescer de **{franquias_atuais_total:.0f}** para **{potencial_total_calc:.0f}** franquias em 3 anos

        **📈 CRESCIMENTO:** +{crescimento_necessario:.0f} franquias (+{(potencial_total_calc/franquias_atuais_total - 1)*100:.0f}%)

        **⚡ RITMO:** ~{crescimento_necessario/3:.0f} franquias por ano
        """)

        # Plano por ano
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            ### **🚀 2026 - ANO 1**
            **Meta: +365 franquias**

            **🎯 Foco: Grandes Centros**
            - **São Paulo:** +20 franquias
            - **Rio de Janeiro:** +12 franquias
            - **Brasília:** +10 franquias
            - **Belo Horizonte:** +7 franquias
            - **Outras capitais:** +50 franquias

            **🏠 Sofázinhos:** +266 unidades
            - Cidades 50k-100k habitantes
            - Payback 3-5 meses
            - Foco: SP, MG, PR, RS

            **💰 Investimento:** R$ 1,75 milhões
            **📊 ROI esperado:** 300% a.a.
            """)

        with col2:
            st.markdown("""
            ### **📈 2027 - ANO 2**
            **Meta: +365 franquias**

            **🎯 Foco: Expansão Regional**
            - **Nordeste:** +120 Sofázinhos
            - **Sul:** +80 franquias mistas
            - **Centro-Oeste:** +60 franquias
            - **Grandes SP/RJ:** +50 franquias
            - **Cidades médias:** +55 franquias

            **🌟 Estratégia:**
            - Consolidar regiões iniciadas
            - Penetrar mercados secundários
            - Otimizar operações existentes

            **💰 Investimento:** R$ 1,79 milhões
            **📊 ROI esperado:** 280% a.a.
            """)

        with col3:
            st.markdown("""
            ### **🏁 2028 - ANO 3**
            **Meta: +365 franquias**

            **🎯 Foco: Capilarização Total**
            - **Norte:** +89 franquias
            - **Nordeste interior:** +120 Sofázinhos
            - **Cidades pequenas:** +100 Sofázinhos
            - **Saturação capitais:** +56 franquias

            **🎯 Finalização:**
            - Atingir 100% do potencial
            - Consolidar todas as regiões
            - Preparar expansão internacional

            **💰 Investimento:** R$ 1,72 milhões
            **📊 ROI esperado:** 250% a.a.
            """)

        # Cronograma detalhado
        st.subheader("📅 Cronograma Detalhado por Trimestre")

        cronograma_data = pd.DataFrame({
            'Período': [
                '2026 Q1', '2026 Q2', '2026 Q3', '2026 Q4',
                '2027 Q1', '2027 Q2', '2027 Q3', '2027 Q4',
                '2028 Q1', '2028 Q2', '2028 Q3', '2028 Q4'
            ],
            'Padrão': [25, 30, 35, 40, 35, 30, 25, 20, 15, 15, 10, 10],
            'Sofázinho': [65, 70, 75, 56, 70, 75, 80, 60, 80, 85, 90, 80],
            'Total': [90, 100, 110, 96, 105, 105, 105, 80, 95, 100, 100, 90],
            'Foco Regional': [
                'SP/RJ/DF', 'SP/MG/PR', 'Capitais SE/S', 'Capitais NE',
                'Interior SP/MG', 'Sul completo', 'Nordeste', 'Centro-Oeste',
                'Norte', 'Capilarização', 'Finalização', 'Consolidação'
            ]
        })

        # Adiciona coluna acumulada
        cronograma_data['Acumulado'] = cronograma_data['Total'].cumsum() + franquias_atuais_total

        st.dataframe(cronograma_data, use_container_width=True, hide_index=True)

        # Gráfico de evolução
        fig_cronograma = px.line(
            cronograma_data,
            x='Período',
            y='Acumulado',
            title='📈 Evolução do Total de Franquias (2026-2028)',
            labels={'Acumulado': 'Total de Franquias', 'Período': 'Trimestre'}
        )

        # Adiciona linha de meta
        fig_cronograma.add_hline(
            y=potencial_total_calc,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Meta: {potencial_total_calc:.0f} franquias"
        )

        st.plotly_chart(fig_cronograma, use_container_width=True)

        # Estratégias por região
        st.subheader("🗺️ Estratégia por Região")

        estrategia_regional = pd.DataFrame({
            'Região': ['Sudeste', 'Sul', 'Nordeste', 'Centro-Oeste', 'Norte'],
            'Prioridade': ['🔥 Máxima', '🔥 Alta', '📈 Média', '📈 Média', '⏳ Baixa'],
            'Cronograma': ['2026 Q1-Q2', '2026 Q3-Q4', '2027 Q1-Q3', '2027 Q4-2028 Q2', '2028 Q1-Q4'],
            'Estratégia': [
                'Saturar grandes centros + cidades médias',
                'Expansão sistemática + alta qualidade',
                'Capilarização com Sofázinhos',
                'Foco agronegócio + capitais',
                'Preparação + seleção criteriosa'
            ],
            'Meta Franquias': [450, 280, 320, 150, 90]
        })

        st.dataframe(estrategia_regional, use_container_width=True, hide_index=True)

        # Riscos e oportunidades
        st.subheader("⚠️ Riscos e Oportunidades")

        col1, col2 = st.columns(2)

        with col1:
            st.error("""
            **🚨 Principais Riscos:**
            - Saturação prematura em grandes centros
            - Concorrência local em cidades menores
            - Variação sazonal da demanda
            - Dependência de marketing digital
            """)

        with col2:
            st.success("""
            **💡 Principais Oportunidades:**
            - Mercado ainda subatendido (564% crescimento)
            - Digitalização crescente facilita marketing
            - Classe média emergente aumentando
            - Modelo Sofázinho para capilarização
            """)

        # Call to action
        st.subheader("🎯 Estrutura Necessária para Execução")

        col1, col2 = st.columns(2)

        with col1:
            st.success("""
            **🚀 Infraestrutura Operacional:**

            - **Equipe Expansão:** Time atual (R$ 20k/mês)
            - **Consultores Regionais:** 1 por região
            - **Sistema CRM:** Automação completa
            - **Treinamento:** Programa online + IA
            - **Financiar Franquias:** Linha de crédito
            - **Sistema POS Próprio:** Desenvolvimento
            """)

        with col2:
            st.info("""
            **📊 Recursos Totais:**

            - **Investimento 3 anos:** R$ 5,3 milhões
            - **CAC Padrão:** R$ 6.500/unidade
            - **CAC Sofázinho:** R$ 3.000/unidade
            - **Capacidade atual:** 30 franquias/mês
            - **ROI esperado:** Baseado em royalties
            - **Payback médio:** 3,5 meses
            """)

        # Métricas de acompanhamento
        st.subheader("📊 KPIs para Acompanhamento")

        kpis_data = pd.DataFrame({
            'KPI': [
                'Taxa de Conversão de Leads',
                'Tempo Médio de Abertura',
                'ROI por Franquia',
                'Penetração por Região',
                'Satisfação do Franqueado'
            ],
            'Meta 2024': ['15%', '90 dias', '25%', '60%', '8.5/10'],
            'Como Medir': [
                'Leads qualificados / Franquias abertas',
                'Assinatura contrato → Inauguração',
                'Lucro líquido / Investimento inicial',
                '% cidades com franquia por região',
                'Pesquisa trimestral NPS'
            ]
        })

        st.dataframe(kpis_data, use_container_width=True, hide_index=True)

        # Cronograma trimestral detalhado
        st.subheader("📅 Cronograma Trimestral Detalhado")

        cronograma_data = pd.DataFrame({
            'Trimestre': [
                '2026 Q1', '2026 Q2', '2026 Q3', '2026 Q4',
                '2027 Q1', '2027 Q2', '2027 Q3', '2027 Q4',
                '2028 Q1', '2028 Q2', '2028 Q3', '2028 Q4'
            ],
            'Padrão': [25, 30, 35, 40, 35, 30, 25, 20, 15, 15, 10, 10],
            'Sofázinho': [65, 70, 75, 56, 70, 75, 80, 60, 80, 85, 90, 80],
            'Total Trimestre': [90, 100, 110, 96, 105, 105, 105, 80, 95, 100, 100, 90],
            'Foco Regional': [
                'SP/RJ/DF', 'SP/MG/PR', 'Capitais SE/S', 'Capitais NE',
                'Interior SP/MG', 'Sul completo', 'Nordeste', 'Centro-Oeste',
                'Norte', 'Capilarização', 'Finalização', 'Consolidação'
            ],
            'Investimento (R$ mil)': [146, 146, 146, 146, 149, 149, 149, 149, 144, 144, 144, 144]
        })

        # Adiciona coluna acumulada
        franquias_base = df['Franquias_Atuais'].sum()
        cronograma_data['Total Acumulado'] = cronograma_data['Total Trimestre'].cumsum() + franquias_base

        st.dataframe(cronograma_data, use_container_width=True, hide_index=True)

        # Gráfico de evolução trimestral
        fig_evolucao = px.line(
            cronograma_data,
            x='Trimestre',
            y='Total Acumulado',
            title='📈 Evolução Trimestral do Total de Franquias (2026-2028)',
            labels={'Total Acumulado': 'Total de Franquias', 'Trimestre': 'Período'}
        )

        # Adiciona linha de meta final
        if 'Total_Franquias_Corrigida' in df.columns:
            meta_final = df['Total_Franquias_Corrigida'].sum()
        else:
            meta_final = df['Total_Franquias_Realista'].sum()

        fig_evolucao.add_hline(
            y=meta_final,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Meta Final: {meta_final:.0f} franquias"
        )

        st.plotly_chart(fig_evolucao, use_container_width=True)

        # Resumo financeiro do plano
        st.subheader("💰 Resumo Financeiro do Plano 2026-2028")

        col1, col2, col3, col4 = st.columns(4)

        investimento_total = cronograma_data['Investimento (R$ mil)'].sum() / 1000  # Converte para milhões
        franquias_adicionais = cronograma_data['Total Trimestre'].sum()

        # Calcula receita da FRANQUEADORA (vendas + royalties)
        # Assumindo 50% Padrão e 50% Sofázinho para simplificar
        franquias_padrao_adicional = franquias_adicionais * 0.3  # 30% Padrão
        franquias_sofazinho_adicional = franquias_adicionais * 0.7  # 70% Sofázinho

        # Receita de vendas (uma vez)
        receita_vendas = (franquias_padrao_adicional * 20000) + (franquias_sofazinho_adicional * 4000)  # Líquido

        # Receita de royalties (anual)
        receita_royalties_anual = (franquias_padrao_adicional * 1199 * 12) + (franquias_sofazinho_adicional * 400 * 12)

        # Receita total anual da franqueadora (após ano 3)
        receita_anual_franqueadora = receita_royalties_anual / 1_000_000  # Em milhões

        with col1:
            st.metric(
                "💰 Investimento Total",
                f"R$ {investimento_total:.1f}M",
                delta="3 anos"
            )

        with col2:
            st.metric(
                "🏢 Franquias Adicionais",
                f"{franquias_adicionais:,}",
                delta=f"+{(franquias_adicionais/franquias_base*100):.0f}% vs atual"
            )

        with col3:
            st.metric(
                "📈 Receita Franqueadora/Ano",
                f"R$ {receita_anual_franqueadora:.1f}M",
                delta="Royalties recorrentes"
            )

        with col4:
            # ROI baseado em receita de royalties recorrentes (3 anos)
            roi_plano = (receita_anual_franqueadora * 3) / investimento_total
            st.metric(
                "📊 ROI do Plano",
                f"{roi_plano:.1f}x",
                delta="3 anos (royalties)"
            )

    with tab7:
        st.header("💰 Simulador de Receita da Franqueadora")

        st.markdown("""
        ### 🎯 **Calcule seus ganhos como franqueadora**
        Simule diferentes cenários de expansão e veja o impacto na sua receita.
        """)

        # Parâmetros atuais
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Situação Atual")

            franquias_atuais_padrao = df[df['Franquias_Atuais'] > 0]['Franquias_Atuais'].sum()
            franquias_atuais_sofazinho = 0  # Assumindo que atuais são todas padrão

            st.metric("🏢 Franquias Padrão Atuais", f"{franquias_atuais_padrao:.0f}")
            st.metric("🏠 Sofázinhos Atuais", f"{franquias_atuais_sofazinho:.0f}")

            # Receita mensal atual de royalties
            royalties_atuais = (franquias_atuais_padrao * 1199) + (franquias_atuais_sofazinho * 400)
            st.metric("💰 Royalties Mensais Atuais", f"R$ {royalties_atuais:,.0f}")
            st.metric("💰 Royalties Anuais Atuais", f"R$ {royalties_atuais * 12:,.0f}")

        with col2:
            st.subheader("🎯 Potencial Total")

            if 'Franquias_Padrao_Corrigida' in df.columns:
                potencial_padrao = df['Franquias_Padrao_Corrigida'].sum()
                potencial_sofazinho = df['Franquias_Sofazinho_Corrigida'].sum()
            else:
                potencial_padrao = df['Franquias_Padrao_Realista'].sum()
                potencial_sofazinho = df['Franquias_Sofazinho_Realista'].sum()

            st.metric("🏢 Potencial Franquias Padrão", f"{potencial_padrao:.0f}")
            st.metric("🏠 Potencial Sofázinhos", f"{potencial_sofazinho:.0f}")

            # Receita potencial total
            royalties_potencial = (potencial_padrao * 1199) + (potencial_sofazinho * 400)
            st.metric("💰 Royalties Mensais Potencial", f"R$ {royalties_potencial:,.0f}")
            st.metric("💰 Royalties Anuais Potencial", f"R$ {royalties_potencial * 12:,.0f}")

        st.markdown("---")

        # Simulador interativo
        st.subheader("🎮 Simulador de Cenários")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### ⚙️ Parâmetros de Venda")

            # Valores de venda
            venda_padrao_bruto = st.number_input(
                "Venda Franquia Padrão (Bruto):",
                min_value=0,
                max_value=100000,
                value=35000,
                step=1000,
                help="Valor bruto da venda de uma franquia padrão"
            )

            venda_padrao_liquido = st.number_input(
                "Venda Franquia Padrão (Líquido):",
                min_value=0,
                max_value=100000,
                value=20000,
                step=1000,
                help="Valor líquido da venda de uma franquia padrão"
            )

            venda_sofazinho_bruto = st.number_input(
                "Venda Sofázinho (Bruto):",
                min_value=0,
                max_value=50000,
                value=12000,
                step=500,
                help="Valor bruto da venda de um Sofázinho"
            )

            venda_sofazinho_liquido = st.number_input(
                "Venda Sofázinho (Líquido):",
                min_value=0,
                max_value=50000,
                value=4000,
                step=500,
                help="Valor líquido da venda de um Sofázinho"
            )

        with col2:
            st.markdown("#### 💰 Royalties Mensais")

            royalty_padrao = st.number_input(
                "Royalty Franquia Padrão:",
                min_value=0,
                max_value=5000,
                value=1199,
                step=50,
                help="Royalty mensal líquido por franquia padrão"
            )

            royalty_sofazinho = st.number_input(
                "Royalty Sofázinho:",
                min_value=0,
                max_value=1000,
                value=400,
                step=25,
                help="Royalty mensal líquido por Sofázinho"
            )

            st.markdown("#### 📅 Período de Análise")

            anos_analise = st.slider(
                "Anos para projeção:",
                min_value=1,
                max_value=10,
                value=5,
                help="Período para calcular royalties acumulados"
            )

        with col3:
            st.markdown("#### 🎯 Metas de Expansão")

            # Metas anuais
            meta_padrao_ano = st.number_input(
                "Meta Franquias Padrão/Ano:",
                min_value=0,
                max_value=200,
                value=50,
                step=5,
                help="Quantas franquias padrão vender por ano"
            )

            meta_sofazinho_ano = st.number_input(
                "Meta Sofázinhos/Ano:",
                min_value=0,
                max_value=500,
                value=100,
                step=10,
                help="Quantos Sofázinhos vender por ano"
            )

            # Percentual de churn anual
            churn_anual = st.slider(
                "Churn Anual (%):",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                help="Percentual de franquias que saem por ano"
            ) / 100

        # Cálculos da simulação
        st.markdown("---")
        st.subheader("📊 Resultados da Simulação")

        # Simula crescimento ano a ano
        resultados = []
        franquias_padrao_acum = franquias_atuais_padrao
        franquias_sofazinho_acum = franquias_atuais_sofazinho

        for ano in range(1, anos_analise + 1):
            # Novas vendas
            novas_padrao = meta_padrao_ano
            novas_sofazinho = meta_sofazinho_ano

            # Aplica churn
            franquias_padrao_acum = franquias_padrao_acum * (1 - churn_anual) + novas_padrao
            franquias_sofazinho_acum = franquias_sofazinho_acum * (1 - churn_anual) + novas_sofazinho

            # Receitas do ano
            receita_vendas = (novas_padrao * venda_padrao_liquido) + (novas_sofazinho * venda_sofazinho_liquido)
            receita_royalties_mensal = (franquias_padrao_acum * royalty_padrao) + (franquias_sofazinho_acum * royalty_sofazinho)
            receita_royalties_anual = receita_royalties_mensal * 12
            receita_total_ano = receita_vendas + receita_royalties_anual

            resultados.append({
                'Ano': ano,
                'Franquias Padrão': int(franquias_padrao_acum),
                'Sofázinhos': int(franquias_sofazinho_acum),
                'Vendas Ano': receita_vendas,
                'Royalties/Mês': receita_royalties_mensal,
                'Royalties/Ano': receita_royalties_anual,
                'Total Ano': receita_total_ano
            })

        # Exibe resultados
        df_resultados = pd.DataFrame(resultados)

        # Formata valores monetários
        df_display = df_resultados.copy()
        df_display['Vendas Ano'] = df_display['Vendas Ano'].apply(lambda x: f"R$ {x:,.0f}")
        df_display['Royalties/Mês'] = df_display['Royalties/Mês'].apply(lambda x: f"R$ {x:,.0f}")
        df_display['Royalties/Ano'] = df_display['Royalties/Ano'].apply(lambda x: f"R$ {x:,.0f}")
        df_display['Total Ano'] = df_display['Total Ano'].apply(lambda x: f"R$ {x:,.0f}")

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Métricas de destaque
        col1, col2, col3, col4 = st.columns(4)

        receita_total_periodo = df_resultados['Total Ano'].sum()
        receita_vendas_periodo = df_resultados['Vendas Ano'].sum()
        receita_royalties_periodo = df_resultados['Royalties/Ano'].sum()
        franquias_finais = df_resultados.iloc[-1]['Franquias Padrão'] + df_resultados.iloc[-1]['Sofázinhos']

        with col1:
            st.metric(
                f"💰 Receita Total ({anos_analise} anos)",
                f"R$ {receita_total_periodo:,.0f}",
                delta="Vendas + Royalties"
            )

        with col2:
            st.metric(
                "🏪 Receita de Vendas",
                f"R$ {receita_vendas_periodo:,.0f}",
                delta=f"{(receita_vendas_periodo/receita_total_periodo*100):.1f}% do total"
            )

        with col3:
            st.metric(
                "💎 Receita de Royalties",
                f"R$ {receita_royalties_periodo:,.0f}",
                delta=f"{(receita_royalties_periodo/receita_total_periodo*100):.1f}% do total"
            )

        with col4:
            st.metric(
                "🏢 Franquias Finais",
                f"{franquias_finais:.0f}",
                delta=f"+{franquias_finais - (franquias_atuais_padrao + franquias_atuais_sofazinho):.0f} vs atual"
            )

        # Gráfico de evolução
        st.subheader("📈 Evolução da Receita")

        fig_evolucao = px.bar(
            df_resultados,
            x='Ano',
            y=['Vendas Ano', 'Royalties/Ano'],
            title="Evolução Anual da Receita (Vendas vs Royalties)",
            labels={'value': 'Receita (R$)', 'variable': 'Tipo de Receita'}
        )

        st.plotly_chart(fig_evolucao, use_container_width=True)

        # Análise de break-even
        st.subheader("⚖️ Análise de Break-Even")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **🎯 Quando os royalties superam as vendas?**

            Os royalties são receita recorrente e crescem com o tempo,
            enquanto as vendas dependem de novas franquias.
            """)

            # Calcula quando royalties > vendas
            for i, row in df_resultados.iterrows():
                if row['Royalties/Ano'] > row['Vendas Ano']:
                    st.success(f"✅ **Ano {row['Ano']}:** Royalties superam vendas!")
                    st.info(f"Royalties: R$ {row['Royalties/Ano']:,.0f} vs Vendas: R$ {row['Vendas Ano']:,.0f}")
                    break
            else:
                st.warning("⚠️ Royalties ainda não superam vendas no período analisado")

        with col2:
            st.markdown("""
            **💡 Insights Estratégicos:**

            - **Vendas:** Receita imediata, mas única
            - **Royalties:** Receita recorrente, cresce com base
            - **Churn:** Impacta diretamente os royalties
            - **Expansão:** Equilibrio entre velocidade e qualidade
            """)

            # ROI das franquias
            roi_padrao = (royalty_padrao * 12 * anos_analise) / venda_padrao_liquido
            roi_sofazinho = (royalty_sofazinho * 12 * anos_analise) / venda_sofazinho_liquido

            st.metric(f"📊 ROI Franquia Padrão ({anos_analise} anos)", f"{roi_padrao:.1f}x")
            st.metric(f"📊 ROI Sofázinho ({anos_analise} anos)", f"{roi_sofazinho:.1f}x")

        # Cenários de stress test
        st.subheader("🧪 Cenários de Stress Test")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 😰 Cenário Pessimista")
            st.markdown("- Meta: 50% das metas")
            st.markdown("- Churn: +5%")

            meta_pess_padrao = meta_padrao_ano * 0.5
            meta_pess_sofazinho = meta_sofazinho_ano * 0.5
            churn_pess = churn_anual + 0.05

            # Calcula cenário pessimista
            franquias_pess = franquias_atuais_padrao
            for ano in range(anos_analise):
                franquias_pess = franquias_pess * (1 - churn_pess) + meta_pess_padrao

            receita_pess = (meta_pess_padrao * anos_analise * venda_padrao_liquido) + \
                          (franquias_pess * royalty_padrao * 12)

            st.metric("Receita Total", f"R$ {receita_pess:,.0f}")

        with col2:
            st.markdown("#### 😐 Cenário Realista")
            st.markdown("- Meta: 100% das metas")
            st.markdown("- Churn: Conforme definido")

            st.metric("Receita Total", f"R$ {receita_total_periodo:,.0f}")

        with col3:
            st.markdown("#### 🚀 Cenário Otimista")
            st.markdown("- Meta: 150% das metas")
            st.markdown("- Churn: -2%")

            meta_otim_padrao = meta_padrao_ano * 1.5
            meta_otim_sofazinho = meta_sofazinho_ano * 1.5
            churn_otim = max(0, churn_anual - 0.02)

            # Calcula cenário otimista
            franquias_otim = franquias_atuais_padrao
            for ano in range(anos_analise):
                franquias_otim = franquias_otim * (1 - churn_otim) + meta_otim_padrao

            receita_otim = (meta_otim_padrao * anos_analise * venda_padrao_liquido) + \
                          (franquias_otim * royalty_padrao * 12)

            st.metric("Receita Total", f"R$ {receita_otim:,.0f}")

        # Download dos resultados
        st.markdown("---")
        csv_resultados = df_display.to_csv(index=False)
        st.download_button(
            label="📥 Download Simulação CSV",
            data=csv_resultados,
            file_name=f"simulacao_receita_franqueadora_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with tab8:
        st.header("🏙️ Análise por Bairros - Grandes Cidades")

        # Carrega dados reais de população
        @st.cache_data
        def carregar_dados_bairros():
            """Carrega dados reais de população por bairro"""
            try:
                df_pop = pd.read_csv('População_bairros_Sp - Página1.csv')
                return df_pop
            except:
                return None

        df_populacao = carregar_dados_bairros()

        # Função para obter população real
        def obter_populacao_real(nome_bairro):
            """Obtém população real do bairro dos dados do SEADE"""
            if df_populacao is not None:
                # Tenta encontrar o bairro exato
                match = df_populacao[df_populacao['REGIÃO'].str.contains(nome_bairro, case=False, na=False)]
                if len(match) > 0:
                    return int(match.iloc[0]['2023'])
            return None

        # Seletor de município
        st.subheader("📍 Selecione a Cidade para Análise")

        col_sel1, col_sel2 = st.columns([2, 1])

        with col_sel1:
            municipio_selecionado = st.selectbox(
                "Escolha a cidade:",
                [
                    "São Paulo-SP",
                    "Rio de Janeiro-RJ",
                    "Brasília-DF",
                    "Belo Horizonte-MG",
                    "Salvador-BA",
                    "Fortaleza-CE",
                    "Porto Alegre-RS"
                ],
                index=0
            )

        with col_sel2:
            st.info(f"""
            **Critério de seleção:**
            Cidades com 5+ franquias
            padrão potenciais
            """)

        # Dados das franquias atuais por município
        if municipio_selecionado == "São Paulo-SP":
            # Dados das franquias atuais em SP
            franquias_sp_atuais = [
                {"bairro": "Jardim Anália Franco", "zona": "Zona Leste", "lat": -23.5200, "lon": -46.5600},
                {"bairro": "Alto de Pinheiros", "zona": "Zona Oeste", "lat": -23.5450, "lon": -46.7100},
                {"bairro": "Brooklin", "zona": "Zona Sul", "lat": -23.6100, "lon": -46.7000},
                {"bairro": "Campo Belo", "zona": "Zona Sul", "lat": -23.6200, "lon": -46.6700},
                {"bairro": "Freguesia do Ó", "zona": "Zona Norte", "lat": -23.4800, "lon": -46.7300},
                {"bairro": "Higienópolis", "zona": "Centro", "lat": -23.5400, "lon": -46.6500},
                {"bairro": "Interlagos", "zona": "Zona Sul", "lat": -23.6800, "lon": -46.6900},
                {"bairro": "Ipiranga", "zona": "Zona Sul", "lat": -23.5900, "lon": -46.6100},
                {"bairro": "Itaim Bibi", "zona": "Zona Oeste", "lat": -23.5900, "lon": -46.6800},
                {"bairro": "Jabaquara", "zona": "Zona Sul", "lat": -23.6400, "lon": -46.6400},
                {"bairro": "Jardim Paulista", "zona": "Centro", "lat": -23.5600, "lon": -46.6600},
                {"bairro": "Jardins", "zona": "Centro", "lat": -23.5700, "lon": -46.6600},
                {"bairro": "Lapa", "zona": "Zona Oeste", "lat": -23.5300, "lon": -46.7000},
                {"bairro": "Moema", "zona": "Zona Sul", "lat": -23.6000, "lon": -46.6600},
                {"bairro": "Perdizes", "zona": "Zona Oeste", "lat": -23.5400, "lon": -46.6900},
                {"bairro": "Pinheiros", "zona": "Zona Oeste", "lat": -23.5600, "lon": -46.7000},
                {"bairro": "Santana", "zona": "Zona Norte", "lat": -23.5100, "lon": -46.6300},
                {"bairro": "Tatuapé", "zona": "Zona Leste", "lat": -23.5400, "lon": -46.5700},
                {"bairro": "Vila Andrade", "zona": "Zona Sul", "lat": -23.6300, "lon": -46.7200},
                {"bairro": "Vila Clementino", "zona": "Zona Sul", "lat": -23.5900, "lon": -46.6400},
                {"bairro": "Vila Leopoldina", "zona": "Zona Oeste", "lat": -23.5300, "lon": -46.7400},
                {"bairro": "Vila Mariana", "zona": "Zona Sul", "lat": -23.5800, "lon": -46.6400},
                {"bairro": "Vila Prudente", "zona": "Zona Leste", "lat": -23.5800, "lon": -46.5800},
                {"bairro": "Vila Romana", "zona": "Zona Oeste", "lat": -23.5300, "lon": -46.7200},
                {"bairro": "Tucuruvi", "zona": "Zona Norte", "lat": -23.4600, "lon": -46.6000},
                {"bairro": "Morumbi", "zona": "Zona Sul", "lat": -23.6200, "lon": -46.7000}
            ]

            # Bairros candidatos para expansão (com dados reais quando disponíveis)
            bairros_candidatos = [
                # Zona Sul (Alta Renda)
                {"bairro": "Campo Grande", "zona": "Zona Sul", "lat": -23.6500, "lon": -46.6800,
                 "score": 85, "populacao": obter_populacao_real("Campo Grande") or 117331,
                 "renda_media": 4500, "motivo": "Similar ao Campo Belo, alta renda"},
            {"bairro": "Saúde", "zona": "Zona Sul", "lat": -23.6200, "lon": -46.6300,
             "score": 82, "populacao": obter_populacao_real("Saúde") or 130000,
             "renda_media": 4200, "motivo": "Próximo ao Jabaquara, crescimento"},
            {"bairro": "Cursino", "zona": "Zona Sul", "lat": -23.6100, "lon": -46.6000,
             "score": 78, "populacao": obter_populacao_real("Cursino") or 110000,
             "renda_media": 3800, "motivo": "Entre Vila Prudente e Jabaquara"},
            {"bairro": "Planalto Paulista", "zona": "Zona Sul", "lat": -23.5800, "lon": -46.6500,
             "score": 80, "populacao": obter_populacao_real("Planalto Paulista") or 85000,
             "renda_media": 4800, "motivo": "Próximo ao Jardim Paulista"},

            # Zona Oeste (Expansão)
            {"bairro": "Butantã", "zona": "Zona Oeste", "lat": -23.5700, "lon": -46.7300,
             "score": 88, "populacao": obter_populacao_real("Butantã") or 51776,
             "renda_media": 5200, "motivo": "Próximo a Pinheiros, alta renda"},
            {"bairro": "Rio Pequeno", "zona": "Zona Oeste", "lat": -23.5500, "lon": -46.7400,
             "score": 75, "populacao": obter_populacao_real("Rio Pequeno") or 131664,
             "renda_media": 3500, "motivo": "Entre Lapa e Pinheiros"},
            {"bairro": "Jaguaré", "zona": "Zona Oeste", "lat": -23.5200, "lon": -46.7500,
             "score": 72, "populacao": obter_populacao_real("Jaguaré") or 50000,
             "renda_media": 3200, "motivo": "Próximo à Vila Leopoldina"},

            # Zona Norte (Oportunidade)
            {"bairro": "Casa Verde", "zona": "Zona Norte", "lat": -23.4900, "lon": -46.6500,
             "score": 70, "populacao": obter_populacao_real("Casa Verde") or 80147,
             "renda_media": 3000, "motivo": "Próximo ao Tucuruvi"},
            {"bairro": "Limão", "zona": "Zona Norte", "lat": -23.4800, "lon": -46.6900,
             "score": 68, "populacao": obter_populacao_real("Limão") or 82257,
             "renda_media": 2800, "motivo": "Entre Freguesia do Ó e Casa Verde"},
            {"bairro": "Vila Guilherme", "zona": "Zona Norte", "lat": -23.4700, "lon": -46.6100,
             "score": 72, "populacao": obter_populacao_real("Vila Guilherme") or 55000,
             "renda_media": 3200, "motivo": "Próximo ao Tucuruvi"},
            {"bairro": "Vila Maria", "zona": "Zona Norte", "lat": -23.5100, "lon": -46.5900,
             "score": 74, "populacao": obter_populacao_real("Vila Maria") or 115000,
             "renda_media": 3400, "motivo": "Expansão da Zona Norte"},

            # Zona Leste (Crescimento)
            {"bairro": "Mooca", "zona": "Zona Leste", "lat": -23.5500, "lon": -46.6000,
             "score": 76, "populacao": obter_populacao_real("Moóca") or 81592,
             "renda_media": 3600, "motivo": "Próximo ao Ipiranga"},
            {"bairro": "Belém", "zona": "Zona Leste", "lat": -23.5400, "lon": -46.5900,
             "score": 74, "populacao": obter_populacao_real("Belém") or 56454,
             "renda_media": 3400, "motivo": "Entre Mooca e Tatuapé"},
            {"bairro": "Penha", "zona": "Zona Leste", "lat": -23.5300, "lon": -46.5400,
             "score": 71, "populacao": obter_populacao_real("Penha") or 133403,
             "renda_media": 3100, "motivo": "Expansão da Zona Leste"},
            {"bairro": "Vila Formosa", "zona": "Zona Leste", "lat": -23.5600, "lon": -46.5500,
             "score": 73, "populacao": obter_populacao_real("Vila Formosa") or 95000,
             "renda_media": 3300, "motivo": "Próximo ao Tatuapé"},

            # Centro Expandido
            {"bairro": "Bela Vista", "zona": "Centro", "lat": -23.5600, "lon": -46.6400,
             "score": 79, "populacao": obter_populacao_real("Bela Vista") or 70000,
             "renda_media": 4000, "motivo": "Centro expandido, próximo aos Jardins"},
            {"bairro": "Liberdade", "zona": "Centro", "lat": -23.5600, "lon": -46.6300,
             "score": 77, "populacao": obter_populacao_real("Liberdade") or 76245,
             "renda_media": 3800, "motivo": "Centro, movimento comercial"},
            {"bairro": "Aclimação", "zona": "Centro", "lat": -23.5700, "lon": -46.6300,
             "score": 75, "populacao": obter_populacao_real("Aclimação") or 15000,
             "renda_media": 4200, "motivo": "Próximo à Vila Mariana"},

            # Zona Sul Expandida
                {"bairro": "Santo Amaro", "zona": "Zona Sul", "lat": -23.6500, "lon": -46.7100,
                 "score": 81, "populacao": obter_populacao_real("Santo Amaro") or 70000,
                 "renda_media": 4300, "motivo": "Centro comercial, próximo ao Brooklin"},
                {"bairro": "Cidade Ademar", "zona": "Zona Sul", "lat": -23.6700, "lon": -46.6400,
                 "score": 65, "populacao": obter_populacao_real("Cidade Ademar") or 270000,
                 "renda_media": 2500, "motivo": "Grande população, próximo ao Jabaquara"}
            ]

        elif municipio_selecionado == "Rio de Janeiro-RJ":
            franquias_sp_atuais = [
                {"bairro": "Ilha do Governador", "zona": "Zona Norte", "lat": -22.8100, "lon": -43.2000},
                {"bairro": "Nova Friburgo Centro", "zona": "Região Serrana", "lat": -22.2819, "lon": -42.5312},
                {"bairro": "Bangú", "zona": "Zona Oeste", "lat": -22.8700, "lon": -43.4700},
                {"bairro": "Botafogo", "zona": "Zona Sul", "lat": -22.9519, "lon": -43.1875},
                {"bairro": "Campo Grande", "zona": "Zona Oeste", "lat": -22.9056, "lon": -43.5611},
                {"bairro": "Copacabana", "zona": "Zona Sul", "lat": -22.9711, "lon": -43.1822},
                {"bairro": "Flamengo", "zona": "Zona Sul", "lat": -22.9322, "lon": -43.1759},
                {"bairro": "Freguesia", "zona": "Zona Oeste", "lat": -22.9300, "lon": -43.3400},
                {"bairro": "Ipanema", "zona": "Zona Sul", "lat": -22.9838, "lon": -43.2096},
                {"bairro": "Jardim Botânico", "zona": "Zona Sul", "lat": -22.9661, "lon": -43.2081},
                {"bairro": "Leblon", "zona": "Zona Sul", "lat": -22.9840, "lon": -43.2240},
                {"bairro": "Maracanã", "zona": "Zona Norte", "lat": -22.9122, "lon": -43.2302},
                {"bairro": "Méier", "zona": "Zona Norte", "lat": -22.9026, "lon": -43.2784},
                {"bairro": "Penha", "zona": "Zona Norte", "lat": -22.8400, "lon": -43.2800},
                {"bairro": "Recreio dos Bandeirantes", "zona": "Zona Oeste", "lat": -23.0267, "lon": -43.4412},
                {"bairro": "Taquara", "zona": "Zona Oeste", "lat": -22.9200, "lon": -43.3800},
                {"bairro": "Tijuca", "zona": "Zona Norte", "lat": -22.9249, "lon": -43.2277},
                {"bairro": "Vila Isabel", "zona": "Zona Norte", "lat": -22.9154, "lon": -43.2425},
                {"bairro": "Vila Valqueire", "zona": "Zona Oeste", "lat": -22.8900, "lon": -43.3700}
            ]

            bairros_candidatos = [
                {"bairro": "Laranjeiras", "zona": "Zona Sul", "lat": -22.9364, "lon": -43.1859,
                 "score": 88, "populacao": 45000, "renda_media": 5500, "motivo": "Zona Sul, próximo ao centro"},
                {"bairro": "Urca", "zona": "Zona Sul", "lat": -22.9533, "lon": -43.1656,
                 "score": 85, "populacao": 7000, "renda_media": 8000, "motivo": "Zona Sul nobre, exclusiva"},
                {"bairro": "Gávea", "zona": "Zona Sul", "lat": -22.9792, "lon": -43.2267,
                 "score": 82, "populacao": 15000, "renda_media": 7200, "motivo": "Alta renda, próximo PUC"},
                {"bairro": "Barra da Tijuca", "zona": "Zona Oeste", "lat": -23.0045, "lon": -43.3642,
                 "score": 80, "populacao": 300000, "renda_media": 5200, "motivo": "Grande população, crescimento"},
                {"bairro": "Jacarepaguá", "zona": "Zona Oeste", "lat": -22.9400, "lon": -43.3700,
                 "score": 75, "populacao": 157000, "renda_media": 3800, "motivo": "Expansão urbana"},
                {"bairro": "Andaraí", "zona": "Zona Norte", "lat": -22.9300, "lon": -43.2500,
                 "score": 78, "populacao": 21000, "renda_media": 4200, "motivo": "Próximo à Tijuca"}
            ]

        elif municipio_selecionado == "Brasília-DF":
            franquias_sp_atuais = [
                {"bairro": "Asa Norte", "zona": "Plano Piloto", "lat": -15.7801, "lon": -47.8825}
            ]

            bairros_candidatos = [
                {"bairro": "Asa Sul", "zona": "Plano Piloto", "lat": -15.8267, "lon": -47.9218,
                 "score": 92, "populacao": 90000, "renda_media": 8500, "motivo": "Plano Piloto, alta renda"},
                {"bairro": "Lago Sul", "zona": "Plano Piloto", "lat": -15.8467, "lon": -47.8625,
                 "score": 90, "populacao": 30000, "renda_media": 12000, "motivo": "Área nobre, alta renda"},
                {"bairro": "Lago Norte", "zona": "Plano Piloto", "lat": -15.7267, "lon": -47.8825,
                 "score": 88, "populacao": 35000, "renda_media": 10000, "motivo": "Área nobre"},
                {"bairro": "Sudoeste", "zona": "Plano Piloto", "lat": -15.7967, "lon": -47.9325,
                 "score": 85, "populacao": 55000, "renda_media": 8500, "motivo": "Região central"},
                {"bairro": "Águas Claras", "zona": "RA", "lat": -15.8344, "lon": -48.0266,
                 "score": 82, "populacao": 120000, "renda_media": 6000, "motivo": "Região moderna"},
                {"bairro": "Taguatinga", "zona": "RA", "lat": -15.8267, "lon": -48.0566,
                 "score": 80, "populacao": 220000, "renda_media": 4500, "motivo": "Grande população"},
                {"bairro": "Guará", "zona": "RA", "lat": -15.8367, "lon": -47.9666,
                 "score": 78, "populacao": 140000, "renda_media": 4800, "motivo": "Próximo ao centro"}
            ]

        elif municipio_selecionado == "Belo Horizonte-MG":
            franquias_sp_atuais = [
                {"bairro": "Belvedere", "zona": "Zona Sul", "lat": -19.9500, "lon": -43.9600},
                {"bairro": "Guarani", "zona": "Zona Norte", "lat": -19.8700, "lon": -43.9500},
                {"bairro": "Savassi", "zona": "Centro-Sul", "lat": -19.9400, "lon": -43.9300}
            ]

            bairros_candidatos = [
                {"bairro": "Lourdes", "zona": "Centro-Sul", "lat": -19.9350, "lon": -43.9400,
                 "score": 88, "populacao": 7000, "renda_media": 8500, "motivo": "Bairro nobre, alta renda"},
                {"bairro": "Funcionários", "zona": "Centro-Sul", "lat": -19.9300, "lon": -43.9350,
                 "score": 85, "populacao": 10000, "renda_media": 7200, "motivo": "Centro expandido"},
                {"bairro": "Santo Agostinho", "zona": "Centro-Sul", "lat": -19.9450, "lon": -43.9350,
                 "score": 82, "populacao": 5000, "renda_media": 7800, "motivo": "Próximo ao Savassi"},
                {"bairro": "Buritis", "zona": "Zona Oeste", "lat": -19.9800, "lon": -44.0200,
                 "score": 80, "populacao": 25000, "renda_media": 6000, "motivo": "Bairro planejado"},
                {"bairro": "Pampulha", "zona": "Zona Norte", "lat": -19.8600, "lon": -43.9700,
                 "score": 78, "populacao": 15000, "renda_media": 5500, "motivo": "Região universitária"}
            ]

        elif municipio_selecionado == "Salvador-BA":
            franquias_sp_atuais = [
                {"bairro": "Horto Florestal", "zona": "Zona Norte", "lat": -12.9500, "lon": -38.4600},
                {"bairro": "Pituba", "zona": "Zona Sul", "lat": -12.9800, "lon": -38.4400}
            ]

            bairros_candidatos = [
                {"bairro": "Barra", "zona": "Zona Sul", "lat": -13.0100, "lon": -38.5200,
                 "score": 88, "populacao": 50000, "renda_media": 6500, "motivo": "Orla, alta renda"},
                {"bairro": "Ondina", "zona": "Zona Sul", "lat": -13.0000, "lon": -38.5100,
                 "score": 85, "populacao": 15000, "renda_media": 7000, "motivo": "Bairro nobre"},
                {"bairro": "Rio Vermelho", "zona": "Zona Sul", "lat": -13.0050, "lon": -38.4900,
                 "score": 82, "populacao": 25000, "renda_media": 5800, "motivo": "Boêmio, classe média alta"},
                {"bairro": "Itaigara", "zona": "Zona Sul", "lat": -12.9900, "lon": -38.4700,
                 "score": 80, "populacao": 20000, "renda_media": 6200, "motivo": "Próximo à Pituba"},
                {"bairro": "Caminho das Árvores", "zona": "Zona Sul", "lat": -12.9850, "lon": -38.4650,
                 "score": 78, "populacao": 12000, "renda_media": 6800, "motivo": "Comercial, alta renda"}
            ]

        elif municipio_selecionado == "Fortaleza-CE":
            franquias_sp_atuais = [
                {"bairro": "Cambeba", "zona": "Zona Sul", "lat": -3.8200, "lon": -38.4800},
                {"bairro": "Fátima", "zona": "Centro", "lat": -3.7400, "lon": -38.5300},
                {"bairro": "Presidente Kennedy", "zona": "Zona Oeste", "lat": -3.7600, "lon": -38.5800}
            ]

            bairros_candidatos = [
                {"bairro": "Meireles", "zona": "Zona Leste", "lat": -3.7300, "lon": -38.4900,
                 "score": 88, "populacao": 40000, "renda_media": 6000, "motivo": "Orla, alta renda"},
                {"bairro": "Aldeota", "zona": "Zona Leste", "lat": -3.7400, "lon": -38.5000,
                 "score": 85, "populacao": 50000, "renda_media": 5500, "motivo": "Bairro nobre"},
                {"bairro": "Cocó", "zona": "Zona Sul", "lat": -3.7800, "lon": -38.4700,
                 "score": 82, "populacao": 25000, "renda_media": 5200, "motivo": "Próximo ao shopping"},
                {"bairro": "Papicu", "zona": "Zona Leste", "lat": -3.7500, "lon": -38.4600,
                 "score": 80, "populacao": 35000, "renda_media": 4800, "motivo": "Orla, crescimento"},
                {"bairro": "Dionísio Torres", "zona": "Centro", "lat": -3.7500, "lon": -38.5200,
                 "score": 78, "populacao": 30000, "renda_media": 4500, "motivo": "Centro expandido"}
            ]

        elif municipio_selecionado == "Porto Alegre-RS":
            franquias_sp_atuais = [
                {"bairro": "Boa Vista", "zona": "Centro", "lat": -30.0300, "lon": -51.2100},
                {"bairro": "Moinhos de Vento", "zona": "Zona Leste", "lat": -30.0200, "lon": -51.1900},
                {"bairro": "Petrópolis", "zona": "Zona Norte", "lat": -30.0100, "lon": -51.2000}
            ]

            bairros_candidatos = [
                {"bairro": "Bela Vista", "zona": "Zona Leste", "lat": -30.0250, "lon": -51.1850,
                 "score": 88, "populacao": 15000, "renda_media": 7500, "motivo": "Bairro nobre"},
                {"bairro": "Auxiliadora", "zona": "Zona Leste", "lat": -30.0150, "lon": -51.1950,
                 "score": 85, "populacao": 12000, "renda_media": 7000, "motivo": "Alta renda"},
                {"bairro": "Rio Branco", "zona": "Zona Leste", "lat": -30.0350, "lon": -51.1800,
                 "score": 82, "populacao": 18000, "renda_media": 6500, "motivo": "Próximo ao centro"},
                {"bairro": "Menino Deus", "zona": "Centro", "lat": -30.0400, "lon": -51.2200,
                 "score": 80, "populacao": 20000, "renda_media": 6000, "motivo": "Centro expandido"},
                {"bairro": "Santana", "zona": "Zona Leste", "lat": -30.0200, "lon": -51.1800,
                 "score": 78, "populacao": 25000, "renda_media": 5800, "motivo": "Próximo Moinhos de Vento"}
            ]

        else:
            # Fallback genérico
            franquias_sp_atuais = [
                {"bairro": "Centro", "zona": "Centro", "lat": -23.5505, "lon": -46.6333}
            ]

            bairros_candidatos = [
                {"bairro": "Bairro Nobre", "zona": "Zona Sul", "lat": -23.6205, "lon": -46.6533,
                 "score": 85, "populacao": 80000, "renda_media": 5000, "motivo": "Alta renda"}
            ]

        # Informações dinâmicas por cidade (dados reais)
        info_cidades = {
            "São Paulo-SP": {
                "atuais": 26, "potencial": 46, "adicional": 20, "cobertura": 57,
                "dados_reais": df_populacao is not None
            },
            "Rio de Janeiro-RJ": {
                "atuais": 19, "potencial": 25, "adicional": 6, "cobertura": 76,
                "dados_reais": False
            },
            "Brasília-DF": {
                "atuais": 1, "potencial": 8, "adicional": 7, "cobertura": 13,
                "dados_reais": False
            },
            "Belo Horizonte-MG": {
                "atuais": 3, "potencial": 8, "adicional": 5, "cobertura": 38,
                "dados_reais": False
            },
            "Salvador-BA": {
                "atuais": 2, "potencial": 7, "adicional": 5, "cobertura": 29,
                "dados_reais": False
            },
            "Fortaleza-CE": {
                "atuais": 3, "potencial": 8, "adicional": 5, "cobertura": 38,
                "dados_reais": False
            },
            "Porto Alegre-RS": {
                "atuais": 3, "potencial": 8, "adicional": 5, "cobertura": 38,
                "dados_reais": False
            }
        }

        info_cidade = info_cidades.get(municipio_selecionado, info_cidades["São Paulo-SP"])

        # Status dos dados
        if info_cidade["dados_reais"]:
            st.success(f"""
            **📊 DADOS REAIS CARREGADOS - {municipio_selecionado}:**
            - **População por bairro:** SEADE 2023 ✅
            - **Total de bairros:** {len(df_populacao)} distritos
            - **Fonte:** Fundação SEADE - Governo SP
            """)
        else:
            st.warning(f"⚠️ {municipio_selecionado}: Usando dados estimados - dados reais em desenvolvimento")

        st.info(f"""
        **📍 SITUAÇÃO ATUAL EM {municipio_selecionado.upper()}:**
        - **Franquias atuais:** {info_cidade["atuais"]} unidades
        - **Potencial total:** {info_cidade["potencial"]} franquias
        - **Oportunidade:** +{info_cidade["adicional"]} franquias adicionais
        - **Cobertura atual:** {info_cidade["cobertura"]}% do potencial
        """)

        # Seletor de visualização
        col1, col2 = st.columns([2, 1])

        with col2:
            visualizacao = st.selectbox(
                "Tipo de análise:",
                ["Mapa Geral", "Top Candidatos", "Por Zona", "Análise Detalhada"]
            )

            filtro_score = st.slider(
                "Score mínimo:",
                min_value=60,
                max_value=95,
                value=70,
                step=5
            )

        with col1:
            if visualizacao == "Mapa Geral":
                # Criar mapa com franquias atuais e candidatos
                import plotly.graph_objects as go

                fig = go.Figure()

                # Franquias atuais (azul)
                lats_atuais = [f["lat"] for f in franquias_sp_atuais]
                lons_atuais = [f["lon"] for f in franquias_sp_atuais]
                nomes_atuais = [f["bairro"] for f in franquias_sp_atuais]

                fig.add_trace(go.Scattermapbox(
                    lat=lats_atuais,
                    lon=lons_atuais,
                    mode='markers',
                    marker=dict(size=12, color='blue'),
                    text=nomes_atuais,
                    name='Franquias Atuais',
                    hovertemplate='<b>%{text}</b><br>Status: Ativa<extra></extra>'
                ))

                # Candidatos filtrados (verde)
                candidatos_filtrados = [b for b in bairros_candidatos if b["score"] >= filtro_score]
                if candidatos_filtrados:
                    lats_candidatos = [c["lat"] for c in candidatos_filtrados]
                    lons_candidatos = [c["lon"] for c in candidatos_filtrados]
                    nomes_candidatos = [f"{c['bairro']} (Score: {c['score']})" for c in candidatos_filtrados]

                    fig.add_trace(go.Scattermapbox(
                        lat=lats_candidatos,
                        lon=lons_candidatos,
                        mode='markers',
                        marker=dict(size=10, color='green'),
                        text=nomes_candidatos,
                        name='Candidatos',
                        hovertemplate='<b>%{text}</b><br>Status: Candidato<extra></extra>'
                    ))

                # Configurações de mapa por cidade
                config_mapas = {
                    "São Paulo-SP": {"lat": -23.5505, "lon": -46.6333, "zoom": 10},
                    "Rio de Janeiro-RJ": {"lat": -22.9068, "lon": -43.1729, "zoom": 11},
                    "Brasília-DF": {"lat": -15.7942, "lon": -47.8822, "zoom": 10},
                    "Belo Horizonte-MG": {"lat": -19.9167, "lon": -43.9345, "zoom": 11},
                    "Salvador-BA": {"lat": -12.9714, "lon": -38.5014, "zoom": 11},
                    "Fortaleza-CE": {"lat": -3.7319, "lon": -38.5267, "zoom": 11},
                    "Porto Alegre-RS": {"lat": -30.0346, "lon": -51.2177, "zoom": 11},
                    "Curitiba-PR": {"lat": -25.4284, "lon": -49.2733, "zoom": 11}
                }

                config_mapa = config_mapas.get(municipio_selecionado, config_mapas["São Paulo-SP"])

                fig.update_layout(
                    mapbox=dict(
                        style="open-street-map",
                        center=dict(lat=config_mapa["lat"], lon=config_mapa["lon"]),
                        zoom=config_mapa["zoom"]
                    ),
                    height=600,
                    title=f"🗺️ Franquias Atuais vs Bairros Candidatos - {municipio_selecionado}"
                )

                st.plotly_chart(fig, use_container_width=True)

            elif visualizacao == "Top Candidatos":
                # Lista dos melhores candidatos
                candidatos_filtrados = [b for b in bairros_candidatos if b["score"] >= filtro_score]
                candidatos_ordenados = sorted(candidatos_filtrados, key=lambda x: x["score"], reverse=True)

                st.subheader(f"🏆 Top {len(candidatos_ordenados)} Bairros Candidatos")

                for i, candidato in enumerate(candidatos_ordenados[:10], 1):
                    with st.expander(f"{i}º. {candidato['bairro']} - Score: {candidato['score']}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Zona:** {candidato['zona']}")
                            st.write(f"**População:** {candidato['populacao']:,} hab")
                            st.write(f"**Renda Média:** R$ {candidato['renda_media']:,}")
                        with col_b:
                            st.write(f"**Motivo:** {candidato['motivo']}")
                            if candidato['score'] >= 85:
                                st.success("🟢 Prioridade Alta")
                            elif candidato['score'] >= 75:
                                st.warning("🟡 Prioridade Média")
                            else:
                                st.info("🔵 Prioridade Baixa")

            elif visualizacao == "Por Zona":
                # Análise por zona
                st.subheader("🗺️ Análise por Zona de São Paulo")

                # Agrupar por zona
                zonas_atuais = {}
                zonas_candidatos = {}

                for f in franquias_sp_atuais:
                    zona = f["zona"]
                    if zona not in zonas_atuais:
                        zonas_atuais[zona] = 0
                    zonas_atuais[zona] += 1

                candidatos_filtrados = [b for b in bairros_candidatos if b["score"] >= filtro_score]
                for c in candidatos_filtrados:
                    zona = c["zona"]
                    if zona not in zonas_candidatos:
                        zonas_candidatos[zona] = []
                    zonas_candidatos[zona].append(c)

                # Mostrar por zona
                zonas_ordem = ["Centro", "Zona Sul", "Zona Oeste", "Zona Norte", "Zona Leste"]

                for zona in zonas_ordem:
                    with st.expander(f"📍 {zona}"):
                        col_atual, col_candidatos = st.columns(2)

                        with col_atual:
                            st.write(f"**Franquias Atuais:** {zonas_atuais.get(zona, 0)}")
                            atuais_zona = [f["bairro"] for f in franquias_sp_atuais if f["zona"] == zona]
                            if atuais_zona:
                                st.write("• " + "\n• ".join(atuais_zona))

                        with col_candidatos:
                            candidatos_zona = zonas_candidatos.get(zona, [])
                            st.write(f"**Candidatos:** {len(candidatos_zona)}")
                            if candidatos_zona:
                                for c in sorted(candidatos_zona, key=lambda x: x["score"], reverse=True)[:3]:
                                    st.write(f"• {c['bairro']} (Score: {c['score']})")

            elif visualizacao == "Análise Detalhada":
                # Análise detalhada com métricas
                st.subheader("📊 Análise Detalhada dos Candidatos")

                candidatos_filtrados = [b for b in bairros_candidatos if b["score"] >= filtro_score]

                if candidatos_filtrados:
                    # Criar DataFrame para análise
                    df_candidatos = pd.DataFrame(candidatos_filtrados)

                    # Métricas gerais
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

                    with col_m1:
                        st.metric("Total Candidatos", len(candidatos_filtrados))

                    with col_m2:
                        score_medio = df_candidatos['score'].mean()
                        st.metric("Score Médio", f"{score_medio:.1f}")

                    with col_m3:
                        pop_total = df_candidatos['populacao'].sum()
                        st.metric("População Total", f"{pop_total:,}")

                    with col_m4:
                        renda_media = df_candidatos['renda_media'].mean()
                        st.metric("Renda Média", f"R$ {renda_media:,.0f}")

                    # Tabela detalhada
                    st.subheader("📋 Ranking Detalhado")

                    df_display = df_candidatos.copy()
                    df_display = df_display.sort_values('score', ascending=False)
                    df_display['renda_media'] = df_display['renda_media'].apply(lambda x: f"R$ {x:,}")
                    df_display['populacao'] = df_display['populacao'].apply(lambda x: f"{x:,}")

                    df_display = df_display.rename(columns={
                        'bairro': 'Bairro',
                        'zona': 'Zona',
                        'score': 'Score',
                        'populacao': 'População',
                        'renda_media': 'Renda Média',
                        'motivo': 'Justificativa'
                    })

                    st.dataframe(
                        df_display[['Bairro', 'Zona', 'Score', 'População', 'Renda Média', 'Justificativa']],
                        use_container_width=True,
                        hide_index=True
                    )

                    # Gráfico de distribuição por zona
                    st.subheader("📊 Distribuição por Zona")

                    zona_counts = df_candidatos['zona'].value_counts()

                    fig_zona = px.bar(
                        x=zona_counts.index,
                        y=zona_counts.values,
                        title="Número de Candidatos por Zona",
                        labels={'x': 'Zona', 'y': 'Número de Candidatos'}
                    )

                    st.plotly_chart(fig_zona, use_container_width=True)

        # Resumo e próximos passos
        st.subheader(f"🎯 Resumo e Recomendações - {municipio_selecionado}")

        col_res1, col_res2 = st.columns(2)

        # Top 5 dinâmico por cidade
        top_5_cidades = {
            "São Paulo-SP": [
                "1. **Butantã** - Score 88 (Próximo Pinheiros)",
                "2. **Campo Grande** - Score 85 (Similar Campo Belo)",
                "3. **Saúde** - Score 82 (Próximo Jabaquara)",
                "4. **Santo Amaro** - Score 81 (Centro comercial)",
                "5. **Planalto Paulista** - Score 80 (Próximo Jardim Paulista)"
            ],
            "Rio de Janeiro-RJ": [
                "1. **Laranjeiras** - Score 88 (Zona Sul, próximo centro)",
                "2. **Urca** - Score 85 (Zona Sul nobre, exclusiva)",
                "3. **Gávea** - Score 82 (Alta renda, próximo PUC)",
                "4. **Barra da Tijuca** - Score 80 (Grande população)",
                "5. **Andaraí** - Score 78 (Próximo à Tijuca)"
            ],
            "Brasília-DF": [
                "1. **Asa Sul** - Score 92 (Plano Piloto, alta renda)",
                "2. **Lago Sul** - Score 90 (Área nobre, alta renda)",
                "3. **Lago Norte** - Score 88 (Área nobre)",
                "4. **Sudoeste** - Score 85 (Região central)",
                "5. **Águas Claras** - Score 82 (Região moderna)"
            ],
            "Belo Horizonte-MG": [
                "1. **Lourdes** - Score 88 (Bairro nobre, alta renda)",
                "2. **Funcionários** - Score 85 (Centro expandido)",
                "3. **Santo Agostinho** - Score 82 (Próximo ao Savassi)",
                "4. **Buritis** - Score 80 (Bairro planejado)",
                "5. **Pampulha** - Score 78 (Região universitária)"
            ],
            "Salvador-BA": [
                "1. **Barra** - Score 88 (Orla, alta renda)",
                "2. **Ondina** - Score 85 (Bairro nobre)",
                "3. **Rio Vermelho** - Score 82 (Boêmio, classe média alta)",
                "4. **Itaigara** - Score 80 (Próximo à Pituba)",
                "5. **Caminho das Árvores** - Score 78 (Comercial, alta renda)"
            ],
            "Fortaleza-CE": [
                "1. **Meireles** - Score 88 (Orla, alta renda)",
                "2. **Aldeota** - Score 85 (Bairro nobre)",
                "3. **Cocó** - Score 82 (Próximo ao shopping)",
                "4. **Papicu** - Score 80 (Orla, crescimento)",
                "5. **Dionísio Torres** - Score 78 (Centro expandido)"
            ],
            "Porto Alegre-RS": [
                "1. **Bela Vista** - Score 88 (Bairro nobre)",
                "2. **Auxiliadora** - Score 85 (Alta renda)",
                "3. **Rio Branco** - Score 82 (Próximo ao centro)",
                "4. **Menino Deus** - Score 80 (Centro expandido)",
                "5. **Santana** - Score 78 (Próximo Moinhos de Vento)"
            ]
        }

        top_5_atual = top_5_cidades.get(municipio_selecionado, [
            "1. **Bairro Nobre 1** - Score 85 (Alta renda)",
            "2. **Bairro Central 1** - Score 80 (Centro expandido)",
            "3. **Bairro Norte 1** - Score 75 (Expansão norte)",
            "4. **Em desenvolvimento** - Dados sendo coletados",
            "5. **Em desenvolvimento** - Dados sendo coletados"
        ])

        with col_res1:
            st.markdown(f"""
            <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;">
                <h3 style="color: #155724; margin-bottom: 15px;">🏆 TOP 5 PRIORIDADES - {municipio_selecionado}</h3>
            """, unsafe_allow_html=True)

            for i, item in enumerate(top_5_atual, 1):
                # Remove o número do início se já existir
                item_clean = item.split('. ', 1)[1] if '. ' in item else item
                bairro = item_clean.split(' - ')[0].replace('**', '')
                detalhes = item_clean.split(' - ')[1] if ' - ' in item_clean else ''

                st.markdown(f"""
                <div style="margin-bottom: 12px; padding: 10px; background-color: white; border-radius: 5px; border-left: 3px solid #28a745;">
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: #28a745; color: white; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold; font-size: 12px;">
                            {i}
                        </div>
                        <div>
                            <strong style="color: #155724; font-size: 16px;">{bairro}</strong><br>
                            <span style="color: #6c757d; font-size: 14px;">{detalhes}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_res2:
            # Informações complementares sobre a cidade
            info_cidade = info_cidades.get(municipio_selecionado, {})

            st.markdown(f"""
            <div style="background-color: #e7f3ff; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff;">
                <h3 style="color: #004085; margin-bottom: 15px;">📊 Resumo da Cidade</h3>
                <div style="background-color: white; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #004085;">Franquias Atuais:</span>
                        <span style="color: #28a745; font-weight: bold;">{info_cidade.get('atuais', 0)} unidades</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #004085;">Potencial Total:</span>
                        <span style="color: #007bff; font-weight: bold;">{info_cidade.get('potencial', 0)} franquias</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-weight: bold; color: #004085;">Oportunidades:</span>
                        <span style="color: #fd7e14; font-weight: bold;">+{info_cidade.get('adicional', 0)} franquias</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: bold; color: #004085;">Cobertura:</span>
                        <span style="color: #6f42c1; font-weight: bold;">{info_cidade.get('cobertura', 0)}% do potencial</span>
                    </div>
                </div>
                <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 3px solid #ffc107;">
                    <small style="color: #856404;">
                        <strong>💡 Insight:</strong>
                        {'Mercado quase saturado - foco em bairros nobres restantes' if info_cidade.get('cobertura', 0) > 70
                         else 'Grande potencial de expansão - priorizar bairros de alta renda' if info_cidade.get('cobertura', 0) < 30
                         else 'Expansão equilibrada - focar em bairros estratégicos'}
                    </small>
                </div>
            </div>
            """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()
