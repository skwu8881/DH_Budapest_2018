class TextminingController < ApplicationController
  skip_before_action :verify_authenticity_token

  def index

  end

  def submit_article
    File.open("algorithms/input.txt", "w") { |f| f.write(params[:article]) }
    `python3 algorithms/myNER2.py`
    `algorithms/query`
    s = File.open("algorithms/resultWeight.txt").each_line.map(&:split).map { |s| s.join ?, } .join(?\n)
    File.open("public/flare.csv", 'w') { |f| f.write("id,value\n" + s) }
    respond_to do |f|
      f.json { render json: { statistics_html:
<<-'EOS',
<svg width="960" height="960" font-family="sans-serif" font-size="10" text-anchor="middle"></svg>
<script src="https://d3js.org/d3.v4.min.js"></script>
<script>

var svg_bubble = d3.select("svg"),
    width = +svg_bubble.attr("width"),
    height = +svg_bubble.attr("height");

var format = d3.format(",d");

var color = d3.scaleOrdinal(d3.schemeCategory20c);

var pack = d3.pack()
    .size([width, height])
    .padding(1.5);

d3.csv("flare.csv", function(d) {
  d.value = +d.value;
  if (d.value) return d;
}, function(error, classes) {
  if (error) throw error;

  var root = d3.hierarchy({children: classes})
      .sum(function(d) { return d.value; })
      .each(function(d) {
        if (id = d.data.id) {
          var id, i = id.lastIndexOf(".");
          d.id = id;
          d.package = id.slice(0, i);
          d.class = id.slice(i + 1);
        }
      });

  var node = svg_bubble.selectAll(".node")
    .data(pack(root).leaves())
    .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

  node.append("circle")
      .attr("id", function(d) { return d.id; })
      .attr("r", function(d) { return d.r; })
      .style("fill", function(d) { return color(d.package); });

  node.append("clipPath")
      .attr("id", function(d) { return "clip-" + d.id; })
    .append("use")
      .attr("xlink:href", function(d) { return "#" + d.id; });

  node.append("text")
      .attr("clip-path", function(d) { return "url(#clip-" + d.id + ")"; })
    .selectAll("tspan")
    .data(function(d) { return d.class.split(/(?=[A-Z][^A-Z])/g); })
    .enter().append("tspan")
      .attr("x", 0)
      .attr("y", function(d, i, nodes) { return 13 + (i - nodes.length / 2 - 0.5) * 10; })
      .text(function(d) { return d; });

  node.append("title")
      .text(function(d) { return d.id + "\n" + format(d.value); });
});

</script>
EOS
tags_html:
<<-EOS,
#{
n = File.open("algorithms/input.txt").each_line.map(&:to_s).join ?\n
s = File.open("algorithms/Json.txt").each_line.map(&:to_s).join
u = JSON.parse(s).to_a.reject { |i| i['word'].match?(/\A[`'"]+\z/) rescue true }

n_ptr, u_ptr = 0, 0
res = '<div class="entities">'
until n_ptr == n.size
  w = u[u_ptr]['word'].strip rescue nil
  if u_ptr < u.size && n[n_ptr, w.size] == w
    res += '<mark data-entity="' + u[u_ptr]['cate'] + '">' if u[u_ptr]['cate'] != 'None'
    res += w
    res += '</mark>' if u[u_ptr]['cate'] != 'None'
    n_ptr += w.size
    u_ptr += 1
  else
    res += n[n_ptr].force_encoding("ISO-8859-1").encode("UTF-8")
    n_ptr += 1
  end
end
res += '</div>'
}
EOS
sentiment_html:
<<-EOS,
#{
js = JSON.parse(`curl -d "text=#{File.open("algorithms/input.txt").each_line.map(&:to_s).join ?\n}" http://text-processing.com/api/sentiment/`)
"<p>The text is most likely <strong style=\"color:#{js['label'] == 'pos' ? 'green' : js['label'] == 'neg' ? 'red' : 'grey'}\">#{js['label']}</strong></p>\n<p>Probability: #{js['probability'][js['label']]}%</p>"
}
EOS
network_html:
<<-'EOS'
<style>

.link line {
  stroke: #999;
  stroke-opacity: 0.6;
}

.labels text {
  pointer-events: none;
  font: 10px sans-serif;
}

</style>
<div id="svg_graph"></div>
<script src="https://d3js.org/d3.v4.min.js"></script>
<script src="assets/js/d3-ellipse-force.js"></script>
<script src="graph.js"></script>
<script>

var svg_graph = d3.select("#svg_graph").append("svg").style("width", 960).style("height", 600),
    width = 960,
    height = 600;

var color = d3.scaleOrdinal(d3.schemeCategory20);

var nd;
for (var i=0; i<graph.nodes.length; i++) {
  nd = graph.nodes[i];
  nd.rx = nd.id.length * 4.5; 
  nd.ry = 12;
} 

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("collide", d3.ellipseForce(6, 0.5, 5))
    .force("center", d3.forceCenter(width / 2, height / 2));

var link = svg_graph.append("g")
    .attr("class", "link")
  .selectAll("line")
  .data(graph.links)
  .enter().append("line")
    .attr("stroke-width", function(d) { return Math.sqrt(d.value); });

var node = svg_graph.append("g")
    .attr("class", "node")
  .selectAll("ellipse")
  .data(graph.nodes)
  .enter().append("ellipse")  
    .attr("rx", function(d) { return d.rx; })
    .attr("ry", function(d) { return d.ry; })
    .attr("fill", function(d) { return color(d.group); })
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

var text = svg_graph.append("g")
    .attr("class", "labels")
  .selectAll("text")
  .data(graph.nodes)
  .enter().append("text")  
    .attr("dy", 2)
    .attr("text-anchor", "middle")
    .text(function(d) {return d.id})
    .attr("fill", "white");


simulation
  .nodes(graph.nodes)
  .on("tick", ticked);

simulation.force("link")
     .links(graph.links);

function ticked() {
  link
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  node
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });
  text
      .attr("x", function(d) { return d.x; })
      .attr("y", function(d) { return d.y; });

}

function dragstarted(d) {
  if (!d3.event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(d) {
  d.fx = d3.event.x;
  d.fy = d3.event.y;
}

function dragended(d) {
  if (!d3.event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}

</script>
EOS
        } # FIXME: there seems to be a constraint on input size
      }
    end
  end
end
