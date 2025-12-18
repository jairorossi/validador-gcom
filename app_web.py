import streamlit as st
import requests

# Configuração da página
st.set_page_config(
    page_title="Consulta CNPJ",
    page_icon="🏢",
    layout="centered" 
)

# Título e Créditos
st.markdown("#### Consulta CNPJ & Fiscal - Dev: Jairo Rossi | v3.0")

# Input e Botão
col_input, col_btn = st.columns([3, 1])
with col_input:
    cnpj_input = st.text_input("", max_chars=18, placeholder="Digite o CNPJ", label_visibility="collapsed")
with col_btn:
    btn_consultar = st.button("Consultar", use_container_width=True)

if btn_consultar:
    if not cnpj_input:
        st.warning("⚠️ Digite um CNPJ.")
    else:
        # Limpeza
        cnpj = "".join([c for c in cnpj_input if c.isdigit()])
        
        if len(cnpj) != 14:
            st.error("❌ CNPJ deve ter 14 dígitos.")
        else:
            with st.spinner('Pesquisando...'):
                try:
                    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        
                        if dados.get('status') == 'ERROR':
                            st.error(f"Erro: {dados.get('message')}")
                        else:
                            # --- Lógica ---
                            simples = dados.get('simples', {})
                            optante = simples.get('optante', False) if simples else False
                            
                            if optante:
                                classif_fiscal = "✅ SIMPLES NACIONAL"
                                reg_fed = "SIMPLES"
                                reg_est = "SIMPLES"
                            else:
                                classif_fiscal = "NORMAL (Lucro Presumido/Real)"
                                reg_fed = "NORMAL"
                                reg_est = "NORMAL"

                            # --- EXIBIÇÃO VERTICAL ---
                            st.markdown("---")
                            
                            # Dados Principais
                            st.write(f"**Empresa:** {dados.get('nome')}")
                            st.write(f"**Fantasia:** {dados.get('fantasia', '')}")
                            st.write(f"**Situação:** {dados.get('situacao')}")
                            
                            st.markdown("<br>", unsafe_allow_html=True) 
                            
                            # Classificação Fiscal
                            st.markdown("**Classificação Fiscal:**")
                            if optante:
                                st.success(classif_fiscal)
                            else:
                                st.info(classif_fiscal)

                            # Regimes (AGORA UM EMBAIXO DO OUTRO)
                            st.write(f"**Regime Federal:** {reg_fed}")
                            # Se quiser um espaço maior entre eles, descomente a linha abaixo:
                            # st.markdown("<br>", unsafe_allow_html=True)
                            st.write(f"**Regime Estadual:** {reg_est}")

                            st.markdown("<br>", unsafe_allow_html=True)

                            # Natureza Jurídica
                            nat_juridica = dados.get('natureza_juridica', '---')
                            st.markdown("**Natureza Jurídica (Tipo):**")
                            st.write(nat_juridica)

                            st.markdown("<br>", unsafe_allow_html=True)

                            # CNAE
                            cnae_principal = dados.get('atividade_principal', [{}])[0]
                            st.markdown("**Atividade Econômica (CNAE):**")
                            st.write(f"Principal: {cnae_principal.get('code')} - {cnae_principal.get('text')}")

                            st.markdown("---")

                            # Endereço (Bloco Final)
                            st.markdown("##### ENDEREÇO DA EMPRESA:")
                            st.write(f"**Logradouro:** {dados.get('logradouro')}, {dados.get('numero')} {dados.get('complemento', '')}")
                            st.write(f"**Bairro:** {dados.get('bairro')}")
                            st.write(f"**Município:** {dados.get('municipio')} / {dados.get('uf')}")
                            st.write(f"**CEP:** {dados.get('cep')}")
                            st.write(f"**Tel:** {dados.get('telefone', '---')}")
                            st.write(f"**Email:** {dados.get('email', '---')}")

                    elif response.status_code == 429:
                        st.warning("⏳ Muitas consultas. Aguarde 1 minuto.")
                    else:
                        st.error("Erro ao conectar na API.")
                        
                except Exception as e:
                    st.error(f"Erro técnico: {e}")
