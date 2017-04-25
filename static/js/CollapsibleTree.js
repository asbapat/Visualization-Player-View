/**
 * Created by asb on 4/17/2017.
 */

function collapsibleTree() {

    d3.selectAll("svg").remove();
    var margin = {top: 20, right: 20, bottom: 30, left: 200},
        width = 1200 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var i = 0,
        duration = 750,
        root;

    var tree = d3.layout.tree()
        .size([height, width]);

    var diagonal = d3.svg.diagonal()
        .projection(function (d) {
            return [d.y, d.x];
        });
    var svg = d3.select("#collapsibleTree").append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.json("./static/leaguejson/league.json", function (error, data) {
        if (error) throw error;

        root = data;
        root.x0 = height / 2;
        root.y0 = 0;



        root.children.forEach(collapse);
        update(root);
    });

    d3.select(self.frameElement).style("height", "800px");

    function collapse(d) {
        if (d.children) {
            d._children = d.children;
            d._children.forEach(collapse);
            d.children = null;
        }
    }
    function update(source) {

        var nodes = tree.nodes(root).reverse(),
            links = tree.links(nodes);

        // Normalize for fixed-depth.
        nodes.forEach(function (d) {
            d.y = d.depth * 120;
        });

        // Update the nodes…
        var node = svg.selectAll("g.node")
            .data(nodes, function (d) {
                return d.id || (d.id = ++i);
            });

        // Enter any new nodes at the parent's previous position.
        var nodeEnter = node.enter().append("g")
            .attr("class", "node")
            .attr("transform", function (d) {
                return "translate(" + source.y0 + "," + source.x0 + ")";
            })
            .on("click", click);

        nodeEnter.append("circle")
            .attr("r", 1e-6)
            .style("fill", function (d) {
                return d._children ? "lightsteelblue" : "#fff";
            });

        nodeEnter.append("text")
            .attr("x", function (d) {
                return d.children || d._children ? -10 : 10;
            })
            .attr("dy", ".35em")
            .attr("text-anchor", function (d) {
                return d.children || d._children ? "end" : "start";
            })
            .text(function (d) {
                return d.name;
            })
            .style("fill-opacity", 1e-6)
            .style("font-weight","bold")
            .style("font-size", "0.75em");

        nodeEnter.append("image")
            .attr("xlink:href", function(d){
                return d.image;
            })
            .attr("x", "-5px")
            .attr("y","-8px")
            .attr("width","15px")
            .attr("height", "15px");

        nodeEnter.append("image")
            .attr("xlink:href", function(d){
                return d.jersey_image;
            })
            .attr("x", "-7px")
            .attr("y","-8px")
            .attr("width","15px")
            .attr("height", "15px");

        // Transition nodes to their new position.
        var nodeUpdate = node.transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + d.y + "," + d.x + ")";
            });

        nodeUpdate.select("circle")
            .attr("r", 4.5)
            .style("fill", function (d) {
                return d._children ? "lightsteelblue" : "#fff";
            });

        nodeUpdate.select("text")
            .style("fill-opacity", 1);

        // Transition exiting nodes to the parent's new position.
        var nodeExit = node.exit().transition()
            .duration(duration)
            .attr("transform", function (d) {
                return "translate(" + source.y + "," + source.x + ")";
            })
            .remove();

        nodeExit.select("circle")
            .attr("r", 1e-6);

        nodeExit.select("text")
            .style("fill-opacity", 1e-6);

        // Update the links…
        var link = svg.selectAll("path.link")
            .data(links, function (d) {
                return d.target.id;
            });

        // Enter any new links at the parent's previous position.
        link.enter().insert("path", "g")
            .attr("class", "link")
            .attr("d", function (d) {
                var o = {x: source.x0, y: source.y0};
                return diagonal({source: o, target: o});
            });

        // Transition links to their new position.
        link.transition()
            .duration(duration)
            .attr("d", diagonal);

        // Transition exiting nodes to the parent's new position.
        link.exit().transition()
            .duration(duration)
            .attr("d", function (d) {
                var o = {x: source.x, y: source.y};
                return diagonal({source: o, target: o});
            })
            .remove();

        // Stash the old positions for transition.
        nodes.forEach(function (d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }

// Toggle children on click.
    function click(d) {

        if(!d._children){
            d3.select("#tableContent").remove();
            // var profile = svg.append("g")
            //     .append("svg:image")
            //     .attr("xlink:href", d.player_image)
            //     .attr("width",150)
            //     .attr("height",150)
            //     .attr("x",850)
            //     .attr("y",0);

            var playerTable = d3.select('#playerDetails')
                .append('table')
                .attr('id', 'tableContent')
                .attr("width", "100%")
                .attr("height", height + margin.top + margin.bottom);

            var columns = [{src:d.player_image}];
            var logo = [{src:d.player_logo}];
            var headers = playerTable.append('thead').append('tr')
                .selectAll('th')
                .data(columns)
                .enter()
                .append('th');

            headers.append('img')
                .attr('src',function (d) {return d.src;})
                .attr('width',100)
                .attr('height', 100);
            //.style("float", "left");

            headers.append('text')
                .data([d.name])
                .text(function (d) {return d;})
                .attr("dx",10)
                .style("padding-left", "70px");

            headers.append('text')
                .data([d.position])
                .text(function (d) {return d;})
                .attr("dx",10)
                .style("padding-left", "25px");

            headers.append('img')
                .data(logo)
                .attr('src',function (d) {return d.src;})
                .attr('width',150)
                .attr('height', 80)
                .style("float", "right");
                //.style("padding-left", "20px");
            // .data([d.name, d.position])
            //  .enter()
            //  .append('th')
            //  .text(function(d) { return d; });


            // var rows = playerTable.append('tbody').selectAll('tr')
            //     .data(d)
            //     .enter()
            //     .append('tr');
            //
            // rows.selectAll('td')
            //     .data(d)
            //     .enter()
            //     .append('td')
            //     .text(function(d) {
            //         return d.position;
            //     });
        }
        if (d.children) {
            d._children = d.children;
            d.children = null;
            d3.select("#teamlogo").remove();
        } else {
            d.children = d._children;
            d._children = null;
            d3.select("#teamlogo").remove();

            var teamDetails = svg.append("g")
                .append("svg:image")
                .attr("xlink:href", d.image)
                .attr("width",150)
                .attr("height",150)
                .attr("id", "teamlogo")
                .attr("x",850)
                .attr("y",0);
        }
        if (d.parent) {
            d.parent.children.forEach(function(element) {
                if (d !== element) {
                    collapse(element);
                }
            });
        }
        update(d);
    }
}
