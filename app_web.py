import streamlit as st
import requests

# Configuração da Página
st.set_page_config(
    page_title="Consulta CNPJ - Jairo Rossi",
    page_icon="🔍",
    layout="centered"
)

# Título e Assinatura
st.title("🔍 Consulta CNPJ & Regime Tributário")
st.markdown("### *Desenvolvido por Jairo Rossi*") 
st.markdown("---")

st.write("Digite o CNPJ para identificar se o cliente é **Simples Nacional** ou **Regime Normal**.")

# Entrada de Dados
cnpj_input = st.text_input("CNPJ do Cliente (somente números):", max_chars=18)

# Botão de Ação
if st.button("Pesquisar Regime"):
    if not cnpj_input:
        st.warning("Por favor, digite um CNPJ.")
    else:
        # Limpeza do CNPJ
        cnpj = "".join([c for c in cnpj_input if c.isdigit()])
        
        if len(cnpj) != 14:
            st.error("ERRO: O CNPJ deve conter 14 dígitos.")
        else:
            with st.spinner('Consultando Receita Federal...'):
                try:
                    # Consulta à API
                    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        
                        if dados.get('status') == 'ERROR':
                            st.error(f"Erro na Receita: {dados.get('message')}")
                        else:
                            # --- LÓGICA DE DECISÃO ---
                            simples_dados = dados.get('simples')
                            optante = False
                            
                            if simples_dados and isinstance(simples_dados, dict):
                                optante = simples_dados.get('optante', False)
                            
                            # Exibição dos Dados
                            st.subheader(f"{dados.get('nome')}")
                            st.text(f"Fantasia: {dados.get('fantasia', '---')}")
                            
                            # Caixas de destaque
                            if optante:
                                st.success("✅ EMPRESA OPTANTE PELO SIMPLES NACIONAL")
                                fed_value = "SIMPLES"
                                est_value = "SIMPLES"
                            else:
                                st.info("ℹ️ EMPRESA DE REGIME NORMAL (Lucro Presumido/Real)")
                                fed_value = "NORMAL"
                                est_value = "NORMAL"

                            st.markdown("### 📝 Sugestão de Cadastro no GCOM")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(label="[1] Regime Federal", value=fed_value)
                            with col2:
                                st.metric(label="[2] Regime Estadual", value=est_value)

                            # Detalhes extras
                            with st.expander("Ver detalhes completos (Endereço/Atividade)"):
                                st.write(f"**Logradouro:** {dados.get('logradouro')}, {dados.get('numero')}")
                                st.write(f"**Bairro:** {dados.get('bairro')} - {dados.get('municipio')}/{dados.get('uf')}")
                                st.write(f"**Atividade:** {dados.get('atividade_principal', [{}])[0].get('text')}")

                    elif response.status_code == 429:
                        st.warning("Muitas consultas seguidas. Aguarde 1 minuto.")
                    else:
                        st.error("Erro de conexão com a API.")
                        
                except Exception as e:
                    st.error(f"Erro técnico: {e}")
