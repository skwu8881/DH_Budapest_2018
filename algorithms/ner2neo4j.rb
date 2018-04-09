require 'json'

nodes = JSON.parse(`curl -H accept:application/json -H content-type:application/json \
  -d '{"statements":[{"statement":"MATCH (n) RETURN n"}]}' \
  http://localhost:7474/db/data/transaction/commit`)

edges = (0...nodes['results'][0]['data'].size).map { |i| [nodes['results'][0]['data'][i]['meta'][0]['id'], JSON.parse(`curl -H accept:application/json -H content-type:application/json http://localhost:7474/db/data/node/#{nodes['results'][0]['data'][i]['meta'][0]['id']}/relationships/out`)[0]['end'].match(/node\/(\d+)/)[1].to_i] }

word2label = {}
JSON.parse(`cat algorithms/Json.txt`).each do |obj|
  word2label[obj['word']] = obj['cate'] unless obj['cate'] == 'None'
end

res = {
  results: [
    columns: nodes['results'][0]['columns'],
    data: [
      graph: {
        nodes: (0...nodes['results'][0]['data'].size).map { |i| {id: nodes['results'][0]['data'][i]['meta'][0]['id'], labels: [word2label[nodes['results'][0]['data'][i]['row'][0]['name']]], name: nodes['results'][0]['data'][i]['row'][0]['name'] } },
        relationships: (0...edges.size).map { |i| {id: i, type: ?-, startNode: edges[i][0], endNode: edges[i][1] } }
      }
    ]
  ],
  errors: []
}

File.open('public/json/neo4jData.json', 'w') { |f| f.write(res.to_json) }
