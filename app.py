import pandas as pd
import streamlit as st
import plotly.express as px

# Defino o título da página la em cima, o ícone e o layout para ocupar a tela inteira.
st.set_page_config(
    page_title="DASHBOARDS",
    page_icon="📊",
    layout="wide",
)

df = pd.read_csv("dados_imersao_tratados.csv")

# Para dividir a pagina em duas colunas e deixar a barra lateral dos filtros à direita
col_main, col_right = st.columns([3, 1])

with col_right:
    st.header("FILTROS ✅")

    # Filtro de Ano
    anos_disponiveis = sorted(df['ano'].unique())
    anos_selecionados = st.multiselect("ANO", anos_disponiveis, default=anos_disponiveis)

    # Filtro de Senioridade
    senioridades_disponiveis = sorted(df['senioridade'].unique())
    senioridades_selecionadas = st.multiselect("SENIORIDADE", senioridades_disponiveis, default=senioridades_disponiveis)

    # Filtro por Tipo de Contrato
    contratos_disponiveis = sorted(df['contrato'].unique())
    contratos_selecionados = st.multiselect("CONTRATO", contratos_disponiveis, default=contratos_disponiveis)

    # Filtro por Tamanho da Empresa
    tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
    tamanhos_selecionados = st.multiselect("TAMANHO DA EMPRESA", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

with col_main:
    st.title("RELATÓRIO DOS SALÁRIOS NA ÁREA DE DADOS 📊")
    st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros para refinar sua análise.")

    if not df_filtrado.empty:
        salario_medio = df_filtrado['usd'].mean()
        salario_maximo = df_filtrado['usd'].max()
        total_registros = df_filtrado.shape[0]
        cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
    else:
        salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Salário Médio Anual (USD)", f"${salario_medio:,.0f}")
    col2.metric("Salário Máximo (USD)", f"${salario_maximo:,.0f}")
    col3.metric("Total de Registros", f"{total_registros:,}")
    col4.metric("Cargo mais Frequente", cargo_mais_frequente)

    st.markdown("---")

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        if not df_filtrado.empty:
            top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
            grafico_cargos = px.bar(
                top_cargos,
                x='usd',
                y='cargo',
                orientation='h',
                color_discrete_sequence=px.colors.sequential.Aggrnyl,
                title="TOP 10 CARGOS POR SALÁRIO MÉDIO",
                labels={'usd': 'MÉDIA SALARIAL ANUAL (USD)', 'cargo': ''}
            )
            grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(grafico_cargos, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir no gráfico de cargos.")

    with col_graf2:
        if not df_filtrado.empty:
            grafico_hist = px.histogram(
                df_filtrado,
                x='usd',
                nbins=30,
                color_discrete_sequence=px.colors.sequential.Aggrnyl,
                title="DISTRIBUIÇÃO DE SALÁRIOS ANUAIS",
                labels={'usd': 'FAIXA SALARIAL (USD)', 'count': ''}
            )
            grafico_hist.update_layout(title_x=0.1)
            st.plotly_chart(grafico_hist, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir no gráfico de distribuição.")

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:
        if not df_filtrado.empty:
            remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
            remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
            grafico_remoto = px.pie(
                remoto_contagem,
                names='tipo_trabalho',
                values='quantidade',
                color_discrete_sequence=px.colors.sequential.Aggrnyl,
                title='PROPORÇÃO DOS TIPOS DE TRABALHO',
                hole=0.5
            )
            grafico_remoto.update_traces(textinfo='percent+label')
            grafico_remoto.update_layout(title_x=0.1)
            st.plotly_chart(grafico_remoto, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

    with col_graf4:
        if not df_filtrado.empty:
            df_ds = df_filtrado[df_filtrado['cargo'] == 'DATA SCIENTIST']
            media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            grafico_paises = px.choropleth(media_ds_pais,
                locations='residencia_iso3',
                color='usd',
                #color_discrete_sequence = px.colors.sequential.Plasma_r,
                color_continuous_scale='aggrnyl',
                title='SALÁRIO MÉDIO DE CIENTISTA DE DADOS POR PAÍS',
                labels={'usd': 'SALÁRIO MÉDIO (USD)', 'residencia_iso3': 'País'})
            grafico_paises.update_layout(title_x=0.1)
            st.plotly_chart(grafico_paises, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir no gráfico de países.")
    # --- Tabela de Dados Detalhados ---
    st.subheader("DADOS DETALHADOS")
    st.dataframe(df_filtrado)