from mongodb_config import get_database

# Dados originais (mantidos para compatibilidade)
perguntas_por_fornecedor = {
    'CANTINA FREITAS': {
        'Atividades Operacionais': [
            '1 - O quantitativo (quadro efetivo) de funcionários da contratada está conforme a necessidade exigida para o atendimento?',
            '2 - A Cantina cumpre a escala de horarios conforme acordado em contrato, observando pontualmente os horários de entrada e saída?',
            '3 - O preposto da contratada atua de maneira presente, efetiva, orientando e zelando pelos seus funcionários?',
            '4 - A Cantina mantem a área cedida sempre em boas condições de conservação e higiene, realizando a limpeza diária de toda a área interna e externa;',
            '5 - Aceitam, sem restrições, a fiscalização por parte do colégio, no que diz respeito ao fiel cumprimento das condições e cláusulas pactuadas?',
            '6 - Mantem profissional NUTRICIONISTA supervisionando permanentemente a prestação dos serviços e, inclusive, promovendo entre os alunos, pais/responsáveis de aluno e empregados do COLÉGIO, a divulgação de bons hábitos alimentares?',
            '7 - Cumprem todas as exigências da Secretaria Municipal de Vigilância Sanitária e da Secretaria Municipal de Posturas e/ou Regulação Urbana e demais órgãos públicos de fiscalização e de normatização?',
            '8 - Recolhem todo o lixo produzido durante o desempenho de sua atividade, de forma a descartá-lo adequadamente no ponto de coleta, obedecendo e cumprindo todas as exigências da Secretaria Municipal?',
            '9 - Procedem a desinsetização e desratização da área cedida durante o período de férias do COLÉGIO, na data estabelecida, previamente, pela CONTRATANTE?',
        ],
        'Segurança': [
            '1 - Fornece aos seus empregados os equipamentos/materiais, uniformes e EPIs (Equipamentos de Proteção Individual) necessários para a realização dos serviços?',
            '2 - Os funcionários da cantina seguem as normas internas e orientações de segurança da SIC?',
            '3 - Os funcionários zelam pela segurança e cuidado com os funcionarios e alunos do colégio?',
            '4 - Os Funcionarios comunicam , qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
            '5 - Obedecem às normas internas do colégio e desenvolvem suas atividades sem perturbar as atividades escolares normais?',
            '6 - Os funcionários da contratada transmitem segurança na execução de suas tarefas?',
        ],
        'Qualidade': [
            '1 - Os funcionários da contratada atendem com cortesia e presteza quando solicitados?',
            '2 - Os funcionários da contratada comunicam-se com eficácia?',
            '3 - Cumprem rigorosamente todas as normas técnicas relacionadas ao transporte e armazenamento de todo o tipo de ALIMENTO, especialmente as relativas a embalagens, volumes, etc?',
            '4 - A Cantina garante e zela pela boa qualidade dos produtos fornecidos aos usuários(alunos, pais/responsáveis de alunos e empregados do COLÉGIO e terceiros visitantes), em consonância com os parâmetros de qualidade fixados e exigidos pelas normas técnicas pertinentes, expedidas pelo Poder Público e/ou por órgãos e/ou entidades competentes?',
            '5 - A cantina Não comercializa bebidas alcoólicas, cigarros, chicletes, balas, pirulitos, laranjinhas, "chup-chup" e tudo o mais que possa contrariar o bom andamento escolar e/ou causar dano a terceiro, sobretudo, mas não exclusivamente, aos alunos, pais de aluno e empregados do COLÉGIO?',
            '6 - Oferecem e fornecem, sempre que necessário, alimentação especial para os alunos, pais de aluno e/ou empregados que possuam alguma restrição alimentar ou dieta especial, recomendada por profissional de saúde?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - CND-FGTS e CRT, relativos à Regularidade Fiscal e Trabalhista, estão atualizados?',
            '5 - Apresentam à SIC cópia autenticada do ALVARÁ DE FUNCIONAMENTO, expedido pelos órgãos competentes, por meio do qual a CONTRATADA ficará autorizada a realizar suas atividades comerciais',
        ],
    },
    'EXPRESSA TURISMO LTDA': {
        'Atividades Operacionais': [
            '1 - A Contratada disponibiliza veículos em perfeitas condições de conservação e funcionamento mecânico, limpeza externa e interna e de segurança, em conformidade com as exigências legais e demais normas existentes?',
            '2 - A Contratada disponibiliza os veículos após o recebimento da autorização de início dos serviços, nos locais e horários fixados pelo Colégio, cumprindo pontualmente os horários  acordados de saída e retorno, conforme alinhado previamente?',
            '3 - Os profissionais indicados para execução dos serviços objeto do presente contrato, possum conhecimento técnico para sua função e estão devidamente habilitados  para conduzir veículo de transporte de passageiros?',
            '4 - A Contratada cumpre com antecedência e em tempo hábil, informando qualquer motivo que a impossibilite de assumir os serviços conforme estabelecido?',
            '5 - Os Funcionarios da Contratada comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários ',
        ],
        'Segurança': [
            '1 - Os funcionários da Contratada durante a prestação de serviço no ambiente interno da escola, seguem as normas internas e orientações demandadas pelo responsável do colégio?',
            '2 - O funcionário da Contratada durante a prestação de serviço segue as normas e regras do Código Brasileiro de Trânsito, respeitando principalmente as regras de limite de velocidade?',
            '3 - Os funcionários zelam pela segurança e cuidado com os alunos e funcionários durante toda a prestação de serviço, apresentando ao serviço sem sinais de embriaguez ou sob efeito de substancia tóxica?',
            '4 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '5 - Os veículos disponibilizados para a prestação de serviços estão com os cintos de segurança adequados e em funcionamento, conforme regulamentação específica?',
            '6 - Os veículos enviados para a prestação de serviços, estão equipados com tacógrafos calibrados e aferidos pelo INMETRO?',
        ],
        'Qualidade': [
            '1 - Os profissionais enviados pela Contratada para prestação de serviços são capacitados, qualificados e devidamente treinados, seguindo todas as normas e exigências da legislação brasileira, sobretudo, da legislação de trânsito brasileira?',
            '2 - O profissional da contratada estão devidamente identificados (crachá e/ou uniforme), apresentado com cortesia e presteza, prestando uma boa relação quando solicitado?',
            '3 - Os profissionais da Contratada prestam os esclarecimentos desejados, bem como comunicam, por meio de líder ou diretamente, quaisquer fatos ou anormalidades que porventura possam prejudicar o bom andamento ou o resultado final dos serviços?',
            '4 - Os profissionais da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - A contratada possui autorizações atualizadas (licenças específicas) que a habilitem para a prestação de serviços de transporte, expedidas pelos órgãos competentes (ANTT, DER, DETRAN, BHTRANS e/ou quaisquer outros);5 - A Contratada possui seguro de Acidentes pessoais, extensivo aos passageiros, e outros exigidos por Lei?',
        ],
    },
    'LEAL VIAGENS E TURISMO': {
        'Atividades Operacionais': [
            '1 - A Contratada disponibiliza veículos em perfeitas condições de conservação e funcionamento mecânico, limpeza externa e interna e de segurança, em conformidade com as exigências legais e demais normas existentes?',
            '2 - A Contratada disponibiliza os veículos após o recebimento da autorização de início dos serviços, nos locais e horários fixados pelo Colégio, cumprindo pontualmente os horários  acordados de saída e retorno, conforme alinhado previamente?',
            '3 - Os profissionais indicados para execução dos serviços objeto do presente contrato, possum conhecimento técnico para sua função e estão devidamente habilitados  para conduzir veículo de transporte de passageiros?',
            '4 - Em relação aos locais de destino para os respectivos passeios, onde há necessidade de entrada no local, almoço, lanche e demais infra-estrtura, a Contratada tem entregado esta estrutura conforme acordado previamente?',
            '5 - Os Funcionarios da Contratada comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Segurança': [
            '1 - Os funcionários da Contratada durante a prestação de serviço no ambiente interno da escola, seguem as normas internas e orientações demandadas pelo responsável do colégio?',
            '2 - O funcionário da Contratada durante a prestação de serviço segue as normas e regras do Código Brasileiro de Trânsito, respeitando principalmente as regras de limite de velocidade?',
            '3 - Os funcionários zelam pela segurança e cuidado com os alunos e funcionários durante toda a prestação de serviço, apresentando ao serviço sem sinais de embriaguez ou sob efeito de substancia tóxica?',
            '4 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '5 - Os veículos disponibilizados para a prestação de serviços estão com os cintos de segurança adequados e em funcionamento, conforme regulamentação específica?',
            '6 - Os veículos enviados para a prestação de serviços, estão equipados com tacógrafos calibrados e aferidos pelo INMETRO?',
        ],
        'Qualidade': [
            '1 - Os profissionais enviados pela Contratada para prestação de serviços são capacitados, qualificados e devidamente treinados, seguindo todas as normas e exigências da legislação brasileira, sobretudo, da legislação de trânsito brasileira?',
            '2 - O profissional da contratada estão devidamente identificados (crachá e/ou uniforme), apresentado com cortesia e presteza, prestando uma boa relação quando solicitado?',
            '3 - Os profissionais da Contratada prestam os esclarecimentos desejados, bem como comunicam, por meio de líder ou diretamente, quaisquer fatos ou anormalidades que porventura possam prejudicar o bom andamento ou o resultado final dos serviços?',
            '4 - Os profissionais da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - A contratada possui autorizações atualizadas (licenças específicas) que a habilitem para a prestação de serviços de transporte, expedidas pelos órgãos competentes (ANTT, DER, DETRAN, BHTRANS e/ou quaisquer outros);5 - A Contratada possui seguro de Acidentes pessoais, extensivo aos passageiros, e outros exigidos por Lei?',
        ],
    },
    'ACREDITE EXCURSÕES E EXPOSIÇÕES INTINERANTE LTDA': {
        'Atividades Operacionais': [
            '1 - A Contratada disponibiliza veículos em perfeitas condições de conservação e funcionamento mecânico, limpeza externa e interna e de segurança, em conformidade com as exigências legais e demais normas existentes?',
            '2 - A Contratada disponibiliza os veículos após o recebimento da autorização de início dos serviços, nos locais e horários fixados pelo Colégio, cumprindo pontualmente os horários  acordados de saída e retorno, conforme alinhado previamente?',
            '3 - Os profissionais indicados para execução dos serviços objeto do presente contrato, possum conhecimento técnico para sua função e estão devidamente habilitados  para conduzir veículo de transporte de passageiros?',
            '4 - Em relação aos locais de destino para os respectivos passeios, onde há necessidade de entrada no local, almoço, lanche e demais infra-estrtura, a Contratada tem entregado esta estrutura conforme acordado previamente?',
            '5 - Os Funcionarios da Contratada comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Segurança': [
            '1 - Os funcionários da Contratada durante a prestação de serviço no ambiente interno da escola, seguem as normas internas e orientações demandadas pelo responsável do colégio?',
            '2 - O funcionário da Contratada durante a prestação de serviço segue as normas e regras do Código Brasileiro de Trânsito, respeitando principalmente as regras de limite de velocidade?',
            '3 - Os funcionários zelam pela segurança e cuidado com os alunos e funcionários durante toda a prestação de serviço, apresentando ao serviço sem sinais de embriaguez ou sob efeito de substancia tóxica?',
            '4 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '5 - Os veículos disponibilizados para a prestação de serviços estão com os cintos de segurança adequados e em funcionamento, conforme regulamentação específica?',
            '6 - Os veículos enviados para a prestação de serviços, estão equipados com tacógrafos calibrados e aferidos pelo INMETRO?',
        ],
        'Qualidade': [
            '1 - Os profissionais enviados pela Contratada para prestação de serviços são capacitados, qualificados e devidamente treinados, seguindo todas as normas e exigências da legislação brasileira, sobretudo, da legislação de trânsito brasileira?',
            '2 - O profissional da contratada estão devidamente identificados (crachá e/ou uniforme), apresentado com cortesia e presteza, prestando uma boa relação quando solicitado?',
            '3 - Os profissionais da Contratada prestam os esclarecimentos desejados, bem como comunicam, por meio de líder ou diretamente, quaisquer fatos ou anormalidades que porventura possam prejudicar o bom andamento ou o resultado final dos serviços?',
            '4 - Os profissionais da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - A contratada possui autorizações atualizadas (licenças específicas) que a habilitem para a prestação de serviços de transporte, expedidas pelos órgãos competentes (ANTT, DER, DETRAN, BHTRANS e/ou quaisquer outros);5 - A Contratada possui seguro de Acidentes pessoais, extensivo aos passageiros, e outros exigidos por Lei?',
        ],
    },
    'REAL VANS LOCAÇÕES': {
        'Atividades Operacionais': [
            '1 - A Contratada disponibiliza veículos em perfeitas condições de conservação e funcionamento mecânico, limpeza externa e interna e de segurança, em conformidade com as exigências legais e demais normas existentes?',
            '2 - A Contratada disponibiliza os veículos após o recebimento da autorização de início dos serviços, nos locais e horários fixados pelo Colégio, cumprindo pontualmente os horários  acordados de saída e retorno, conforme alinhado previamente?',
            '3 - Os profissionais indicados para execução dos serviços objeto do presente contrato, possum conhecimento técnico para sua função e estão devidamente habilitados  para conduzir veículo de transporte de passageiros?',
            '4 - Em relação aos locais de destino para os respectivos passeios, onde há necessidade de entrada no local, almoço, lanche e demais infra-estrtura, a Contratada tem entregado esta estrutura conforme acordado previamente?',
            '5 - Os Funcionarios da Contratada comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Segurança': [
            '1 - Os funcionários da Contratada durante a prestação de serviço no ambiente interno da escola, seguem as normas internas e orientações demandadas pelo responsável do colégio?',
            '2 - O funcionário da Contratada durante a prestação de serviço segue as normas e regras do Código Brasileiro de Trânsito, respeitando principalmente as regras de limite de velocidade?',
            '3 - Os funcionários zelam pela segurança e cuidado com os alunos e funcionários durante toda a prestação de serviço, apresentando ao serviço sem sinais de embriaguez ou sob efeito de substancia tóxica?',
            '4 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '5 - Os veículos disponibilizados para a prestação de serviços estão com os cintos de segurança adequados e em funcionamento, conforme regulamentação específica?',
            '6 - Os veículos enviados para a prestação de serviços, estão equipados com tacógrafos calibrados e aferidos pelo INMETRO?',
        ],
        'Qualidade': [
            '1 - Os profissionais enviados pela Contratada para prestação de serviços são capacitados, qualificados e devidamente treinados, seguindo todas as normas e exigências da legislação brasileira, sobretudo, da legislação de trânsito brasileira?',
            '2 - O profissional da contratada estão devidamente identificados (crachá e/ou uniforme), apresentado com cortesia e presteza, prestando uma boa relação quando solicitado?',
            '3 - Os profissionais da Contratada prestam os esclarecimentos desejados, bem como comunicam, por meio de líder ou diretamente, quaisquer fatos ou anormalidades que porventura possam prejudicar o bom andamento ou o resultado final dos serviços?',
            '4 - Os profissionais da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - A contratada possui autorizações atualizadas (licenças específicas) que a habilitem para a prestação de serviços de transporte, expedidas pelos órgãos competentes (ANTT, DER, DETRAN, BHTRANS e/ou quaisquer outros);5 - A Contratada possui seguro de Acidentes pessoais, extensivo aos passageiros, e outros exigidos por Lei?',
        ],
    },
    'AC TRANSPORTES E SERVIÇOS LTDA - ACTUR': {
        'Atividades Operacionais': [
            '1 - A Contratada disponibiliza veículos em perfeitas condições de conservação e funcionamento mecânico, limpeza externa e interna e de segurança, em conformidade com as exigências legais e demais normas existentes?',
            '2 - A Contratada disponibiliza os veículos após o recebimento da autorização de início dos serviços, nos locais e horários fixados pelo Colégio, cumprindo pontualmente os horários  acordados de saída e retorno, conforme alinhado previamente?',
            '3 - Os profissionais indicados para execução dos serviços objeto do presente contrato, possum conhecimento técnico para sua função e estão devidamente habilitados  para conduzir veículo de transporte de passageiros?',
            '4 - Em relação aos locais de destino para os respectivos passeios, onde há necessidade de entrada no local, almoço, lanche e demais infra-estrtura, a Contratada tem entregado esta estrutura conforme acordado previamente?',
            '5 - Os Funcionarios da Contratada comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Segurança': [
            '1 - Os funcionários da Contratada durante a prestação de serviço no ambiente interno da escola, seguem as normas internas e orientações demandadas pelo responsável do colégio?',
            '2 - O funcionário da Contratada durante a prestação de serviço segue as normas e regras do Código Brasileiro de Trânsito, respeitando principalmente as regras de limite de velocidade?',
            '3 - Os funcionários zelam pela segurança e cuidado com os alunos e funcionários durante toda a prestação de serviço, apresentando ao serviço sem sinais de embriaguez ou sob efeito de substancia tóxica?',
            '4 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '5 - Os veículos disponibilizados para a prestação de serviços estão com os cintos de segurança adequados e em funcionamento, conforme regulamentação específica?',
            '6 - Os veículos enviados para a prestação de serviços, estão equipados com tacógrafos calibrados e aferidos pelo INMETRO?',
        ],
        'Qualidade': [
            '1 - Os profissionais enviados pela Contratada para prestação de serviços são capacitados, qualificados e devidamente treinados, seguindo todas as normas e exigências da legislação brasileira, sobretudo, da legislação de trânsito brasileira?',
            '2 - O profissional da contratada estão devidamente identificados (crachá e/ou uniforme), apresentado com cortesia e presteza, prestando uma boa relação quando solicitado?',
            '3 - Os profissionais da Contratada prestam os esclarecimentos desejados, bem como comunicam, por meio de líder ou diretamente, quaisquer fatos ou anormalidades que porventura possam prejudicar o bom andamento ou o resultado final dos serviços?',
            '4 - Os profissionais da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - A contratada possui autorizações atualizadas (licenças específicas) que a habilitem para a prestação de serviços de transporte, expedidas pelos órgãos competentes (ANTT, DER, DETRAN, BHTRANS e/ou quaisquer outros);5 - A Contratada possui seguro de Acidentes pessoais, extensivo aos passageiros, e outros exigidos por Lei?',
        ],
    },
    'TRANSCELO TRANSPORTES LTDA': {
        'Atividades Operacionais': [
            '1 - A Contratada disponibiliza veículos em perfeitas condições de conservação e funcionamento mecânico, limpeza externa e interna e de segurança, em conformidade com as exigências legais e demais normas existentes?',
            '2 - A Contratada disponibiliza os veículos após o recebimento da autorização de início dos serviços, nos locais e horários fixados pelo Colégio, cumprindo pontualmente os horários  acordados de saída e retorno, conforme alinhado previamente?',
            '3 - Os profissionais indicados para execução dos serviços objeto do presente contrato, possum conhecimento técnico para sua função e estão devidamente habilitados  para conduzir veículo de transporte de passageiros?',
            '4 - A Contratada cumpre com antecedência e em tempo hábil, informando qualquer motivo que a impossibilite de assumir os serviços conforme estabelecido?',
            '5 - Os Funcionarios da Contratada comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Segurança': [
            '1 - Os funcionários da Contratada durante a prestação de serviço no ambiente interno da escola, seguem as normas internas e orientações demandadas pelo responsável do colégio?',
            '2 - O funcionário da Contratada durante a prestação de serviço segue as normas e regras do Código Brasileiro de Trânsito, respeitando principalmente as regras de limite de velocidade?',
            '3 - Os funcionários zelam pela segurança e cuidado com os alunos e funcionários durante toda a prestação de serviço, apresentando ao serviço sem sinais de embriaguez ou sob efeito de substancia tóxica?',
            '4 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '5 - Os veículos disponibilizados para a prestação de serviços estão com os cintos de segurança adequados e em funcionamento, conforme regulamentação específica?',
            '6 - Os veículos enviados para a prestação de serviços, estão equipados com tacógrafos calibrados e aferidos pelo INMETRO?',
        ],
        'Qualidade': [
            '1 - Os profissionais enviados pela Contratada para prestação de serviços são capacitados, qualificados e devidamente treinados, seguindo todas as normas e exigências da legislação brasileira, sobretudo, da legislação de trânsito brasileira?',
            '2 - O profissional da contratada estão devidamente identificados (crachá e/ou uniforme), apresentado com cortesia e presteza, prestando uma boa relação quando solicitado?',
            '3 - Os profissionais da Contratada prestam os esclarecimentos desejados, bem como comunicam, por meio de líder ou diretamente, quaisquer fatos ou anormalidades que porventura possam prejudicar o bom andamento ou o resultado final dos serviços?',
            '4 - Os profissionais da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - A contratada possui autorizações atualizadas (licenças específicas) que a habilitem para a prestação de serviços de transporte, expedidas pelos órgãos competentes (ANTT, DER, DETRAN, BHTRANS e/ou quaisquer outros);5 - A Contratada possui seguro de Acidentes pessoais, extensivo aos passageiros, e outros exigidos por Lei?',
        ],
    },
    'MINASCOPY NACIONAL EIRELI': {
        'Atividades Operacionais': [
            '1 - O quantitativo (quadro efetivo) de funcionários da contratada está conforme especificação e acordado em contrato?',
            '2 - Os funcionários cumprem a escala de serviço, observando pontualmente os horários de entrada e saída, sendo assíduos e pontuais ao trabalho?',
            '3 - A empresa fornece o ponto eletrônico e o mantem em pleno funcionamento, registrando e apurando os horários registrados dos respectivos funcionários?',
            '4 - A SIC é informada previamente das eventuais substituições dos funcionários da contratada?',
            '5 - Os profissionais indicados para execução dos serviços objeto do presente Instrumento, possuem conhecimento técnico necessário para operar e manusear as máquinas, bem como executar as funções que lhe forem atribuídas?',
        ],
        'Segurança': [
            '1 - Os funcionários seguem as normas internas e orientações de segurança da SIC?',
            '2 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '3 - Os funcionários zelam pela segurança e cuidado com suas entregas, conforme são demandados?',
            '4 - Os Funcionarios comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Qualidade': [
            '1 - Os funcionários da contratada executam suas atividades diárias com qualidade, atendendo todas as demandas inerentes ao objeto deste contrato?',
            '2 - Os funcionários da contratada atendem com cortesia e presteza, prestando uma boa relação quando solicitados?',
            '3 - Os funcionários da contratada comunicam-se com eficácia?',
            '4 - Os funcionários da contratada ocupam-se permanentemente no local designado para exercicio de suas funções, não se afastando deste local, salvo em situações de necessidade?',
            '5 - Os funcionários da contratada transmitem segurança na execução de suas tarefas?',
            '6 - Os funcionários da contratada zelam pelos materiais e equipamentos quando estão dentro das dependências do colégio?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - CND e CRT, relativos à Regularidade Fiscal e Trabalhista, estão atualizados?',
        ],
    },
    'OTIMIZA VIGILÂNCIA E SEG. PATRIMONIAL': {
        'Atividades Operacionais': [
            '1 - O quantitativo (quadro efetivo) de funcionários da contratada está conforme especificação e acordado em contrato?',
            '2 - Os funcionários cumprem a escala de serviço, observando pontualmente os horários de entrada e saída, sendo assíduos e pontuais ao trabalho?',
            '3 - Na ocorrência de faltas, é providenciada pela contratada a reposição do funcionário no período previsto no contrato?',
            '4 - A empresa fornece o ponto eletrônico e o mantem em pleno funcionamento, registrando e apurando os horários registrados dos respectivos funcionários?',
            '5 - A SIC é  informada previamente das eventuais substituições dos funcionários da contratada?',
            '6 - O preposto da contratada atua de maneira presente, efetiva, orientando e zelando pelos seus funcionários?',
        ],
        'Segurança': [
            '1 - Os funcionários estão devidamente uniformizados (padrão único) e identificados (crachá)?',
            '2 - Os funcionários seguem as normas internas e orientações de segurança da SIC?',
            '3 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '4 - Os funcionários zelam pela segurança e cuidado com os funcionarios e alunos do colégio?',
            '5 - Os Funcionarios comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Qualidade': [
            '1 - Os funcionários da contratada executam suas atividades diárias com qualidade, atendendo todas as demandas inerentes ao objeto deste contrato?',
            '2 - Os funcionários da contratada atendem com cortesia e presteza, prestando uma boa relação quando solicitados?',
            '3 - Os funcionários da contratada comunicam-se com eficácia?',
            '4 - Os funcionários da contratada ocupam-se permanentemente no local designado para exercicio de suas funções, não se afastando deste local, salvo em situações de necessidade?',
            '5 - Os funcionários da contratada transmitem segurança na execução de suas tarefas?',
            '6 - Os funcionários da contratada zelam pelos materiais e equipamentos quando estão dentro das dependências do colégio?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - CND e CRT, relativos à Regularidade Fiscal e Trabalhista, estão atualizados?',
        ],
    },
    'PHP SERVICE EIRELI': {
        'Atividades Operacionais': [
            '1 - O quantitativo (quadro efetivo) de funcionários da contratada está conforme especificação e acordado em contrato?',
            '2 - Os funcionários cumprem a escala de serviço, observando pontualmente os horários de entrada e saída, sendo assíduos e pontuais ao trabalho?',
            '3 - Na ocorrência de faltas, é providenciada pela contratada a reposição do funcionário no período previsto no contrato?',
            '4 - A empresa fornece o ponto eletrônico e o mantem em pleno funcionamento, registrando e apurando os horários registrados dos respectivos funcionários?',
            '5 - A SIC é  informada previamente das eventuais substituições dos funcionários da contratada?',
            '6 - O preposto da contratada atua de maneira presente, efetiva, orientando e zelando pelos seus funcionários?',
        ],
        'Segurança': [
            '1 - Os funcionários estão devidamente uniformizados (padrão único) e identificados (crachá)?',
            '2 - Os funcionários seguem as normas internas e orientações de segurança da SIC?',
            '3 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '4 - Os funcionários zelam pela segurança e cuidado com os funcionarios e alunos do colégio?',
            '5 - Os Funcionarios comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários?',
        ],
        'Qualidade': [
            '1 - Os funcionários da contratada executam suas atividades diárias com qualidade, atendendo todas as demandas inerentes ao objeto deste contrato?',
            '2 - Os funcionários da contratada atendem com cortesia e presteza, prestando uma boa relação quando solicitados?',
            '3 - Os funcionários da contratada comunicam-se com eficácia?',
            '4 - Os funcionários da contratada ocupam-se permanentemente no local designado para exercicio de suas funções, não se afastando deste local, salvo em situações de necessidade?',
            '5 - Os funcionários da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
            '6 - Os funcionários da contratada zelam pelos materiais e equipamentos quando estão dentro das dependências do colégio?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - CND e CRT, relativos à Regularidade Fiscal e Trabalhista, estão atualizados?',
        ],
    },
    'QA - IT ANSWER - CONSULTORIA - N1': {
        'Atividades Operacionais': [
            '1 - O quantitativo (quadro efetivo) de funcionários da contratada está conforme especificação e acordado em contrato?',
            '2 - Os funcionários cumprem a escala de serviço, observando pontualmente os horários de entrada e saída, sendo assíduos e pontuais ao trabalho?',
            '3 - A empresa fornece o ponto eletrônico e o mantem em pleno funcionamento, registrando e apurando os horários registrados dos respectivos funcionários?',
            '4 - A SIC é  informada previamente das eventuais substituições dos funcionários da contratada?',
            '5 - O(s) profissional (is) indicado(s) para execução dos serviços objeto do presente contrato, possue conhecimento técnico necessário para realizar as atividades pertinentes ao Analista de Suporte Tecnico em TI - N1, executando as funções que lhe forem atribuídas ?',
            '6 - o profissional N2 da Contratada, executa a coordenação da  equipe de técnicos N1 , direcionando as demandas conforme orientação da SIC?',
        ],
        'Segurança': [
            '1 - Os funcionários seguem as normas internas e orientações de segurança da SIC ?',
            '2 - Os funcionários mantem sigilo das informações das quais possuem acesso?',
            '3 - Os funcionários zelam pela segurança e cuidado com suas entregas, conforme são demandados?',
            '4 - Os Funcionarios comunicam, qualquer anormalidade em relação ao andamento dos serviços, prestando à SIC os esclarecimentos, que julgar necessários',
        ],
        'Qualidade': [
            '1 - Os funcionários da contratada executam suas atividades diárias com qualidade, atendendo todas as demandas inerentes ao objeto deste contrato?',
            '2 - Os funcionários da contratada atendem com cortesia e presteza, prestando uma boa relação quando solicitados?',
            '3 - Os funcionários da contratada comunicam-se com eficácia?',
            '4 - Os funcionários da contratada ocupam-se permanentemente no local designado para exercicio de suas funções, não se afastando deste local, salvo em situações de necessidade?',
            '5 - Os funcionários da contratada transmitem segurança e conhecimento técnico na execução de suas tarefas?',
            '6 - Os funcionários da contratada zelam pelos materiais e equipamentos quando estão dentro das dependências do colégio?',
        ],
        'Documentação': [
            '1 - Os documentos obrigatórios para análise e faturamento foram entregues dentro do prazo acordado em contrato?',
            '2 - A contratada apresentou todas as documentações exigidas, conforme contrato com os devidos recolhimentos e pagamentos?',
            '3 - A Nota Fiscal foi emitida com dados corretos?',
            '4 - CND e CRT, relativos à Regularidade Fiscal e Trabalhista, estão atualizados?',
        ],
    },
    'GULP SÃO TOMAS': {
        'Segurança': [
        ],
        'Atividades Operacionais': [
        ],
    },
}

# Funções para manipular perguntas no MongoDB
def get_perguntas():
    try:
        db = get_database()
        collection = db["perguntas"]
        
        # Verificar se já existem perguntas no banco
        if collection.count_documents({}) == 0:
            # Se não existir, inicializar com os dados padrão
            for fornecedor, categorias in perguntas_por_fornecedor.items():
                for categoria, perguntas in categorias.items():
                    collection.insert_one({
                        "fornecedor": fornecedor,
                        "categoria": categoria,
                        "perguntas": perguntas
                    })
            return perguntas_por_fornecedor
        else:
            # Se existir, retornar as perguntas do banco
            result = collection.find({})
            perguntas = {}
            for doc in result:
                fornecedor = doc["fornecedor"]
                categoria = doc["categoria"]
                lista_perguntas = doc["perguntas"]
                
                if fornecedor not in perguntas:
                    perguntas[fornecedor] = {}
                
                perguntas[fornecedor][categoria] = lista_perguntas
            
            return perguntas
    except Exception as e:
        print(f"Erro ao obter perguntas do MongoDB: {str(e)}")
        return perguntas_por_fornecedor

def add_pergunta(fornecedor, categoria, pergunta):
    if fornecedor and categoria and pergunta:
        try:
            db = get_database()
            collection = db["perguntas"]
            
            # Verificar se já existe documento para este fornecedor e categoria
            existing = collection.find_one({"fornecedor": fornecedor, "categoria": categoria})
            
            if existing:
                # Atualizar lista de perguntas
                collection.update_one(
                    {"fornecedor": fornecedor, "categoria": categoria},
                    {"$push": {"perguntas": pergunta}}
                )
            else:
                # Criar novo documento
                collection.insert_one({
                    "fornecedor": fornecedor,
                    "categoria": categoria,
                    "perguntas": [pergunta]
                })
            return True
        except Exception as e:
            print(f"Erro ao adicionar pergunta no MongoDB: {str(e)}")
            return False
    return False

def remove_pergunta(fornecedor, categoria, pergunta):
    if fornecedor and categoria and pergunta:
        try:
            db = get_database()
            collection = db["perguntas"]
            
            # Remover a pergunta da lista
            collection.update_one(
                {"fornecedor": fornecedor, "categoria": categoria},
                {"$pull": {"perguntas": pergunta}}
            )
            return True
        except Exception as e:
            print(f"Erro ao remover pergunta do MongoDB: {str(e)}")
            return False
    return False

def get_perguntas_por_fornecedor(fornecedor):
    try:
        db = get_database()
        collection = db["perguntas"]
        
        # Buscar todas as perguntas para o fornecedor
        result = collection.find({"fornecedor": fornecedor})
        
        perguntas_fornecedor = {}
        for doc in result:
            categoria = doc["categoria"]
            perguntas = doc["perguntas"]
            perguntas_fornecedor[categoria] = perguntas
        
        return perguntas_fornecedor
    except Exception as e:
        print(f"Erro ao obter perguntas do fornecedor do MongoDB: {str(e)}")
        # Fallback para dados locais
        if fornecedor in perguntas_por_fornecedor:
            return perguntas_por_fornecedor[fornecedor]
        return {}

# Inicializar a coleção se for a primeira execução
if __name__ == "__main__":
    get_perguntas()
