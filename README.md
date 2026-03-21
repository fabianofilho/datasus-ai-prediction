# DataSUS para IA: Um Guia de Fontes de Dados para Modelagem Preditiva

## Visão Geral

O DataSUS, departamento de informática do Sistema Único de Saúde (SUS) do Brasil, disponibiliza um vasto volume de dados de saúde, abrangendo desde registros de nascimentos e óbitos até internações hospitalares, procedimentos ambulatoriais e vigilância de doenças. Esses dados representam uma oportunidade única para a pesquisa em saúde e o desenvolvimento de modelos de inteligência artificial capazes de prever desfechos, otimizar a alocação de recursos e melhorar a gestão do cuidado.

Este repositório serve como um guia abrangente para pesquisadores, cientistas de dados e desenvolvedores que desejam utilizar os microdados do DataSUS para projetos de machine learning. Aqui, você encontrará uma análise detalhada dos principais sistemas de informação, suas potencialidades, limitações e as estratégias necessárias para transformá-los em datasets acionáveis para IA.

## Índice de Datasets Documentados

A seguir, uma lista dos sistemas de informação documentados neste repositório, com links para suas respectivas análises detalhadas:

*   **Sistemas de Informação de Mortalidade e Nascimentos:**
    *   [SIH - Sistema de Informações Hospitalares](./docs/sih.md)
    *   [SIM - Sistema de Informações sobre Mortalidade](./docs/sim.md)
    *   [SINASC - Sistema de Informações sobre Nascidos Vivos](./docs/sinasc.md)
*   **Sistemas de Vigilância em Saúde:**
    *   [SINAN - Sistema de Informação de Agravos de Notificação](./docs/sinan.md)
    *   [SIVEP-Gripe - Sistema de Informação da Vigilância Epidemiológica da Gripe](./docs/sivep_gripe.md)
    *   [e-SUS Vigilância em Saúde (e-SUS VS)](./docs/esus_vs.md)
*   **Sistemas de Informação Ambulatorial e de Atenção Primária:**
    *   [SIA - Sistema de Informações Ambulatoriais (incluindo APAC)](./docs/sia.md)
    *   [e-SUS Atenção Primária (e-SUS AB / SISAB)](./docs/esus_ab.md)
    *   [SI-PNI - Sistema de Informação do Programa Nacional de Imunizações](./docs/si_pni.md)
*   **Sistemas de Acompanhamento Específico:**
    *   [HIPERDIA - Sistema de Cadastramento e Acompanhamento de Hipertensos e Diabéticos](./docs/hiperdia.md)
    *   [SISVAN - Sistema de Vigilância Alimentar e Nutricional](./docs/sisvan.md)
    *   [SIS-Pré-Natal (SISPRENATAL)](./docs/sisprenatal.md)
*   **Sistemas de Cadastro e Estrutura:**
    *   [CNES - Cadastro Nacional de Estabelecimentos de Saúde](./docs/cnes.md)
    *   [CIHA - Comunicação de Informação Hospitalar e Ambulatorial](./docs/ciha.md)

## Documentação Adicional

Para facilitar o uso prático desses dados, o repositório também inclui:

*   [**Tabela Comparativa de Datasets**](./docs/comparative_table.md): Uma visão consolidada das características de cada sistema, facilitando a escolha do dataset mais adequado para sua necessidade.
*   [**Guia de Record Linkage**](./docs/record_linkage_guide.md): Um guia metodológico para realizar o pareamento de registros entre as diferentes bases do DataSUS, uma etapa crucial para a construção de uma visão longitudinal do paciente.
*   [**Exemplos de Construção de Cohorts**](./docs/cohort_building_examples.md): Demonstrações práticas de como estruturar janelas de observação e predição para diferentes desfechos de saúde.
*   [**Referências de Estudos**](./docs/references.md): Uma lista de publicações científicas que utilizaram dados do DataSUS para modelagem preditiva, servindo como inspiração e base metodológica.

## Como Contribuir

Este é um projeto em constante evolução. Se você tiver sugestões, correções ou desejar adicionar a análise de um novo dataset, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.
