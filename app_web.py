import streamlit as st
import requests

# Configuração minimalista da página
st.set_page_config(
    page_title="Consulta CNPJ",
    page_icon="🔍",
    layout="centered"
)

# Layout compacto (Título e Assinatura na mesma linha visual)
col_header, col_sign = st.columns([2,1])
with col_header:
    st.markdown("### 🔍 Consulta CNPJ")
with col_sign:
    st.caption("Dev: Jairo Rossi")

# Entrada de Dados (Sem textos explicativos longos)
cnpj_input = st.text_input("CNPJ:", max_chars=18, placeholder="Digite o CNPJ aqui")

if st.button("Consultar"):
    if not cnpj_input:
        st.warning("Informe um CNPJ.")
    else:
        cnpj = "".join([c for c in cnpj_input if c.isdigit()])
        
        if len(cnpj) != 14:
            st.error("CNPJ inválido (deve ter 14 dígitos).")
        else:
            with st.spinner('Buscando...'):
                try:
                    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        
                        if dados.get('status') == 'ERROR':
                            st.error(f"Erro: {dados.get('message')}")
                        else:
                            # --- Lógica ---
                            simples_dados = dados.get('simples')
                            optante = False
                            if simples_dados and isinstance(simples_dados, dict):
                                optante = simples_dados.get('optante', False)
                            
                            # --- Exibição Compacta ---
                            st.markdown("---")
                            st.markdown(f"**{dados.get('nome')}**")
                            st.caption(f"CNPJ: {dados.get('cnpj')} | {dados.get('municipio')}/{dados.get('uf')}")

                            # Definição dos valores
                            if optante:
                                msg_status = "✅ SIMPLES NACIONAL"
                                val_fed = "SIMPLES"
                                val_est = "SIMPLES"
                            else:
                                msg_status = "ℹ️ NORMAL (Lucro Presumido/Real)"
                                val_fed = "NORMAL"
                                val_est = "NORMAL / RPA"

                            # Exibe o Status Principal
                            if optante:
                                st.success(msg_status)
                            else:
                                st.info(msg_status)

                            # Exibe os Regimes (Genérico)
                            st.markdown("##### Regime Tributário")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.text_input("Federal", value=val_fed, disabled=True)
                            with col2:
                                st.text_input("Estadual", value=val_est, disabled=True)

                    elif response.status_code == 429:
                        st.warning("Aguarde 1 min (limite de consultas).")
                    else:
                        st.error("Erro na API.")
                        
                except Exception as e:
                    st.error("Erro de conexão.")
