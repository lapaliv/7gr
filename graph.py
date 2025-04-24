import rdflib
import networkx as nx
import matplotlib.pyplot as plt

# Заменить путь к своему .n3 файлу
ttl_file_path = "knowledgebase.n3"

# Загружаем RDF-граф из файла
g = rdflib.Graph()
g.parse(ttl_file_path, format="ttl")

# Создаем NetworkX граф
G = nx.DiGraph()

# Добавляем связи (rdf:type и rdfs:subClassOf)
for s, p, o in g:
    if p in [rdflib.RDF.type, rdflib.RDFS.subClassOf]:
        G.add_edge(str(s), str(o), label=str(p).split('#')[-1])

# Настройки визуализации
plt.figure(figsize=(16, 12))
pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
edge_labels = nx.get_edge_attributes(G, 'label')

# Отрисовка
nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=800)
nx.draw_networkx_labels(G, pos, font_size=8)
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=12)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

plt.title("RDF Graph: Class Relationships", fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.show()
