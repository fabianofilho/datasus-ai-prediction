> [!NOTE]
> Esta tabela oferece uma visão geral e comparativa dos principais sistemas de informação do DataSUS sob a ótica da modelagem preditiva. A escolha do dataset ideal dependerá do desfecho de interesse, da população-alvo e da necessidade de acompanhamento longitudinal.

# Tabela Comparativa de Datasets do DataSUS para IA

| Sistema | Foco Principal | Identificador Principal | Necessidade de Linkage | Granularidade Temporal | Principais Desfechos Preditivos | 
| :--- | :--- | :--- | :--- | :--- | :--- | 
| **SIH** | Internações Hospitalares | CNS, CPF (recente), AIH | Alta (para longitudinalidade) | Episódico (por internação) | Reinternação, Mortalidade hospitalar, Tempo de permanência, Custos | 
| **SIM** | Óbitos | CNS, CPF (recente), Nome+Mãe+DN | **Essencial** (é a base do outcome) | Pontual (data do óbito) | **Mortalidade** (variável-alvo para outras bases) | 
| **SINASC** | Nascimentos | CNS (mãe/bebê), DN | Alta (link com SIM, SIH) | Pontual (data do nascimento) | Baixo peso, Prematuridade, Apgar baixo, Mortalidade neonatal (com SIM) | 
| **SINAN** | Doenças de Notificação | CNS, CPF, Nome+Mãe+DN | Média (longitudinal intra-base), Alta (link com SIM/SIH) | Longitudinal (para doenças crônicas) | Abandono de tratamento, Progressão da doença, Óbito, Surtos | 
| **SIA/APAC** | Procedimentos Ambulatoriais de Alto Custo | CNS, APAC anterior | Baixa (longitudinal intra-base), Alta (link com SIH/SIM) | Longitudinal (por autorização) | Resposta ao tratamento, Adesão, Hospitalização, Sobrevida (com SIM) | 
| **SIVEP-Gripe** | Síndrome Respiratória Aguda Grave (SRAG) | CPF, CNS | Média (link com SI-PNI, SIM) | Episódico (por hospitalização) | Necessidade de UTI, Ventilação mecânica, Óbito | 
| **e-SUS AB** | Atenção Primária à Saúde | CNS, CPF | Baixa (longitudinal intra-base), Alta (link com SIH/SIM) | Contínua (por atendimento) | Risco de doenças crônicas, Hospitalização (ICSAP), Baixa adesão | 
| **CNES** | Infraestrutura de Saúde | Código CNES | **Essencial** (para enriquecer outras bases) | Transversal (por competência) | N/A (fonte de **features contextuais** para outros modelos) | 
| **SI-PNI** | Imunizações | CNS, CPF | Alta (link com SINASC, SIVEP) | Longitudinal (por dose) | Falha vacinal, Efetividade de vacinas (com SIVEP/SIH) | 
| **HIPERDIA** | Hipertensão e Diabetes | CNS | Média (link com SIH, SIM) | Longitudinal (por acompanhamento) | Complicações (IAM, AVC), Necessidade de diálise, Mortalidade (com SIM) | 
| **SISVAN** | Vigilância Nutricional | CNS, NIS | Alta (link com e-SUS AB, SINASC) | Longitudinal (por medição) | Desnutrição, Obesidade, Anemia | 
