from services.croma_service import CromaService

service = CromaService()
queries = [
    'Apple iPhone 15 128GB Black',
    'Apple iPhone 15 128GB',
    'iPhone 15 128GB Black',
    'iPhone 15 128GB',
    'iPhone 15 Black',
    'Apple iPhone 15 Black',
    'iPhone 15',
]
for query in queries:
    results = service.search_products(query, max_results=5)
    print('QUERY:', query, 'RESULTS:', len(results))
    for item in results[:5]:
        print(' ', item.get('title'), item.get('price'))
