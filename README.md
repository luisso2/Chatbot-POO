# Chatbot-POO
## Descrição do projeto
O desafio deste projeto é desenvolver um chatbot para o aprendizado de Programação Orientada a Objetos (POO) por meio da técnica de Aprendizagem através do Ensino (LBT). Aprendizagem através do ensino é uma técnica pedagógica na qual o aluno desenvolve o seu conhecimento ensinando outros alunos, em uma relação tutor-aluno esta função de aluno pode ser substituída por um LLM.

## Metodologia
Propõe-se a implementação de um sistema multiagentes que atuará como aluno no contexto de aprendizagem através do ensino, onde o usuário (aluno de graduação) desempenha o papel de tutor. O sistema é baseado na arquitetura desenvolvida em [1] e está organizado em duas componentes principais:
- Reflect-Response: Agente ensinável que extrai informações do prompt do tutor, atualiza o seu estado e gera respostas;
- Mode-Shifting: Agente responsável por decidir  o momento ideal para a transição entre os dois modos de operação do agente ensinável:
  - Modo Receptor de Ajuda: Aprende passivamente com o tutor, solicitando e processando as explicações do usuário.
  - Modo Questionador: Formula perguntas instigantes para estimular e aprofundar a construção de conhecimento do usuário.

## Etapas do projeto
- 1 - Desenvolver dataset de perguntas e respostas para avaliar o bloco de Refletir-Responder;
- 2 - Implementar e validar o bloco Reflect-Respond;
- 3 - Implementar o bloco Mode-shifting;
- 4 - Implementar a interface do chatbot.

## Métricas
| Métrica | Forma de medição | Tipo de teste |
| :---: | :---: | :---: |
| Reconfigurabilidade | Mudança de desempenho com diferentes níveis de conhecimento | Resposta |
| Persistência | Variação após conversas aleatórias | Resposta antes e depois |
| Adaptabilidade | Variação após ensino correto/incorreto | Resposta antes e depois |

## Cronograma
| Estágio | Data de entrega	| Atividade
|:---:|:---:|:---:|
| Entrega I | 30 de outubro | Plano de trabalho |
| Entrega II | 06 de novembro | Dataset de validação |
| Entrega III | 13 de novembro | Reflect-Response e Validação |

## Referências
[1]	H. Jin, S. Lee, H. Shin, and J. Kim, "Teach AI How to Code: Using Large Language Models as Teachable Agents for Programming Education," in Proceedings of the 2024 CHI Conference on Human Factors in Computing Systems (CHI '24), Honolulu, HI, USA, 2024, Art. no. 652. doi: 10.1145/3613904.3642349.

[2]	M. Zhu, L. Xu, and B. Ericson, "A systematic review of research on large language models for computer programming education," 2025. [Online]. Available: https://arxiv.org/abs/2506.21818
| Entrega final | 27 de novembro | Interface gráfica com Mode-Shifting |
