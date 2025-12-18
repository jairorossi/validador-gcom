import streamlit as st
import requests

# Configuração da página (Modo Wide aproveita melhor a tela lateralmente)
st.set_page_config(
    page_title="Consulta CNPJ",
    page_icon="🏢",
    layout="wide" 
)

# Cabeçalho Compacto
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("### 🏢 Consulta CNPJ & Fiscal")
with c2:
    st.caption("Dev: Jairo Rossi | v3.0")

# Input e Botão na mesma linha para economizar espaço
with st.container():
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        cnpj_input = st.text_input("", max_chars=18, placeholder="Digite o CNPJ (apenas números)", label_visibility="collapsed")
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
            with st.spinner('Buscando dados na Receita...'):
                try:
                    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        dados = response.json()
                        
                        if dados.get('status') == 'ERROR':
                            st.error(f"Erro: {dados.get('message')}")
                        else:
                            # --- Lógica de Regime ---
                            simples = dados.get('simples', {})
                            optante = simples.get('optante', False) if simples else False
                            
                            # Definição visual do Regime
                            if optante:
                                regime_box = "✅ SIMPLES NACIONAL"
                                regime_cor = "success"
                                val_fed = "SIMPLES"
                                val_est = "SIMPLES"
                            else:
                                regime_box = "ℹ️ NORMAL (Lucro Presumido/Real)"
                                regime_cor = "info"
                                val_fed = "NORMAL"
                                val_est = "NORMAL"

                            # --- EXIBIÇÃO DOS DADOS ---
                            
                            st.markdown("---")

                            # BLOCO 1: Identificação Principal (Nome e Status)
                            col_nome, col_status = st.columns([3, 1])
                            with col_nome:
                                st.subheader(dados.get('nome'))
                                st.caption(f"Fantasia: {dados.get('fantasia', '---')}")
                            with col_status:
                                st.metric("Situação", dados.get('situacao'), delta_color="normal")

                            # BLOCO 2: Regime Tributário (Destaque)
                            st.markdown("##### 📝 Classificação Fiscal")
                            if regime_cor == "success":
                                st.success(regime_box)
                            else:
                                st.info(regime_box)
                            
                            c_fed, c_est, c_nat = st.columns(3)
                            with c_fed:
                                st.text_input("Regime Federal", value=val_fed, disabled=True)
                            with c_est:
                                st.text_input("Regime Estadual", value=val_est, disabled=True)
                            with c_nat:
                                st.text_input("Natureza Jurídica (Tipo)", value=dados.get('natureza_juridica', '').split(' ')[0], help=dados.get('natureza_juridica'), disabled=True)

                            # BLOCO 3: Detalhes Completos (Abas para não poluir)
                            st.markdown("##### 📍 Detalhes do Cadastro")
                            aba1, aba2 = st.tabs(["Endereço & Contato", "Atividade Econômica (CNAE)"])
                            
                            with aba1:
                                ce1, ce2, ce3 = st.columns([2, 1, 1])
                                with ce1:
                                    st.write(f"**Logradouro:** {dados.get('logradouro')}, {dados.get('numero')} {dados.get('complemento', '')}")
                                    st.write(f"**Bairro:** {dados.get('bairro')}")
                                with ce2:
                                    st.write(f"**Município:** {dados.get('municipio')} / {dados.get('uf')}")
                                    st.write(f"**CEP:** {dados.get('cep')}")
                                with ce3:
                                    st.write(f"**Email:** {dados.get('email', '---')}")
                                    st.write(f"**Tel:** {dados.get('telefone', '---')}")

                            with aba2:
                                main_cnae = dados.get('atividade_principal', [{}])[0]
                                st.write(f"**Principal:** {main_cnae.get('code')} - {main_cnae.get('text')}")
                                # Lista secundários se quiser (opcional)
                                # st.caption("Atividades Secundárias não listadas para brevidade.")

                    elif response.status_code == 429:
                        st.warning("⏳ Muitas consultas. Aguarde 1 minuto.")
                    else:
                        st.error("Erro ao conectar na API.")
                        
                except Exception as e:
                    st.error(f"Erro técnico: {e}")
