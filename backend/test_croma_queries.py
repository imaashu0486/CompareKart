from services.croma_service import CromaService

service = CromaService()
queries = ['Apple iPhone 15 128Gb Black', 'iPhone 15', 'Apple iPhone 15', 'iPhone', 'Apple']
for query in queries:
    results = service.search_products(query, max_results=3)
    print('QUERY:', query, 'RESULTS:', len(results))
    for item in results[:3]:
        print(' ', item.get('title'), item.get('price'), item.get('url'))
