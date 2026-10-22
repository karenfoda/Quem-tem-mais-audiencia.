import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Qual canal tem mais audiência?",
    layout="wide"
)

st.title("📺 Qual canal tem mais audiência?")
st.write(
    "**Realizado por:** Karen Farias Menezes, Victor Mattheo e Rhyan Lopes.\n"
    "\n**Orientado por:** Prof. Felipe Garbin\n",
    "\nEste projeto analisa a audiência dos principais canais infantis "
    "(Disney, Nickelodeon e Cartoon Network), comparando dados demográficos, "
    "público estimado e audiência dos episódios mais vistos."
)

# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

# Arquivo principal: episódios mais vistos
episodios = pd.read_excel("Kids Show most Viewed .xlsx")

# Arquivos de audiência por canal
aud_disney = pd.read_csv("Audiencia Disney.txt", sep=",")
aud_nick = pd.read_csv("Audiencia Nickelodeon.txt", sep=",")
aud_cartoon = pd.read_csv("Audiencia Cartoon.txt", sep=",")

# Adicionar coluna "Canal" para identificar a origem
aud_disney["Canal"] = "Disney"
aud_nick["Canal"] = "Nickelodeon"
aud_cartoon["Canal"] = "Cartoon Network"

# Combinar os 3 arquivos de audiência
audiencia = pd.concat([aud_disney, aud_nick, aud_cartoon], ignore_index=True)
audiencia.columns = audiencia.columns.str.strip()
episodios.columns = episodios.columns.str.strip()

# ============================================================
# TRATAMENTO DOS DADOS DE EPISÓDIOS
# ============================================================

episodios["Total Live Viewers"] = pd.to_numeric(
    episodios["Total Live Viewers"], errors="coerce"
)
episodios["Release Year"] = pd.to_numeric(
    episodios["Release Year"], errors="coerce"
)

# ============================================================
# MÉTRICAS GERAIS POR CANAL
# ============================================================

st.subheader("📊 Resumo por canal")

# Audiência estimada (demografia)
demo = audiencia[audiencia["tipo"] == "demografia"]
audiencia_estimada = (
    demo[demo["nome"] == "audiencia_estimada"]
    .set_index("Canal")["valor"]
    .astype(float)
)

# Audiência média dos episódios (do Excel)
media_episodios = (
    episodios.groupby("Channel")["Total Live Viewers"]
    .mean()
    .sort_values(ascending=False)
)

# Pico de audiência (episódio mais visto)
pico_episodios = (
    episodios.groupby("Channel")["Total Live Viewers"]
    .max()
    .sort_values(ascending=False)
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🏆 Canal com maior audiência estimada",
        audiencia_estimada.idxmax() if not audiencia_estimada.empty else "N/A",
        f"{audiencia_estimada.max():,.0f} pessoas".replace(",", ".")
        if not audiencia_estimada.empty else ""
    )

with col2:
    st.metric(
        "📺 Maior média de audiência por episódio",
        media_episodios.idxmax() if not media_episodios.empty else "N/A",
        f"{media_episodios.max():,.0f} espectadores".replace(",", ".")
        if not media_episodios.empty else ""
    )

with col3:
    st.metric(
        "🔥 Maior pico de audiência",
        pico_episodios.idxmax() if not pico_episodios.empty else "N/A",
        f"{pico_episodios.max():,.0f} espectadores".replace(",", ".")
        if not pico_episodios.empty else ""
    )

# ============================================================
# GRÁFICO 1: Audiência estimada por canal
# ============================================================

st.subheader("👥 Audiência estimada por canal")

if not audiencia_estimada.empty:
    df_aud = audiencia_estimada.reset_index()
    df_aud.columns = ["Canal", "Audiência Estimada"]

    fig1 = px.bar(
        df_aud,
        x="Canal",
        y="Audiência Estimada",
        title="Audiência estimada por canal (pessoas)",
        color="Canal",
        text="Audiência Estimada",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig1.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig1.update_layout(
        yaxis_title="Pessoas",
        xaxis_title="Canal",
        showlegend=False
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    **O que podemos observar?**
    - Este gráfico compara a audiência estimada (pessoas) de cada canal.
    - Quanto maior a barra, maior o público estimado do canal.
    - ⚠️ Observação: a Disney e o Cartoon não possuem o mesmo tipo de medição
      que a Nickelodeon (que reporta audiência mundial e dos EUA separadamente),
      então a comparação é uma aproximação.
    """)

# ============================================================
# GRÁFICO 2: Média e pico de audiência dos episódios
# ============================================================

st.subheader("🎬 Audiência dos episódios por canal")

if not media_episodios.empty:
    df_ep = pd.DataFrame({
        "Canal": media_episodios.index,
        "Média": media_episodios.values,
        "Pico": pico_episodios.reindex(media_episodios.index).values
    })

    fig2 = px.bar(
        df_ep,
        x="Canal",
        y=["Média", "Pico"],
        barmode="group",
        title="Média e pico de audiência dos episódios por canal",
        color_discrete_sequence=["#636EFA", "#EF553B"]
    )
    fig2.update_layout(
        yaxis_title="Espectadores",
        xaxis_title="Canal",
        legend_title="Métrica"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    **O que podemos observar?**
    - A barra azul mostra a **média** de audiência dos episódios de cada canal.
    - A barra vermelha mostra o **pico** (episódio mais visto).
    - Canais com pico muito acima da média tiveram um "hit" isolado.
    """)

# ============================================================
# GRÁFICO 3: Distribuição da audiência por canal (boxplot)
# ============================================================

st.subheader("📦 Distribuição da audiência dos episódios")

fig3 = px.box(
    episodios,
    x="Channel",
    y="Total Live Viewers",
    color="Channel",
    title="Distribuição da audiência dos episódios por canal",
    points="all"
)
fig3.update_layout(
    yaxis_title="Espectadores",
    xaxis_title="Canal",
    showlegend=False
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
**O que podemos observar?**
- O boxplot mostra como a audiência se distribui em cada canal.
- A linha central é a **mediana**; a caixa mostra o intervalo interquartil.
- Pontos fora da caixa são episódios atípicos (muito acima ou abaixo do padrão).
""")

# ============================================================
# GRÁFICO 4: Top 15 episódios mais vistos (geral)
# ============================================================

st.subheader("🔥 Top 15 episódios mais vistos (todos os canais)")

top15 = (
    episodios.nlargest(15, "Total Live Viewers")
    [["Channel", "Series", "Episode title", "Total Live Viewers", "Release Year"]]
)

fig4 = px.bar(
    top15,
    x="Total Live Viewers",
    y="Series",
    color="Channel",
    orientation="h",
    title="Top 15 episódios mais vistos",
    hover_data=["Episode title", "Release Year"],
    text="Total Live Viewers"
)
fig4.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig4.update_layout(
    xaxis_title="Espectadores",
    yaxis_title="Série",
    yaxis=dict(autorange="reversed")
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
**O que podemos observar?**
- Os episódios com maior audiência ao vivo em todos os canais.
- A cor indica o canal de origem.
- Permite identificar quais séries foram "fenômenos" de audiência.
""")

# ============================================================
# GRÁFICO 5: Evolução temporal da audiência média
# ============================================================

st.subheader("📈 Evolução temporal da audiência média")

evo = (
    episodios.dropna(subset=["Release Year"])
    .groupby(["Release Year", "Channel"])["Total Live Viewers"]
    .mean()
    .reset_index()
)

fig5 = px.line(
    evo,
    x="Release Year",
    y="Total Live Viewers",
    color="Channel",
    markers=True,
    title="Audiência média dos episódios por ano e canal"
)
fig5.update_layout(
    xaxis_title="Ano",
    yaxis_title="Audiência média",
    xaxis=dict(dtick=1)
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("""
**O que podemos observar?**
- Como a audiência média dos episódios evoluiu ao longo dos anos.
- Permite ver períodos de auge e queda de cada canal.
""")

# ============================================================
# GRÁFICO 6: Perfil demográfico (gênero) por canal
# ============================================================

st.subheader("🚻 Perfil de gênero do público por canal")

genero = audiencia[
    (audiencia["tipo"] == "demografia") &
    (audiencia["nome"].isin(["publico_feminino", "publico_masculino"]))
].copy()

if not genero.empty:
    genero["nome"] = genero["nome"].map({
        "publico_feminino": "Feminino",
        "publico_masculino": "Masculino"
    })
    genero["valor"] = pd.to_numeric(genero["valor"], errors="coerce")

    fig6 = px.bar(
        genero,
        x="Canal",
        y="valor",
        color="nome",
        barmode="group",
        title="Distribuição por gênero (%)",
        color_discrete_sequence=["#FF6692", "#636EFA"]
    )
    fig6.update_layout(
        yaxis_title="Percentual (%)",
        xaxis_title="Canal",
        legend_title="Gênero"
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("""
    **O que podemos observar?**
    - Compara a proporção de público feminino e masculino em cada canal.
    - Todos os canais têm maioria feminina, mas as proporções variam.
    """)

# ============================================================
# GRÁFICO 7: Distribuição etária por canal
# ============================================================

st.subheader("👶 Distribuição etária por canal")

idade = audiencia[audiencia["tipo"] == "idade"].copy()
idade["valor"] = pd.to_numeric(idade["valor"], errors="coerce")

if not idade.empty:
    fig7 = px.bar(
        idade,
        x="nome",
        y="valor",
        color="Canal",
        barmode="group",
        title="Distribuição etária por canal (%)",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig7.update_layout(
        xaxis_title="Faixa etária",
        yaxis_title="Percentual (%)",
        xaxis_tickangle=-45,
        legend_title="Canal"
    )
    st.plotly_chart(fig7, use_container_width=True)

    st.markdown("""
    **O que podemos observar?**
    - Compara as faixas etárias predominantes em cada canal.
    - Ajuda a entender para qual público cada canal é mais atraente.
    """)

# ============================================================
# TABELA COMPLETA POR CANAL
# ============================================================

st.subheader("📋 Tabela resumo por canal")

resumo = pd.DataFrame({
    "Canal": media_episodios.index,
    "Média de audiência (episódios)": media_episodios.values,
    "Pico de audiência": pico_episodios.reindex(media_episodios.index).values,
    "Nº de episódios na base": episodios.groupby("Channel").size()
        .reindex(media_episodios.index).values
}).reset_index(drop=True)

resumo.insert(0, "Posição", range(1, len(resumo) + 1))
st.dataframe(resumo, use_container_width=True, height=300)

csv = resumo.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Baixar resumo (CSV)",
    data=csv,
    file_name="resumo_audiencia_canais.csv",
    mime="text/csv"
)

# ============================================================
# BUSCAR EPISÓDIO ESPECÍFICO
# ============================================================

st.subheader("🔍 Buscar episódio específico")

if len(episodios) > 0:
    busca = st.text_input("Digite o nome da série ou episódio (ex: SpongeBob, iCarly, Hannah Montana)")

    if busca:
        resultado = episodios[
            episodios["Series"].str.contains(busca, case=False, na=False) |
            episodios["Episode title"].str.contains(busca, case=False, na=False)
        ]
        st.success(f"{len(resultado)} episódio(s) encontrado(s).")
        st.dataframe(resultado, use_container_width=True)
    else:
        st.info("Digite algo para buscar.")
else:
    st.warning("Nenhum episódio encontrado na base.")

# ============================================================
# ESTATÍSTICAS
# ============================================================

with st.expander("📊 Estatísticas descritivas dos episódios"):
    st.dataframe(episodios.describe())

with st.expander("ℹ️ Informações das colunas dos episódios"):
    col_info = pd.DataFrame({
        "Coluna": episodios.columns,
        "Tipo": episodios.dtypes.values,
        "Valores nulos": episodios.isnull().sum().values,
        "Valores únicos": episodios.nunique().values
    })
    st.dataframe(col_info)
