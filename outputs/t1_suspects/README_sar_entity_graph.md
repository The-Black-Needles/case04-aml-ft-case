# Grafo entidade 360° — SAR C101208

Esta pasta adiciona uma visão gráfica do caso usado no SAR,

## Arquivos

- `08_sar_entity_nodes_C101208,csv`: nós do grafo. como cliente. KYC. rails. países. merchants e alertas,
- `09_sar_entity_edges_C101208,csv`: relações entre os nós. com evidência e nota de risco,
- `10_sar_entity_graph_C101208,mmd`: diagrama Mermaid para visualizar no GitHub ou em ferramentas compatíveis,
- `10_sar_entity_graph_summary_C101208,json`: resumo estruturado do caso,
- `11_sar_entity_graph_C101208,png`: imagem pronta para apresentação,

## Como explicar

“Eu criei esse grafo para consolidar a visão 360° do SAR, No centro está o cliente C101208, Ao redor aparecem perfil KYC. renda declarada. rails usados. países envolvidos. grupo de merchants de risco e alertas acionados, O objetivo não é provar crime pelo grafo. mas facilitar a leitura investigativa e mostrar por que o caso foi priorizado,”

## Principais sinais

- Cliente movimentou R$ 162.018,32 em 34 transações,
- Renda anual declarada: R$ 13.047,00,
- 9 transações cross-border,
- 1 hit de sanctions screening,
- País de alto risco envolvido: SY,
- 27 merchants/contrapartes merchant ligados ao cliente. com presença de MCC/flags de risco,

## Uso na apresentação

Abrir primeiro o PNG:

`outputs/t1_suspects/11_sar_entity_graph_C101208,png`

Depois. se quiser demonstrar rastreabilidade. abrir os CSVs de nós e arestas,
